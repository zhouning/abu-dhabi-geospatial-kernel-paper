#!/usr/bin/env python3
"""Check whether the public-data benchmark checkout is rerunnable.

This check intentionally distinguishes source code from generated artifacts.
Missing rasters or private model checkpoints produce a blocked status instead
of an optimistic PASS based on stale JSON reports.
"""

from __future__ import annotations

import argparse
import json
from datetime import UTC, datetime
from pathlib import Path


HERE = Path(__file__).resolve().parent


def _display_path(path: Path) -> str:
    """Use stable relative labels instead of machine-specific absolute paths."""

    try:
        return str(path.resolve().relative_to(HERE.parents[1].resolve()))
    except ValueError:
        return f"external/{path.name}"


def check() -> dict[str, object]:
    required_code = [
        HERE / "run_geospatial_kernel.py",
        HERE / "run_geosos_flus.py",
        HERE / "run_planning_scenarios.py",
        HERE / "compile_comparison.py",
        HERE / "compile_planning.py",
        HERE / "shared.py",
        HERE / "planning.py",
        HERE.parents[1] / "data_agent/uwm/geospatial_kernel/runtime.py",
    ]
    required_public = [
        HERE / "planning_scenarios_public_2025_2031.json",
        HERE / "protocol.json",
        HERE / "boundary_manifest.json",
        HERE / "grid_profile.json",
    ]
    generated_inputs = {
        "artifacts/gee": HERE / "artifacts/gee",
        "artifacts/bundle": HERE / "artifacts/bundle",
        "artifacts/predictions": HERE / "artifacts/predictions",
        "artifacts/bundle/common_valid_mask_100m.tif": HERE / "artifacts/bundle/common_valid_mask_100m.tif",
        "artifacts/bundle/hard_exclusion_2022_100m.tif": HERE / "artifacts/bundle/hard_exclusion_2022_100m.tif",
        "artifacts/bundle/hard_exclusion_2024_100m.tif": HERE / "artifacts/bundle/hard_exclusion_2024_100m.tif",
        "artifacts/gee/land_cover/land_cover_2022_100m.tif": HERE / "artifacts/gee/land_cover/land_cover_2022_100m.tif",
        "artifacts/gee/land_cover/land_cover_2024_100m.tif": HERE / "artifacts/gee/land_cover/land_cover_2024_100m.tif",
    }
    external = [
        HERE / "external/geofm_ldn/experiments/abu_dhabi/run_paper58_abu_dhabi.py",
        HERE / "external/flus_console",
    ]
    rows = {
        "required_code": {_display_path(path): path.is_file() for path in required_code},
        "required_public_manifests": {_display_path(path): path.is_file() for path in required_public},
        "generated_public_inputs": {
            label: path.exists() and (path.is_file() or any(path.iterdir()))
            for label, path in generated_inputs.items()
        },
        "external_model_dependencies": {_display_path(path): path.exists() for path in external},
    }
    code_ok = all(rows["required_code"].values())
    manifests_ok = all(rows["required_public_manifests"].values())
    generated_ok = all(rows["generated_public_inputs"].values())
    external_ok = all(rows["external_model_dependencies"].values())
    status = "PASS" if code_ok and manifests_ok and generated_ok and external_ok else "BLOCKED"
    return {
        "schema": "gwm.abu_dhabi_reproducibility_check.v1",
        "benchmark_id": "abu-dhabi-land-use-v1",
        "created_at": datetime.now(UTC).isoformat(),
        "status": status,
        "code_and_manifests_complete": code_ok and manifests_ok,
        "generated_inputs_complete": generated_ok,
        "external_dependencies_complete": external_ok,
        "checks": rows,
        "claim_boundary": "BLOCKED means the checkout is not sufficient for a clean rerun; existing reports are not treated as proof of reproducibility.",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    report = check()
    if args.output:
        args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
