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
        "schema": "gwm.abu_dhabi_flus_matched_input_evidence.v2",
        "benchmark_id": "abu-dhabi-land-use-v1",
        "created_at": datetime.now(UTC).isoformat(),
        "failed_relative_path_attempt": {
            "ann_log": _read_if_present(failed_root / "flus_ann.log"),
            "ann_config": _read_if_present(failed_root / "CCregiontrainlogCC.txt"),
            "interpretation": "The console returned a configuration-path error. This record does not support a SIGSEGV claim.",
        },
        "corrected_absolute_path_runs": runs,
        "claim_boundary": "The 25-feature corrected run is archived for seeds 31, 47 and 73 and is reported as a matched-input diagnostic. Seeds 47 and 73 produce zero-change outputs because current-class one-hot inputs leak the same-year label target; only seed 31 is retained as the valid point comparison. It shares the Kernel feature family only; FLUS still learns same-year label suitability rather than the Kernel's next-state transition target and does not share the Kernel projection implementation. The original seven-driver run remains the unmatched headline control.",
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return report


if __name__ == "__main__":
    result = collect()
    print(json.dumps({"status": "complete", "run_count": len(result["corrected_absolute_path_runs"])}))
