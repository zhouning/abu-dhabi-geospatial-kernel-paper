#!/usr/bin/env python3
"""Run the archived v2 experiment from already materialized public inputs.

This entry point deliberately does not re-query the live ArcGIS ImageServer or
Google Earth Engine.  The versioned archive contains the exact downloaded
inputs and their hashes; rerunning against an evolving remote service would no
longer be the same experiment.  Materialization commands remain documented in
the benchmark README for a separately versioned future refresh.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


HERE = Path(__file__).resolve().parents[1]
REPO = HERE.parents[1]
PYTHON = sys.executable


def run(label: str, script: Path, *args: str) -> None:
    command = [PYTHON, str(script), *args]
    print(f"\n== {label} ==\n$ {' '.join(command)}", flush=True)
    subprocess.run(command, cwd=REPO, check=True)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--skip-documents", action="store_true")
    parser.add_argument("--device", default="cpu")
    parser.add_argument("--bootstrap-resamples", type=int, default=1000)
    args = parser.parse_args()

    run("integrity gate", HERE / "reproducibility" / "reproducibility_check.py")
    run(
        "train ArcGIS GeoFM-LDN", HERE / "train_arcgis_geofm_ldn.py",
        "--seeds", "31,47,73", "--epochs", "8", "--device", args.device,
    )
    run(
        "ArcGIS conditional planning", HERE / "run_planning_scenarios.py",
        "--models", "geospatial_kernel,geosos_flus,paper58", "--seeds", "31,47,73",
        "--start-year", "2026", "--end-year", "2031",
        "--output", "benchmarks/abu_dhabi_land_use_v2/artifacts/planning_arcgis_2026_2031",
        "--report", "benchmarks/abu_dhabi_land_use_v2/planning_scenario_report_arcgis_2026_2031.json",
    )
    run("compile ArcGIS planning", HERE / "analyze_arcgis_v2.py")
    run("export planning vectors", HERE / "export_shapefiles_arcgis_v2.py")
    run("export native observed change", HERE / "export_native_10m_observed_change.py")
    for source_track, years, output_name in (
        ("arcgis", "2021,2022,2023,2024,2025", "arcgis_v2_historical_backtest"),
        ("dynamic_world", "2021,2022,2023,2024", "dynamic_world_matched_backtest"),
    ):
        run(
            f"{source_track} matched backtest", HERE / "run_arcgis_historical_backtest.py",
            "--output", f"benchmarks/abu_dhabi_land_use_v2/artifacts/{output_name}",
            "--source-track", source_track, "--seeds", "31,47,73", "--target-years", years,
            "--epochs", "8", "--batch-size", "2", "--device", args.device,
            "--bootstrap-resamples", str(args.bootstrap_resamples),
        )
    run("analyze cross-product robustness", HERE / "analyze_product_robustness.py")
    run("rebuild archive manifests", HERE / "reproducibility" / "build_reproducibility_manifest.py")
    run(
        "verify rebuilt archive", HERE / "reproducibility" / "reproducibility_check.py",
        "--output", "benchmarks/abu_dhabi_land_use_v2/reproducibility_check.json",
    )
    if not args.skip_documents:
        run("rebuild submission documents", REPO / "manuscript" / "build_submission_package.py")


if __name__ == "__main__":
    main()
