#!/usr/bin/env python3
"""Run the three-model cross-product historical allocation backtest.

Every fold predicts ``t + 1`` from the observed state at ``t``.  The target
label is used only to form the oracle allocation total and to score the output;
it never enters a model fit, decoder fit, or LDN epoch-selection pass.  This
is deliberately separate from the v2 planning run, whose purpose is a
2025-origin conditional scenario rollout rather than historical validation.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import statistics
import time
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import numpy as np
import rasterio

try:
    from .run_geosos_flus import (
        DEFAULT_BINARY as FLUS_BINARY,
        FlusInputs,
        _write_like as write_flus_state,
        simulate_year,
        train_suitability,
    )
    from .run_geospatial_kernel import (
        AbuDhabiInputs,
        _write_state as write_kernel_state,
        allocate_action,
        probability_cube,
    )
    from .run_paper58_abu_dhabi import (
        BenchmarkData,
        _write_state as write_ldn_state,
        choose_device,
        predict_tiled,
        train_decoder,
        train_ldn,
    )
    from .run_rolling_backtest import _fit_window, valid_through_year
    from .shared import (
        CLASSES,
        class_counts,
        evaluate_prediction,
        feasible_target_counts,
        paired_model_difference_bootstrap_ci,
        random_feasible_allocation,
        spatial_block_bootstrap_ci,
    )
except ImportError:  # Direct execution from this benchmark directory.
    from run_geosos_flus import (  # type: ignore
        DEFAULT_BINARY as FLUS_BINARY,
        FlusInputs,
        _write_like as write_flus_state,
        simulate_year,
        train_suitability,
    )
    from run_geospatial_kernel import (  # type: ignore
        AbuDhabiInputs,
        _write_state as write_kernel_state,
        allocate_action,
        probability_cube,
    )
    from run_paper58_abu_dhabi import (  # type: ignore
        BenchmarkData,
        _write_state as write_ldn_state,
        choose_device,
        predict_tiled,
        train_decoder,
        train_ldn,
    )
    from run_rolling_backtest import _fit_window, valid_through_year  # type: ignore
    from shared import (  # type: ignore
        CLASSES,
        class_counts,
        evaluate_prediction,
        feasible_target_counts,
        paired_model_difference_bootstrap_ci,
        random_feasible_allocation,
        spatial_block_bootstrap_ci,
    )


HERE = Path(__file__).resolve().parent
DEFAULT_OUTPUT = HERE / "artifacts" / "arcgis_v2_historical_backtest"
SEEDS = (31, 47, 73)
TARGET_YEARS = (2021, 2022, 2023, 2024, 2025)
MODEL_IDS = ("geosos_flus", "geospatial_kernel", "paper58")
ZERO_MODELS = ("persistence", "random_minimum_change")
BOOTSTRAP_RESAMPLES = 1000
BOOTSTRAP_BLOCK_SIZE = 8
SOURCE_TRACKS = ("arcgis", "dynamic_world")
V1_ROOT = HERE.parent / "abu_dhabi_land_use_v1"


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _read_band(path: Path) -> np.ndarray:
    with rasterio.open(path) as dataset:
        return dataset.read(1)


def _configure_source_track(
    source_track: str,
    *,
    inputs: AbuDhabiInputs,
    flus_inputs: FlusInputs,
    ldn_data: BenchmarkData,
) -> dict[str, Any]:
    if source_track == "arcgis":
        return {
            "id": "arcgis_sentinel2_10m_landcover",
            "display_name": "ArcGIS Sentinel2_10m_LandCover",
            "available_years": list(range(2017, 2026)),
            "quality_semantics": "100 m majority fraction after canonical class mapping",
            "native_resolution_m": 10,
        }
    if source_track != "dynamic_world":
        raise ValueError(f"unsupported_source_track:{source_track}")
    years = tuple(range(2017, 2025))
    state_root = V1_ROOT / "artifacts" / "gee" / "land_cover"
    states = {
        year: _read_band(state_root / f"land_cover_{year}_100m.tif")
        for year in years
    }
    qualities = {
        year: _read_band(state_root / f"land_cover_quality_{year}_100m.tif")
        for year in years
    }
    inputs.states = states
    inputs.quality = qualities
    flus_inputs.states = states
    ldn_data.states = states
    return {
        "id": "google_dynamic_world_v1",
        "display_name": "Google Dynamic World V1",
        "available_years": list(years),
        "quality_semantics": "annual mean top-class probability",
        "native_resolution_m": 10,
    }


def _relative(path: Path) -> str:
    try:
        return path.resolve().relative_to(HERE.resolve()).as_posix()
    except ValueError:
        return str(path.resolve())


def _write_prediction(
    path: Path,
    prediction: np.ndarray,
    *,
    reference: dict[str, Any],
    valid: np.ndarray,
) -> dict[str, Any]:
    write_kernel_state(path, prediction, reference, valid_mask=valid)
    return {
        "path": _relative(path),
        "sha256": _sha256(path),
        "size_bytes": path.stat().st_size,
    }


def _fold_transitions(origin_year: int) -> tuple[tuple[int, int], ...]:
    """Return LDN fit transitions ending before the held-out validation year."""

    transitions = tuple((year, year + 1) for year in range(2017, origin_year - 1))
    if not transitions:
        raise ValueError(f"insufficient_ldn_history_for_origin:{origin_year}")
    return transitions


def _action_vector(target_counts: dict[int, int], start_counts: dict[int, int]) -> np.ndarray:
    target = np.asarray([target_counts[value] for value in CLASSES], dtype=np.float32)
    start = np.asarray([start_counts[value] for value in CLASSES], dtype=np.float32)
    total = float(target.sum())
    return np.concatenate([target / total, (target - start) / total]).astype(np.float32)


def _paper58_prediction(
    data: BenchmarkData,
    *,
    origin_year: int,
    target_counts: dict[int, int],
    training_valid: np.ndarray,
    evaluation_valid: np.ndarray,
    hard: np.ndarray,
    seed: int,
    device: Any,
    epochs: int,
    batch_size: int,
    learning_rate: float,
) -> tuple[np.ndarray, dict[str, Any]]:
    """Fit GeoFM-LDN without exposing the target-year observation."""

    # Decoder labels end before the validation/origin state. The LDN selection
    # transition is origin-1 -> origin; the test target is never read in fit.
    label_years = tuple(range(2017, origin_year))
    validation_transition = (origin_year - 1, origin_year)
    fit_transitions = _fold_transitions(origin_year)
    data.valid = np.asarray(training_valid, dtype=bool)
    decoder, decoder_report = train_decoder(
        data,
        seed=seed,
        label_years=label_years,
        validation_year=origin_year,
    )
    model, training = train_ldn(
        data,
        decoder=decoder,
        seed=seed,
        epochs=epochs,
        batch_size=batch_size,
        learning_rate=learning_rate,
        device=device,
        fit_transitions=fit_transitions,
        validation_transition=validation_transition,
    )
    start_counts = class_counts(data.states[origin_year], evaluation_valid)
    predicted_embedding = predict_tiled(
        model,
        data.embedding(origin_year),
        _action_vector(target_counts, start_counts),
        device=device,
    )
    predicted_embedding[:, hard & evaluation_valid] = data.embedding(origin_year)[:, hard & evaluation_valid]
    logits = decoder.coef_ @ predicted_embedding.reshape(64, -1) + decoder.intercept_[:, None]
    logits -= logits.max(axis=0, keepdims=True)
    probability = np.exp(logits)
    probability /= probability.sum(axis=0, keepdims=True)
    probability = probability.reshape(len(CLASSES), *evaluation_valid.shape).astype(np.float32)
    prediction, allocation = allocate_action(
        data.states[origin_year],
        probability,
        valid=evaluation_valid,
        hard=hard,
        target_counts=target_counts,
    )
    return prediction, {
        "decoder": decoder_report,
        "training": training,
        "fit_label_years": list(label_years),
        "fit_transitions": [list(value) for value in fit_transitions],
        "selection_transition": list(validation_transition),
        "target_year_used_in_fit": False,
        "allocation": allocation,
    }


def _flus_prediction(
    inputs: FlusInputs,
    *,
    binary: Path,
    origin_year: int,
    target_year: int,
    target_counts: dict[int, int],
    training_valid: np.ndarray,
    evaluation_valid: np.ndarray,
    hard: np.ndarray,
    seed: int,
    work_root: Path,
) -> tuple[np.ndarray, dict[str, Any]]:
    fit_years = tuple(range(2017, origin_year + 1))
    inputs.valid = np.asarray(training_valid, dtype=bool)
    probability, training = train_suitability(
        inputs,
        binary=binary,
        seed=seed,
        work_root=work_root / "ann",
        target_driver_year=origin_year,
        feature_mode="baseline_7",
        fit_years=fit_years,
        include_road_snapshot=False,
    )
    action = {
        "target_year": target_year,
        "feasible_target_counts": {str(key): value for key, value in target_counts.items()},
    }
    prediction, simulation = simulate_year(
        inputs.states[origin_year],
        probability,
        action=action,
        inputs=inputs,
        binary=binary,
        seed=seed,
        work_root=work_root / "ca",
        valid_mask=evaluation_valid,
        hard_exclusion_mask=hard,
    )
    return prediction, {
        "training": training,
        "fit_label_years": list(fit_years),
        "target_year_used_in_fit": False,
        "simulation": simulation,
    }


def _kernel_prediction(
    inputs: AbuDhabiInputs,
    *,
    origin_year: int,
    target_counts: dict[int, int],
    training_valid: np.ndarray,
    evaluation_valid: np.ndarray,
    hard: np.ndarray,
    seed: int,
) -> tuple[np.ndarray, dict[str, Any]]:
    model, training = _fit_window(
        inputs,
        origin_year=origin_year,
        seed=seed,
        training_valid=training_valid,
    )
    probability = probability_cube(
        model,
        inputs,
        inputs.states[origin_year],
        driver_year=origin_year,
        valid_mask=training_valid,
        include_road_snapshot=False,
    )
    prediction, allocation = allocate_action(
        inputs.states[origin_year],
        probability,
        valid=evaluation_valid,
        hard=hard,
        target_counts=target_counts,
    )
    return prediction, {
        "training": training,
        "target_year_used_in_fit": False,
        "road_snapshot_features_used": False,
        "allocation": allocation,
    }


def _metric_summary(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    result = []
    for target_year in TARGET_YEARS:
        for model_id in (*MODEL_IDS, *ZERO_MODELS):
            selected = [
                row for row in rows
                if row["target_year"] == target_year and row["model_id"] == model_id
            ]
            if not selected:
                continue
            metrics = {}
            for metric in (
                "change_figure_of_merit",
                "change_f1",
                "overall_accuracy",
                "macro_f1",
            ):
                values = [float(row["evaluation"][metric]) for row in selected]
                metrics[metric] = {
                    "mean": float(statistics.mean(values)),
                    "population_standard_deviation": float(statistics.pstdev(values)),
                    "values": values,
                }
            result.append(
                {
                    "origin_year": target_year - 1,
                    "target_year": target_year,
                    "model_id": model_id,
                    "seed_count": len(selected),
                    "metrics": metrics,
                }
            )
    return result


def run(
    *,
    output_root: Path,
    binary: Path,
    seeds: tuple[int, ...],
    target_years: tuple[int, ...],
    epochs: int,
    batch_size: int,
    learning_rate: float,
    requested_device: str,
    bootstrap_resamples: int,
    source_track: str,
) -> dict[str, Any]:
    if not binary.is_file() or not binary.stat().st_mode & 0o111:
        raise FileNotFoundError(f"flus_binary_not_executable:{binary}")
    if source_track not in SOURCE_TRACKS:
        raise ValueError(f"unsupported_source_track:{source_track}")
    output_root = output_root.resolve()
    inputs = AbuDhabiInputs()
    flus_inputs = FlusInputs()
    ldn_data = BenchmarkData(HERE)
    source = _configure_source_track(
        source_track,
        inputs=inputs,
        flus_inputs=flus_inputs,
        ldn_data=ldn_data,
    )
    allowed_target_years = tuple(source["available_years"])[4:]
    if not target_years or any(year not in allowed_target_years for year in target_years):
        raise ValueError(
            f"unsupported_target_years_for_{source_track}:{target_years}:"
            f"allowed={allowed_target_years}"
        )
    device = choose_device(requested_device)
    if not np.array_equal(inputs.valid, flus_inputs.valid) or not np.array_equal(inputs.valid, ldn_data.valid):
        raise RuntimeError("cross_model_valid_mask_mismatch")
    output_root.mkdir(parents=True, exist_ok=True)
    rows: list[dict[str, Any]] = []
    predictions: dict[tuple[int, int, str], np.ndarray] = {}
    started = time.perf_counter()

    for target_year in target_years:
        origin_year = target_year - 1
        training_valid = valid_through_year(inputs, origin_year)
        target = inputs.states[target_year]
        evaluation_valid = training_valid & np.isin(target, CLASSES)
        hard = evaluation_valid & np.isin(inputs.states[origin_year], (1, 4))
        desired = class_counts(target, evaluation_valid)
        target_counts = feasible_target_counts(
            desired,
            origin_state=inputs.states[origin_year],
            valid_mask=evaluation_valid,
            hard_exclusion_mask=hard,
        )
        fold = {
            "origin_year": origin_year,
            "target_year": target_year,
            "source_track": source_track,
            "fit_uses_observations_through_year": origin_year,
            "target_observation_used_only_for": [
                "oracle_target_class_counts",
                "evaluation",
                "evaluation_coverage_mask",
            ],
            "road_snapshot_features_used": False,
            "training_valid_pixel_count": int(training_valid.sum()),
            "evaluation_valid_pixel_count": int(evaluation_valid.sum()),
            "hard_exclusion_pixel_count": int(hard.sum()),
            "observed_target_counts": {str(key): value for key, value in desired.items()},
            "feasible_oracle_target_counts": {str(key): value for key, value in target_counts.items()},
        }
        for seed in seeds:
            model_results: list[tuple[str, np.ndarray, dict[str, Any]]] = []
            kernel_prediction, kernel_trace = _kernel_prediction(
                inputs,
                origin_year=origin_year,
                target_counts=target_counts,
                training_valid=training_valid,
                evaluation_valid=evaluation_valid,
                hard=hard,
                seed=seed,
            )
            model_results.append(("geospatial_kernel", kernel_prediction, kernel_trace))
            flus_prediction, flus_trace = _flus_prediction(
                flus_inputs,
                binary=binary.resolve(),
                origin_year=origin_year,
                target_year=target_year,
                target_counts=target_counts,
                training_valid=training_valid,
                evaluation_valid=evaluation_valid,
                hard=hard,
                seed=seed,
                work_root=output_root / "work" / f"target_{target_year}" / f"seed_{seed}" / "geosos_flus",
            )
            model_results.append(("geosos_flus", flus_prediction, flus_trace))
            paper_prediction, paper_trace = _paper58_prediction(
                ldn_data,
                origin_year=origin_year,
                target_counts=target_counts,
                training_valid=training_valid,
                evaluation_valid=evaluation_valid,
                hard=hard,
                seed=seed,
                device=device,
                epochs=epochs,
                batch_size=batch_size,
                learning_rate=learning_rate,
            )
            model_results.append(("paper58", paper_prediction, paper_trace))
            model_results.extend(
                [
                    ("persistence", inputs.states[origin_year].copy(), {"is_zero_model": True}),
                    (
                        "random_minimum_change",
                        random_feasible_allocation(
                            inputs.states[origin_year],
                            valid_mask=evaluation_valid,
                            hard_exclusion_mask=hard,
                            target_counts=target_counts,
                            seed=seed + target_year * 1000,
                        ),
                        {"is_zero_model": True, "random_seed": seed + target_year * 1000},
                    ),
                ]
            )
            for model_id, prediction, trace in model_results:
                exact_count_models = {
                    "geospatial_kernel",
                    "paper58",
                    "random_minimum_change",
                }
                if model_id in exact_count_models and not np.array_equal(
                    np.asarray([class_counts(prediction, evaluation_valid)[value] for value in CLASSES]),
                    np.asarray([target_counts[value] for value in CLASSES]),
                ):
                    raise AssertionError(f"oracle_count_not_exact:{target_year}:{seed}:{model_id}")
                evaluation = evaluate_prediction(
                    prediction,
                    origin_state=inputs.states[origin_year],
                    observed_target=target,
                    valid_mask=evaluation_valid,
                    hard_exclusion_mask=hard,
                    requested_counts=target_counts,
                )
                output_path = output_root / "predictions" / f"target_{target_year}" / f"seed_{seed}" / f"{model_id}.tif"
                artifact = _write_prediction(
                    output_path,
                    prediction,
                    reference=inputs.reference,
                    valid=evaluation_valid,
                )
                predictions[(target_year, seed, model_id)] = prediction
                rows.append(
                    {
                        **fold,
                        "model_id": model_id,
                        "seed": seed,
                        "trace": trace,
                        "evaluation": evaluation,
                        "prediction": artifact,
                    }
                )
        print(f"{source_track}_backtest:target_{target_year}:complete", flush=True)

    bootstrap: dict[str, Any] = {}
    for target_year in target_years:
        origin_year = target_year - 1
        valid = valid_through_year(inputs, origin_year) & np.isin(inputs.states[target_year], CLASSES)
        bootstrap[str(target_year)] = {"per_seed": {}, "paired_model_differences": {}}
        for seed in seeds:
            bootstrap[str(target_year)]["per_seed"][str(seed)] = {
                model_id: spatial_block_bootstrap_ci(
                    predictions[(target_year, seed, model_id)],
                    origin_state=inputs.states[origin_year],
                    observed_target=inputs.states[target_year],
                    valid_mask=valid,
                    n_resamples=bootstrap_resamples,
                    seed=target_year * 100 + seed,
                    block_size=BOOTSTRAP_BLOCK_SIZE,
                )
                for model_id in (*MODEL_IDS, *ZERO_MODELS)
            }
            for left, right in (
                ("geospatial_kernel", "geosos_flus"),
                ("paper58", "geospatial_kernel"),
                ("geospatial_kernel", "random_minimum_change"),
            ):
                key = f"{left}_minus_{right}"
                bootstrap[str(target_year)]["paired_model_differences"].setdefault(key, {})[str(seed)] = paired_model_difference_bootstrap_ci(
                    predictions[(target_year, seed, left)],
                    predictions[(target_year, seed, right)],
                    origin_state=inputs.states[origin_year],
                    observed_target=inputs.states[target_year],
                    valid_mask=valid,
                    n_resamples=bootstrap_resamples,
                    seed=target_year * 1000 + seed,
                    block_size=BOOTSTRAP_BLOCK_SIZE,
                )

    report = {
        "schema": "gwm.abu_dhabi_cross_product_historical_backtest.v1",
        "benchmark_id": f"abu-dhabi-land-use-{source_track}-product-track",
        "created_at": datetime.now(UTC).isoformat(),
        "status": "complete",
        "source_track": source_track,
        "source": source,
        "spatial_scope": "Frozen Abu Dhabi city research boundary (OSM relation R4479763), not Abu Dhabi emirate-wide",
        "model_resolution_m": 100,
        "native_source_resolution_m": 10,
        "class_system": ["water", "woody_vegetation", "low_vegetation", "wetland", "built", "bare"],
        "evaluation_mode": "one_step_expanding_window_oracle_allocation",
        "claim_boundary": [
            f"Historical results measure conditional spatial allocation agreement with {source['display_name']}, not statutory land-use forecast accuracy.",
            "The 10 m source is aggregated to the published 100 m modelling contract; this run does not claim 10 m predictive accuracy.",
            "Both source tracks are public global remote-sensing products and not authoritative Abu Dhabi zoning, cadastral, permit, or planning data.",
        ],
        "temporal_firewall": {
            "fit_uses_observations_through_origin_only": True,
            "target_label_used_only_for_oracle_action_and_evaluation": True,
            "late_osm_road_snapshot_features_used": False,
            "geofm_ldn_selection_transition_ends_at_origin": True,
        },
        "seeds": list(seeds),
        "target_years": list(target_years),
        "models": list(MODEL_IDS),
        "zero_models": list(ZERO_MODELS),
        "bootstrap": {
            "method": "paired_spatial_block_bootstrap",
            "resamples": bootstrap_resamples,
            "block_size_pixels": BOOTSTRAP_BLOCK_SIZE,
            "results": bootstrap,
        },
        "rows": rows,
        "summaries": _metric_summary(rows),
        "wall_seconds": time.perf_counter() - started,
    }
    (output_root / "report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return report


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--binary", type=Path, default=FLUS_BINARY)
    parser.add_argument("--seeds", default=",".join(map(str, SEEDS)))
    parser.add_argument("--target-years", default=",".join(map(str, TARGET_YEARS)))
    parser.add_argument("--epochs", type=int, default=8)
    parser.add_argument("--batch-size", type=int, default=2)
    parser.add_argument("--learning-rate", type=float, default=3e-4)
    parser.add_argument("--device", default="cpu")
    parser.add_argument("--bootstrap-resamples", type=int, default=BOOTSTRAP_RESAMPLES)
    parser.add_argument("--source-track", choices=SOURCE_TRACKS, default="arcgis")
    args = parser.parse_args()
    report = run(
        output_root=args.output,
        binary=args.binary,
        seeds=tuple(int(value) for value in args.seeds.split(",") if value.strip()),
        target_years=tuple(int(value) for value in args.target_years.split(",") if value.strip()),
        epochs=args.epochs,
        batch_size=args.batch_size,
        learning_rate=args.learning_rate,
        requested_device=args.device,
        bootstrap_resamples=args.bootstrap_resamples,
        source_track=args.source_track,
    )
    print(json.dumps({"status": report["status"], "wall_seconds": report["wall_seconds"]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
