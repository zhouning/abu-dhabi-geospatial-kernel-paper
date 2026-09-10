#!/usr/bin/env python3
"""Run an expanding-window, one-step land-cover backtest.

The released headline experiment uses 2022 as the origin and 2023--2024 as
the allocation targets.  This script adds earlier origins without changing
those released rasters: for each origin year ``t`` it fits only transitions
whose target is at or before ``t`` and predicts ``t+1``.  Observed target
counts are used only to isolate spatial allocation skill; the report labels
this as an oracle-demand evaluation.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import time
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import numpy as np
from sklearn.ensemble import HistGradientBoostingClassifier

try:
    from .run_geospatial_kernel import (
        AbuDhabiInputs,
        _display_output_path,
        _write_state,
        allocate_action,
        probability_cube,
    )
    from .shared import (
        CLASSES,
        class_counts,
        evaluate_prediction,
        feasible_target_counts,
        random_feasible_allocation,
    )
except ImportError:  # Direct script execution from the benchmark directory.
    from run_geospatial_kernel import (  # type: ignore
        AbuDhabiInputs,
        _display_output_path,
        _write_state,
        allocate_action,
        probability_cube,
    )
    from shared import (  # type: ignore
        CLASSES,
        class_counts,
        evaluate_prediction,
        feasible_target_counts,
        random_feasible_allocation,
    )


HERE = Path(__file__).resolve().parent
DEFAULT_OUTPUT = HERE / "artifacts/rolling_backtest"
SEEDS = (31, 47, 73)
ORIGINS = (2020, 2021, 2022, 2023)
FIRST_OBSERVED_YEAR = 2017
# ArcGIS v2 materializes annual observations through 2025.  Keeping this
# explicit prevents the expanding-window helper from silently truncating the
# final independent 2024 -> 2025 test fold.
LAST_OBSERVED_YEAR = 2025
SUMMARY_METRICS = (
    "overall_accuracy",
    "macro_f1",
    "change_figure_of_merit",
    "binary_change_figure_of_merit",
    "change_f1",
)


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def fit_transitions_for_origin(origin_year: int) -> tuple[tuple[int, int], ...]:
    """Return expanding-window transitions without reading the target year."""

    if not FIRST_OBSERVED_YEAR + 1 <= origin_year < LAST_OBSERVED_YEAR:
        raise ValueError(f"unsupported_origin_year:{origin_year}")
    transitions = tuple(
        (year, year + 1) for year in range(FIRST_OBSERVED_YEAR, origin_year)
    )
    target_year = origin_year + 1
    if not transitions or max(end for _, end in transitions) != origin_year:
        raise AssertionError("rolling_training_does_not_end_at_origin")
    if any(end >= target_year for _, end in transitions):
        raise AssertionError("rolling_target_label_leaked_into_training")
    return transitions


def valid_through_year(inputs: AbuDhabiInputs, year: int) -> np.ndarray:
    """Build a validity mask using observations no later than ``year``."""

    valid = inputs.city.copy()
    for observed_year in range(FIRST_OBSERVED_YEAR, year + 1):
        valid &= np.isin(inputs.states[observed_year], CLASSES)
    return valid


def _fit_window(
    inputs: AbuDhabiInputs,
    *,
    origin_year: int,
    seed: int,
    training_valid: np.ndarray,
) -> tuple[HistGradientBoostingClassifier, dict[str, Any]]:
    rng = np.random.default_rng(seed)
    feature_rows: list[np.ndarray] = []
    labels: list[np.ndarray] = []
    weights: list[np.ndarray] = []
    transitions: list[dict[str, Any]] = []
    fit_transitions = fit_transitions_for_origin(origin_year)
    for start_year, target_year in fit_transitions:
        start = inputs.states[start_year]
        target = inputs.states[target_year]
        features = inputs.features(
            start,
            driver_year=start_year,
            valid_mask=training_valid,
            include_road_snapshot=False,
        )
        changed = training_valid & (start != target)
        selected = training_valid & (
            changed | (rng.random(start.shape) < 0.20)
        )
        feature_rows.append(features[:, selected].T)
        labels.append(target[selected].astype(np.int64))
        confidence = np.minimum(
            inputs.quality[start_year][selected],
            inputs.quality[target_year][selected],
        )
        weights.append(
            (1.0 + 5.0 * changed[selected])
            * (0.5 + np.clip(confidence, 0, 1))
        )
        transitions.append(
            {
                "start_year": start_year,
                "target_year": target_year,
                "selected_pixels": int(selected.sum()),
                "selected_changed_pixels": int(changed[selected].sum()),
            }
        )
    x = np.concatenate(feature_rows)
    y = np.concatenate(labels)
    sample_weight = np.concatenate(weights)
    model = HistGradientBoostingClassifier(
        learning_rate=0.08,
        max_iter=120,
        max_leaf_nodes=31,
        min_samples_leaf=40,
        l2_regularization=1.0,
        random_state=seed,
    )
    started = time.perf_counter()
    model.fit(x, y, sample_weight=sample_weight)
    return model, {
        "seed": seed,
        "origin_year": origin_year,
        "prediction_target_year": origin_year + 1,
        "fit_target_latest_year": origin_year,
        "prediction_target_used_in_fit": False,
        "training_pixel_rows": int(len(x)),
        "feature_count": int(x.shape[1]),
        "model_classes": model.classes_.tolist(),
        "fit_transitions": transitions,
        "fit_seconds": time.perf_counter() - started,
    }


def _evaluate_one(
    prediction: np.ndarray,
    *,
    inputs: AbuDhabiInputs,
    origin_year: int,
    target_year: int,
    hard: np.ndarray,
    valid: np.ndarray,
    requested_counts: dict[int, int],
) -> dict[str, Any]:
    return evaluate_prediction(
        prediction,
        origin_state=inputs.states[origin_year],
        observed_target=inputs.states[target_year],
        valid_mask=valid,
        hard_exclusion_mask=hard,
        requested_counts=requested_counts,
        reliability_mask=(
            valid
            & (inputs.quality[origin_year] >= 0.5)
            & (inputs.quality[target_year] >= 0.5)
        ),
    )


def _aggregate_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    summaries: list[dict[str, Any]] = []
    keys = sorted({(row["origin_year"], row["model_id"]) for row in rows})
    for origin_year, model_id in keys:
        selected = [
            row for row in rows
            if row["origin_year"] == origin_year and row["model_id"] == model_id
        ]
        metrics: dict[str, Any] = {}
        for metric in SUMMARY_METRICS:
            values = np.asarray(
                [row["evaluation"][metric] for row in selected], dtype=np.float64
            )
            metrics[metric] = {
                "mean": float(values.mean()),
                "sample_standard_deviation": (
                    float(values.std(ddof=1)) if len(values) > 1 else 0.0
                ),
                "minimum": float(values.min()),
                "maximum": float(values.max()),
            }
        summaries.append(
            {
                "origin_year": origin_year,
                "target_year": origin_year + 1,
                "model_id": model_id,
                "seed_count": len(selected),
                "metrics": metrics,
            }
        )
    return summaries


def run(
    *,
    origins: tuple[int, ...],
    seeds: tuple[int, ...],
    output_root: Path | None = None,
) -> dict[str, Any]:
    inputs = AbuDhabiInputs()
    rows: list[dict[str, Any]] = []
    started = time.perf_counter()
    for origin_year in origins:
        target_year = origin_year + 1
        if target_year not in inputs.states:
            raise ValueError(f"target_year_not_available:{target_year}")
        origin = inputs.states[origin_year]
        target = inputs.states[target_year]
        training_valid = valid_through_year(inputs, origin_year)
        valid = training_valid & np.isin(target, CLASSES)
        # Only origin-year state is used here. WorldCover 2021 and the later
        # OSM snapshot are excluded from early folds to avoid temporal leakage.
        hard = valid & np.isin(origin, (1, 4))
        desired = class_counts(target, valid)
        requested = feasible_target_counts(
            desired,
            origin_state=origin,
            valid_mask=valid,
            hard_exclusion_mask=hard,
        )
        for seed in seeds:
            model, training = _fit_window(
                inputs,
                origin_year=origin_year,
                seed=seed,
                training_valid=training_valid,
            )
            probability = probability_cube(
                model,
                inputs,
                origin,
                driver_year=origin_year,
                valid_mask=training_valid,
                include_road_snapshot=False,
            )
            kernel_prediction, allocation = allocate_action(
                origin,
                probability,
                valid=valid,
                hard=hard,
                target_counts=requested,
            )
            persistence = origin.copy()
            random_prediction = random_feasible_allocation(
                origin,
                valid_mask=valid,
                hard_exclusion_mask=hard,
                target_counts=requested,
                seed=seed + origin_year * 1000,
            )
            for model_id, prediction in (
                ("geospatial_kernel", kernel_prediction),
                ("persistence", persistence),
                ("random_allocation", random_prediction),
            ):
                evaluation = _evaluate_one(
                    prediction,
                    inputs=inputs,
                    origin_year=origin_year,
                    target_year=target_year,
                    hard=hard,
                    valid=valid,
                    requested_counts=requested,
                )
                if model_id != "persistence" and not evaluation["demand_target_exact"]:
                    raise AssertionError(
                        f"rolling_oracle_demand_not_exact:{origin_year}:{model_id}"
                    )
                prediction_artifact = None
                if output_root is not None:
                    prediction_path = (
                        output_root
                        / "predictions"
                        / f"origin_{origin_year}_target_{target_year}"
                        / f"seed_{seed}"
                        / f"{model_id}.tif"
                    )
                    _write_state(
                        prediction_path,
                        prediction,
                        inputs.reference,
                        valid_mask=valid,
                    )
                    prediction_artifact = {
                        "path": _display_output_path(prediction_path),
                        "sha256": _sha256_file(prediction_path),
                        "size_bytes": prediction_path.stat().st_size,
                    }
                rows.append(
                    {
                        "origin_year": origin_year,
                        "target_year": target_year,
                        "seed": seed,
                        "model_id": model_id,
                        "training": training if model_id == "geospatial_kernel" else None,
                        "allocation": allocation if model_id == "geospatial_kernel" else None,
                        "evaluation": evaluation,
                        "prediction_artifact": prediction_artifact,
                        "valid_pixel_count": int(valid.sum()),
                        "training_valid_pixel_count": int(training_valid.sum()),
                        "hard_exclusion_pixel_count": int(hard.sum()),
                        "requested_target_counts": {
                            str(key): int(value) for key, value in requested.items()
                        },
                        "observed_target_counts": {
                            str(key): int(value) for key, value in desired.items()
                        },
                    }
                )
        print(f"rolling_backtest:origin_{origin_year}:complete", flush=True)
    report = {
        "schema": "gwm.abu_dhabi_rolling_backtest.v1",
        "benchmark_id": "abu-dhabi-land-use-v1",
        "status": "complete",
        "created_at": datetime.now(UTC).isoformat(),
        "evaluation_mode": "one_step_expanding_window_oracle_allocation",
        "model_target_boundary": (
            "For origin t, fit transitions end at t and predict t+1; observed "
            "target counts are used only for allocation-skill isolation."
        ),
        "temporal_firewall": {
            "training_state_and_driver_latest_year": "origin_year",
            "prediction_target_used_in_fit": False,
            "target_observation_uses": [
                "evaluation",
                "oracle_target_class_counts",
                "evaluation_coverage_mask",
            ],
            "early_fold_constraint_policy": (
                "Lock origin-year water and wetland only; exclude WorldCover "
                "2021 and the later OSM snapshot from rolling folds."
            ),
            "road_snapshot_features_used": False,
        },
        "origins": list(origins),
        "seeds": list(seeds),
        "models": ["geospatial_kernel", "persistence", "random_allocation"],
        "rows": rows,
        "summaries": _aggregate_rows(rows),
        "wall_seconds": time.perf_counter() - started,
    }
    return report


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--origins", default=",".join(map(str, ORIGINS)))
    parser.add_argument("--seeds", default=",".join(map(str, SEEDS)))
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    origins = tuple(int(item) for item in args.origins.split(",") if item.strip())
    seeds = tuple(int(item) for item in args.seeds.split(",") if item.strip())
    args.output.mkdir(parents=True, exist_ok=True)
    report = run(origins=origins, seeds=seeds, output_root=args.output)
    path = args.output / "report.json"
    path.write_text(
        json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps({"status": report["status"], "row_count": len(report["rows"]), "output": str(path)}))


if __name__ == "__main__":
    main()
