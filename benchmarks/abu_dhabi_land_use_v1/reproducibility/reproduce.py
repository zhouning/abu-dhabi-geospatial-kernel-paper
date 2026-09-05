#!/usr/bin/env python3
"""One-command rerun of the Abu Dhabi public-data benchmark.

Run from a clean checkout with the locked Python environment:

    python benchmarks/abu_dhabi_land_use_v1/reproducibility/reproduce.py

The script verifies the immutable manifest first, runs the three historical
models and the 2025--2031 planning scenarios, compiles metrics, exports change
polygons, renders figures and finishes with the output audit. Generated files
live under ``artifacts/`` and are intentionally not part of the input hash
manifest.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path


HERE = Path(__file__).resolve().parents[1]
REPO = HERE.parents[1]
PYTHON = sys.executable
SEEDS = "31,47,73"


def _run(label: str, script: Path, *args: str) -> None:
    command = [PYTHON, str(script), *args]
    print(f"\n== {label} ==\n$ {' '.join(command)}", flush=True)
    subprocess.run(command, cwd=REPO, check=True, env=os.environ.copy())


def _verify_gate() -> None:
    command = [PYTHON, str(HERE / "reproducibility_check.py")]
    subprocess.run(command, cwd=REPO, check=True)


def _hash_outputs() -> dict[str, object]:
    paths = [
        HERE / "comparison_report_current.json",
        HERE / "planning_scenario_report_public_2025_2031_current.json",
        HERE / "planning_comparison_report_public_2025_2031_current.json",
        HERE / "output_audit_reproducible.json",
        HERE / "planning_public_2025_2031_delivery_manifest_current.json",
    ]
    records = []
    for path in paths:
        if not path.is_file():
            continue
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        records.append({"path": path.relative_to(REPO).as_posix(), "bytes": path.stat().st_size, "sha256": digest})
    report = {"schema": "gwm.abu_dhabi_generated_output_hashes.v1", "records": records}
    target = HERE / "reproducibility/generated_output_hashes.json"
    target.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return report


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--device", default="cpu", choices=("cpu", "auto", "mps", "cuda"))
    parser.add_argument("--skip-ablations", action="store_true")
    parser.add_argument("--skip-figures", action="store_true")
    args = parser.parse_args()

    _verify_gate()
    # The checkpoint mode is intentional: the declared GeoFM-LDN checkpoints
    # are immutable model inputs. It regenerates the historical rasters without
    # overwriting those inputs; the vendored runner also exposes full retraining
    # when ``--use-checkpoints`` is omitted.
    paper58 = HERE / "external/geofm_ldn/experiments/abu_dhabi/run_paper58_abu_dhabi.py"
    _run(
        "GeoFM-LDN historical predictions",
        paper58,
        "--benchmark-root",
        str(HERE),
        "--output",
        str(HERE / "artifacts/predictions/paper58"),
        "--checkpoint-root",
        str(HERE / "artifacts/predictions/paper58"),
        "--use-checkpoints",
        "--seeds",
        SEEDS,
        "--device",
        args.device,
    )
    _run("GeoSOS-FLUS historical predictions", HERE / "run_geosos_flus.py", "--binary", str(HERE / "vendor/flus_console"), "--seeds", SEEDS)
    _run("Geospatial Kernel historical predictions", HERE / "run_geospatial_kernel.py", "--seeds", SEEDS)
    _run("Historical comparison", HERE / "compile_comparison.py")
    _run(
        "Planning scenarios 2025-2031",
        HERE / "run_planning_scenarios.py",
        "--models",
        "geosos_flus,geospatial_kernel,paper58",
        "--seeds",
        SEEDS,
        "--device",
        args.device,
        "--binary",
        str(HERE / "vendor/flus_console"),
    )
    _run("Planning comparison", HERE / "compile_planning.py")
    if not args.skip_ablations:
        _run("Mechanism ablations", HERE / "run_mechanism_ablations.py", "--seeds", SEEDS)
    _run(
        "Planning change polygons",
        HERE / "export_planning_change_polygons.py",
        "--comparison-report",
        str(HERE / "planning_comparison_report_public_2025_2031_current.json"),
        "--output-root",
        str(HERE / "artifacts/planning_public_2025_2031/vector"),
        "--manifest",
        str(HERE / "planning_public_2025_2031_delivery_manifest_current.json"),
        "--overwrite",
    )
    _run("Output audit", HERE / "audit_outputs.py", "--output", str(HERE / "output_audit_reproducible.json"))
    if not args.skip_figures:
        _run("Publication figures", HERE / "render_nature_figures.py")
    result = _hash_outputs()
    print(json.dumps({"status": "complete", "generated_output_count": len(result["records"])}, ensure_ascii=False))


if __name__ == "__main__":
    main()
