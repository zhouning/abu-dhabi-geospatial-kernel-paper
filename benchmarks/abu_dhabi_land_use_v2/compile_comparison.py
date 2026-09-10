#!/usr/bin/env python3
"""Compile the shared three-model historical comparison and ensembles."""

from __future__ import annotations

import argparse
import json
import os
import statistics
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import numpy as np
import rasterio
from shared import (
    evaluate_prediction,
    paired_pixel_bootstrap_ci,
    paired_model_difference_bootstrap_ci,
    random_feasible_allocation,
)

HERE = Path(__file__).resolve().parent
PREDICTION_ROOT = HERE / "artifacts/predictions"
BUNDLE_ROOT = HERE / "artifacts/bundle"
INPUT_ROOT = HERE / "artifacts/gee"
# Versioned outputs prevent a new rerun from mutating the archived legacy
# report.  Pass --output explicitly when publishing a numbered release.
DEFAULT_OUTPUT = HERE / "comparison_report_current.json"
DEFAULT_MARKDOWN = HERE / "comparison_report_current.md"
MODELS = ("geosos_flus", "geospatial_kernel", "paper58")
MATCHED_MODEL = "flus_matched_input"
NEIGHBOURHOOD_MODEL = "flus_baseline_plus_neighbourhood"
YEARS = (2023, 2024)
BOOTSTRAP_RESAMPLES = 1000
BOOTSTRAP_BLOCK_SIZE_PIXELS = 8
CONFIDENCE_THRESHOLD = 0.5
MODEL_DISPLAY_NAMES = {
    "geosos_flus": "GeoSOS-derived FLUS-style ANN–CA console (author-modified build)",
    "geospatial_kernel": "Geospatial Kernel",
    "paper58": "GeoFM-LDN",
    MATCHED_MODEL: "FLUS 25-feature input diagnostic",
    NEIGHBOURHOOD_MODEL: "FLUS 19-feature neighbourhood diagnostic",
}


def _read(path: Path) -> tuple[np.ndarray, dict[str, Any]]:
    with rasterio.open(path) as dataset:
        return dataset.read(), dataset.profile.copy()


def _write(path: Path, state: np.ndarray, reference: dict[str, Any]) -> None:
    profile = reference.copy()
    profile.update(
        count=1,
        dtype="uint8",
        nodata=0,
        compress="deflate",
        tiled=True,
        blockxsize=256,
        blockysize=256,
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(f".partial.{os.getpid()}.tif")
    with rasterio.open(temp, "w", **profile) as dataset:
        dataset.write(state.astype(np.uint8), 1)
        dataset.set_band_description(1, "three_seed_majority_prediction")
    os.replace(temp, path)


def majority_vote(states: list[np.ndarray]) -> np.ndarray:
    stack = np.stack(states)
    counts = np.stack([np.count_nonzero(stack == value, axis=0) for value in range(1, 7)])
    result = np.argmax(counts, axis=0).astype(np.uint8) + 1
    result[np.all(stack == 0, axis=0)] = 0
    return result


def _aggregate(rows: list[dict[str, Any]]) -> dict[str, Any]:
    keys = (
        "change_figure_of_merit",
        "change_f1",
        "overall_accuracy",
        "macro_f1",
        "demand_total_variation",
        "constraint_violation_rate",
    )
    result = {}
    for key in keys:
        values = [float(row[key]) for row in rows]
        result[key] = {
            "mean": statistics.mean(values),
            "population_std": statistics.pstdev(values),
            "values": values,
        }
    binary_values = [float(row.get("binary_change_figure_of_merit", float("nan"))) for row in rows]
    if not all(np.isnan(binary_values)):
        result["binary_change_figure_of_merit"] = {
            "mean": statistics.mean(binary_values),
            "population_std": statistics.pstdev(binary_values),
            "values": binary_values,
        }
    reliability_values = [
        float(row["reliability_sensitivity"]["change_figure_of_merit"]) for row in rows
    ]
    result["reliability_change_figure_of_merit"] = {
        "mean": statistics.mean(reliability_values),
        "population_std": statistics.pstdev(reliability_values),
        "values": reliability_values,
    }
    return result


def _aggregate_bootstrap(rows: list[dict[str, Any]]) -> dict[str, Any]:
    """Summarize per-seed spatial-block bootstrap intervals."""

    result: dict[str, Any] = {}
    for metric in ("change_figure_of_merit", "overall_accuracy", "macro_f1"):
        intervals = [row[metric] for row in rows]
        result[metric] = {
            "lower_mean": statistics.mean(float(value["lower"]) for value in intervals),
            "median_mean": statistics.mean(float(value["median"]) for value in intervals),
            "upper_mean": statistics.mean(float(value["upper"]) for value in intervals),
            "per_seed": intervals,
        }
    return result


def _aggregate_difference_bootstrap(rows: list[dict[str, Any]]) -> dict[str, Any]:
    """Summarize paired model-difference intervals over frozen seeds."""

    result: dict[str, Any] = {}
    for metric in ("change_figure_of_merit", "overall_accuracy", "macro_f1"):
        intervals = [row[metric] for row in rows]
        result[metric] = {
            "lower_mean": statistics.mean(float(value["lower"]) for value in intervals),
            "median_mean": statistics.mean(float(value["median"]) for value in intervals),
            "upper_mean": statistics.mean(float(value["upper"]) for value in intervals),
            "per_seed": intervals,
        }
    return result


def _dynamic_interpretation(
    summaries: dict[str, dict[str, dict[str, Any]]],
    deltas: dict[str, dict[str, float]],
) -> list[str]:
    """Generate statements only from computed values; never pre-write rankings."""

    lines: list[str] = []
    for year in YEARS:
        key = str(year)
        ranked = sorted(
            MODELS,
            key=lambda model: summaries[model][key]["change_figure_of_merit"]["mean"],
            reverse=True,
        )
        labels = [MODEL_DISPLAY_NAMES[model] for model in ranked]
        lines.append(
            f"Computed strict transition FoM ranking for {year}: " + " > ".join(labels) + "."
        )
        for left, right in (
            ("geospatial_kernel", "geosos_flus"),
            ("paper58", "geosos_flus"),
            ("paper58", "geospatial_kernel"),
        ):
            delta = deltas[key][f"{left}_minus_{right}_change_fom"]
            direction = "above" if delta > 0 else "below" if delta < 0 else "equal to"
            lines.append(
                f"{MODEL_DISPLAY_NAMES[left]} is {direction} {MODEL_DISPLAY_NAMES[right]} "
                f"by {abs(delta):.6f} strict FoM at {year}."
            )
    lines.extend(
        [
            "Persistence and random-minimum-change controls are reported as explicit zero-model controls.",
            "Dynamic World quality-proxy sensitivity is a label-quality diagnostic; it is not a separate validation set.",
            "These results establish historical conditional allocation skill, not future policy prediction or causal planning effects.",
        ]
    )
    return lines


def _mask_observation_summary(
    *, mask: np.ndarray, valid_mask: np.ndarray, origin_state: np.ndarray, observed_target: np.ndarray
) -> dict[str, Any]:
    """Describe how a Dynamic World quality-proxy filter selects change events."""

    eligible = np.asarray(valid_mask, dtype=bool) & np.asarray(mask, dtype=bool)
    observed_change = np.asarray(valid_mask, dtype=bool) & (observed_target != origin_state)
    full_grid_changes = int(np.count_nonzero(observed_change))
    retained_changes = int(np.count_nonzero(observed_change & eligible))
    return {
        "eligible_pixels": int(np.count_nonzero(eligible)),
        "observed_change_pixels": retained_changes,
        "observed_change_retention_fraction": (
            float(retained_changes / full_grid_changes) if full_grid_changes else 0.0
        ),
    }


def _label_quality_diagnostics(
    *,
    action_by_year: dict[int, dict[str, Any]],
    hard_mask: np.ndarray,
    origin_state: np.ndarray,
    observed: dict[int, np.ndarray],
    prediction_cache: dict[str, dict[int, dict[int, np.ndarray]]],
    valid_mask: np.ndarray,
) -> dict[str, Any]:
    """Compile quality-proxy diagnostics without treating them as validation."""

    by_target_year: dict[str, Any] = {}
    for year in YEARS:
        action = action_by_year[year]
        target_counts = {
            int(key): int(value)
            for key, value in action["feasible_target_counts"].items()
        }
        dual_year, _ = _read(HERE / action["reliability_mask"])
        preceding_year = year - 1
        preceding_path = (
            INPUT_ROOT
            / "land_cover"
            / f"land_cover_quality_{preceding_year}_100m.tif"
        )
        preceding_quality, _ = _read(preceding_path)
        preceding_mask = preceding_quality[0] >= CONFIDENCE_THRESHOLD
        strict_fom_by_model: dict[str, dict[str, Any]] = {}
        for model in MODELS:
            rows = []
            for seed in (31, 47, 73):
                evaluation = evaluate_prediction(
                    prediction_cache[model][seed][year],
                    origin_state=origin_state,
                    observed_target=observed[year],
                    valid_mask=valid_mask,
                    hard_exclusion_mask=hard_mask,
                    requested_counts=target_counts,
                    reliability_mask=preceding_mask,
                )
                rows.append(
                    float(evaluation["reliability_sensitivity"]["change_figure_of_merit"])
                )
            strict_fom_by_model[model] = {
                "mean": statistics.mean(rows),
                "population_std": statistics.pstdev(rows),
                "values": rows,
            }
        full_grid_changes = int(
            np.count_nonzero(valid_mask & (observed[year] != origin_state))
        )
        by_target_year[str(year)] = {
            "full_grid_observed_change_pixels": full_grid_changes,
            "dual_year_confidence": {
                "rule": (
                    "origin and target Dynamic World maximum temporal-mean "
                    "probability must both be at least 0.5"
                ),
                "mask_path": Path(action["reliability_mask"]).as_posix(),
                **_mask_observation_summary(
                    mask=dual_year[0].astype(bool),
                    valid_mask=valid_mask,
                    origin_state=origin_state,
                    observed_target=observed[year],
                ),
            },
            "preceding_year_confidence_only": {
                "origin_year": preceding_year,
                "rule": (
                    "only the Dynamic World maximum temporal-mean probability "
                    "for the year immediately preceding the target must be at least 0.5"
                ),
                "quality_path": preceding_path.relative_to(HERE).as_posix(),
                **_mask_observation_summary(
                    mask=preceding_mask,
                    valid_mask=valid_mask,
                    origin_state=origin_state,
                    observed_target=observed[year],
                ),
                "strict_fom_by_model": strict_fom_by_model,
            },
        }
    return {
        "purpose": "Label-quality and selection-effect diagnostics only; neither filtered subset is an independent validation set or a model-skill test.",
        "confidence_threshold": CONFIDENCE_THRESHOLD,
        "interpretation": "The dual-year rule may exclude an observed change because its target label has a low Dynamic World quality-proxy value. The preceding-year-only variant is reported to expose that selection effect, not to rescue or validate model skill.",
        "by_target_year": by_target_year,
    }


def compile_report(*, output_path: Path, markdown_path: Path) -> dict[str, Any]:
    common, reference = _read(BUNDLE_ROOT / "common_valid_mask_100m.tif")
    hard, _ = _read(BUNDLE_ROOT / "hard_exclusion_2022_100m.tif")
    valid = common[0].astype(bool)
    hard_mask = hard[0].astype(bool)
    origin, _ = _read(INPUT_ROOT / "land_cover/land_cover_2022_100m.tif")
    actions = json.loads((BUNDLE_ROOT / "allocation_actions.json").read_text())["actions"]
    action_by_year = {int(row["target_year"]): row for row in actions}
    observed = {
        year: _read(INPUT_ROOT / "land_cover" / f"land_cover_{year}_100m.tif")[0][0]
        for year in YEARS
    }
    reports = {
        model: json.loads((PREDICTION_ROOT / model / "report.json").read_text())
        for model in MODELS
    }
    accepted_model_revisions = {"current_protocol_run", "recomputed_from_existing_rasters"}
    stale_models = [
        model
        for model, report in reports.items()
        if report.get("status") != "complete"
        or report.get("revision_status") not in accepted_model_revisions
    ]
    if stale_models:
        raise ValueError(
            "model_reports_not_current_protocol_run:"
            + ",".join(stale_models)
        )
    summaries = {}
    ensembles = {}
    bootstrap = {}
    pairwise_bootstrap: dict[str, Any] = {}
    baseline_bootstrap: dict[str, Any] = {"persistence": {}, "random_allocation": {}}
    prediction_cache: dict[str, dict[int, dict[int, np.ndarray]]] = {
        model: {seed: {} for seed in (31, 47, 73)} for model in MODELS
    }
    seed_diagnostics: dict[str, dict[str, list[dict[str, Any]]]] = {
        model: {} for model in MODELS
    }
    for model in MODELS:
        summaries[model] = {}
        ensembles[model] = {}
        bootstrap[model] = {}
        seed_ids = [int(row["seed"]) for row in reports[model]["seeds"]]
        if seed_ids != [31, 47, 73]:
            raise ValueError(f"three_frozen_seeds_required:{model}:{seed_ids}")
        for year in YEARS:
            action = action_by_year[year]
            reliability, _ = _read(HERE / action["reliability_mask"])
            target_counts = {
                int(key): int(value)
                for key, value in action["feasible_target_counts"].items()
            }
            evaluation_rows = []
            bootstrap_rows = []
            diagnostic_rows = []
            for seed in seed_ids:
                prediction, _ = _read(
                    PREDICTION_ROOT / model / f"seed_{seed}/prediction_{year}.tif"
                )
                prediction_cache[model][seed][year] = prediction[0]
                evaluation = evaluate_prediction(
                    prediction[0],
                    origin_state=origin[0],
                    observed_target=observed[year],
                    valid_mask=valid,
                    hard_exclusion_mask=hard_mask,
                    requested_counts=target_counts,
                    reliability_mask=reliability[0].astype(bool),
                )
                evaluation_rows.append(evaluation)
                diagnostic_rows.append(
                    {
                        "seed": seed,
                        "target_year": year,
                        "predicted_change_pixels": evaluation["predicted_change_pixels"],
                        "zero_change_output": evaluation["predicted_change_pixels"] == 0,
                        "degeneracy_reason": (
                            "zero_change_output_detected"
                            if evaluation["predicted_change_pixels"] == 0
                            else None
                        ),
                        "change_figure_of_merit": evaluation["change_figure_of_merit"],
                        "change_f1": evaluation["change_f1"],
                        "overall_accuracy": evaluation["overall_accuracy"],
                        "macro_f1": evaluation["macro_f1"],
                    }
                )
                bootstrap_rows.append(
                    paired_pixel_bootstrap_ci(
                        prediction[0],
                        origin_state=origin[0],
                        observed_target=observed[year],
                        valid_mask=valid,
                        n_resamples=BOOTSTRAP_RESAMPLES,
                        seed=seed + year,
                        block_size=BOOTSTRAP_BLOCK_SIZE_PIXELS,
                    )
                )
            summaries[model][str(year)] = _aggregate(evaluation_rows)
            seed_diagnostics[model][str(year)] = diagnostic_rows
            bootstrap[model][str(year)] = _aggregate_bootstrap(bootstrap_rows)
            states = [
                _read(PREDICTION_ROOT / model / f"seed_{seed}/prediction_{year}.tif")[0][0]
                for seed in seed_ids
            ]
            ensemble = majority_vote(states)
            ensemble_path = PREDICTION_ROOT / model / "ensemble" / f"prediction_{year}.tif"
            _write(ensemble_path, ensemble, reference)
            ensembles[model][str(year)] = {
                "prediction_path": ensemble_path.relative_to(HERE).as_posix(),
                "evaluation": evaluate_prediction(
                    ensemble,
                    origin_state=origin[0],
                    observed_target=observed[year],
                    valid_mask=valid,
                    hard_exclusion_mask=hard_mask,
                    requested_counts=target_counts,
                    reliability_mask=reliability[0].astype(bool),
                ),
            }

    def compile_flus_feature_diagnostic(
        *, directory: str, model_id: str, feature_count: int, includes_current_class: bool
    ) -> dict[str, Any]:
        source = PREDICTION_ROOT / directory / "report.json"
        source_report = json.loads(source.read_text(encoding="utf-8"))
        seed_ids = [int(row["seed"]) for row in source_report["seeds"]]
        if seed_ids != [31, 47, 73]:
            raise ValueError(f"three_feature_diagnostic_seeds_required:{model_id}:{seed_ids}")

        per_seed: dict[str, list[dict[str, Any]]] = {}
        ranges: dict[str, dict[str, Any]] = {}
        for year in YEARS:
            action = action_by_year[year]
            reliability, _ = _read(HERE / action["reliability_mask"])
            target_counts = {
                int(key): int(value)
                for key, value in action["feasible_target_counts"].items()
            }
            rows = []
            for seed in seed_ids:
                prediction, _ = _read(
                    PREDICTION_ROOT / directory / f"seed_{seed}/prediction_{year}.tif"
                )
                evaluation = evaluate_prediction(
                    prediction[0],
                    origin_state=origin[0],
                    observed_target=observed[year],
                    valid_mask=valid,
                    hard_exclusion_mask=hard_mask,
                    requested_counts=target_counts,
                    reliability_mask=reliability[0].astype(bool),
                )
                zero_change = evaluation["predicted_change_pixels"] == 0
                rows.append(
                    {
                        "seed": seed,
                        "target_year": year,
                        "observed_change_pixels": evaluation["observed_change_pixels"],
                        "predicted_change_pixels": evaluation["predicted_change_pixels"],
                        "zero_change_output": zero_change,
                        "degeneracy_reason": (
                            "current_class_identity_leakage_zero_change"
                            if zero_change and includes_current_class
                            else "zero_change_output_detected" if zero_change else None
                        ),
                        "change_figure_of_merit": evaluation["change_figure_of_merit"],
                        "change_f1": evaluation["change_f1"],
                        "macro_f1": evaluation["macro_f1"],
                        "overall_accuracy": evaluation["overall_accuracy"],
                        "demand_total_variation": evaluation["demand_total_variation"],
                    }
                )
            per_seed[str(year)] = rows
            ranges[str(year)] = {
                "observed_change_pixels": rows[0]["observed_change_pixels"],
                "strict_fom_min": min(row["change_figure_of_merit"] for row in rows),
                "strict_fom_max": max(row["change_figure_of_merit"] for row in rows),
                "predicted_change_pixels_min": min(row["predicted_change_pixels"] for row in rows),
                "predicted_change_pixels_max": max(row["predicted_change_pixels"] for row in rows),
                "demand_total_variation_min": min(row["demand_total_variation"] for row in rows),
                "demand_total_variation_max": max(row["demand_total_variation"] for row in rows),
            }
        return {
            "model_id": model_id,
            "display_name": MODEL_DISPLAY_NAMES[model_id],
            "feature_count": feature_count,
            "archive_platform": "macOS arm64",
            "source_report": f"artifacts/predictions/{directory}/report.json",
            "per_seed": per_seed,
            "ranges": ranges,
        }

    matched_input_diagnostic = compile_flus_feature_diagnostic(
        directory="flus_matched_inputs_abs",
        model_id=MATCHED_MODEL,
        feature_count=25,
        includes_current_class=True,
    )
    matched_input_diagnostic.update(
        {
            "estimator_status": "invalid_platform_sensitive_identity_leakage_diagnostic",
            "non_collapsed_seeds_on_archive_platform": [31],
            "collapsed_seeds_on_archive_platform": [47, 73],
            "training_target_boundary": "same-year label suitability; not next-state transition learning",
            "interpretation": "The macOS arm64 seed-31 run did not collapse, but it is not treated as a valid point estimate because independent external Windows x86_64 verification collapsed for all three seeds. Across the six platform-seed runs, five were zero-change outputs.",
        }
    )
    neighbourhood_input_diagnostic = compile_flus_feature_diagnostic(
        directory="flus_7_plus_neighbourhood_abs",
        model_id=NEIGHBOURHOOD_MODEL,
        feature_count=19,
        includes_current_class=False,
    )
    neighbourhood_input_diagnostic.update(
        {
            "estimator_status": "partial_demand_underfill_diagnostic",
            "interpretation": "All three macOS arm64 seeds produced changes, but each underfilled the requested demand in both target years. This mode remains a mechanism diagnostic, not a comparable headline estimator.",
        }
    )

    for year in YEARS:
        year_key = str(year)
        pairwise_bootstrap[year_key] = {}
        for left, right in (
            ("geospatial_kernel", "geosos_flus"),
            ("paper58", "geosos_flus"),
            ("paper58", "geospatial_kernel"),
        ):
            seed_rows = []
            for seed in (31, 47, 73):
                seed_rows.append(
                    paired_model_difference_bootstrap_ci(
                        prediction_cache[left][seed][year],
                        prediction_cache[right][seed][year],
                        origin_state=origin[0],
                        observed_target=observed[year],
                        valid_mask=valid,
                        n_resamples=BOOTSTRAP_RESAMPLES,
                        seed=200000 + seed + year,
                        block_size=BOOTSTRAP_BLOCK_SIZE_PIXELS,
                    )
                )
            pairwise_bootstrap[year_key][f"{left}_minus_{right}"] = {
                "model_a": left,
                "model_b": right,
                "summary": _aggregate_difference_bootstrap(seed_rows),
            }
    persistence = {}
    random_baseline = {}
    for year in YEARS:
        action = action_by_year[year]
        reliability, _ = _read(HERE / action["reliability_mask"])
        target_counts = {
            int(key): int(value)
            for key, value in action["feasible_target_counts"].items()
        }
        persistence_eval = evaluate_prediction(
            origin[0],
            origin_state=origin[0],
            observed_target=observed[year],
            valid_mask=valid,
            hard_exclusion_mask=hard_mask,
            requested_counts=target_counts,
            reliability_mask=reliability[0].astype(bool),
        )
        persistence_bootstrap = paired_pixel_bootstrap_ci(
            origin[0],
            origin_state=origin[0],
            observed_target=observed[year],
            valid_mask=valid,
            n_resamples=BOOTSTRAP_RESAMPLES,
            seed=10000 + year,
            block_size=BOOTSTRAP_BLOCK_SIZE_PIXELS,
        )
        persistence[str(year)] = persistence_eval
        baseline_bootstrap["persistence"][str(year)] = persistence_bootstrap
        random_rows = []
        random_bootstrap_rows = []
        for seed in (31, 47, 73):
            random_prediction = random_feasible_allocation(
                origin[0],
                valid_mask=valid,
                hard_exclusion_mask=hard_mask,
                target_counts=target_counts,
                seed=100000 + seed + year,
            )
            random_rows.append(
                evaluate_prediction(
                    random_prediction,
                    origin_state=origin[0],
                    observed_target=observed[year],
                    valid_mask=valid,
                    hard_exclusion_mask=hard_mask,
                    requested_counts=target_counts,
                    reliability_mask=reliability[0].astype(bool),
                )
            )
            random_bootstrap_rows.append(
                paired_pixel_bootstrap_ci(
                    random_prediction,
                    origin_state=origin[0],
                    observed_target=observed[year],
                    valid_mask=valid,
                    n_resamples=BOOTSTRAP_RESAMPLES,
                    seed=110000 + seed + year,
                    block_size=BOOTSTRAP_BLOCK_SIZE_PIXELS,
                )
            )
        random_baseline[str(year)] = _aggregate(random_rows)
        baseline_bootstrap["random_allocation"][str(year)] = _aggregate_bootstrap(random_bootstrap_rows)

    deltas = {}
    for year in YEARS:
        key = str(year)
        deltas[key] = {}
        for left, right in (
            ("geospatial_kernel", "geosos_flus"),
            ("paper58", "geosos_flus"),
            ("paper58", "geospatial_kernel"),
        ):
            deltas[key][f"{left}_minus_{right}_change_fom"] = (
                summaries[left][key]["change_figure_of_merit"]["mean"]
                - summaries[right][key]["change_figure_of_merit"]["mean"]
            )
    label_quality_diagnostics = _label_quality_diagnostics(
        action_by_year=action_by_year,
        hard_mask=hard_mask,
        origin_state=origin[0],
        observed=observed,
        prediction_cache=prediction_cache,
        valid_mask=valid,
    )
    report = {
        "schema": "gwm.abu_dhabi_three_model_comparison.v4",
        "benchmark_id": "abu-dhabi-land-use-v1",
        "metric_version": "strict_multiclass_fom_v2",
        "revision_status": "rerun_from_current_rasters",
        "reproducibility_status": "complete_if_all_input_and_model_artifacts_are_present",
        "evidence_mode": "current_evaluator_on_current_reproduced_prediction_rasters",
        "created_at": datetime.now(UTC).isoformat(),
        "status": "HISTORICAL_ALLOCATION_COMPLETE",
        "models": list(MODELS),
        "model_display_names": MODEL_DISPLAY_NAMES,
        "seeds": [31, 47, 73],
        "summaries": summaries,
        "matched_input_diagnostic": matched_input_diagnostic,
        "neighbourhood_input_diagnostic": neighbourhood_input_diagnostic,
        "cross_platform_verification": {
            "flus_windows_x86_64": {
                "evidence_status": "reviewer_provided_external_verification_no_local_rasters",
                "same_platform_seed_31_repeat_difference_pixels": {"2023": 0, "2024": 0},
                "baseline_7_mean_strict_fom": {"2023": 0.1335, "2024": 0.1800},
                "baseline_7_windows_vs_macos_difference_pixels": {
                    "31": {"2023": 1910, "2024": 3261},
                    "47": {"2023": 2137, "2024": 3325},
                    "73": {"2023": 2018, "2024": 3131},
                },
                "matched_25_collapsed_seeds": [31, 47, 73],
                "interpretation": "Reported by the reviewer after rebuilding the tagged source on Windows x86_64. The Windows rasters are not present locally and are not claimed as author-run reproduction outputs.",
            },
            "kernel_github_actions_ubuntu_x86_64": {
                "evidence_status": "author_controlled_archived_ci_rerun",
                "commit": "e06a99763de71db396ac44e1339ff211b21e7519",
                "run_url": "https://github.com/zhouning/abu-dhabi-geospatial-kernel-paper/actions/runs/34107504198",
                "comparison_path": "artifacts/cross_platform/github_actions_ubuntu_x86_64_kernel_reference_e06a997.json",
                "runtime": {
                    "python": "3.11.16",
                    "machine": "x86_64",
                    "scikit_learn": "1.9.0",
                },
                "categorical_difference_pixels_range": [0, 0],
                "interpretation": "An author-controlled GitHub Actions Ubuntu x86_64 run reran all three seeds under the resolved lock and matched all six current macOS-reference categorical rasters exactly. This is a scoped locked-stack regression result, not a claim about every architecture or numerical stack.",
            },
        },
        "seed_diagnostics": seed_diagnostics,
        "bootstrap_95ci": bootstrap,
        "pairwise_bootstrap_95ci": pairwise_bootstrap,
        "ensembles": ensembles,
        "persistence": persistence,
        "persistence_summary": {
            str(year): {
                key: {
                    "mean": float(value),
                    "population_std": 0.0,
                    "values": [float(value)],
                }
                for key, value in persistence[str(year)].items()
                if isinstance(value, (int, float))
            }
            for year in YEARS
        },
        "random_baseline": random_baseline,
        "baseline_bootstrap_95ci": baseline_bootstrap,
        "mean_change_fom_deltas": deltas,
        "label_quality_diagnostics": label_quality_diagnostics,
        "interpretation": _dynamic_interpretation(summaries, deltas),
    }
    output_path.write_text(
        json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    markdown_path.write_text(render_markdown(report), encoding="utf-8")
    return report


def render_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# Abu Dhabi 三模型土地覆盖历史模拟比较",
        "",
        f"生成时间：{report['created_at']}",
        "",
        "同一 100 m 网格、需求动作、硬约束和评价器下的三随机种子均值；严格 FoM 与两个零模型均已列出。区间采用 8×8 像元空间块 bootstrap，并提供同一空间块上的模型差值区间。",
        "",
        "| 年份 | 模型 | change FoM | change F1 | OA | macro-F1 | demand TV |",
        "|---:|---|---:|---:|---:|---:|---:|",
    ]
    labels = {
        "geosos_flus": "GeoSOS-derived FLUS-style ANN–CA console (author-modified build)",
        "geospatial_kernel": "Geospatial Kernel",
        "paper58": "GeoFM-LDN",
    }
    def metric_summary(model: str, year: int, key: str) -> dict[str, float]:
        if model in MODELS:
            return report["summaries"][model][str(year)][key]
        if model == "persistence":
            return report["persistence_summary"][str(year)][key]
        return report["random_baseline"][str(year)][key]

    table_models = list(MODELS) + ["persistence", "random_allocation"]
    table_labels = {
        **labels,
        "persistence": "Persistence zero model",
        "random_allocation": "Random minimum-change zero model",
    }
    for year in YEARS:
        for model in table_models:
            row = {key: metric_summary(model, year, key) for key in ("change_figure_of_merit", "change_f1", "overall_accuracy", "macro_f1", "demand_total_variation")}
            lines.append(
                f"| {year} | {table_labels[model]} | "
                f"{row['change_figure_of_merit']['mean']:.4f} | "
                f"{row['change_f1']['mean']:.4f} | "
                f"{row['overall_accuracy']['mean']:.4f} | "
                f"{row['macro_f1']['mean']:.4f} | "
                f"{row['demand_total_variation']['mean']:.5f} |"
            )
    lines.extend(
        [
            "",
            "## FLUS feature diagnostics",
            "",
            "The 25-feature run shares the Kernel feature family but not its next-state target or projection semantics. It is not a comparable estimator: five of six platform-seed runs collapsed to zero change, including every independent external Windows x86_64 run. The non-collapsed macOS seed-31 result is retained only as a platform-sensitive diagnostic.",
            "",
            "| 年份 | 19-feature FoM range | Predicted change range | Observed change | Demand TV range |",
            "|---:|---:|---:|---:|---:|",
        ]
    )
    neighbourhood = report["neighbourhood_input_diagnostic"]
    for year in YEARS:
        summary = neighbourhood["ranges"][str(year)]
        lines.append(
            f"| {year} | {summary['strict_fom_min']:.4f}–{summary['strict_fom_max']:.4f} | "
            f"{summary['predicted_change_pixels_min']:,}–{summary['predicted_change_pixels_max']:,} | "
            f"{summary['observed_change_pixels']:,} | "
            f"{summary['demand_total_variation_min']:.4f}–{summary['demand_total_variation_max']:.4f} |"
        )
    quality = report["label_quality_diagnostics"]
    lines.extend(
        [
            "",
            "## Label-quality diagnostics",
            "",
            "The Dynamic World quality-proxy filters below are diagnostics of annual-product quality and selection effects, not independent validation sets or model-skill tests.",
            "",
            "| Target year | Full-grid observed changes | Dual-year retained changes | Dual-year retention | Preceding-year-only retained changes | Preceding-year-only retention | Preceding-year-only FoM (FLUS / Kernel / GeoFM-LDN) |",
            "|---:|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for year in YEARS:
        diagnostic = quality["by_target_year"][str(year)]
        dual = diagnostic["dual_year_confidence"]
        preceding = diagnostic["preceding_year_confidence_only"]
        fom = preceding["strict_fom_by_model"]
        lines.append(
            f"| {year} | {diagnostic['full_grid_observed_change_pixels']:,} | "
            f"{dual['observed_change_pixels']:,} | {dual['observed_change_retention_fraction']:.2%} | "
            f"{preceding['observed_change_pixels']:,} | {preceding['observed_change_retention_fraction']:.2%} | "
            f"{fom['geosos_flus']['mean']:.4f} / {fom['geospatial_kernel']['mean']:.4f} / {fom['paper58']['mean']:.4f} |"
        )
    lines.extend(
        [
            "",
            "## 当前结论",
            "",
            "- 2023 单步和 2024 两步开环均同时报告严格多类别 FoM 与旧二值 FoM。",
            "- 持久性与随机可行分配是预先声明的零模型，不得从主模型表中省略。",
            "- 模型比较应读取 JSON 中的 pairwise_bootstrap_95ci，而不是比较两个边际区间是否重叠。",
            "- Dynamic World质量代理筛选会改变被评分的观测变化组成，因此仅作为标签质量与选择效应诊断。",
            "- 这是历史条件分配结果，不是未来政策预测，也不是因果效应证据。",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--markdown", type=Path, default=DEFAULT_MARKDOWN)
    args = parser.parse_args()
    report = compile_report(output_path=args.output, markdown_path=args.markdown)
    print(
        json.dumps(
            {
                "status": report["status"],
                "mean_change_fom_deltas": report["mean_change_fom_deltas"],
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
