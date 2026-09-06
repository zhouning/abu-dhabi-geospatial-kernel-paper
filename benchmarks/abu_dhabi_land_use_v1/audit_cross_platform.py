#!/usr/bin/env python3
"""Compare the reference macOS Kernel rasters with archived Linux reruns.

This is an evidence-producing script, not a claim that categorical outputs
must be bitwise identical across numerical environments.  It reports both
cell-level disagreement and the strict multi-class FoM measured with the same
public evaluator used by the benchmark.
"""

from __future__ import annotations

import argparse
import json
import platform
import sys
from datetime import UTC, datetime
from pathlib import Path

import numpy as np
import rasterio

try:
    from .shared import evaluate_prediction
except ImportError:  # Direct script execution from the benchmark directory.
    from shared import evaluate_prediction

HERE = Path(__file__).resolve().parent
DEFAULT_OUTPUT = HERE / "artifacts/cross_platform/linux_vs_macos_kernel_comparison.json"


def _read(path: Path) -> np.ndarray:
    with rasterio.open(path) as dataset:
        return dataset.read(1)


def _load_actions() -> dict[int, dict[int, int]]:
    actions = json.loads((HERE / "artifacts/bundle/allocation_actions.json").read_text(encoding="utf-8"))["actions"]
    return {
        int(row["target_year"]): {int(k): int(v) for k, v in row["feasible_target_counts"].items()}
        for row in actions
    }


def compare(*, linux_root: Path, output: Path) -> dict[str, object]:
    valid = _read(HERE / "artifacts/bundle/common_valid_mask_100m.tif").astype(bool)
    hard = _read(HERE / "artifacts/bundle/hard_exclusion_2022_100m.tif").astype(bool)
    origin = _read(HERE / "artifacts/gee/land_cover/land_cover_2022_100m.tif")
    actions = _load_actions()
    rows: list[dict[str, object]] = []
    for seed in (31, 47, 73):
        for year in (2023, 2024):
            mac_path = HERE / "artifacts/predictions/geospatial_kernel" / f"seed_{seed}" / f"prediction_{year}.tif"
            linux_path = linux_root / f"seed_{seed}" / f"prediction_{year}.tif"
            mac = _read(mac_path)
            linux = _read(linux_path)
            if mac.shape != linux.shape or mac.shape != valid.shape:
                raise ValueError(f"cross_platform_shape_mismatch:{seed}:{year}")
            mask = valid & np.isin(mac, np.arange(1, 7)) & np.isin(linux, np.arange(1, 7))
            differing = mask & (mac != linux)
            mac_eval = evaluate_prediction(
                mac,
                origin_state=origin,
                observed_target=_read(HERE / "artifacts/gee/land_cover" / f"land_cover_{year}_100m.tif"),
                valid_mask=valid,
                hard_exclusion_mask=hard,
                requested_counts=actions[year],
            )
            linux_eval = evaluate_prediction(
                linux,
                origin_state=origin,
                observed_target=_read(HERE / "artifacts/gee/land_cover" / f"land_cover_{year}_100m.tif"),
                valid_mask=valid,
                hard_exclusion_mask=hard,
                requested_counts=actions[year],
            )
            rows.append(
                {
                    "seed": seed,
                    "target_year": year,
                    "macos_prediction": str(mac_path.relative_to(HERE)),
                    "linux_prediction": str(linux_path.relative_to(HERE)),
                    "valid_pixel_count": int(mask.sum()),
                    "differing_cells": int(differing.sum()),
                    "differing_cell_rate": float(differing.sum() / max(1, mask.sum())),
                    "macos_strict_fom": float(mac_eval["change_figure_of_merit"]),
                    "linux_strict_fom": float(linux_eval["change_figure_of_merit"]),
                    "strict_fom_delta_linux_minus_macos": float(
                        linux_eval["change_figure_of_merit"] - mac_eval["change_figure_of_merit"]
                    ),
                    "macos_demand_total_variation": float(mac_eval["demand_total_variation"]),
                    "linux_demand_total_variation": float(linux_eval["demand_total_variation"]),
                }
            )
    diff = np.asarray([row["differing_cells"] for row in rows], dtype=float)
    rates = np.asarray([row["differing_cell_rate"] for row in rows], dtype=float)
    fom_delta = np.asarray([row["strict_fom_delta_linux_minus_macos"] for row in rows], dtype=float)
    report: dict[str, object] = {
        "schema": "gwm.abu_dhabi_cross_platform_kernel_comparison.v1",
        "benchmark_id": "abu-dhabi-land-use-v1",
        "created_at": datetime.now(UTC).isoformat(),
        "reference_environment": "macOS arm64 reference checkout (the released prediction rasters)",
        "comparison_environment": "Linux rerun archived under artifacts/cross_platform/linux_geospatial_kernel",
        "archived_linux_environment": {
            "system": "Linux",
            "machine": str(
                json.loads(
                    (linux_root / "report.json").read_text(encoding="utf-8")
                ).get("platform", {}).get("machine", "unknown")
            ),
            "python": "3.12.3",
            "numpy": "2.3.5",
            "scikit_learn": "1.8.0",
            "rasterio": "1.5.0",
        },
        "comparison_scope": "Geospatial Kernel historical predictions for seeds 31, 47 and 73 and target years 2023 and 2024",
        "rows": rows,
        "summary": {
            "n_comparisons": len(rows),
            "differing_cells_min": int(diff.min()),
            "differing_cells_max": int(diff.max()),
            "differing_cells_mean": float(diff.mean()),
            "differing_cell_rate_min": float(rates.min()),
            "differing_cell_rate_max": float(rates.max()),
            "strict_fom_delta_min": float(fom_delta.min()),
            "strict_fom_delta_max": float(fom_delta.max()),
            "strict_fom_delta_mean": float(fom_delta.mean()),
        },
        "claim_boundary": "This measures numerical/platform sensitivity of the released Kernel implementation. It does not establish domain validity or official Abu Dhabi forecasting skill.",
        "comparison_script_platform": {"system": platform.system(), "machine": platform.machine(), "python": sys.version.split()[0]},
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return report


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--linux-root", type=Path, default=HERE / "artifacts/cross_platform/linux_geospatial_kernel")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    report = compare(linux_root=args.linux_root, output=args.output)
    print(json.dumps(report["summary"], ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
