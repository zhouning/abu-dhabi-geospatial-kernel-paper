#!/usr/bin/env python3
"""Collect reviewer-requested FLUS feature diagnostics into one tracked file."""

from __future__ import annotations

import json
import re
import shutil
from datetime import UTC, datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
PREDICTIONS = HERE / "artifacts/predictions"
OUTPUT = HERE / "artifacts/flus_matched_input_review/evidence.json"

RUNS = {
    "baseline_plus_onehot": "flus_7_plus_onehot_abs",
    "baseline_plus_neighborhood": "flus_7_plus_neighbourhood_abs",
    "matched_kernel": "flus_matched_inputs_abs",
}

# The Windows values were supplied by the independent reviewer after rebuilding
# commit deb0a54. The underlying Windows rasters and logs are not present in
# this repository, so this record is provenance-labelled external evidence.
REVIEWER_WINDOWS_X86_64 = {
    "evidence_status": "reviewer_provided_external_verification_no_local_rasters",
    "platform": "Windows 11 x86_64",
    "compiler": "MSVC 19.51",
    "gdal": "3.12.4",
    "source_commit": "deb0a54",
    "path_requirement": "pure ASCII benchmark and working directories",
    "same_platform_seed_31_repeat_difference_pixels": {"2023": 0, "2024": 0},
    "baseline_7": {
        "strict_fom": {
            "31": {"2023": 0.1365, "2024": 0.1758},
            "47": {"2023": 0.1379, "2024": 0.1873},
            "73": {"2023": 0.1261, "2024": 0.1769},
            "mean": {"2023": 0.1335, "2024": 0.1800},
        },
        "windows_vs_macos_difference_pixels": {
            "31": {"2023": 1910, "2024": 3261},
            "47": {"2023": 2137, "2024": 3325},
            "73": {"2023": 2018, "2024": 3131},
        },
    },
    "matched_kernel_25": {
        "strict_fom_all_seeds": {"2023": 0.0, "2024": 0.0},
        "predicted_change_pixels_all_seeds": {"2023": 0, "2024": 0},
        "demand_total_variation_all_seeds": {"2023": 0.0388, "2024": 0.0857},
        "ann_rmse": {"31": 1.66e-5, "47": 1.72e-5, "73": 1.66e-5},
        "collapsed_seeds": [31, 47, 73],
    },
    "baseline_plus_neighborhood_19": {
        "strict_fom": {
            "31": {"2023": 0.1299, "2024": 0.1081},
            "47": {"2023": 0.1897, "2024": 0.1724},
            "73": {"2023": 0.1068, "2024": 0.0863},
        },
        "predicted_change_pixels_range_across_years": [1831, 3026],
    },
    "random_stream_boundary": "FLUS_RANDOM_SEED is deterministic within the tested platform, but C rand()/srand() sequences differ by platform runtime.",
}


def _sanitize(text: str) -> str:
    return text.replace(str(REPO), "<REPO>")


def _read_if_present(path: Path) -> str | None:
    return _sanitize(path.read_text(encoding="utf-8")) if path.is_file() else None


def _ann_log_record(path: Path, *, seed: int, mode: str) -> dict[str, object]:
    text = path.read_text(encoding="utf-8") if path.is_file() else ""
    rmse_match = re.search(r"RMSE\s*=\s*([^\s]+)", text)
    seed_match = re.search(r"FLUS NN random seed:\s*(\d+)", text)
    return {
        "seed": seed,
        "feature_mode": mode,
        "path": str(path.relative_to(HERE)) if path.is_file() else None,
        "archived_path": f"artifacts/flus_matched_input_review/logs/seed_{seed}/{mode}_flus_ann.log",
        "ann_returncode": 0 if path.is_file() and "write success!" in text else None,
        "random_seed": int(seed_match.group(1)) if seed_match else None,
        "ann_rmse": float(rmse_match.group(1)) if rmse_match else None,
        "log": _sanitize(text) if path.is_file() else None,
    }


def collect() -> dict[str, object]:
    runs: dict[str, object] = {}
    for mode, directory in RUNS.items():
        root = PREDICTIONS / directory
        report_path = root / "report.json"
        report = json.loads(report_path.read_text(encoding="utf-8"))
        seed = report["seeds"][0]
        ann = root / "work/seed_31/ann"
        seed_metrics = {
            str(seed_row["seed"]): {
                str(row["target_year"]): {
                    "strict_fom": row["evaluation"]["change_figure_of_merit"],
                    "overall_accuracy": row["evaluation"]["overall_accuracy"],
                    "predicted_change_pixels": row["evaluation"]["predicted_change_pixels"],
                    "zero_change_output": row["evaluation"]["predicted_change_pixels"] == 0,
                    "demand_total_variation": row["evaluation"]["demand_total_variation"],
                    "high_confidence_strict_fom": row["evaluation"]["reliability_sensitivity"]["change_figure_of_merit"],
                }
                for row in seed_row["years"]
            }
            for seed_row in report["seeds"]
        }
        runs[mode] = {
            "output_root": str(root.relative_to(HERE)),
            "status": report["status"],
            "feature_count": len(seed["training"]["feature_names"]),
            "feature_names": seed["training"]["feature_names"],
            "metrics": {
                str(row["target_year"]): {
                    "strict_fom": row["evaluation"]["change_figure_of_merit"],
                    "demand_total_variation": row["evaluation"]["demand_total_variation"],
                    "high_confidence_strict_fom": row["evaluation"]["reliability_sensitivity"]["change_figure_of_merit"],
                }
                for row in seed["years"]
            },
            "seed_metrics": seed_metrics,
            "seeds": [int(seed_row["seed"]) for seed_row in report["seeds"]],
            "probability_surface_present": (ann / "target_probability.tif").is_file(),
            "prediction_2023_present": (root / "seed_31/prediction_2023.tif").is_file(),
            "prediction_2024_present": (root / "seed_31/prediction_2024.tif").is_file(),
            "ann_log": _read_if_present(ann / "flus_ann.log"),
            "ann_config": _read_if_present(ann / "CCregiontrainlogCC.txt"),
            "update_driver_config": _read_if_present(ann / "update_drivers.csv"),
        }
        if mode == "matched_kernel":
            log_records = []
            for seed_row in report["seeds"]:
                seed_id = int(seed_row["seed"])
                source = root / f"work/seed_{seed_id}/ann/flus_ann.log"
                record = _ann_log_record(source, seed=seed_id, mode=mode)
                record["years"] = [
                    {
                        "target_year": int(year_row["target_year"]),
                        "strict_fom": float(year_row["evaluation"]["change_figure_of_merit"]),
                        "overall_accuracy": float(year_row["evaluation"]["overall_accuracy"]),
                        "predicted_change_pixels": int(year_row["evaluation"]["predicted_change_pixels"]),
                        "zero_change_output": int(year_row["evaluation"]["predicted_change_pixels"]) == 0,
                    }
                    for year_row in seed_row["years"]
                ]
                destination = HERE / "artifacts/flus_matched_input_review/logs" / f"seed_{seed_id}" / f"{mode}_flus_ann.log"
                if source.is_file():
                    destination.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copyfile(source, destination)
                log_records.append(record)
            runs[mode]["seed_logs"] = log_records
    failed_root = PREDICTIONS / "flus_matched_inputs/work/seed_31/ann"
    report: dict[str, object] = {
        "schema": "gwm.abu_dhabi_flus_feature_diagnostic_evidence.v3",
        "benchmark_id": "abu-dhabi-land-use-v1",
        "created_at": datetime.now(UTC).isoformat(),
        "failed_relative_path_attempt": {
            "ann_log": _read_if_present(failed_root / "flus_ann.log"),
            "ann_config": _read_if_present(failed_root / "CCregiontrainlogCC.txt"),
            "interpretation": "The console returned a configuration-path error. This record does not support a SIGSEGV claim.",
        },
        "corrected_absolute_path_runs": runs,
        "reviewer_provided_windows_x86_64": REVIEWER_WINDOWS_X86_64,
        "claim_boundary": "The 25-feature corrected run is diagnostic-only. Across the six platform-seed runs, five collapse to zero change through current-class identity leakage; the sole non-collapsed macOS seed-31 run is not a valid point estimate because it is not reproducible in the reviewer-provided Windows x86_64 build. The 19-feature mode produces changes for all three archived macOS seeds but underfills demand. Neither feature-expanded mode is used as a headline estimator or paired model contrast. The original seven-driver run remains the unmatched headline control.",
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return report


if __name__ == "__main__":
    result = collect()
    print(json.dumps({"status": "complete", "run_count": len(result["corrected_absolute_path_runs"])}))
