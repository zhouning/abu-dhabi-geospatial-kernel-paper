#!/usr/bin/env python3
"""Run the strict-FoM neighbourhood-weight sensitivity for the Kernel.

The previous CSV was produced by an older binary-FoM evaluator.  This small
runner uses the current mechanism path and current strict multi-class
evaluator so the sensitivity table is generated from the same evidence
definition as the manuscript's historical results.
"""

from __future__ import annotations

import argparse
import csv
import json
import statistics
from pathlib import Path

try:
    from .run_geospatial_kernel import SEEDS, AbuDhabiInputs
    from .run_mechanism_ablations import _run_historical_seed
except ImportError:
    from run_geospatial_kernel import SEEDS, AbuDhabiInputs
    from run_mechanism_ablations import _run_historical_seed


HERE = Path(__file__).resolve().parent
DEFAULT_OUTPUT = HERE / "neighbourhood_weight_sensitivity.csv"
DEFAULT_REPORT = HERE / "artifacts/mechanism_ablations/neighbourhood_weight_sensitivity_report.json"
WEIGHTS = (0.0, 0.175, 0.35, 0.7)


def run(*, output: Path, report_path: Path, seeds: tuple[int, ...]) -> dict[str, object]:
    inputs = AbuDhabiInputs()
    rows: list[dict[str, object]] = []
    for weight in WEIGHTS:
        for seed in seeds:
            results = _run_historical_seed(
                inputs,
                seed=seed,
                proposal_variant="full",
                runtime_variant="neighbourhood_weight_sensitivity",
                action_mode="observed",
                writeback=True,
                neighborhood_weight=weight,
                hard_constraints=True,
            )
            for result in results:
                rows.append(
                    {
                        "year": int(result["target_year"]),
                        "neighbourhood_weight": weight,
                        "seed": seed,
                        "change_figure_of_merit": float(
                            result["evaluation"]["change_figure_of_merit"]
                        ),
                    }
                )

    summary: list[dict[str, object]] = []
    for year in (2023, 2024):
        for weight in WEIGHTS:
            values = [
                float(row["change_figure_of_merit"])
                for row in rows
                if int(row["year"]) == year
                and float(row["neighbourhood_weight"]) == weight
            ]
            summary.append(
                {
                    "year": year,
                    "neighbourhood_weight": weight,
                    "mean_change_fom": statistics.mean(values),
                    "population_std": statistics.pstdev(values),
                    "seed_values": values,
                    "metric": "strict_multiclass_change_figure_of_merit",
                    "purpose": "posthoc_sensitivity",
                }
            )

    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["year", "neighbourhood_weight", "mean_change_fom", "population_std", "metric", "purpose"],
            lineterminator="\n",
        )
        writer.writeheader()
        for row in summary:
            writer.writerow(
                {
                    "year": row["year"],
                    "neighbourhood_weight": f"{float(row['neighbourhood_weight']):.3f}",
                    "mean_change_fom": f"{float(row['mean_change_fom']):.8f}",
                    "population_std": f"{float(row['population_std']):.8f}",
                    "metric": row["metric"],
                    "purpose": row["purpose"],
                }
            )
    report = {
        "schema": "gwm.abu_dhabi_neighbourhood_sensitivity.v2",
        "metric": "strict_multiclass_change_figure_of_merit",
        "weights": list(WEIGHTS),
        "seeds": list(seeds),
        "rows": summary,
        "raw_seed_rows": rows,
    }
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return report


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("--seeds", default=",".join(str(seed) for seed in SEEDS))
    args = parser.parse_args()
    report = run(
        output=args.output,
        report_path=args.report,
        seeds=tuple(int(value) for value in args.seeds.split(",") if value.strip()),
    )
    print(json.dumps({"status": "complete", "rows": len(report["rows"]), "output": str(args.output)}))


if __name__ == "__main__":
    main()
