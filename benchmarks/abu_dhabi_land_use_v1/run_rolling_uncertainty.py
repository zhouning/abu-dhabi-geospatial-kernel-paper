#!/usr/bin/env python3
"""Compute paired spatial-block uncertainty for rolling backtest contrasts."""

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
    from .run_rolling_backtest import valid_through_year
    from .shared import paired_model_difference_bootstrap_ci
except ImportError:
    from run_geospatial_kernel import AbuDhabiInputs  # type: ignore
    from run_rolling_backtest import valid_through_year  # type: ignore
    from shared import paired_model_difference_bootstrap_ci  # type: ignore


HERE = Path(__file__).resolve().parent
DEFAULT_REPORT = HERE / "artifacts/rolling_backtest/report.json"
DEFAULT_OUTPUT = HERE / "artifacts/rolling_backtest/paired_spatial_uncertainty.json"


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _read_artifact(row: dict[str, Any]) -> np.ndarray:
    artifact = row.get("prediction_artifact") or {}
    path = Path(str(artifact.get("path", "")))
    if not path.is_absolute():
        path = HERE / path
    if not path.is_file():
        raise FileNotFoundError(f"rolling_prediction_missing:{path}")
    if _sha256_file(path) != artifact.get("sha256"):
        raise ValueError(f"rolling_prediction_hash_mismatch:{path}")
    with rasterio.open(path) as dataset:
        return dataset.read(1)


def run(
    *,
    report_path: Path,
    output_path: Path,
    n_resamples: int,
    block_size: int,
) -> dict[str, Any]:
    report = json.loads(report_path.read_text(encoding="utf-8"))
    inputs = AbuDhabiInputs()
    indexed = {
        (int(row["origin_year"]), int(row["seed"]), str(row["model_id"])): row
        for row in report["rows"]
    }
    rows: list[dict[str, Any]] = []
    for origin_year in report["origins"]:
        target_year = int(origin_year) + 1
        valid = valid_through_year(inputs, target_year)
        for seed in report["seeds"]:
            kernel = _read_artifact(indexed[(origin_year, seed, "geospatial_kernel")])
            for baseline in ("random_allocation", "persistence"):
                control = _read_artifact(indexed[(origin_year, seed, baseline)])
                bootstrap_seed = int(20_260_000 + origin_year * 100 + seed)
                interval = paired_model_difference_bootstrap_ci(
                    kernel,
                    control,
                    origin_state=inputs.states[origin_year],
                    observed_target=inputs.states[target_year],
                    valid_mask=valid,
                    n_resamples=n_resamples,
                    seed=bootstrap_seed,
                    block_size=block_size,
                )
                interval["change_fom_interval_excludes_zero"] = not (
                    interval["change_figure_of_merit"]["lower"] <= 0
                    <= interval["change_figure_of_merit"]["upper"]
                )
                rows.append(
                    {
                        "origin_year": origin_year,
                        "target_year": target_year,
                        "model_a": "geospatial_kernel",
                        "model_b": baseline,
                        "model_seed": seed,
                        "interval": interval,
                    }
                )
        print(f"rolling_uncertainty:origin_{origin_year}:complete", flush=True)
    output = {
        "schema": "gwm.abu_dhabi_rolling_uncertainty.v1",
        "benchmark_id": "abu-dhabi-land-use-v1",
        "status": "complete",
        "created_at": datetime.now(UTC).isoformat(),
        "source_report_sha256": _sha256_file(report_path),
        "method": "paired_spatial_block_bootstrap",
        "n_resamples": n_resamples,
        "block_size_pixels": block_size,
        "block_size_metres": block_size * 100,
        "interpretation": (
            "Conditional mapped-domain uncertainty under the public-product "
            "labels; not a population or authoritative-validation interval."
        ),
        "rows": rows,
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(output, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return output


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--resamples", type=int, default=1000)
    parser.add_argument("--block-size", type=int, default=8)
    args = parser.parse_args()
    result = run(
        report_path=args.report.resolve(),
        output_path=args.output.resolve(),
        n_resamples=args.resamples,
        block_size=args.block_size,
    )
    print(json.dumps({"status": result["status"], "row_count": len(result["rows"])}))


if __name__ == "__main__":
    main()
