#!/usr/bin/env python3
"""Compile planning metrics, ensemble rasters, and a transparent Pareto frontier."""

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
from planning import OBJECTIVE_METADATA, OBJECTIVES, pareto_frontier, planning_metrics

HERE = Path(__file__).resolve().parent
BUNDLE_ROOT = HERE / "artifacts/bundle"
INPUT_ROOT = HERE / "artifacts/gee"
OSM_ROOT = HERE / "artifacts/osm"
DEFAULT_INPUT = HERE / "planning_scenario_report_public_2025_2031_current.json"
DEFAULT_OUTPUT = HERE / "planning_comparison_report_public_2025_2031_current.json"
DEFAULT_MARKDOWN = HERE / "planning_comparison_report_public_2025_2031_current.md"
DEFAULT_SCENARIO_CONFIG = HERE / "planning_scenarios_public_2025_2031.json"
DEFAULT_ENSEMBLE_ROOT = HERE / "artifacts/planning_public_2025_2031"
MODEL_IDS = ("geosos_flus", "geospatial_kernel", "paper58")
SCENARIO_IDS = ("compact", "ecological_priority", "outward_growth")
SCENARIO_LABELS = {
    "compact": "Moderate growth (legacy compact)",
    "ecological_priority": "Green-priority growth",
    "outward_growth": "High outward growth",
}


def _read(path: Path) -> tuple[np.ndarray, dict[str, Any]]:
    with rasterio.open(path) as dataset:
        return dataset.read(), dataset.profile.copy()


def _report_path(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(HERE.resolve()))
    except ValueError:
        return f"external/{path.name}"


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
    temporary = path.with_suffix(f".partial.{os.getpid()}.tif")
    with rasterio.open(temporary, "w", **profile) as dataset:
        dataset.write(state.astype(np.uint8), 1)
        dataset.set_band_description(1, "three_seed_majority_scenario")
    os.replace(temporary, path)


def majority_vote(states: list[np.ndarray]) -> np.ndarray:
    stack = np.stack(states)
    counts = np.stack(
        [np.count_nonzero(stack == value, axis=0) for value in range(1, 7)]
    )
    result = np.argmax(counts, axis=0).astype(np.uint8) + 1
    result[np.all(stack == 0, axis=0)] = 0
    return result


def _normalize_counts(values: dict[str | int, Any]) -> dict[int, int]:
    return {int(key): int(value) for key, value in values.items()}


def _scenario_targets(
    scenario_config: Path, years: tuple[int, ...]
) -> dict[tuple[str, int], dict[int, int]]:
    scenarios = json.loads(scenario_config.read_text(encoding="utf-8"))["scenarios"]
    return {
        (str(row["scenario_id"]), year): _normalize_counts(
            row["target_counts_by_year"][str(year)]
        )
        for row in scenarios
        for year in years
    }


def _numeric_means(rows: list[dict[str, Any]]) -> dict[str, float]:
    keys = [
        key
        for key, value in rows[0].items()
        if isinstance(value, (int, float)) and not isinstance(value, bool)
    ]
    return {key: statistics.mean(float(row[key]) for row in rows) for key in keys}


def _objective_summary(rows: list[dict[str, Any]]) -> dict[str, Any]:
    result = {}
    for key in OBJECTIVES:
        values = [float(row[key]) for row in rows]
        result[key] = {
            "mean": statistics.mean(values),
            "population_std": statistics.pstdev(values),
            "values": values,
        }
    return result


def _find_year(
    model_report: dict[str, Any], *, seed: int, scenario_id: str, year: int
) -> dict[str, Any]:
    seed_row = next(row for row in model_report["seeds"] if int(row["seed"]) == seed)
    scenario = next(
        row for row in seed_row["scenarios"] if row["scenario_id"] == scenario_id
    )
    return next(row for row in scenario["years"] if int(row["target_year"]) == year)


def compile_report(
    *,
    input_path: Path,
    output_path: Path,
    markdown_path: Path,
    scenario_config: Path,
    ensemble_root: Path,
) -> dict[str, Any]:
    source = json.loads(input_path.read_text(encoding="utf-8"))
    if source.get("status") != "complete" or source.get("revision_status") not in {
        "current_protocol_run",
        "recomputed_from_existing_rasters",
    }:
        raise ValueError(
            "planning_scenarios_not_current_protocol_run:"
            f"{source.get('status', 'no_status')}/"
            f"{source.get('revision_status', 'no_revision')}"
        )
    if set(source["models"]) != set(MODEL_IDS):
        raise ValueError("planning_three_models_required")

    years = tuple(int(value) for value in source["target_years"])
    if not years or years != tuple(range(years[0], years[-1] + 1)):
        raise ValueError(f"target_years_must_be_contiguous:{years}")
    scenario_ids = tuple(str(value) for value in source["scenario_ids"])
    if set(scenario_ids) != set(SCENARIO_IDS):
        raise ValueError(f"unexpected_scenarios:{scenario_ids}")
    origin_data, reference = _read(
        INPUT_ROOT / "land_cover/land_cover_2024_100m.tif"
    )
    valid_data, _ = _read(BUNDLE_ROOT / "common_valid_mask_100m.tif")
    hard_data, _ = _read(BUNDLE_ROOT / "hard_exclusion_2024_100m.tif")
    roads, _ = _read(OSM_ROOT / "road_accessibility_100m.tif")
    origin = origin_data[0]
    valid = valid_data[0].astype(bool)
    hard = hard_data[0].astype(bool)
    targets = _scenario_targets(scenario_config, years)
    seeds = tuple(int(value) for value in source["seeds"])
    if seeds != (31, 47, 73):
        raise ValueError(f"three_frozen_seeds_required:{seeds}")

    seed_metrics = []
    aggregate: dict[str, dict[str, dict[str, Any]]] = {}
    ensembles: dict[str, dict[str, dict[str, Any]]] = {}
    final_candidates = []
    for model_id in MODEL_IDS:
        aggregate[model_id] = {}
        ensembles[model_id] = {}
        model_report = source["models"][model_id]
        for scenario_id in scenario_ids:
            aggregate[model_id][scenario_id] = {}
            ensembles[model_id][scenario_id] = {}
            final_seed_rows = []
            for year in years:
                rows = []
                states = []
                for seed in seeds:
                    year_record = _find_year(
                        model_report,
                        seed=seed,
                        scenario_id=scenario_id,
                        year=year,
                    )
                    source_prediction_path = Path(year_record["prediction_path"])
                    prediction_path = (
                        source_prediction_path
                        if source_prediction_path.is_absolute()
                        else HERE / source_prediction_path
                    )
                    state_data, _ = _read(prediction_path)
                    state = state_data[0]
                    metrics = planning_metrics(
                        state,
                        origin_state=origin,
                        valid_mask=valid,
                        hard_exclusion_mask=hard,
                        target_counts=targets[(scenario_id, year)],
                        road_distance_m=roads[0],
                        major_road_distance_m=roads[1],
                    )
                    row = {
                        "model_id": model_id,
                        "scenario_id": scenario_id,
                        "seed": seed,
                        "target_year": year,
                        "prediction_path": _report_path(prediction_path),
                        **metrics,
                    }
                    seed_metrics.append(row)
                    rows.append(metrics)
                    states.append(state)
                aggregate[model_id][scenario_id][str(year)] = {
                    "means": _numeric_means(rows),
                    "objectives": _objective_summary(rows),
                }
                if year == years[-1]:
                    final_seed_rows = rows

                ensemble = majority_vote(states)
                ensemble_path = (
                    ensemble_root
                    / model_id
                    / scenario_id
                    / "ensemble"
                    / f"prediction_{year}.tif"
                )
                _write(ensemble_path, ensemble, reference)
                ensembles[model_id][scenario_id][str(year)] = {
                    "prediction_path": _report_path(ensemble_path),
                    "metrics": planning_metrics(
                        ensemble,
                        origin_state=origin,
                        valid_mask=valid,
                        hard_exclusion_mask=hard,
                        target_counts=targets[(scenario_id, year)],
                        road_distance_m=roads[0],
                        major_road_distance_m=roads[1],
                    ),
                }
            candidate = {
                "candidate_id": f"{model_id}:{scenario_id}",
                "model_id": model_id,
                "scenario_id": scenario_id,
                **_numeric_means(final_seed_rows),
                "objective_uncertainty": _objective_summary(final_seed_rows),
            }
            final_candidates.append(candidate)

    frontier = pareto_frontier(final_candidates)
    report = {
        "schema": "gwm.abu_dhabi_planning_comparison.v1",
        "benchmark_id": "abu-dhabi-land-use-v1",
        "metric_version": "frozen_balanced_objectives_v3",
        "revision_status": "rerun_from_current_rasters",
        "pareto_status": "conditional_on_declared_objectives",
        "reproducibility_status": "complete_if_all_input_and_model_artifacts_are_present",
        "evidence_mode": "current_planning_evaluator_on_existing_prediction_rasters",
        "created_at": datetime.now(UTC).isoformat(),
        "status": "complete",
        "origin_year": 2024,
        "final_year": years[-1],
        "target_years": list(years),
        "scenario_config": _report_path(scenario_config),
        "models": list(MODEL_IDS),
        "model_display_names": {
            "geosos_flus": "GeoSOS-FLUS",
            "geospatial_kernel": "Geospatial Kernel",
            "paper58": "GeoFM-LDN",
        },
        "scenarios": list(scenario_ids),
        "seeds": list(seeds),
        "objective_directions": OBJECTIVES,
        "objective_metadata": OBJECTIVE_METADATA,
        "final_candidates": final_candidates,
        "pareto_frontier": frontier,
        "aggregate": aggregate,
        "ensembles": ensembles,
        "seed_metrics": seed_metrics,
        "claim_boundary": [
            "Scenario demands are planner-supplied stress tests, not forecasts.",
            (
                "Accessibility, compactness, fragmentation and vegetation-balance quantities are "
                "public-data proxies, not monetary, statutory or equity impacts."
            ),
            (
                "Pareto membership is conditional on this frozen objective set and cannot "
                "establish policy causality."
            ),
        ],
    }
    output_path.write_text(
        json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    markdown_path.write_text(render_markdown(report), encoding="utf-8")
    return report


def render_markdown(report: dict[str, Any]) -> str:
    labels = {
        "geosos_flus": "GeoSOS-FLUS",
        "geospatial_kernel": "Geospatial Kernel",
        "paper58": "GeoFM-LDN",
    }
    frontier = set(report["pareto_frontier"])
    lines = [
        f"# Abu Dhabi {report['target_years'][0]}-{report['final_year']} 土地覆盖情景压力测试",
        "",
        f"以下为 {report['final_year']} 年三随机种子均值。Pareto 表示在冻结目标集合下未被其他方案全面支配。",
        "",
        (
            "| 模型 | 情景 | demand TV | 集成目标偏差(px) | 绿色增益(px) | 距主干路(m) | "
            "距原建成区(m) | 建成斑块/千像元 | 生态转建成率 | 蛙跳率 | Pareto |"
        ),
        "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|:---:|",
    ]
    for row in report["final_candidates"]:
        ensemble_metrics = report["ensembles"][row["model_id"]][row["scenario_id"]][
            str(report["final_year"])
        ]["metrics"]
        lines.append(
            f"| {labels[row['model_id']]} | {SCENARIO_LABELS.get(row['scenario_id'], row['scenario_id'])} | "
            f"{row['demand_total_variation']:.5f} | "
            f"{ensemble_metrics['demand_l1_error_pixels']} | "
            f"{row['green_gain_pixels']:.0f} | "
            f"{row['new_built_mean_major_road_distance_m']:.1f} | "
            f"{row['new_built_mean_prior_built_distance_m']:.1f} | "
            f"{row['built_components_per_1000_pixels']:.3f} | "
            f"{row['ecological_conversion_rate']:.4f} | "
            f"{row['new_built_leapfrog_rate']:.3f} | "
            f"{'是' if row['candidate_id'] in frontier else '否'} |"
        )
    lines.extend(
        [
            "",
            "## 解释边界",
            "",
            "- 三组需求是规划压力测试，不是对阿布扎比未来的预测。",
            "- 生态和基础设施指标来自公开数据代理，不等于法定或货币化影响。",
            "- Pareto 结果只在冻结的可达性、紧凑性、碎片化和植被平衡目标、100 m 网格和公共约束下成立。",
            "- 斑块密度是碎片化目标；生态转化率、500 m 蛙跳率、邻域比例和建成退出是描述性诊断。",
            "- 集成栅格采用三种子多数投票，可能不再精确满足动作总量；表中的集成目标偏差是对此的显式审计。",
            "- ‘Moderate growth’保留 legacy compact 路径名，但动作本身不含紧凑性优化。",
            "- FLUS 的既有建成退出是其冻结转换规则下的模型行为，未做事后修正。",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--markdown", type=Path, default=DEFAULT_MARKDOWN)
    parser.add_argument("--scenario-config", type=Path, default=DEFAULT_SCENARIO_CONFIG)
    parser.add_argument("--ensemble-root", type=Path, default=DEFAULT_ENSEMBLE_ROOT)
    args = parser.parse_args()
    report = compile_report(
        input_path=args.input,
        output_path=args.output,
        markdown_path=args.markdown,
        scenario_config=args.scenario_config,
        ensemble_root=args.ensemble_root,
    )
    print(
        json.dumps(
            {"status": report["status"], "pareto_frontier": report["pareto_frontier"]},
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
