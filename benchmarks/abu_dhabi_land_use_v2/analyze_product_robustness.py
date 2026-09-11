#!/usr/bin/env python3
"""Compile the cross-product backtest and ArcGIS-v2 planning evidence."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import statistics
from pathlib import Path
from typing import Any

import matplotlib as mpl

mpl.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import rasterio

try:
    from .planning import OBJECTIVES, pareto_frontier, planning_metrics
except ImportError:
    from planning import OBJECTIVES, pareto_frontier, planning_metrics


HERE = Path(__file__).resolve().parent
REPOSITORY_ROOT = HERE.parents[1]
V1_ROOT = HERE.parent / "abu_dhabi_land_use_v1"
DEFAULT_ARCGIS_REPORT = HERE / "artifacts" / "arcgis_v2_historical_backtest" / "report.json"
DEFAULT_DYNAMIC_WORLD_REPORT = HERE / "artifacts" / "dynamic_world_matched_backtest" / "report.json"
DEFAULT_OUTPUT = HERE / "results_arcgis_v2" / "paper_refresh"
FIGURE_ROOT = REPOSITORY_ROOT / "figures"
MANUSCRIPT_ROOT = REPOSITORY_ROOT / "manuscript"
MODEL_IDS = ("geosos_flus", "geospatial_kernel", "paper58")
MODEL_LABELS = {
    "geosos_flus": "FLUS-style ANN–CA",
    "geospatial_kernel": "Geospatial Kernel",
    "paper58": "GeoFM-LDN",
    "random_minimum_change": "Random minimum-change",
}
MODEL_COLORS = {
    "geosos_flus": "#0072B2",
    "geospatial_kernel": "#D55E00",
    "paper58": "#009E73",
    "random_minimum_change": "#6B7280",
}
CLASS_NAMES = {
    1: "Water",
    2: "Woody vegetation",
    3: "Low vegetation",
    4: "Wetland",
    5: "Built",
    6: "Bare",
}
ARCGIS_RAW_TO_CANONICAL = {1: 1, 2: 2, 4: 4, 5: 3, 7: 5, 8: 6, 9: 0, 10: 0, 11: 3}
SCENARIOS = ("compact", "ecological_priority", "outward_growth")
SCENARIO_LABELS = {
    "compact": "Moderate growth",
    "ecological_priority": "Green-priority growth",
    "outward_growth": "High outward growth",
}


mpl.rcParams.update(
    {
        "font.family": "sans-serif",
        "font.sans-serif": ["Arial", "DejaVu Sans", "Liberation Sans"],
        "font.size": 8.4,
        "axes.titlesize": 9.3,
        "axes.labelsize": 8.5,
        "xtick.labelsize": 7.7,
        "ytick.labelsize": 7.7,
        "legend.fontsize": 7.7,
        "svg.fonttype": "none",
        "pdf.fonttype": 42,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.linewidth": 0.65,
        "savefig.facecolor": "white",
    }
)


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def repository_relative(path: Path) -> str:
    resolved = path.resolve()
    try:
        return resolved.relative_to(REPOSITORY_ROOT.resolve()).as_posix()
    except ValueError:
        return resolved.name


def read_band(path: Path) -> np.ndarray:
    with rasterio.open(path) as dataset:
        return dataset.read(1)


def require_backtest(path: Path, source_track: str) -> dict[str, Any]:
    if not path.is_file():
        raise FileNotFoundError(f"missing_backtest:{source_track}:{path}")
    report = read_json(path)
    if report.get("schema") != "gwm.abu_dhabi_cross_product_historical_backtest.v1":
        raise RuntimeError(f"backtest_schema_mismatch:{source_track}")
    if report.get("status") != "complete" or report.get("source_track") != source_track:
        raise RuntimeError(f"backtest_not_current:{source_track}")
    if report.get("temporal_firewall", {}).get("target_label_used_only_for_oracle_action_and_evaluation") is not True:
        raise RuntimeError(f"backtest_temporal_firewall_missing:{source_track}")
    return report


def source_agreement() -> list[dict[str, Any]]:
    source = read_json(HERE / "results_arcgis_v2" / "source_comparison.json")
    rows = []
    for year, entries in sorted(source["dynamic_world_cross_product_100m"].items()):
        matrix = np.zeros((6, 6), dtype=np.int64)
        for transition, count in entries.items():
            old, new = (int(value) for value in transition.split("->"))
            matrix[old - 1, new - 1] = int(count)
        total = int(matrix.sum())
        old_built = int(matrix[4].sum())
        new_built = int(matrix[:, 4].sum())
        both_built = int(matrix[4, 4])
        rows.append(
            {
                "year": int(year),
                "valid_cells": total,
                "same_class_agreement": float(np.trace(matrix) / total),
                "dynamic_world_built_cells": old_built,
                "arcgis_built_cells": new_built,
                "built_intersection_cells": both_built,
                "built_iou": float(both_built / (old_built + new_built - both_built)),
                "built_f1": float(2 * both_built / (old_built + new_built)),
            }
        )
    return rows


def cross_product_class_matrix() -> list[dict[str, Any]]:
    """Materialize the frozen 6 x 6 annual cross-product matrices in long form."""

    source = read_json(HERE / "results_arcgis_v2" / "source_comparison.json")
    rows = []
    for year, entries in sorted(source["dynamic_world_cross_product_100m"].items()):
        for dynamic_world_class in range(1, 7):
            for arcgis_class in range(1, 7):
                key = f"{dynamic_world_class}->{arcgis_class}"
                rows.append(
                    {
                        "year": int(year),
                        "dynamic_world_class_id": dynamic_world_class,
                        "dynamic_world_class": CLASS_NAMES[dynamic_world_class],
                        "arcgis_class_id": arcgis_class,
                        "arcgis_class": CLASS_NAMES[arcgis_class],
                        "cells": int(entries.get(key, 0)),
                    }
                )
    return rows


def product_class_counts() -> list[dict[str, Any]]:
    """Report product-native annual stocks without conflating them with truth."""

    tracks = (
        (
            "Dynamic World",
            V1_ROOT / "artifacts" / "abu_dhabi_city_100m_mask.tif",
            V1_ROOT / "artifacts" / "gee" / "land_cover",
            range(2017, 2025),
        ),
        (
            "ArcGIS-served IO/MS/Esri",
            HERE / "artifacts" / "abu_dhabi_city_100m_mask.tif",
            HERE / "artifacts" / "gee" / "land_cover",
            range(2017, 2026),
        ),
    )
    rows = []
    for product, mask_path, state_root, years in tracks:
        city = read_band(mask_path).astype(bool)
        for year in years:
            state = read_band(state_root / f"land_cover_{year}_100m.tif")
            valid = city & np.isin(state, range(1, 7))
            rows.append(
                {
                    "product": product,
                    "year": int(year),
                    "valid_cells": int(valid.sum()),
                    **{
                        CLASS_NAMES[class_id].lower().replace(" ", "_"): int(
                            np.count_nonzero(valid & (state == class_id))
                        )
                        for class_id in range(1, 7)
                    },
                }
            )
    return rows


def _aggregate_raw_to_canonical(raw: np.ndarray, mapping: dict[int, int], city: np.ndarray) -> np.ndarray:
    """Apply the frozen 10 m-to-100 m majority contract without writing a raster."""

    height, width = city.shape
    if raw.shape != (height * 10, width * 10):
        raise ValueError(f"native_shape_mismatch:{raw.shape}:{height},{width}")
    canonical_native = np.zeros_like(raw, dtype=np.uint8)
    for raw_class, canonical_class in mapping.items():
        canonical_native[raw == raw_class] = canonical_class
    blocks = canonical_native.reshape(height, 10, width, 10)
    class_counts = np.stack(
        [(blocks == class_id).sum(axis=(1, 3)) for class_id in range(1, 7)], axis=0
    )
    canonical = np.arange(1, 7, dtype=np.uint8)[class_counts.argmax(axis=0)]
    canonical[class_counts.max(axis=0) == 0] = 0
    canonical[~city] = 0
    return canonical


def rangeland_mapping_sensitivity() -> list[dict[str, Any]]:
    """Quantify the descriptive effect of mapping raw class 11 to bare instead.

    This uses the archived native labels and aggregation rule only. It does not
    refit any model, so it cannot be interpreted as a model-rank sensitivity.
    """

    city = read_band(HERE / "artifacts" / "abu_dhabi_city_100m_mask.tif").astype(bool)
    alternate = {**ARCGIS_RAW_TO_CANONICAL, 11: 6}
    rows = []
    native_root = HERE / "artifacts" / "arcgis_sentinel2_landcover" / "native"
    for year in range(2017, 2026):
        raw = read_band(native_root / f"arcgis_sentinel2_landcover_{year}_10m.tif")
        baseline = _aggregate_raw_to_canonical(raw, ARCGIS_RAW_TO_CANONICAL, city)
        alternate_state = _aggregate_raw_to_canonical(raw, alternate, city)
        valid = city & np.isin(baseline, range(1, 7))
        rows.append(
            {
                "year": year,
                "raw_rangeland_10m_pixels": int(np.count_nonzero(raw == 11)),
                "changed_100m_labels": int(np.count_nonzero(valid & (baseline != alternate_state))),
                "baseline_low_vegetation_cells": int(np.count_nonzero(valid & (baseline == 3))),
                "alternate_low_vegetation_cells": int(np.count_nonzero(valid & (alternate_state == 3))),
                "baseline_bare_cells": int(np.count_nonzero(valid & (baseline == 6))),
                "alternate_bare_cells": int(np.count_nonzero(valid & (alternate_state == 6))),
            }
        )
    return rows


def temporal_product_diagnostics() -> list[dict[str, Any]]:
    city = read_band(HERE / "artifacts" / "abu_dhabi_city_100m_mask.tif").astype(bool)
    roots = {
        "arcgis": HERE / "artifacts" / "gee" / "land_cover",
        "dynamic_world": V1_ROOT / "artifacts" / "gee" / "land_cover",
    }
    year_sets = {"arcgis": tuple(range(2017, 2026)), "dynamic_world": tuple(range(2017, 2025))}
    output = []
    for source_track, root in roots.items():
        years = year_sets[source_track]
        states = {year: read_band(root / f"land_cover_{year}_100m.tif") for year in years}
        for start_year, target_year in zip(years[:-1], years[1:], strict=True):
            valid = city & np.isin(states[start_year], range(1, 7)) & np.isin(states[target_year], range(1, 7))
            changed = valid & (states[start_year] != states[target_year])
            row = {
                "source_track": source_track,
                "start_year": start_year,
                "target_year": target_year,
                "valid_cells": int(valid.sum()),
                "changed_cells": int(changed.sum()),
                "changed_fraction": float(changed.sum() / valid.sum()),
                "one_year_reversion_fraction": None,
            }
            if target_year + 1 in states:
                next_valid = valid & np.isin(states[target_year + 1], range(1, 7))
                changed_next_eligible = changed & next_valid
                row["one_year_reversion_fraction"] = float(
                    np.count_nonzero(changed_next_eligible & (states[target_year + 1] == states[start_year]))
                    / max(1, np.count_nonzero(changed_next_eligible))
                )
            output.append(row)
    return output


def backtest_rows(report: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for summary in report["summaries"]:
        metrics = summary["metrics"]
        rows.append(
            {
                "source_track": report["source_track"],
                "origin_year": int(summary["origin_year"]),
                "target_year": int(summary["target_year"]),
                "model_id": summary["model_id"],
                "seed_count": int(summary["seed_count"]),
                "change_fom_mean": float(metrics["change_figure_of_merit"]["mean"]),
                "change_fom_sd": float(metrics["change_figure_of_merit"]["population_standard_deviation"]),
                "change_f1_mean": float(metrics["change_f1"]["mean"]),
                "overall_accuracy_mean": float(metrics["overall_accuracy"]["mean"]),
                "macro_f1_mean": float(metrics["macro_f1"]["mean"]),
            }
        )
    return rows


def backtest_rankings(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    output = []
    keys = sorted({(row["source_track"], row["target_year"]) for row in rows})
    for source_track, target_year in keys:
        selected = [
            row for row in rows
            if row["source_track"] == source_track
            and row["target_year"] == target_year
            and row["model_id"] in MODEL_IDS
        ]
        ranked = sorted(selected, key=lambda row: row["change_fom_mean"], reverse=True)
        for rank, row in enumerate(ranked, start=1):
            output.append({**row, "rank": rank})
    return output


def planning_v2() -> dict[str, Any]:
    planning_root = HERE / "artifacts" / "planning_arcgis_2026_2031"
    origin = read_band(HERE / "artifacts" / "gee" / "land_cover" / "land_cover_2025_100m.tif")
    valid = read_band(HERE / "artifacts" / "bundle" / "common_valid_mask_100m.tif").astype(bool)
    hard = read_band(HERE / "artifacts" / "bundle" / "hard_exclusion_2025_100m.tif").astype(bool)
    roads = read_band(HERE / "artifacts" / "osm" / "road_accessibility_100m.tif")
    with rasterio.open(HERE / "artifacts" / "osm" / "road_accessibility_100m.tif") as dataset:
        road_stack = dataset.read()
    road_distance = road_stack[0]
    major_road_distance = road_stack[1]
    scenarios = read_json(HERE / "planning_scenarios_arcgis_2025_2031.json")
    scenario_targets = {
        row["scenario_id"]: {int(key): int(value) for key, value in row["target_counts_by_year"]["2031"].items()}
        for row in scenarios["scenarios"]
    }
    seed_rows = []
    for model_id in MODEL_IDS:
        for scenario_id in SCENARIOS:
            for seed in (31, 47, 73):
                prediction = read_band(
                    planning_root / model_id / scenario_id / f"seed_{seed}" / "prediction_2031.tif"
                )
                metrics = planning_metrics(
                    prediction,
                    origin_state=origin,
                    valid_mask=valid,
                    hard_exclusion_mask=hard,
                    target_counts=scenario_targets[scenario_id],
                    road_distance_m=road_distance,
                    major_road_distance_m=major_road_distance,
                )
                seed_rows.append(
                    {
                        "model_id": model_id,
                        "scenario_id": scenario_id,
                        "target_year": 2031,
                        "seed": seed,
                        **metrics,
                    }
                )
    candidates = []
    for model_id in MODEL_IDS:
        for scenario_id in SCENARIOS:
            selected = [
                row for row in seed_rows
                if row["model_id"] == model_id and row["scenario_id"] == scenario_id
            ]
            mean_metrics = {
                key: float(statistics.mean(float(row[key]) for row in selected))
                for key in selected[0]
                if key not in {"model_id", "scenario_id", "target_year", "seed", "actual_class_counts", "target_class_counts"}
                and isinstance(selected[0][key], (int, float))
            }
            objective_uncertainty = {
                objective: {
                    "mean": float(statistics.mean(float(row[objective]) for row in selected)),
                    "population_std": float(statistics.pstdev(float(row[objective]) for row in selected)),
                    "values": [float(row[objective]) for row in selected],
                }
                for objective in OBJECTIVES
            }
            candidates.append(
                {
                    "candidate_id": f"{model_id}:{scenario_id}",
                    "model_id": model_id,
                    "scenario_id": scenario_id,
                    **mean_metrics,
                    "objective_uncertainty": objective_uncertainty,
                }
            )
    frontiers = {}
    for scenario_id in SCENARIOS:
        selected = [row for row in candidates if row["scenario_id"] == scenario_id]
        frontiers[scenario_id] = pareto_frontier(selected, objectives=OBJECTIVES)
    v1 = read_json(V1_ROOT / "planning_comparison_report_public_2025_2031_current.json")
    return {
        "objective_set": OBJECTIVES,
        "arcgis_v2_seed_rows": seed_rows,
        "arcgis_v2_final_candidates": candidates,
        "arcgis_v2_frontier_within_scenario": frontiers,
        "dynamic_world_v1_frontier_within_scenario": v1["pareto_frontier_within_scenario"],
    }


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        raise ValueError(f"empty_csv:{path}")
    columns = list(rows[0])
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def figure_source_rows(
    agreement: list[dict[str, Any]],
    rows: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    columns = (
        "panel",
        "year",
        "source_track",
        "model_id",
        "same_class_agreement",
        "built_iou",
        "mapped_built_area_km2",
        "change_fom_mean",
        "change_fom_population_sd",
        "arcgis_minus_dynamic_world_change_fom",
    )

    def record(**values: Any) -> dict[str, Any]:
        return {column: values.get(column, "") for column in columns}

    def public_model_id(model_id: str) -> str:
        return "geofm_ldn" if model_id == "paper58" else model_id

    output = []
    for row in agreement:
        output.extend(
            [
                record(
                    panel="a_b_source_agreement",
                    year=row["year"],
                    source_track="dynamic_world",
                    same_class_agreement=row["same_class_agreement"],
                    built_iou=row["built_iou"],
                    mapped_built_area_km2=row["dynamic_world_built_cells"] / 100,
                ),
                record(
                    panel="a_b_source_agreement",
                    year=row["year"],
                    source_track="arcgis_served_io_microsoft_esri",
                    same_class_agreement=row["same_class_agreement"],
                    built_iou=row["built_iou"],
                    mapped_built_area_km2=row["arcgis_built_cells"] / 100,
                ),
            ]
        )
    arcgis_2025 = read_json(HERE / "results_arcgis_v2" / "source_comparison.json")["class_counts_100m"]["2025"]["5"] / 100
    output.append(
        record(
            panel="a_source_stock_only",
            year=2025,
            source_track="arcgis_served_io_microsoft_esri",
            mapped_built_area_km2=arcgis_2025,
        )
    )
    for row in rows:
        output.append(
            record(
                panel="c_backtest" if row["source_track"] == "arcgis" else "d_matched_difference_input",
                year=row["target_year"],
                source_track=row["source_track"],
                model_id=public_model_id(row["model_id"]),
                change_fom_mean=row["change_fom_mean"],
                change_fom_population_sd=row["change_fom_sd"],
            )
        )
    for model_id in MODEL_IDS:
        for target_year in sorted(
            set(row["target_year"] for row in rows if row["source_track"] == "arcgis")
            & set(row["target_year"] for row in rows if row["source_track"] == "dynamic_world")
        ):
            values = {
                row["source_track"]: row["change_fom_mean"]
                for row in rows
                if row["model_id"] == model_id and row["target_year"] == target_year
            }
            output.append(
                record(
                    panel="d_product_difference",
                    year=target_year,
                    model_id=public_model_id(model_id),
                    arcgis_minus_dynamic_world_change_fom=values["arcgis"] - values["dynamic_world"],
                )
            )
    return output


def render_supplementary_table(summary: dict[str, Any]) -> str:
    metrics = summary["backtest_rows"]
    temporal = {
        (row["source_track"], row["target_year"]): row
        for row in summary["temporal_product_diagnostics"]
    }
    lines = [
        "# Supplementary Table S6. Cross-product historical robustness",
        "",
        "All values use the frozen Abu Dhabi city 100-m grid. Strict destination-change FoM values are means across seeds 31, 47 and 73. Each expanding-window fold fits only observations available through its origin year; the target label supplies oracle class totals and evaluation only. Dynamic World and the ArcGIS-served Impact Observatory/Microsoft/Esri series retain their product-native label and aggregation-quality semantics, so this is a whole-product-pipeline robustness test rather than an isolated label substitution. Neither product is authoritative local land-use truth.",
        "",
        "| Product | Target | Observed change (%) | One-year reversion (%) | Random | FLUS-style | Kernel | GeoFM-LDN |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for source_track in ("dynamic_world", "arcgis"):
        targets = sorted(
            set(row["target_year"] for row in metrics if row["source_track"] == source_track)
        )
        for target_year in targets:
            values = {
                row["model_id"]: row["change_fom_mean"]
                for row in metrics
                if row["source_track"] == source_track and row["target_year"] == target_year
            }
            diagnostic = temporal[(source_track, target_year)]
            reversion = diagnostic["one_year_reversion_fraction"]
            reversion_text = "n/a" if reversion is None else f"{100 * reversion:.2f}"
            label = "Dynamic World" if source_track == "dynamic_world" else "ArcGIS-served IO/MS/Esri"
            lines.append(
                f"| {label} | {target_year} | {100 * diagnostic['changed_fraction']:.2f} | {reversion_text} | "
                f"{values['random_minimum_change']:.4f} | {values['geosos_flus']:.4f} | "
                f"{values['geospatial_kernel']:.4f} | {values['paper58']:.4f} |"
            )
    lines += [
        "",
        "Same-year agreement between the two harmonized products is reported below. A 100-m cell contributes only where both products have a usable canonical label.",
        "",
        "| Year | All-class agreement | Built-class IoU | Dynamic World built (km2) | ArcGIS-served built (km2) |",
        "|---:|---:|---:|---:|---:|",
    ]
    for row in summary["source_agreement"]:
        lines.append(
            f"| {row['year']} | {row['same_class_agreement']:.4f} | {row['built_iou']:.4f} | "
            f"{row['dynamic_world_built_cells'] / 100:.2f} | {row['arcgis_built_cells'] / 100:.2f} |"
        )
    lines += [
        "",
        "## Product-native annual class stocks",
        "",
        "Counts below use each product's own city-valid 100-m state layer, rather than the smaller pairwise common-coverage mask. They describe mapped class prevalence, not verified land-cover change or land-use truth.",
        "",
        "| Product | Year | Valid cells | Water | Woody vegetation | Low vegetation | Wetland | Built | Bare |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in summary["product_class_counts"]:
        lines.append(
            f"| {row['product']} | {row['year']} | {row['valid_cells']} | {row['water']} | "
            f"{row['woody_vegetation']} | {row['low_vegetation']} | {row['wetland']} | "
            f"{row['built']} | {row['bare']} |"
        )
    lines += [
        "",
        "The ArcGIS-served sequence has a material class-composition discontinuity: built rises from 21,608 cells in 2021 to 28,214 in 2022, while bare falls from 34,521 to 27,821; woody vegetation and wetland later approach zero. The upstream Living Atlas item does not publish annual model-version identifiers, so this table cannot assign a cause. It is therefore evidence of a product-series break, not evidence that these mapped transitions occurred on the ground.",
        "",
        "The full annual 6 x 6 Dynamic World-to-ArcGIS class matrix is supplied as `results_arcgis_v2/paper_refresh/cross_product_class_matrix.csv`. Its rows use the pairwise common-coverage grid; zeros are retained so every annual matrix is explicit.",
        "",
        "## Rangeland crosswalk sensitivity",
        "",
        "The source service names raw class 11 `Rangeland`. The frozen benchmark maps it to low vegetation. The counterfactual below maps only raw class 11 to bare before the identical 10 x 10 majority aggregation. No model was refit, so this is a label-aggregation sensitivity, not a historical-skill or planning-rank sensitivity.",
        "",
        "| Year | Raw rangeland 10-m pixels | Changed 100-m labels | Baseline low vegetation | Alternate low vegetation | Baseline bare | Alternate bare |",
        "|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in summary["rangeland_mapping_sensitivity"]:
        lines.append(
            f"| {row['year']} | {row['raw_rangeland_10m_pixels']} | {row['changed_100m_labels']} | "
            f"{row['baseline_low_vegetation_cells']} | {row['alternate_low_vegetation_cells']} | "
            f"{row['baseline_bare_cells']} | {row['alternate_bare_cells']} |"
        )
    lines += [
        "",
        f"ArcGIS report SHA-256: `{summary['input_reports']['arcgis']['sha256']}`.",
        "",
        f"Dynamic World report SHA-256: `{summary['input_reports']['dynamic_world']['sha256']}`.",
        "",
    ]
    return "\n".join(lines)


def render_supplementary_planning_table(summary: dict[str, Any]) -> str:
    """Expose the ArcGIS-track objective trade-offs behind frontier membership."""

    planning = summary["planning"]
    frontiers = planning["arcgis_v2_frontier_within_scenario"]
    lines = [
        "# Supplementary Table S1. ArcGIS-served 2031 planning objective profiles",
        "",
        "Values are means plus or minus population standard deviations across computational seeds 31, 47 and 73. All values are conditional on the ArcGIS-served 2025 origin state and product-specific 2026–2031 scenario actions. Lower values are preferred for all three public proxy objectives. A frontier mark denotes non-domination within that scenario only; it is not a forecast-accuracy or welfare ranking.",
        "",
        "| Scenario | Model | New built to major roads (m) | New built to prior built (m) | Union-built components per 1,000 cells | Within-scenario frontier |",
        "|---|---|---:|---:|---:|:---:|",
    ]
    for scenario in SCENARIOS:
        candidates = [
            row for row in planning["arcgis_v2_final_candidates"] if row["scenario_id"] == scenario
        ]
        for row in candidates:
            uncertainty = row["objective_uncertainty"]
            road = uncertainty["new_built_mean_major_road_distance_m"]
            prior = uncertainty["new_built_mean_prior_built_distance_m"]
            components = uncertainty["combined_built_components_per_1000_pixels"]
            mark = "*" if row["candidate_id"] in frontiers[scenario] else ""
            lines.append(
                f"| {SCENARIO_LABELS[scenario]} | {MODEL_LABELS[row['model_id']]} | "
                f"{road['mean']:.1f} +/- {road['population_std']:.1f} | "
                f"{prior['mean']:.1f} +/- {prior['population_std']:.1f} | "
                f"{components['mean']:.3f} +/- {components['population_std']:.3f} | {mark} |"
            )
    lines += [
        "",
        "In this product track, FLUS-style ANN-CA has lower mean major-road distance and lower union-built component density, while Kernel has lower mean distance to prior built cells in all three scenarios. This dimension-specific trade-off differs from the Dynamic World-origin table and is why unchanged frontier membership must not be interpreted as unchanged planning behaviour.",
        "",
    ]
    return "\n".join(lines)


def panel_label(axis: plt.Axes, label: str) -> None:
    axis.text(-0.15, 1.10, label, transform=axis.transAxes, fontweight="bold", fontsize=10, va="top")


def render_figure(
    agreement: list[dict[str, Any]],
    rows: list[dict[str, Any]],
) -> None:
    FIGURE_ROOT.mkdir(parents=True, exist_ok=True)
    fig, axes = plt.subplots(2, 2, figsize=(7.35, 6.2))

    axis = axes[0, 0]
    years = [row["year"] for row in agreement]
    axis.plot(years, [row["dynamic_world_built_cells"] / 100 for row in agreement], "o-", color="#5B6F95", label="Dynamic World")
    axis.plot(years, [row["arcgis_built_cells"] / 100 for row in agreement], "s-", color="#C65B4B", label="IO/Microsoft/Esri")
    arcgis_2025 = read_json(HERE / "results_arcgis_v2" / "source_comparison.json")["class_counts_100m"]["2025"]["5"] / 100
    axis.plot([2025], [arcgis_2025], "s", color="#C65B4B")
    axis.plot([2024, 2025], [agreement[-1]["arcgis_built_cells"] / 100, arcgis_2025], "--", color="#C65B4B", linewidth=1)
    axis.set(title="Built-area stock differs by product", xlabel="Year", ylabel="Mapped built area (km²)")
    axis.annotate(
        "IO/Microsoft/Esri",
        xy=(2024, agreement[-1]["arcgis_built_cells"] / 100),
        xytext=(2021.9, 344),
        color="#A34434",
        fontsize=7.2,
        ha="left",
        va="bottom",
    )
    axis.annotate(
        "Dynamic World",
        xy=(2024, agreement[-1]["dynamic_world_built_cells"] / 100),
        xytext=(2022.0, 132),
        color="#40577F",
        fontsize=7.2,
        ha="left",
        va="top",
    )
    axis.set_ylim(60, 360)
    panel_label(axis, "A")

    axis = axes[0, 1]
    axis.plot(years, [row["same_class_agreement"] for row in agreement], "o-", color="#6B7280", label="All-class agreement")
    axis.plot(years, [row["built_iou"] for row in agreement], "s-", color="#B45309", label="Built-class IoU")
    axis.set(title="Same-year cross-product agreement", xlabel="Year", ylabel="Agreement")
    axis.set_ylim(0, 1)
    axis.legend(frameon=False)
    panel_label(axis, "B")

    axis = axes[1, 0]
    arcgis_rows = [row for row in rows if row["source_track"] == "arcgis"]
    for model_id in (*MODEL_IDS, "random_minimum_change"):
        selected = sorted(
            [row for row in arcgis_rows if row["model_id"] == model_id],
            key=lambda row: row["target_year"],
        )
        axis.errorbar(
            [row["target_year"] for row in selected],
            [row["change_fom_mean"] for row in selected],
            yerr=[row["change_fom_sd"] for row in selected],
            marker="o" if model_id != "random_minimum_change" else "x",
            linewidth=1.3,
            capsize=2,
            color=MODEL_COLORS[model_id],
            label=MODEL_LABELS[model_id],
        )
    axis.set(title="ArcGIS-served product: one-step allocation skill", xlabel="Target year", ylabel="Strict change FoM")
    axis.set_ylim(0, 0.62)
    axis.legend(frameon=False, ncol=2, fontsize=6.7, loc="upper center")
    panel_label(axis, "C")

    axis = axes[1, 1]
    matched_years = sorted(
        set(row["target_year"] for row in rows if row["source_track"] == "arcgis")
        & set(row["target_year"] for row in rows if row["source_track"] == "dynamic_world")
    )
    matrix = np.zeros((len(MODEL_IDS), len(matched_years)), dtype=float)
    for model_index, model_id in enumerate(MODEL_IDS):
        for year_index, target_year in enumerate(matched_years):
            values = {
                row["source_track"]: row["change_fom_mean"]
                for row in rows
                if row["model_id"] == model_id and row["target_year"] == target_year
            }
            matrix[model_index, year_index] = values["arcgis"] - values["dynamic_world"]
    limit = max(0.05, float(np.max(np.abs(matrix))))
    image = axis.imshow(matrix, cmap="RdBu_r", vmin=-limit, vmax=limit, aspect="auto")
    for model_index in range(len(MODEL_IDS)):
        for year_index in range(len(matched_years)):
            value = matrix[model_index, year_index]
            axis.text(year_index, model_index, f"{value:+.3f}", ha="center", va="center", fontsize=7, color="white" if abs(value) > 0.55 * limit else "#111827")
    axis.set_xticks(range(len(matched_years)), matched_years)
    axis.set_yticks(range(len(MODEL_IDS)), [MODEL_LABELS[value] for value in MODEL_IDS])
    axis.set(title="Product difference in strict FoM", xlabel="Matched one-step target year")
    fig.colorbar(image, ax=axis, fraction=0.045, pad=0.04, label="FoM difference")
    panel_label(axis, "D")

    axis = axes[0, 0]
    axis.axvline(2021.5, color="#4B5563", linestyle="--", linewidth=0.8, zorder=0)
    axis.annotate(
        "possible series\nbreak",
        xy=(2021.5, 276),
        xytext=(2020.1, 310),
        arrowprops={"arrowstyle": "-", "color": "#4B5563", "linewidth": 0.6},
        color="#4B5563",
        fontsize=6.6,
        ha="center",
        va="bottom",
    )
    axes[1, 0].legend(
        frameon=False,
        ncol=2,
        fontsize=6.5,
        loc="upper center",
        bbox_to_anchor=(0.58, 0.99),
        handletextpad=0.4,
        columnspacing=0.8,
    )
    fig.tight_layout(h_pad=2.0, w_pad=1.5)
    base = FIGURE_ROOT / "fig04_product_robustness"
    svg = base.with_suffix(".svg")
    fig.savefig(svg, bbox_inches="tight", pad_inches=0.04)
    svg.write_text("\n".join(line.rstrip() for line in svg.read_text(encoding="utf-8").splitlines()) + "\n", encoding="utf-8")
    fig.savefig(base.with_suffix(".pdf"), bbox_inches="tight", pad_inches=0.04)
    fig.savefig(base.with_suffix(".png"), dpi=600, bbox_inches="tight", pad_inches=0.04)
    fig.savefig(base.with_suffix(".tiff"), dpi=600, bbox_inches="tight", pad_inches=0.04)
    plt.close(fig)


def render_markdown(summary: dict[str, Any]) -> str:
    rankings = summary["backtest_rankings"]
    lines = [
        "# ArcGIS and Dynamic World product-robustness analysis",
        "",
        "This is a whole-public-product-pipeline robustness experiment on the frozen Abu Dhabi city research boundary. It is not validation against authoritative local land-use truth.",
        "",
        "## Same-year product agreement",
        "",
        "| Year | All-class agreement | Built IoU | Dynamic World built (km²) | ArcGIS built (km²) |",
        "|---:|---:|---:|---:|---:|",
    ]
    for row in summary["source_agreement"]:
        lines.append(
            f"| {row['year']} | {row['same_class_agreement']:.3f} | {row['built_iou']:.3f} | "
            f"{row['dynamic_world_built_cells'] / 100:.2f} | {row['arcgis_built_cells'] / 100:.2f} |"
        )
    lines += ["", "## Matched one-step model rankings", "", "| Product | Target | Rank 1 | Rank 2 | Rank 3 |", "|---|---:|---|---|---|"]
    for source_track, target_year in sorted({(row["source_track"], row["target_year"]) for row in rankings}):
        selected = sorted(
            [row for row in rankings if row["source_track"] == source_track and row["target_year"] == target_year],
            key=lambda row: row["rank"],
        )
        cells = [f"{MODEL_LABELS[row['model_id']]} ({row['change_fom_mean']:.3f})" for row in selected]
        lines.append(f"| {source_track} | {target_year} | " + " | ".join(cells) + " |")
    lines += [
        "",
        "## Planning frontier sensitivity",
        "",
        "The planning comparison is conditional on each product-specific origin state and the same released public proxy objectives. Frontier membership is not a forecast-accuracy ranking, and stable membership does not imply unchanged objective trade-offs.",
        "",
        "| Scenario | Dynamic World v1 frontier | ArcGIS v2 frontier |",
        "|---|---|---|",
    ]
    planning = summary["planning"]
    for scenario in SCENARIOS:
        lines.append(
            f"| {SCENARIO_LABELS[scenario]} | "
            f"{', '.join(planning['dynamic_world_v1_frontier_within_scenario'][scenario])} | "
            f"{', '.join(planning['arcgis_v2_frontier_within_scenario'][scenario])} |"
        )
    lines += [
        "",
        "## Interpretation boundary",
        "",
        "- Native source pixels are 10 m, but all model comparisons use the frozen 100 m contract.",
        "- Product-native quality terms are retained: Dynamic World maximum temporal-mean probability (a quality proxy) and ArcGIS 100 m majority fraction. The comparison therefore tests complete public-product pipelines rather than an isolated label effect.",
        "- Origin states, oracle actions and origin-year water/wetland masks are product specific; all other protocol settings are matched.",
        "- Oracle target class counts isolate spatial allocation; they are not a deployable demand forecast.",
        "- Differences between product tracks quantify label-product dependence, not which product is correct.",
        "- The 2026-2031 maps remain conditional scenario stress tests until authoritative local validation is available.",
        "",
    ]
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--arcgis-report", type=Path, default=DEFAULT_ARCGIS_REPORT)
    parser.add_argument("--dynamic-world-report", type=Path, default=DEFAULT_DYNAMIC_WORLD_REPORT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    arcgis = require_backtest(args.arcgis_report, "arcgis")
    dynamic_world = require_backtest(args.dynamic_world_report, "dynamic_world")
    agreement = source_agreement()
    class_matrix = cross_product_class_matrix()
    class_counts = product_class_counts()
    rangeland_sensitivity = rangeland_mapping_sensitivity()
    temporal = temporal_product_diagnostics()
    rows = backtest_rows(arcgis) + backtest_rows(dynamic_world)
    rankings = backtest_rankings(rows)
    planning = planning_v2()
    summary = {
        "schema": "gwm.abu_dhabi_product_robustness_analysis.v1",
        "status": "complete",
        "spatial_scope": "Frozen Abu Dhabi city research boundary (OSM R4479763)",
        "input_reports": {
            "arcgis": {"path": repository_relative(args.arcgis_report), "sha256": sha256(args.arcgis_report)},
            "dynamic_world": {"path": repository_relative(args.dynamic_world_report), "sha256": sha256(args.dynamic_world_report)},
        },
        "comparison_design": {
            "type": "whole_public_product_pipeline_robustness",
            "matched": ["boundary", "100_m_grid", "model_implementations", "seeds", "target_year_protocol", "oracle_action_rule", "evaluator", "bootstrap"],
            "product_specific": ["annual_labels", "origin_state", "oracle_class_totals", "origin_water_wetland_mask", "quality_weight_semantics"],
        },
        "source_agreement": agreement,
        "cross_product_class_matrix": class_matrix,
        "product_class_counts": class_counts,
        "rangeland_mapping_sensitivity": rangeland_sensitivity,
        "temporal_product_diagnostics": temporal,
        "backtest_rows": rows,
        "backtest_rankings": rankings,
        "planning": planning,
        "claim_boundary": "Cross-public-product robustness, not authoritative local validation.",
    }
    args.output.mkdir(parents=True, exist_ok=True)
    (args.output / "product_robustness_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (args.output / "product_robustness_summary.md").write_text(render_markdown(summary), encoding="utf-8")
    write_csv(args.output / "source_agreement.csv", agreement)
    write_csv(args.output / "cross_product_class_matrix.csv", class_matrix)
    write_csv(args.output / "product_class_counts.csv", class_counts)
    write_csv(args.output / "rangeland_mapping_sensitivity.csv", rangeland_sensitivity)
    write_csv(args.output / "temporal_product_diagnostics.csv", temporal)
    write_csv(args.output / "historical_backtest_metrics.csv", rows)
    write_csv(args.output / "historical_backtest_rankings.csv", rankings)
    write_csv(MANUSCRIPT_ROOT / "source_data_fig04_product_robustness.csv", figure_source_rows(agreement, rows))
    (MANUSCRIPT_ROOT / "supplementary_table_S6_product_robustness.md").write_text(
        render_supplementary_table(summary),
        encoding="utf-8",
    )
    (MANUSCRIPT_ROOT / "supplementary_table_S1_arcgis_planning_objectives.md").write_text(
        render_supplementary_planning_table(summary),
        encoding="utf-8",
    )
    render_figure(agreement, rows)
    print(json.dumps({"status": "complete", "output": str(args.output), "figure": str(FIGURE_ROOT / "fig04_product_robustness.png")}, ensure_ascii=False))


if __name__ == "__main__":
    main()
