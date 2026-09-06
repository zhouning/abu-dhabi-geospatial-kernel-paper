#!/usr/bin/env python3
"""Hash and validate every published historical and planning prediction."""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import numpy as np
import rasterio

HERE = Path(__file__).resolve().parent
BUNDLE_ROOT = HERE / "artifacts/bundle"
INPUT_ROOT = HERE / "artifacts/gee"
DEFAULT_OUTPUT = HERE / "output_audit.json"
LEGACY_HISTORICAL_REPORT = HERE / "comparison_report.json"
LEGACY_PLANNING_REPORT = HERE / "planning_comparison_report_public_2025_2031.json"
LEGACY_PLANNING_SCENARIO_REPORT = HERE / "planning_scenario_report_public_2025_2031.json"


def _select_report(current_name: str, legacy_path: Path) -> Path:
    """Prefer a versioned rerun without mutating the immutable legacy path."""

    current = HERE / current_name
    return current if current.is_file() else legacy_path


HISTORICAL_REPORT = _select_report("comparison_report_current.json", LEGACY_HISTORICAL_REPORT)
PLANNING_REPORT = _select_report(
    "planning_comparison_report_public_2025_2031_current.json",
    LEGACY_PLANNING_REPORT,
)
PLANNING_SCENARIO_REPORT = _select_report(
    "planning_scenario_report_public_2025_2031_current.json",
    LEGACY_PLANNING_SCENARIO_REPORT,
)
CLASSES = tuple(range(1, 7))


def _read(path: Path) -> tuple[np.ndarray, dict[str, Any]]:
    with rasterio.open(path) as dataset:
        return dataset.read(1), dataset.profile.copy()


def _resolve(path_value: str) -> Path:
    path = Path(path_value)
    return path if path.is_absolute() else HERE / path


def _report_path(path: Path) -> str:
    """Return a repository-relative path without exposing local prefixes."""

    try:
        return str(path.resolve().relative_to(HERE.resolve()))
    except ValueError:
        return f"external/{path.name}"


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _historical_records() -> list[dict[str, Any]]:
    records = []
    for model_id in ("geosos_flus", "geospatial_kernel", "paper58"):
        report = json.loads(
            (HERE / f"artifacts/predictions/{model_id}/report.json").read_text(
                encoding="utf-8"
            )
        )
        for seed in report["seeds"]:
            for year in seed["years"]:
                records.append(
                    {
                        "track": "historical_seed",
                        "model_id": model_id,
                        "seed": int(seed["seed"]),
                        "target_year": int(year["target_year"]),
                        "path": year["prediction_path"],
                        "origin_year": 2022,
                    }
                )
    comparison = json.loads(HISTORICAL_REPORT.read_text(encoding="utf-8"))
    for model_id, years in comparison["ensembles"].items():
        for year, row in years.items():
            records.append(
                {
                    "track": "historical_ensemble",
                    "model_id": model_id,
                    "seed": None,
                    "target_year": int(year),
                    "path": row["prediction_path"],
                    "origin_year": 2022,
                }
            )
    return records


def _planning_records() -> list[dict[str, Any]]:
    records = []
    source = json.loads(PLANNING_SCENARIO_REPORT.read_text(encoding="utf-8"))
    for model_id, model in source["models"].items():
        for seed in model["seeds"]:
            for scenario in seed["scenarios"]:
                for year in scenario["years"]:
                    records.append(
                        {
                            "track": "planning_seed",
                            "model_id": model_id,
                            "scenario_id": scenario["scenario_id"],
                            "seed": int(seed["seed"]),
                            "target_year": int(year["target_year"]),
                            "path": year["prediction_path"],
                            "origin_year": 2024,
                        }
                    )
    comparison = json.loads(
        PLANNING_REPORT.read_text(encoding="utf-8")
    )
    for model_id, scenarios in comparison["ensembles"].items():
        for scenario_id, years in scenarios.items():
            for year, row in years.items():
                records.append(
                    {
                        "track": "planning_ensemble",
                        "model_id": model_id,
                        "scenario_id": scenario_id,
                        "seed": None,
                        "target_year": int(year),
                        "path": row["prediction_path"],
                        "origin_year": 2024,
                    }
                )
    return records


def audit(*, output_path: Path) -> dict[str, Any]:
    required_inputs = [
        BUNDLE_ROOT / "common_valid_mask_100m.tif",
        INPUT_ROOT / "land_cover/land_cover_2022_100m.tif",
        INPUT_ROOT / "land_cover/land_cover_2024_100m.tif",
        BUNDLE_ROOT / "hard_exclusion_2022_100m.tif",
        BUNDLE_ROOT / "hard_exclusion_2024_100m.tif",
        HISTORICAL_REPORT,
        PLANNING_SCENARIO_REPORT,
        PLANNING_REPORT,
    ]
    missing_inputs = [_report_path(path) for path in required_inputs if not path.is_file()]
    stale_reports = []
    report_requirements = {
        HISTORICAL_REPORT: "strict_multiclass_fom_v2",
        PLANNING_REPORT: "planning_objectives_v6",
        PLANNING_SCENARIO_REPORT: "current_protocol_run",
    }
    for path, required_revision in report_requirements.items():
        if not path.is_file():
            continue
        try:
            report = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            stale_reports.append(f"{_report_path(path)}:unreadable")
            continue
        if path == PLANNING_SCENARIO_REPORT:
            valid_report = (
                report.get("status") == "complete"
                and report.get("revision_status") in {
                    required_revision,
                    "recomputed_from_existing_rasters",
                }
            )
        else:
            valid_report = (
                report.get("revision_status") == "rerun_from_current_rasters"
                and report.get("metric_version") == required_revision
            )
        if not valid_report:
            stale_reports.append(
                f"{_report_path(path)}:"
                f"{report.get('status', 'no_status')}/"
                f"{report.get('revision_status', 'no_revision')}/"
                f"{report.get('metric_version', 'no_metric_version')}"
            )
    if missing_inputs or stale_reports:
        report = {
            "schema": "gwm.abu_dhabi_output_audit.v2",
            "benchmark_id": "abu-dhabi-land-use-v1",
            "status": "INCOMPLETE_INPUTS",
            "prediction_count": 0,
            "failure_count": len(missing_inputs) + len(stale_reports),
            "missing_inputs": missing_inputs,
            "stale_reports": stale_reports,
            "claim_boundary": "A PASS audit cannot be claimed until all raster artifacts and revised source reports are present.",
        }
        output_path.write_text(
            json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        return report
    valid, reference = _read(BUNDLE_ROOT / "common_valid_mask_100m.tif")
    valid_mask = valid.astype(bool)
    origins = {
        year: _read(INPUT_ROOT / f"land_cover/land_cover_{year}_100m.tif")[0]
        for year in (2022, 2024)
    }
    hard_masks = {
        year: _read(BUNDLE_ROOT / f"hard_exclusion_{year}_100m.tif")[0].astype(bool)
        for year in (2022, 2024)
    }
    records = _historical_records() + _planning_records()
    if len({_resolve(row["path"]).resolve() for row in records}) != len(records):
        raise ValueError("duplicate_prediction_paths")

    artifacts = []
    failure_count = 0
    for record in records:
        path = _resolve(record["path"])
        if not path.is_file():
            failure_count += 1
            artifacts.append(
                {
                    **record,
                    "path": _report_path(path),
                    "bytes": None,
                    "sha256": None,
                    "grid_aligned": False,
                    "invalid_class_pixels": None,
                    "nonzero_outside_valid_pixels": None,
                    "constraint_violation_pixels": None,
                    "missing": True,
                    "valid": False,
                }
            )
            continue
        values, profile = _read(path)
        origin_year = int(record["origin_year"])
        aligned = (
            profile["width"] == reference["width"]
            and profile["height"] == reference["height"]
            and profile["crs"] == reference["crs"]
            and profile["transform"] == reference["transform"]
        )
        invalid_class_pixels = int(
            np.count_nonzero(valid_mask & ~np.isin(values, CLASSES))
        )
        nonzero_outside = int(np.count_nonzero(values[~valid_mask]))
        constraint_violations = int(
            np.count_nonzero(
                valid_mask
                & hard_masks[origin_year]
                & (values != origins[origin_year])
            )
        )
        valid_output = (
            aligned
            and invalid_class_pixels == 0
            and nonzero_outside == 0
            and constraint_violations == 0
        )
        failure_count += int(not valid_output)
        artifacts.append(
            {
                **record,
                "path": _report_path(path),
                "bytes": path.stat().st_size,
                "sha256": _sha256(path),
                "grid_aligned": aligned,
                "invalid_class_pixels": invalid_class_pixels,
                "nonzero_outside_valid_pixels": nonzero_outside,
                "constraint_violation_pixels": constraint_violations,
                "valid": valid_output,
            }
        )
    report = {
        "schema": "gwm.abu_dhabi_output_audit.v2",
        "benchmark_id": "abu-dhabi-land-use-v1",
        "created_at": datetime.now(UTC).isoformat(),
        "status": "PASS" if failure_count == 0 else "FAIL",
        "prediction_count": len(artifacts),
        "failure_count": failure_count,
        "track_counts": {
            track: sum(row["track"] == track for row in artifacts)
            for track in (
                "historical_seed",
                "historical_ensemble",
                "planning_seed",
                "planning_ensemble",
            )
        },
        "artifacts": artifacts,
    }
    output_path.write_text(
        json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return report


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    report = audit(output_path=args.output)
    print(
        json.dumps(
            {
                "status": report["status"],
                "prediction_count": report["prediction_count"],
                "failure_count": report["failure_count"],
            }
        )
    )


if __name__ == "__main__":
    main()
