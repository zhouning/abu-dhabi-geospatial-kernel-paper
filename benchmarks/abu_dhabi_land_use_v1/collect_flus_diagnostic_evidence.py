#!/usr/bin/env python3
"""Collect reviewer-requested FLUS feature diagnostics into one tracked file."""

from __future__ import annotations

import json
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


def collect() -> dict[str, object]:
    runs: dict[str, object] = {}
    for mode, directory in RUNS.items():
        root = PREDICTIONS / directory
        report_path = root / "report.json"
        report = json.loads(report_path.read_text(encoding="utf-8"))
        seed = report["seeds"][0]
        ann = root / "work/seed_31/ann"
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
            "probability_surface_present": (ann / "target_probability.tif").is_file(),
            "prediction_2023_present": (root / "seed_31/prediction_2023.tif").is_file(),
            "prediction_2024_present": (root / "seed_31/prediction_2024.tif").is_file(),
            "ann_log": _read_if_present(ann / "flus_ann.log"),
            "ann_config": _read_if_present(ann / "CCregiontrainlogCC.txt"),
            "update_driver_config": _read_if_present(ann / "update_drivers.csv"),
        }
    failed_root = PREDICTIONS / "flus_matched_inputs/work/seed_31/ann"
    report: dict[str, object] = {
        "schema": "gwm.abu_dhabi_flus_matched_input_evidence.v1",
        "benchmark_id": "abu-dhabi-land-use-v1",
        "created_at": datetime.now(UTC).isoformat(),
        "failed_relative_path_attempt": {
            "ann_log": _read_if_present(failed_root / "flus_ann.log"),
            "ann_config": _read_if_present(failed_root / "CCregiontrainlogCC.txt"),
            "interpretation": "The console returned a configuration-path error. This record does not support a SIGSEGV claim.",
        },
        "corrected_absolute_path_runs": runs,
        "claim_boundary": "All corrected runs use one computational seed and diagnose feature-input compatibility. They do not replace the three-seed seven-driver headline control.",
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return report


if __name__ == "__main__":
    result = collect()
    print(json.dumps({"status": "complete", "run_count": len(result["corrected_absolute_path_runs"])}))
