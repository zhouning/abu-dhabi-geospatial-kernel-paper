#!/usr/bin/env python3
"""Build v2 input/code and publication-output integrity manifests.

The two manifests have intentionally different roles.  ``MANIFEST.json``
freezes the materialized public inputs, model assets and executable code needed
to rerun the ArcGIS-served v2 study.  ``PUBLICATION_OUTPUTS.json`` freezes the
reports, source-data tables, figures and delivery layers that support the
refreshed manuscript.  This avoids treating a generated result as an input
while still making the archived result set independently auditable.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from collections.abc import Iterable
from pathlib import Path


HERE = Path(__file__).resolve().parents[1]
REPO = HERE.parents[1]
OUT = HERE / "reproducibility"
V1 = HERE.parent / "abu_dhabi_land_use_v1"

TEXT_SUFFIXES = {
    ".c", ".cc", ".cpp", ".h", ".hpp", ".ini", ".json", ".md", ".py",
    ".rst", ".tex", ".toml", ".txt", ".yaml", ".yml", ".csv", ".tsv", ".geojson", ".svg",
}


def hash_file(path: Path) -> tuple[str, str, int]:
    """Return a portable hash, normalizing text line endings only."""

    raw = path.read_bytes()
    if path.suffix.lower() in TEXT_SUFFIXES:
        raw = raw.replace(b"\r\n", b"\n").replace(b"\r", b"\n")
        mode = "text_lf_normalized"
    else:
        mode = "raw"
    return hashlib.sha256(raw).hexdigest(), mode, len(raw)


def add_files(destination: set[Path], candidates: Iterable[Path]) -> None:
    for candidate in candidates:
        if candidate.is_file():
            destination.add(candidate)


def add_tree(destination: set[Path], root: Path, patterns: tuple[str, ...] = ("*",)) -> None:
    for pattern in patterns:
        add_files(destination, root.rglob(pattern))


def rerun_inputs() -> dict[str, set[Path]]:
    """Collect precisely the files read by the v2 rerun and matched tracks."""

    public_inputs: set[Path] = set()
    add_files(public_inputs, [HERE / "artifacts" / "abu_dhabi_city_100m_mask.tif"])
    add_tree(public_inputs, HERE / "artifacts" / "arcgis_sentinel2_landcover")
    add_tree(public_inputs, HERE / "artifacts" / "bundle")
    add_tree(public_inputs, HERE / "artifacts" / "gee")
    add_tree(public_inputs, HERE / "artifacts" / "osm")
    add_tree(public_inputs, HERE / "source")
    # Dynamic World states and their quality terms are read by the matched
    # comparison; they are input data to v2 even though their lineage is v1.
    add_files(public_inputs, (V1 / "artifacts" / "gee" / "land_cover").glob("*.tif"))

    model_assets: set[Path] = set()
    add_files(model_assets, [HERE / "vendor" / "flus_console"])
    add_files(model_assets, (HERE / "artifacts" / "predictions" / "geofm_ldn_arcgis").glob("*.pt"))

    configuration: set[Path] = {
        HERE / "README.md",
        HERE / "bundle_manifest_arcgis.json",
        HERE / "grid_profile.json",
        HERE / "planning_scenarios_arcgis_2025_2031.json",
        HERE / "planning_scenario_report_arcgis_2026_2031.json",
        V1 / "reproducibility" / "requirements.lock.txt",
        V1 / "reproducibility" / "environment.json",
        REPO / "manuscript" / "build_submission_package.py",
        REPO / "manuscript" / "main.tex",
        REPO / "manuscript" / "lup_submission.tex",
        REPO / "manuscript" / "submission_header.tex",
    }
    code: set[Path] = set()
    add_files(code, HERE.glob("*.py"))
    add_files(code, (REPO / "data_agent" / "uwm" / "geospatial_kernel").glob("*.py"))
    add_files(
        code,
        [
            HERE / "reproducibility" / "build_reproducibility_manifest.py",
            HERE / "reproducibility" / "reproduce.py",
            HERE / "reproducibility" / "reproducibility_check.py",
        ],
    )
    return {
        "public_input": public_inputs,
        "model_asset": model_assets,
        "configuration": configuration,
        "code": code,
    }


def publication_outputs() -> dict[str, set[Path]]:
    """Collect frozen v2 evidence, excluding ephemeral intermediate work files."""

    reports: set[Path] = {
        HERE / "artifacts" / "arcgis_v2_historical_backtest" / "report.json",
        HERE / "artifacts" / "dynamic_world_matched_backtest" / "report.json",
        HERE / "planning_scenario_report_arcgis_2026_2031.json",
        HERE / "results_arcgis_v2" / "results_summary.json",
        HERE / "results_arcgis_v2" / "source_comparison.json",
    }
    add_tree(reports, HERE / "results_arcgis_v2" / "paper_refresh")
    add_tree(reports, HERE / "results_arcgis_v2" / "allocation_limits")
    evidence: set[Path] = {
        REPO / "figures" / "fig04_product_robustness.png",
        REPO / "figures" / "fig04_product_robustness.pdf",
        REPO / "figures" / "fig04_product_robustness.svg",
        REPO / "manuscript" / "source_data_fig04_product_robustness.csv",
        REPO / "manuscript" / "supplementary_table_S1_arcgis_planning_objectives.md",
        REPO / "manuscript" / "supplementary_table_S4_cross_product_class_matrices.md",
        REPO / "manuscript" / "supplementary_table_S6_product_robustness.md",
        REPO / "manuscript" / "manuscript.md",
        REPO / "manuscript" / "supplementary_table_S7_allocation_limits.md",
        REPO / "manuscript" / "response_to_LUP_review_round17.md",
        REPO / "manuscript" / "response_to_LUP_review_round18.md",
    }
    if OUT.name == "working":
        # A working submission freeze covers its rendered artifacts as well as
        # the scientific source. These are not attributed to the old DOI.
        add_files(evidence, (REPO / "manuscript").glob("*.pdf"))
        add_files(evidence, (REPO / "manuscript").glob("*.docx"))
        add_tree(evidence, REPO / "manuscript" / "submission_files", ("*.pdf", "*.docx", "*.md"))
        # These supplementary figures are cited by the working manuscript and
        # carry the revised Dynamic World quality-proxy terminology.
        for stem in (
            "figS02_input_label_quality",
            "figS04_driver_layers_and_experiment_design",
        ):
            add_files(
                evidence,
                (REPO / "figures" / f"{stem}{suffix}" for suffix in (".pdf", ".png", ".svg")),
            )
        add_files(evidence, [HERE / "reproducibility" / "WORKING_REVISION.md"])
        add_files(evidence, [REPO / "manuscript" / "reference_revision_2026_09_10_zh.md"])
    delivery: set[Path] = set()
    add_tree(delivery, HERE / "results_arcgis_v2" / "ensembles")
    add_tree(delivery, HERE / "results_arcgis_v2" / "vectors")
    # The cross-product compiler reads these 27 frozen per-seed end states to
    # recreate Fig. 4, Supplementary Table S1 and Supplementary Table S6
    # without rerunning the macOS-only FLUS executable.
    add_files(
        delivery,
        HERE.glob("artifacts/planning_arcgis_2026_2031/*/*/seed_*/prediction_2031.tif"),
    )
    return {
        "report": reports,
        "manuscript_evidence": evidence,
        "delivery": delivery,
    }


def records(groups: dict[str, set[Path]]) -> list[dict[str, object]]:
    missing = [path for paths in groups.values() for path in paths if not path.is_file()]
    if missing:
        names = ",".join(str(path.relative_to(REPO)) for path in sorted(missing))
        raise FileNotFoundError(f"manifest_missing:{names}")
    output: list[dict[str, object]] = []
    for role, paths in groups.items():
        for path in sorted(paths):
            digest, mode, byte_count = hash_file(path)
            output.append(
                {
                    "path": path.relative_to(REPO).as_posix(),
                    "role": role,
                    "bytes": byte_count,
                    "sha256": digest,
                    "hash_mode": mode,
                }
            )
    return sorted(output, key=lambda row: str(row["path"]))


def write_manifest(name: str, schema: str, scope: str, values: list[dict[str, object]]) -> None:
    document = {
        "schema": schema,
        "benchmark_id": "abu-dhabi-land-use-v2",
        "repository_root": ".",
        "scope": scope,
        "generated_by": "benchmarks/abu_dhabi_land_use_v2/reproducibility/build_reproducibility_manifest.py",
        "records": values,
    }
    (OUT / name).write_text(json.dumps(document, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def build() -> tuple[int, int]:
    OUT.mkdir(parents=True, exist_ok=True)
    rerun = records(rerun_inputs())
    outputs = records(publication_outputs())
    write_manifest(
        "MANIFEST.json",
        "gwm.abu_dhabi_v2.reproducibility_inputs.v1",
        "Immutable public inputs, model assets, configurations and code required for rerun.",
        rerun,
    )
    write_manifest(
        "PUBLICATION_OUTPUTS.json",
        "gwm.abu_dhabi_v2.publication_outputs.v1",
        "Reports, source data, figures, delivered v2 raster/vector products and per-seed 2031 planning states cited by the refreshed paper.",
        outputs,
    )
    sums = "# SHA-256 hashes. Text files use CRLF/CR -> LF normalization; see manifests.\n"
    sums += "\n".join(
        f"{row['sha256']}  {row['path']}"
        for row in [*rerun, *outputs]
    ) + "\n"
    (OUT / "SHA256SUMS").write_text(sums, encoding="utf-8")
    return len(rerun), len(outputs)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--working", action="store_true", help="Write a separate working revision; preserve published manifests")
    args = parser.parse_args()
    if args.working:
        OUT = HERE / "reproducibility" / "working"
    input_count, output_count = build()
    print(json.dumps({"status": "complete", "input_records": input_count, "output_records": output_count}))
