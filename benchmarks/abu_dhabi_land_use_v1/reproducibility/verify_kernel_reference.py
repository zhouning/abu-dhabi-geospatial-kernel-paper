#!/usr/bin/env python3
"""Compare a fresh Kernel rerun with the released categorical references."""

from __future__ import annotations

import argparse
import json
import platform
import sys
from datetime import UTC, datetime
from pathlib import Path

import numpy as np
import rasterio
import sklearn


HERE = Path(__file__).resolve().parents[1]
DEFAULT_REFERENCE = HERE / "artifacts/predictions/geospatial_kernel"


def _display(path: Path) -> str:
    try:
        return path.relative_to(HERE).as_posix()
    except ValueError:
        return str(path.resolve())


def _read(path: Path) -> np.ndarray:
    with rasterio.open(path) as dataset:
        return dataset.read(1)


def compare(*, candidate_root: Path, reference_root: Path) -> dict[str, object]:
    records = []
    for seed in (31, 47, 73):
        for year in (2023, 2024):
            relative = Path(f"seed_{seed}") / f"prediction_{year}.tif"
            candidate_path = candidate_root / relative
            reference_path = reference_root / relative
            if not candidate_path.is_file() or not reference_path.is_file():
                raise FileNotFoundError(f"kernel_reference_missing:{candidate_path}:{reference_path}")
            candidate = _read(candidate_path)
            reference = _read(reference_path)
            if candidate.shape != reference.shape:
                raise ValueError(
                    f"kernel_reference_shape_mismatch:{candidate.shape}:{reference.shape}"
                )
            records.append(
                {
                    "seed": seed,
                    "target_year": year,
                    "candidate_path": _display(candidate_path),
                    "reference_path": _display(reference_path),
                    "difference_pixels": int(np.count_nonzero(candidate != reference)),
                    "pixel_count": int(reference.size),
                }
            )
    status = "PASS" if all(row["difference_pixels"] == 0 for row in records) else "FAIL"
    return {
        "schema": "gwm.abu_dhabi_kernel_reference_comparison.v1",
        "created_at": datetime.now(UTC).isoformat(),
        "status": status,
        "comparison_scope": "six categorical historical Kernel rasters (three seeds by two target years)",
        "runtime": {
            "python": sys.version.split()[0],
            "platform": platform.platform(),
            "machine": platform.machine(),
            "scikit_learn": sklearn.__version__,
        },
        "records": records,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidate", type=Path, required=True)
    parser.add_argument("--reference", type=Path, default=DEFAULT_REFERENCE)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    report = compare(candidate_root=args.candidate, reference_root=args.reference)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    raise SystemExit(0 if report["status"] == "PASS" else 1)


if __name__ == "__main__":
    main()
