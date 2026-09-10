"""Audit count-limited allocation and paired intervals without refitting models.

Only frozen reports are read. The FoM bound is count-only and need not be
attainable under destination, location, and hard-mask restrictions.
"""
from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def count_bound(predicted: int, observed: int) -> float | None:
    if min(predicted, observed) < 0:
        raise ValueError("negative_change_count")
    return min(predicted, observed) / max(predicted, observed) if max(predicted, observed) else None


def analyze() -> None:
    rows, contrasts, sources = [], [], []
    for product, folder in (("Dynamic World", "dynamic_world_matched_backtest"), ("ArcGIS", "arcgis_v2_historical_backtest")):
        path = HERE / "artifacts" / folder / "report.json"
        raw = path.read_bytes()
        report = json.loads(raw)
        if report["status"] != "complete":
            raise ValueError(f"incomplete_report:{folder}")
        canonical = raw.replace(b"\r\n", b"\n").replace(b"\r", b"\n")
        sources.append({"path": path.relative_to(ROOT).as_posix(), "sha256": hashlib.sha256(canonical).hexdigest(), "hash_mode": "text_lf_normalized"})
        for year in report["target_years"]:
            selected = [r for r in report["rows"] if r["target_year"] == year]
            origins = [r["evaluation"]["actual_class_counts"] for r in selected if r["model_id"] == "persistence"]
            assert origins and all(o == origins[0] for o in origins)
            kernels = [r for r in selected if r["model_id"] == "geospatial_kernel"]
            assert len(kernels) == len(report["seeds"])
            changes = set()
            for row in kernels:
                target = row["feasible_oracle_target_counts"]
                origin = origins[0]
                assert sum(target.values()) == sum(origin.values())
                moved = sum(abs(target[k] - origin[k]) for k in target) // 2
                e = row["evaluation"]
                assert moved == e["predicted_change_pixels"]
                observed = e["observed_change_pixels"]
                bound = count_bound(moved, observed)
                assert bound is None or e["change_figure_of_merit"] <= bound + 1e-12
                changes.add((moved, observed))
            assert len(changes) == 1
            moved, observed = changes.pop()
            bound = count_bound(moved, observed)
            rows.append({"product": product, "target_year": year, "observed_change_pixels": observed,
                         "minimum_feasible_moves": moved, "count_only_fom_upper_bound": bound,
                         "kernel_mean_fom": sum(r["evaluation"]["change_figure_of_merit"] for r in kernels) / len(kernels)})
            for comparison, seeds in report["bootstrap"]["results"][str(year)]["paired_model_differences"].items():
                if comparison not in ("geospatial_kernel_minus_geosos_flus", "paper58_minus_geospatial_kernel"):
                    continue
                for seed, result in seeds.items():
                    ci = result["change_figure_of_merit"]
                    contrasts.append({"product": product, "target_year": year, "comparison": comparison,
                                      "seed": int(seed), **ci,
                                      "direction": "positive" if ci["lower"] > 0 else "negative" if ci["upper"] < 0 else "includes_zero"})
    out = HERE / "results_arcgis_v2" / "allocation_limits"
    out.mkdir(parents=True, exist_ok=True)
    for name, values in (("count_limits", rows), ("paired_intervals", contrasts)):
        with (out / f"{name}.csv").open("w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=list(values[0]))
            writer.writeheader()
            writer.writerows(values)
    (out / "sources.json").write_text(json.dumps(sources, indent=2) + "\n", encoding="utf-8")
    text = ["# Supplementary Table S7. Net-change limits and conditional model contrasts", "",
            "Derived from frozen three-seed expanding-window reports; no models were refit. Origin counts are recovered from persistence outputs on the same evaluation mask. M is half the L1 difference between origin and feasible target class totals. O is observed gross change. For strict destination-change FoM, hits cannot exceed min(M,O), and the union contains at least max(M,O) cells, hence FoM <= min(M,O)/max(M,O). This loose count-only upper bound is not necessarily attainable: destination, hard-mask and spatial restrictions can lower the achievable maximum. Feasible counts may differ from observed counts. The bound is not a corrected skill score or a validation reference.", "",
            "| Product | Target | Observed changes O | Feasible moves M | Count-only FoM upper bound | Kernel FoM |",
            "|---|---:|---:|---:|---:|---:|"]
    for r in rows:
        text.append(f"| {r['product']} | {r['target_year']} | {r['observed_change_pixels']} | {r['minimum_feasible_moves']} | {r['count_only_fom_upper_bound']:.4f} | {r['kernel_mean_fom']:.4f} |")
    text += ["", "## Seed-specific paired spatial-block intervals", "",
             "Each interval uses the archived 1,000 shared resamples of 8 × 8 cells. Seeds are computational replicates, not independent field samples. Intervals are conditional on each product, fold, seed and mask; no pooled confidence interval or multiple-comparison adjustment is claimed. An interval containing zero does not establish equivalence. Block-size sensitivity and spatial transfer remain untested.", "",
             "| Product | Target | Contrast | Seed | Median | Lower 95% | Upper 95% | Direction |", "|---|---:|---|---:|---:|---:|---:|---|"]
    labels = {"geospatial_kernel_minus_geosos_flus": "Kernel minus FLUS-style", "paper58_minus_geospatial_kernel": "GeoFM-LDN minus Kernel"}
    for r in contrasts:
        text.append(f"| {r['product']} | {r['target_year']} | {labels[r['comparison']]} | {r['seed']} | {r['median']:.4f} | {r['lower']:.4f} | {r['upper']:.4f} | {r['direction']} |")
    (ROOT / "manuscript" / "supplementary_table_S7_allocation_limits.md").write_text("\n".join(text) + "\n", encoding="utf-8")
    print(json.dumps({"folds": len(rows), "paired_intervals": len(contrasts), "status": "PASS"}))


if __name__ == "__main__":
    analyze()
