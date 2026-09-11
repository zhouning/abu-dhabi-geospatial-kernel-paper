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
CSV_FLOAT_DECIMALS = 12
MODEL_ORDER = ("geosos_flus", "geospatial_kernel", "paper58", "random_minimum_change")
MODEL_LABELS = {
    "geosos_flus": "FLUS-style",
    "geospatial_kernel": "Kernel",
    "paper58": "GeoFM-LDN",
    "random_minimum_change": "Random minimum-change",
}
EXACT_MINIMUM_CHANGE_MODELS = ("geospatial_kernel", "paper58", "random_minimum_change")


def count_bound(predicted: int, observed: int) -> float | None:
    if min(predicted, observed) < 0:
        raise ValueError("negative_change_count")
    return min(predicted, observed) / max(predicted, observed) if max(predicted, observed) else None


def require(condition: bool, code: str) -> None:
    if not condition:
        raise ValueError(code)


def csv_value(value: object) -> object:
    """Use a platform-independent text representation for derived floats."""

    return f"{value:.{CSV_FLOAT_DECIMALS}f}" if isinstance(value, float) else value


def _seed_text(values: list[tuple[int, int]]) -> str:
    return "/".join(str(value) for _, value in sorted(values))


def write_text_lf(path: Path, content: str) -> None:
    """Write text deterministically on POSIX and Windows."""

    with path.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(content)


def analyze(output_dir: Path | None = None, supplementary_path: Path | None = None) -> dict[str, int | str]:
    rows, model_changes, contrasts, sources = [], [], [], []
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
            require(bool(origins) and all(o == origins[0] for o in origins), f"inconsistent_origin_counts:{folder}:{year}")
            kernels = [r for r in selected if r["model_id"] == "geospatial_kernel"]
            require(len(kernels) == len(report["seeds"]), f"unexpected_kernel_seed_count:{folder}:{year}")
            changes = set()
            for row in kernels:
                target = row["feasible_oracle_target_counts"]
                origin = origins[0]
                require(set(target) == set(origin), f"mismatched_class_domain:{folder}:{year}")
                require(sum(target.values()) == sum(origin.values()), f"inconsistent_target_total:{folder}:{year}")
                moved = sum(abs(target[k] - origin[k]) for k in target) // 2
                e = row["evaluation"]
                require(moved == e["predicted_change_pixels"], f"inconsistent_predicted_moves:{folder}:{year}")
                observed = e["observed_change_pixels"]
                bound = count_bound(moved, observed)
                require(bound is None or e["change_figure_of_merit"] <= bound + 1e-12, f"count_bound_violation:{folder}:{year}")
                changes.add((moved, observed))
            require(len(changes) == 1, f"inconsistent_kernel_change_counts:{folder}:{year}")
            moved, observed = changes.pop()
            bound = count_bound(moved, observed)
            changed_by_model: dict[str, list[tuple[int, int]]] = {}
            for model_id in MODEL_ORDER:
                model_rows = sorted(
                    [row for row in selected if row["model_id"] == model_id],
                    key=lambda row: int(row["seed"]),
                )
                require(len(model_rows) == len(report["seeds"]), f"unexpected_seed_count:{folder}:{year}:{model_id}")
                values = [
                    (int(row["seed"]), int(row["evaluation"]["predicted_change_pixels"]))
                    for row in model_rows
                ]
                changed_by_model[model_id] = values
                for seed, predicted_change_pixels in values:
                    model_changes.append(
                        {
                            "product": product,
                            "target_year": year,
                            "model_id": model_id,
                            "seed": seed,
                            "predicted_change_pixels": predicted_change_pixels,
                            "observed_change_pixels": observed,
                            "minimum_feasible_moves": moved,
                            "is_exact_minimum_change_projection": model_id in EXACT_MINIMUM_CHANGE_MODELS,
                        }
                    )
            for model_id in EXACT_MINIMUM_CHANGE_MODELS:
                require(
                    all(predicted == moved for _, predicted in changed_by_model[model_id]),
                    f"inconsistent_exact_minimum_changes:{folder}:{year}:{model_id}",
                )
            rows.append({
                "product": product,
                "target_year": year,
                "observed_change_pixels": observed,
                "minimum_feasible_moves": moved,
                "count_only_fom_upper_bound": bound,
                "kernel_mean_fom": sum(r["evaluation"]["change_figure_of_merit"] for r in kernels) / len(kernels),
                **{
                    f"{model_id}_predicted_change_pixels_seeds_31_47_73": _seed_text(changed_by_model[model_id])
                    for model_id in MODEL_ORDER
                },
            })
            for comparison, seeds in report["bootstrap"]["results"][str(year)]["paired_model_differences"].items():
                if comparison not in ("geospatial_kernel_minus_geosos_flus", "paper58_minus_geospatial_kernel"):
                    continue
                for seed, result in seeds.items():
                    ci = result["change_figure_of_merit"]
                    contrasts.append({"product": product, "target_year": year, "comparison": comparison,
                                      "seed": int(seed), **ci,
                                      "direction": "positive" if ci["lower"] > 0 else "negative" if ci["upper"] < 0 else "includes_zero"})
    out = output_dir or HERE / "results_arcgis_v2" / "allocation_limits"
    out.mkdir(parents=True, exist_ok=True)
    for name, values in (("count_limits", rows), ("model_change_counts", model_changes), ("paired_intervals", contrasts)):
        with (out / f"{name}.csv").open("w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=list(values[0]), lineterminator="\n")
            writer.writeheader()
            writer.writerows([{key: csv_value(value) for key, value in row.items()} for row in values])
    write_text_lf(out / "sources.json", json.dumps(sources, indent=2) + "\n")
    text = ["# Supplementary Table S7. Net-change limits and conditional model contrasts", "",
            "Derived from frozen three-seed expanding-window reports; no models were refit. Origin counts are recovered from persistence outputs on the same evaluation mask. M is half the L1 difference between origin and feasible target class totals. O is observed gross change. For strict destination-change FoM, hits cannot exceed min(M,O), and the union contains at least max(M,O) cells, hence FoM <= min(M,O)/max(M,O). This loose count-only upper bound is not necessarily attainable: destination, hard-mask and spatial restrictions can lower the achievable maximum. Feasible counts may differ from observed counts. The bound is not a corrected skill score or a validation reference.", "",
            "The count-only bound applies only to the exact minimum-change projections (Kernel, GeoFM-LDN and random minimum-change), each of which changes exactly M cells. The finite-iteration FLUS-style CA can meet near-exact final class totals through simultaneous class inflows and outflows and therefore can change more than M cells; it is not constrained by this bound. The seed triplets below expose this asymmetric transition budget.", "",
            "| Product | Target | O | M | Exact-count FoM upper bound | FLUS changed cells (31/47/73) | Kernel changed cells (31/47/73) | GeoFM-LDN changed cells (31/47/73) | Random changed cells (31/47/73) | Kernel FoM |",
            "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|"]
    for r in rows:
        text.append(
            f"| {r['product']} | {r['target_year']} | {r['observed_change_pixels']} | {r['minimum_feasible_moves']} | "
            f"{r['count_only_fom_upper_bound']:.4f} | {r['geosos_flus_predicted_change_pixels_seeds_31_47_73']} | "
            f"{r['geospatial_kernel_predicted_change_pixels_seeds_31_47_73']} | "
            f"{r['paper58_predicted_change_pixels_seeds_31_47_73']} | "
            f"{r['random_minimum_change_predicted_change_pixels_seeds_31_47_73']} | {r['kernel_mean_fom']:.4f} |"
        )
    arcgis_bounds = [float(row["count_only_fom_upper_bound"]) for row in rows if row["product"] == "ArcGIS"]
    arcgis_bounds_without_2022 = [
        float(row["count_only_fom_upper_bound"])
        for row in rows
        if row["product"] == "ArcGIS" and int(row["target_year"]) != 2022
    ]
    text += [
             "",
             "For the ArcGIS folds, the exact-count upper bounds span "
             f"{min(arcgis_bounds):.4f}–{max(arcgis_bounds):.4f} across all targets and "
             f"{min(arcgis_bounds_without_2022):.4f}–{max(arcgis_bounds_without_2022):.4f} after excluding the 2022 product-series-break target. "
             "This sensitivity concerns the net-versus-gross change relation, not verified land-cover accuracy.",
             "",
             "## Seed-specific paired spatial-block intervals", "",
             "Each interval uses the archived 1,000 shared resamples of 8 × 8 cells. Seeds are computational replicates, not independent field samples. Intervals are conditional on each product, fold, seed and mask; no pooled confidence interval or multiple-comparison adjustment is claimed. An interval containing zero does not establish equivalence. Block-size sensitivity and spatial transfer remain untested.", "",
             "| Product | Target | Contrast | Seed | Median | Lower 95% | Upper 95% | Direction |", "|---|---:|---|---:|---:|---:|---:|---|"]
    labels = {"geospatial_kernel_minus_geosos_flus": "Kernel minus FLUS-style", "paper58_minus_geospatial_kernel": "GeoFM-LDN minus Kernel"}
    for r in contrasts:
        text.append(f"| {r['product']} | {r['target_year']} | {labels[r['comparison']]} | {r['seed']} | {r['median']:.4f} | {r['lower']:.4f} | {r['upper']:.4f} | {r['direction']} |")
    table_path = supplementary_path or ROOT / "manuscript" / "supplementary_table_S7_allocation_limits.md"
    write_text_lf(table_path, "\n".join(text) + "\n")
    return {"folds": len(rows), "model_change_rows": len(model_changes), "paired_intervals": len(contrasts), "status": "PASS"}


if __name__ == "__main__":
    print(json.dumps(analyze()))
