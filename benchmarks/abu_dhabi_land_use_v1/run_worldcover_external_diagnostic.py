#!/usr/bin/env python3
"""Compare 2020--2021 predictions with an independent WorldCover diagnostic.

This is product agreement, not official ground-truth validation. WorldCover
2020/2021 are used only to locate built-up gain at several 100-m fraction
thresholds; the Dynamic World transition remains a separate public-product
reference.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import numpy as np
import rasterio

try:
    from .run_geospatial_kernel import AbuDhabiInputs
    from .shared import CLASSES
except ImportError:
    from run_geospatial_kernel import AbuDhabiInputs  # type: ignore
    from shared import CLASSES  # type: ignore


HERE = Path(__file__).resolve().parent
DEFAULT_ROLLING_REPORT = HERE / "artifacts/rolling_backtest/report.json"
DEFAULT_WORLDCOVER_ROOT = HERE / "artifacts/external_validation/worldcover"
DEFAULT_OUTPUT = HERE / "artifacts/external_validation/worldcover/diagnostic.json"
THRESHOLDS = (0.05, 0.10, 0.20, 0.30)


def _read(path: Path) -> np.ndarray:
    with rasterio.open(path) as dataset:
        return dataset.read(1)


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _binary_metrics(predicted: np.ndarray, observed: np.ndarray, mask: np.ndarray) -> dict[str, Any]:
    p = predicted[mask].astype(bool)
    o = observed[mask].astype(bool)
    tp = int(np.count_nonzero(p & o))
    fp = int(np.count_nonzero(p & ~o))
    fn = int(np.count_nonzero(~p & o))
    tn = int(np.count_nonzero(~p & ~o))
    precision = tp / (tp + fp) if tp + fp else None
    recall = tp / (tp + fn) if tp + fn else None
    if not (tp + fp + fn):
        f1 = 1.0
        iou = 1.0
    else:
        f1 = float(2 * tp / (2 * tp + fp + fn))
        iou = float(tp / (tp + fp + fn))
    return {
        "pixel_count": int(mask.sum()),
        "observed_positive_pixels": int(o.sum()),
        "predicted_positive_pixels": int(p.sum()),
        "true_positive": tp,
        "false_positive": fp,
        "false_negative": fn,
        "true_negative": tn,
        "precision": float(precision) if precision is not None else None,
        "recall": float(recall) if recall is not None else None,
        "f1": f1,
        "intersection_over_union": iou,
    }


def _mean_optional(rows: list[dict[str, Any]], key: str) -> float | None:
    values = [float(row[key]) for row in rows if row[key] is not None]
    return float(np.mean(values)) if values else None


def _prediction_paths(report: dict[str, Any], *, model_id: str) -> list[tuple[int, Path]]:
    rows = [
        row
        for row in report["rows"]
        if row["origin_year"] == 2020
        and row["target_year"] == 2021
        and row["model_id"] == model_id
        and row.get("prediction_artifact")
    ]
    return [
        (int(row["seed"]), (HERE / row["prediction_artifact"]["path"]).resolve())
        for row in rows
    ]


def run(
    *,
    rolling_report_path: Path,
    worldcover_root: Path,
    output_path: Path,
    thresholds: tuple[float, ...] = THRESHOLDS,
) -> dict[str, Any]:
    report = json.loads(rolling_report_path.read_text(encoding="utf-8"))
    inputs = AbuDhabiInputs()
    wc2020_path = worldcover_root / "worldcover_2020_built_fraction_100m.tif"
    wc2021_path = worldcover_root / "worldcover_2021_built_fraction_100m.tif"
    wc2020 = _read(wc2020_path)
    wc2021 = _read(wc2021_path)
    if wc2020.shape != inputs.states[2020].shape or wc2021.shape != wc2020.shape:
        raise ValueError("worldcover_grid_shape_mismatch")
    valid = (
        inputs.city
        & np.isin(inputs.states[2020], CLASSES)
        & np.isin(inputs.states[2021], CLASSES)
        & np.isfinite(wc2020)
        & np.isfinite(wc2021)
        & (wc2020 >= 0)
        & (wc2021 >= 0)
    )
    dynamic_world_2020 = inputs.states[2020] == 5
    dynamic_world_2021 = inputs.states[2021] == 5
    dynamic_world_gain = ~dynamic_world_2020 & dynamic_world_2021
    dynamic_world_loss = dynamic_world_2020 & ~dynamic_world_2021
    model_ids = ("geospatial_kernel", "persistence", "random_allocation")
    predictions: dict[str, list[tuple[int, np.ndarray]]] = {}
    for model_id in model_ids:
        entries = _prediction_paths(report, model_id=model_id)
        if not entries:
            raise FileNotFoundError(f"missing_rolling_prediction_artifacts:{model_id}")
        predictions[model_id] = [(seed, _read(path) == 5) for seed, path in entries]

    threshold_rows: list[dict[str, Any]] = []
    for threshold in thresholds:
        wc_gain = (wc2020 < threshold) & (wc2021 >= threshold)
        wc_loss = (wc2020 >= threshold) & (wc2021 < threshold)
        wc_built_2020 = wc2020 >= threshold
        wc_built_2021 = wc2021 >= threshold
        gain_metrics: dict[str, Any] = {
            "dynamic_world_observed": _binary_metrics(dynamic_world_gain, wc_gain, valid)
        }
        loss_metrics: dict[str, Any] = {
            "dynamic_world_observed": _binary_metrics(dynamic_world_loss, wc_loss, valid)
        }
        stock_metrics: dict[str, Any] = {
            "dynamic_world_observed_2020": _binary_metrics(
                dynamic_world_2020, wc_built_2020, valid
            ),
            "dynamic_world_observed_2021": _binary_metrics(
                dynamic_world_2021, wc_built_2021, valid
            ),
        }
        for model_id, entries in predictions.items():
            gain_per_seed = []
            loss_per_seed = []
            stock_per_seed = []
            for seed, built_prediction in entries:
                predicted_gain = ~dynamic_world_2020 & built_prediction
                predicted_loss = dynamic_world_2020 & ~built_prediction
                gain_per_seed.append(
                    {"seed": seed, **_binary_metrics(predicted_gain, wc_gain, valid)}
                )
                loss_per_seed.append(
                    {"seed": seed, **_binary_metrics(predicted_loss, wc_loss, valid)}
                )
                stock_per_seed.append(
                    {"seed": seed, **_binary_metrics(built_prediction, wc_built_2021, valid)}
                )
            gain_metrics[model_id] = {
                "seed_results": gain_per_seed,
                "mean": {
                    key: _mean_optional(gain_per_seed, key)
                    for key in ("precision", "recall", "f1", "intersection_over_union")
                },
            }
            loss_metrics[model_id] = {
                "seed_results": loss_per_seed,
                "mean": {
                    key: _mean_optional(loss_per_seed, key)
                    for key in ("precision", "recall", "f1", "intersection_over_union")
                },
            }
            stock_metrics[f"{model_id}_2021"] = {
                "seed_results": stock_per_seed,
                "mean": {
                    key: _mean_optional(stock_per_seed, key)
                    for key in ("precision", "recall", "f1", "intersection_over_union")
                },
            }
        threshold_rows.append(
            {
                "worldcover_built_fraction_threshold": threshold,
                "worldcover_built_2020_pixels": int(np.count_nonzero(valid & wc_built_2020)),
                "worldcover_built_2021_pixels": int(np.count_nonzero(valid & wc_built_2021)),
                "worldcover_built_gain_pixels": int(np.count_nonzero(valid & wc_gain)),
                "worldcover_built_loss_pixels": int(np.count_nonzero(valid & wc_loss)),
                "built_stock_agreement": stock_metrics,
                "built_gain_agreement": gain_metrics,
                "built_loss_agreement": loss_metrics,
            }
        )
    output = {
        "schema": "gwm.abu_dhabi_worldcover_external_diagnostic.v1",
        "benchmark_id": "abu-dhabi-land-use-v1",
        "status": "complete",
        "created_at": datetime.now(UTC).isoformat(),
        "interpretation": "independent_public_product_agreement_not_ground_truth",
        "comparison_window": {"origin_year": 2020, "target_year": 2021},
        "valid_pixel_count": int(valid.sum()),
        "worldcover_input_artifacts": {
            "2020": {"path": str(wc2020_path), "sha256": _sha256_file(wc2020_path)},
            "2021": {"path": str(wc2021_path), "sha256": _sha256_file(wc2021_path)},
        },
        "thresholds": list(thresholds),
        "known_limitations": [
            "WorldCover 2020 v1.0 and 2021 v2.0 are different product versions.",
            "WorldCover and Dynamic World share satellite-family inputs and are not fully independent.",
            "The diagnostic evaluates built-up gain only and does not validate all land-cover classes.",
            "No official Abu Dhabi planning or cadastral truth is available in this benchmark.",
        ],
        "rows": threshold_rows,
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(output, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return output


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--rolling-report", type=Path, default=DEFAULT_ROLLING_REPORT)
    parser.add_argument("--worldcover-root", type=Path, default=DEFAULT_WORLDCOVER_ROOT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    result = run(
        rolling_report_path=args.rolling_report.resolve(),
        worldcover_root=args.worldcover_root.resolve(),
        output_path=args.output.resolve(),
    )
    print(json.dumps({"status": result["status"], "row_count": len(result["rows"])}))


if __name__ == "__main__":
    main()
