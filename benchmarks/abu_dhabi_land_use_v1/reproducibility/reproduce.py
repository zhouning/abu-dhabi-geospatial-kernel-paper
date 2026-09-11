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
    """Fail closed when manuscript values drift from current reports."""

    comparison = json.loads(
        (HERE / "comparison_report_current.json").read_text(encoding="utf-8")
    )
    planning = json.loads(
        (HERE / "planning_comparison_report_public_2025_2031_current.json").read_text(
            encoding="utf-8"
        )
    )
    manuscript = (REPO / "manuscript/manuscript.md").read_text(encoding="utf-8")
    manuscript_numeric = " ".join(manuscript.replace("−", "-").split())

    # Table 1: all primary strict-FoM cells. Feature-expanded FLUS runs are
    # diagnostics and must not be treated as headline estimators.
    for model in ("geosos_flus", "geospatial_kernel", "paper58"):
        for year in ("2023", "2024"):
            value = comparison["summaries"][model][year]["change_figure_of_merit"]["mean"]
            if f"{value:.4f}" not in manuscript_numeric:
                raise RuntimeError(f"manuscript_table1_fom_missing:{model}:{year}:{value:.4f}")
    matched = comparison["matched_input_diagnostic"]
    if matched.get("estimator_status") != "invalid_platform_sensitive_identity_leakage_diagnostic":
        raise RuntimeError("matched_input_diagnostic_status_missing")
    if matched.get("collapsed_seeds_on_archive_platform") != [47, 73]:
        raise RuntimeError("matched_input_archive_collapsed_seed_record_missing")
    if matched.get("non_collapsed_seeds_on_archive_platform") != [31]:
        raise RuntimeError("matched_input_archive_non_collapsed_seed_record_missing")
    neighbourhood = comparison["neighbourhood_input_diagnostic"]
    if neighbourhood.get("estimator_status") != "partial_demand_underfill_diagnostic":
        raise RuntimeError("neighbourhood_input_diagnostic_status_missing")
    expected_ranges = {
        "2023": (0.1071, 0.1617, 1702, 2417, 4500, 0.0153, 0.0305),
        "2024": (0.0872, 0.1386, 1805, 2499, 8464, 0.0615, 0.0767),
    }
    for year, values in expected_ranges.items():
        actual = neighbourhood["ranges"][year]
        if not (round(actual["strict_fom_min"], 4) == values[0] and round(actual["strict_fom_max"], 4) == values[1]):
            raise RuntimeError(f"neighbourhood_fom_range_missing:{year}")
        if (actual["predicted_change_pixels_min"], actual["predicted_change_pixels_max"], actual["observed_change_pixels"]) != values[2:5]:
            raise RuntimeError(f"neighbourhood_change_range_missing:{year}")
        if not (
            round(actual["demand_total_variation_min"], 4) == values[5]
            and round(actual["demand_total_variation_max"], 4) == values[6]
        ):
            raise RuntimeError(f"neighbourhood_demand_variation_range_missing:{year}")
        for fragment in (
            f"{values[0]:.4f}",
            f"{values[1]:.4f}",
            f"{values[2]:,}",
            f"{values[3]:,}",
            f"{values[4]:,}",
            f"{values[5]:.4f}",
            f"{values[6]:.4f}",
        ):
            if fragment not in manuscript_numeric:
                raise RuntimeError(f"manuscript_neighbourhood_diagnostic_missing:{year}:{fragment}")

    # Confidence-filtered values are label-quality and selection-effect
    # diagnostics. Keep their retention counts and the manuscript disclaimer
    # synchronized so they cannot be relabelled as skill validation.
    quality = comparison.get("label_quality_diagnostics", {})
    if quality.get("confidence_threshold") != 0.5:
        raise RuntimeError("label_quality_confidence_threshold_missing")
    expected_quality = {
        "2023": (4500, 25, 0.005555555555555556, 129, 0.028666666666666667),
        "2024": (8464, 56, 0.006616257088846881, 93, 0.010987712665406428),
    }
    for year, expected in expected_quality.items():
        actual = quality.get("by_target_year", {}).get(year, {})
        dual = actual.get("dual_year_confidence", {})
        preceding = actual.get("preceding_year_confidence_only", {})
        actual_selection = (
            actual.get("full_grid_observed_change_pixels"),
            dual.get("observed_change_pixels"),
            round(float(dual.get("observed_change_retention_fraction", -1)), 12),
            preceding.get("observed_change_pixels"),
            round(float(preceding.get("observed_change_retention_fraction", -1)), 12),
        )
        expected_selection = (
            expected[0],
            expected[1],
            round(expected[2], 12),
            expected[3],
            round(expected[4], 12),
        )
        if actual_selection != expected_selection:
            raise RuntimeError(f"label_quality_selection_counts_missing:{year}")
        required_fragments = (
            f"{expected[1]:,} of {expected[0]:,}",
            f"({expected[2]:.2%})",
            f"{expected[3]:,}",
            f"({expected[4]:.2%})",
        )
        if not all(fragment in manuscript for fragment in required_fragments):
            raise RuntimeError(f"manuscript_label_quality_selection_missing:{year}")
    if "not an independent validation set or a model-skill test" not in manuscript:
        raise RuntimeError("manuscript_label_quality_boundary_missing")
    if "0.0055 for Geospatial Kernel" not in manuscript:
        raise RuntimeError("manuscript_label_quality_rounding_missing")

    # Main paired contrasts reported in Results.
    for year, pair_names in (
        ("2023", ("geospatial_kernel_minus_geosos_flus", "paper58_minus_geospatial_kernel")),
        ("2024", ("paper58_minus_geospatial_kernel",)),
    ):
        for pair_name in pair_names:
            interval = comparison["pairwise_bootstrap_95ci"][year][pair_name]["summary"]["change_figure_of_merit"]
            for bound in ("lower_mean", "median_mean", "upper_mean"):
                fragment = f"{interval[bound]:.4f}"
                if fragment not in manuscript_numeric:
                    raise RuntimeError(
                        f"manuscript_pairwise_value_missing:{year}:{pair_name}:{bound}:{fragment}"
                    )

    # Rolling-origin and WorldCover diagnostic evidence. These checks prevent
    # the manuscript from reverting to a single favourable split or silently
    # relabelling external-product agreement as authoritative validation.
    rolling = json.loads(
        (HERE / "artifacts/rolling_backtest/report.json").read_text(encoding="utf-8")
    )
    if rolling.get("temporal_firewall", {}).get("prediction_target_used_in_fit") is not False:
        raise RuntimeError("rolling_temporal_firewall_missing")
    if rolling.get("temporal_firewall", {}).get("road_snapshot_features_used") is not False:
        raise RuntimeError("rolling_road_snapshot_firewall_missing")
    expected_rolling = {
        2020: (0.2595, 0.0524),
        2021: (0.0724, 0.0048),
        2022: (0.2116, 0.0200),
        2023: (0.1816, 0.0323),
    }
    for origin, (kernel_fom, random_fom) in expected_rolling.items():
        kernel_summary = next(
            row for row in rolling["summaries"]
            if row["origin_year"] == origin and row["model_id"] == "geospatial_kernel"
        )
        random_summary = next(
            row for row in rolling["summaries"]
            if row["origin_year"] == origin and row["model_id"] == "random_allocation"
        )
        if round(kernel_summary["metrics"]["change_figure_of_merit"]["mean"], 4) != kernel_fom:
            raise RuntimeError(f"rolling_kernel_fom_missing:{origin}")
        if round(random_summary["metrics"]["change_figure_of_merit"]["mean"], 4) != random_fom:
            raise RuntimeError(f"rolling_random_fom_missing:{origin}")
    for fragment in ("0.2595, 0.0724, 0.2116 and 0.1816", "0.0524, 0.0048, 0.0200 and 0.0323"):
        if fragment not in manuscript_numeric:
            raise RuntimeError(f"manuscript_rolling_value_missing:{fragment}")

    worldcover = json.loads(
        (HERE / "artifacts/external_validation/worldcover/diagnostic.json")
        .read_text(encoding="utf-8")
    )
    if worldcover.get("interpretation") != "independent_public_product_agreement_not_ground_truth":
        raise RuntimeError("worldcover_claim_boundary_missing")
    if worldcover.get("thresholds") != [0.05, 0.1, 0.2, 0.3]:
        raise RuntimeError("worldcover_thresholds_missing")
    first = worldcover["rows"][0]
    last = worldcover["rows"][-1]
    if round(first["built_gain_agreement"]["dynamic_world_observed"]["f1"], 4) != 0.0111:
        raise RuntimeError("worldcover_dynamic_gain_f1_missing")
    if round(last["built_gain_agreement"]["dynamic_world_observed"]["f1"], 4) != 0.0192:
        raise RuntimeError("worldcover_dynamic_gain_f1_upper_missing")
    if any(row["built_gain_agreement"]["geospatial_kernel"]["mean"]["f1"] != 0.0 for row in worldcover["rows"]):
        raise RuntimeError("worldcover_kernel_gain_not_zero")
    expected_action = {
        0.05: (0.0157, 0.0008, 0.0268, 0.0058),
        0.10: (0.0228, 0.0007, 0.0277, 0.0036),
        0.20: (0.0268, 0.0011, 0.0251, 0.0011),
        0.30: (0.0397, 0.0007, 0.0251, 0.0075),
    }
    expected_stock = {
        0.05: (0.3908, 0.3501),
        0.10: (0.3998, 0.3603),
        0.20: (0.4186, 0.3780),
        0.30: (0.4334, 0.3924),
    }
    for row in worldcover["rows"]:
        threshold = float(row["worldcover_built_fraction_threshold"])
        action = row["worldcover_gain_count_action"]
        expected_kernel, expected_kernel_sd, expected_random, expected_random_sd = expected_action[threshold]
        if round(action["geospatial_kernel"]["mean"]["f1"], 4) != expected_kernel:
            raise RuntimeError(f"worldcover_action_kernel_f1_missing:{threshold}")
        if round(action["geospatial_kernel"]["sample_standard_deviation"]["f1"], 4) != expected_kernel_sd:
            raise RuntimeError(f"worldcover_action_kernel_sd_missing:{threshold}")
        if round(action["random_allocation"]["mean"]["f1"], 4) != expected_random:
            raise RuntimeError(f"worldcover_action_random_f1_missing:{threshold}")
        if round(action["random_allocation"]["sample_standard_deviation"]["f1"], 4) != expected_random_sd:
            raise RuntimeError(f"worldcover_action_random_sd_missing:{threshold}")
        expected_2020, expected_2021 = expected_stock[threshold]
        stock = row["built_stock_agreement"]
        if round(stock["dynamic_world_observed_2020"]["f1"], 4) != expected_2020:
            raise RuntimeError(f"worldcover_dynamic_stock_2020_missing:{threshold}")
        if round(stock["dynamic_world_observed_2021"]["f1"], 4) != expected_2021:
            raise RuntimeError(f"worldcover_dynamic_stock_2021_missing:{threshold}")
    for fragment in (
        "0.0111–0.0192",
        "Kernel F1 was 0.3518–0.3971",
        "0.0157 ± 0.0008 versus 0.0268 ± 0.0058",
        "0.0397 ± 0.0007 versus 0.0251 ± 0.0075",
        "below random at 0.05",
        "0.3908–0.4334 and 0.3501–0.3924",
        "structural-zero, zero-power result",
    ):
        if fragment not in manuscript_numeric:
            raise RuntimeError(f"manuscript_worldcover_value_missing:{fragment}")

    # Table 2: assert each displayed 2031 candidate row and frontier marker.
    model_labels = {
        "geosos_flus": "FLUS-style ANN–CA",
        "geospatial_kernel": "Geospatial Kernel",
        "paper58": "GeoFM-LDN",
    }
    frontier = {
        candidate_id
        for candidate_ids in planning["pareto_frontier_within_scenario"].values()
        for candidate_id in candidate_ids
    }
    for candidate in planning["final_candidates"]:
        marker = "*" if candidate["candidate_id"] in frontier else ""
        fragment = (
            f"| {model_labels[candidate['model_id']]} | "
            f"{candidate['new_built_mean_major_road_distance_m']:.1f} | "
            f"{candidate['new_built_mean_prior_built_distance_m']:.1f} | "
            f"{candidate['combined_built_components_per_1000_pixels']:.3f} | "
            f"{candidate['ecological_conversion_rate']:.4f} | {marker} |"
        )
        if fragment not in manuscript:
            raise RuntimeError(f"manuscript_table2_row_missing:{candidate['candidate_id']}")

    scenarios = ("compact", "ecological_priority", "outward_growth")
    kernel_errors = [
        int(planning["ensembles"]["geospatial_kernel"][scenario]["2031"]["metrics"]["demand_l1_error_pixels"])
        for scenario in scenarios
    ]
    geofm_errors = [
        int(planning["ensembles"]["paper58"][scenario]["2031"]["metrics"]["demand_l1_error_pixels"])
        for scenario in scenarios
    ]
    kernel_values = ", ".join(f"{value:,}" for value in kernel_errors[:-1]) + " and " + f"{kernel_errors[-1]:,}"
    geofm_values = ", ".join(f"{value:,}" for value in geofm_errors[:-1]) + " and " + f"{geofm_errors[-1]:,}"
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
        HERE / "artifacts/cross_platform/github_actions_ubuntu_x86_64_kernel_reference_e06a997.json",
        HERE / "artifacts/rolling_backtest/report.json",
        HERE / "artifacts/rolling_backtest/paired_spatial_uncertainty.json",
        HERE / "artifacts/external_validation/worldcover/input_manifest.json",
        HERE / "artifacts/external_validation/worldcover/diagnostic.json",
        REPO / "manuscript/supplementary_table_S2_neighbourhood_weight_sensitivity.md",
        REPO / "manuscript/supplementary_table_S3_flus_feature_diagnostics.md",
        REPO / "manuscript/supplementary_table_S5_rolling_external_diagnostics.md",
        REPO / "manuscript/source_data_fig03_rolling_external_diagnostics.csv",
        REPO / "manuscript/main.pdf",
        REPO / "manuscript/lup_submission.pdf",
        REPO / "manuscript/manuscript.pdf",
        REPO / "manuscript/manuscript.docx",
        REPO / "manuscript/manuscript_pandoc.tex",
    ]
    paths.extend(
        sorted(
            (HERE / "artifacts/rolling_backtest/predictions").glob(
                "origin_*_target_*/seed_*/*.tif"
            )
        )
    )
    paths.extend(
        sorted(
            (HERE / "artifacts/external_validation/worldcover").glob(
                "worldcover_*_built_fraction_100m.tif"
            )
        )
    )
    for stem in (
        "fig01_benchmark_contract",
        "fig02_historical_validation",
        "fig03_rolling_external_diagnostics",
        "fig05_planning_objectives",
        "fig06_mechanism_ablation",
        "fig07_planning_maps_2031",
        "figS01_planning_atlas_2031",
        "figS02_input_label_quality",
        "figS03_historical_2024_maps_and_errors",
        "figS04_driver_layers_and_experiment_design",
    ):
        for suffix in (".pdf", ".svg", ".png", ".tiff"):
            paths.append(REPO / "figures" / f"{stem}{suffix}")
    records = []
    for path in paths:
        if not path.is_file():
            continue
        raw = path.read_bytes()
        if path.suffix.lower() in {".json", ".md", ".py", ".txt", ".csv", ".tex", ".svg"}:
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
    _run(
        "Geospatial Kernel rolling-origin backtest",
        HERE / "run_rolling_backtest.py",
        "--origins",
        "2020,2021,2022,2023",
        "--seeds",
        SEEDS,
    )
    _run("Rolling-origin paired spatial uncertainty", HERE / "run_rolling_uncertainty.py")
    _run("WorldCover external-product diagnostic", HERE / "run_worldcover_external_diagnostic.py")
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
        _run("Rolling and external-product figure", HERE / "render_rolling_validation_figure.py")
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
