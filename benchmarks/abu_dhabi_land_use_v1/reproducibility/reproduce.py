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
import shutil
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


def _verify_manuscript_report_consistency() -> None:
    """Fail closed when the manuscript's reported planning counts drift."""

    report = json.loads(
        (HERE / "planning_comparison_report_public_2025_2031_current.json").read_text(
            encoding="utf-8"
        )
    )
    manuscript = (REPO / "manuscript/manuscript.md").read_text(encoding="utf-8")
    expected = {
        "Kernel integrated demand errors": [
            int(
                report["ensembles"]["geospatial_kernel"][scenario]["2031"]["metrics"][
                    "demand_l1_error_pixels"
                ]
            )
            for scenario in ("compact", "ecological_priority", "outward_growth")
        ],
        "GeoFM-LDN integrated demand errors": [
            int(
                report["ensembles"]["paper58"][scenario]["2031"]["metrics"][
                    "demand_l1_error_pixels"
                ]
            )
            for scenario in ("compact", "ecological_priority", "outward_growth")
        ],
    }
    kernel_values = ", ".join(f"{value:,}" for value in expected["Kernel integrated demand errors"][:-1]) + " and " + f"{expected['Kernel integrated demand errors'][-1]:,}"
    geofm_values = ", ".join(f"{value:,}" for value in expected["GeoFM-LDN integrated demand errors"][:-1]) + " and " + f"{expected['GeoFM-LDN integrated demand errors'][-1]:,}"
    required_fragments = (
        f"The 2031 majority-vote ensemble L1 demand errors were {kernel_values} pixels",
        f"the corresponding GeoFM-LDN errors were {geofm_values} pixels",
    )
    for fragment in required_fragments:
        if fragment not in manuscript:
            raise RuntimeError(f"manuscript_consistency_missing:{fragment}")


def _hash_outputs() -> dict[str, object]:
    paths = [
        HERE / "comparison_report_current.json",
        HERE / "planning_scenario_report_public_2025_2031_current.json",
        HERE / "planning_comparison_report_public_2025_2031_current.json",
        HERE / "output_audit_reproducible.json",
        HERE / "output_audit.json",
        HERE / "planning_public_2025_2031_delivery_manifest_current.json",
        HERE / "neighbourhood_weight_sensitivity.csv",
        HERE / "artifacts/mechanism_ablations/neighbourhood_weight_sensitivity_report.json",
        HERE / "artifacts/flus_matched_input_review/evidence.json",
        HERE / "artifacts/predictions/flus_matched_inputs_abs/report.json",
        HERE / "artifacts/cross_platform/linux_vs_macos_kernel_comparison.json",
        REPO / "manuscript/supplementary_table_S2_neighbourhood_weight_sensitivity.md",
        REPO / "manuscript/main.pdf",
        REPO / "manuscript/lup_submission.pdf",
        REPO / "manuscript/manuscript.pdf",
        REPO / "manuscript/manuscript.docx",
        REPO / "manuscript/manuscript_pandoc.tex",
    ]
    for stem in (
        "fig01_benchmark_contract",
        "fig02_historical_validation",
        "fig03_planning_objectives",
        "fig04_mechanism_ablation",
        "fig05_planning_maps_2031",
    ):
        for suffix in (".pdf", ".svg", ".png", ".tiff"):
            paths.append(REPO / "figures" / f"{stem}{suffix}")
    records = []
    for path in paths:
        if not path.is_file():
            continue
        raw = path.read_bytes()
        if path.suffix.lower() in {".json", ".md", ".py", ".txt", ".csv", ".tex"}:
            raw = raw.replace(b"\r\n", b"\n").replace(b"\r", b"\n")
            hash_mode = "text_lf_normalized"
        else:
            hash_mode = "raw"
        digest = hashlib.sha256(raw).hexdigest()
        records.append({"path": path.relative_to(REPO).as_posix(), "bytes": len(raw), "sha256": digest, "hash_mode": hash_mode})
    report = {"schema": "gwm.abu_dhabi_generated_output_hashes.v2", "records": records}
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
    _run("FLUS-style ANN–CA console historical predictions", HERE / "run_geosos_flus.py", "--binary", str(HERE / "vendor/flus_console"), "--seeds", SEEDS)
    for mode, directory in (
        ("baseline_plus_onehot", "flus_7_plus_onehot_abs"),
        ("baseline_plus_neighborhood", "flus_7_plus_neighbourhood_abs"),
        ("matched_kernel", "flus_matched_inputs_abs"),
    ):
        _run(
            f"FLUS input diagnostic: {mode}",
            HERE / "run_geosos_flus.py",
            "--binary",
            str(HERE / "vendor/flus_console"),
            "--seeds",
            SEEDS,
            "--output",
            str(HERE / "artifacts/predictions" / directory),
            "--feature-mode",
            mode,
        )
    _run("Archive FLUS input diagnostics", HERE / "collect_flus_diagnostic_evidence.py")
    _run("Geospatial Kernel historical predictions", HERE / "run_geospatial_kernel.py", "--seeds", SEEDS)
    _run("Cross-platform Kernel comparison", HERE / "audit_cross_platform.py")
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
            "Strict neighbourhood-weight sensitivity",
            HERE / "run_neighbourhood_sensitivity.py",
            "--seeds",
            SEEDS,
        )
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
    _run("Output audit", HERE / "audit_outputs.py", "--output", str(HERE / "output_audit.json"))
    shutil.copyfile(HERE / "output_audit.json", HERE / "output_audit_reproducible.json")
    _verify_manuscript_report_consistency()
    if not args.skip_figures:
        _run("Publication figures", HERE / "render_nature_figures.py")
    result = _hash_outputs()
    _run(
        "Final input manifest",
        HERE / "reproducibility/build_reproducibility_manifest.py",
    )
    _run(
        "Final reproducibility gate",
        HERE / "reproducibility_check.py",
        "--output",
        str(HERE / "reproducibility_check.json"),
    )
    print(json.dumps({"status": "complete", "generated_output_count": len(result["records"])}, ensure_ascii=False))


if __name__ == "__main__":
    main()
