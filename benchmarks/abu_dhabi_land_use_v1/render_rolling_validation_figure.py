#!/usr/bin/env python3
"""Render the rolling-origin and external-product diagnostic figure."""

from __future__ import annotations

import json
import csv
from pathlib import Path

import matplotlib as mpl

mpl.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.lines import Line2D


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
OUT = REPO / "figures"
ROLLING = HERE / "artifacts/rolling_backtest/report.json"
UNCERTAINTY = HERE / "artifacts/rolling_backtest/paired_spatial_uncertainty.json"
WORLDCOVER = HERE / "artifacts/external_validation/worldcover/diagnostic.json"

mpl.rcParams.update(
    {
        "font.family": "sans-serif",
        "font.sans-serif": ["Arial", "DejaVu Sans", "Liberation Sans"],
        "font.size": 8.0,
        "axes.titlesize": 9.0,
        "axes.labelsize": 8.0,
        "xtick.labelsize": 7.2,
        "ytick.labelsize": 7.2,
        "legend.fontsize": 7.2,
        "svg.fonttype": "none",
        "pdf.fonttype": 42,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.linewidth": 0.65,
        "savefig.facecolor": "white",
    }
)

COLORS = {
    "geospatial_kernel": "#D55E00",
    "random_allocation": "#CC79A7",
    "persistence": "#6A737D",
    "dynamic_world_observed": "#0072B2",
    "dynamic_world_observed_2020": "#56B4E9",
    "dynamic_world_observed_2021": "#0072B2",
    "geospatial_kernel_worldcover_action": "#D55E00",
    "random_worldcover_action": "#CC79A7",
}
LABELS = {
    "geospatial_kernel": "Geospatial Kernel",
    "random_allocation": "Random allocation",
    "persistence": "Persistence",
    "dynamic_world_observed": "Dynamic World observed",
    "dynamic_world_observed_2020": "Dynamic World 2020",
    "dynamic_world_observed_2021": "Dynamic World 2021",
    "geospatial_kernel_worldcover_action": "Kernel (WorldCover count)",
    "random_worldcover_action": "Random (WorldCover count)",
}


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _panel_label(ax, label: str) -> None:
    ax.text(
        -0.12,
        1.08,
        label,
        transform=ax.transAxes,
        fontsize=10,
        fontweight="bold",
        va="top",
        ha="left",
    )


def _save(fig: plt.Figure) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for suffix, kwargs in (
        ("svg", {"bbox_inches": "tight", "pad_inches": 0.04}),
        ("pdf", {"bbox_inches": "tight", "pad_inches": 0.04}),
        ("png", {"dpi": 600, "bbox_inches": "tight", "pad_inches": 0.04}),
        ("tiff", {"dpi": 600, "bbox_inches": "tight", "pad_inches": 0.04}),
    ):
        path = OUT / f"fig03_rolling_external_diagnostics.{suffix}"
        fig.savefig(path, **kwargs)
        if suffix == "svg":
            normalized = "\n".join(
                line.rstrip() for line in path.read_text(encoding="utf-8").splitlines()
            )
            path.write_text(normalized + "\n", encoding="utf-8")
    plt.close(fig)


def _write_source_data(rolling: dict, uncertainty: dict, worldcover: dict) -> None:
    path = REPO / "manuscript/source_data_fig03_rolling_external_diagnostics.csv"
    fields = ("panel", "series", "x", "seed", "estimate", "lower", "upper", "metric")
    records: list[dict[str, object]] = []
    for item in rolling["summaries"]:
        metric = item["metrics"]["change_figure_of_merit"]
        records.append(
            {
                "panel": "a",
                "series": item["model_id"],
                "x": item["target_year"],
                "seed": "mean_n3",
                "estimate": metric["mean"],
                "lower": metric["mean"] - metric["sample_standard_deviation"],
                "upper": metric["mean"] + metric["sample_standard_deviation"],
                "metric": "strict_change_fom_mean_plus_minus_sample_sd",
            }
        )
    for item in uncertainty["rows"]:
        interval = item["interval"]["change_figure_of_merit"]
        records.append(
            {
                "panel": "b",
                "series": f"kernel_minus_{item['model_b']}",
                "x": item["target_year"],
                "seed": item["model_seed"],
                "estimate": interval["median"],
                "lower": interval["lower"],
                "upper": interval["upper"],
                "metric": "paired_spatial_block_bootstrap_strict_fom_difference",
            }
        )
    for item in worldcover["rows"]:
        threshold = item["worldcover_built_fraction_threshold"]
        for panel, section in (("c", "built_stock_agreement"), ("d", "built_gain_agreement")):
            for series, metric in item[section].items():
                if panel == "d" and series != "dynamic_world_observed":
                    continue
                value = metric["f1"] if "mean" not in metric else metric["mean"]["f1"]
                records.append(
                    {
                        "panel": panel,
                        "series": series,
                        "x": threshold,
                        "seed": "deterministic_or_mean_n3",
                        "estimate": value,
                        "lower": "",
                        "upper": "",
                        "metric": "binary_f1_against_worldcover",
                    }
                )
        for series, metric in item["worldcover_gain_count_action"].items():
            if series == "gain_count":
                continue
            records.append(
                {
                    "panel": "d",
                    "series": f"{series}_worldcover_count_action",
                    "x": threshold,
                    "seed": "mean_n3",
                    "estimate": metric["mean"]["f1"],
                    "lower": "",
                    "upper": "",
                    "metric": "binary_f1_against_worldcover_with_worldcover_gain_count_action",
                }
            )
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(records)


def main() -> None:
    rolling = _load(ROLLING)
    uncertainty = _load(UNCERTAINTY)
    worldcover = _load(WORLDCOVER)
    origins = np.asarray(rolling["origins"], dtype=int)
    target_years = origins + 1

    fig, axes = plt.subplots(2, 2, figsize=(7.2, 5.8))
    fig.subplots_adjust(left=0.10, right=0.98, top=0.91, bottom=0.17, wspace=0.31, hspace=0.46)

    # A: rolling-origin FoM.
    ax = axes[0, 0]
    for model in ("geospatial_kernel", "random_allocation", "persistence"):
        means, sds = [], []
        for origin in origins:
            item = next(
                row
                for row in rolling["summaries"]
                if row["origin_year"] == int(origin) and row["model_id"] == model
            )
            metric = item["metrics"]["change_figure_of_merit"]
            means.append(metric["mean"])
            sds.append(metric["sample_standard_deviation"])
        ax.errorbar(
            target_years,
            means,
            yerr=sds,
            marker="o",
            markersize=4,
            linewidth=1.5,
            capsize=2.2,
            color=COLORS[model],
            label=LABELS[model],
        )
    ax.set_title("Expanding-window allocation skill", loc="left", fontweight="bold")
    ax.set_xlabel("One-step target year")
    ax.set_ylabel("Strict change FoM")
    ax.set_xticks(target_years)
    ax.set_ylim(bottom=0)
    ax.grid(axis="y", color="#D8DDE3", linewidth=0.45)
    _panel_label(ax, "a")

    # B: paired spatial-block differences.
    ax = axes[0, 1]
    baselines = ("random_allocation", "persistence")
    y_base = np.arange(len(target_years)) * 2.5
    offsets = {"random_allocation": -0.34, "persistence": 0.34}
    for baseline in baselines:
        for idx, target in enumerate(target_years):
            rows = [
                row
                for row in uncertainty["rows"]
                if row["target_year"] == int(target) and row["model_b"] == baseline
            ]
            medians = np.array([row["interval"]["change_figure_of_merit"]["median"] for row in rows])
            lows = np.array([row["interval"]["change_figure_of_merit"]["lower"] for row in rows])
            highs = np.array([row["interval"]["change_figure_of_merit"]["upper"] for row in rows])
            y = y_base[idx] + offsets[baseline]
            ax.errorbar(
                medians.mean(),
                y,
                xerr=[[medians.mean() - lows.min()], [highs.max() - medians.mean()]],
                fmt="o",
                markersize=4,
                color=COLORS[baseline],
                ecolor=COLORS[baseline],
                linewidth=1.2,
                capsize=2.0,
            )
    ax.axvline(0, color="#4D4D4D", linewidth=0.7, linestyle="--")
    ax.set_yticks(y_base, [f"{year}" for year in target_years])
    ax.set_xlabel("Kernel − baseline strict FoM")
    ax.set_title("Paired spatial-block contrasts", loc="left", fontweight="bold")
    ax.grid(axis="x", color="#D8DDE3", linewidth=0.45)
    ax.set_ylim(y_base[-1] + 1.1, -1.1)
    ax.text(
        0.02,
        -0.26,
        "Whiskers span the minimum–maximum of seed-specific 95% spatial-block intervals (n = 3 seeds).",
        transform=ax.transAxes,
        fontsize=6.8,
        color="#4A5560",
    )
    _panel_label(ax, "b")

    thresholds = np.array([row["worldcover_built_fraction_threshold"] for row in worldcover["rows"]])

    # C: built-stock agreement.
    ax = axes[1, 0]
    for key in ("dynamic_world_observed_2020", "dynamic_world_observed_2021", "geospatial_kernel_2021", "persistence_2021"):
        if key.startswith("dynamic"):
            label_key = key
        else:
            label_key = key.removesuffix("_2021")
        values = [row["built_stock_agreement"][key]["f1"] if "mean" not in row["built_stock_agreement"][key] else row["built_stock_agreement"][key]["mean"]["f1"] for row in worldcover["rows"]]
        ax.plot(
            thresholds,
            values,
            marker="o",
            linewidth=1.5,
            markersize=4,
            color=COLORS[label_key],
            label=LABELS[label_key],
            linestyle="--" if key == "dynamic_world_observed_2020" else "-",
        )
    ax.set_title("Built-stock agreement", loc="left", fontweight="bold")
    ax.set_xlabel("WorldCover built fraction threshold")
    ax.set_ylabel("F1")
    ax.set_ylim(0, 0.5)
    ax.set_xticks(thresholds)
    ax.grid(axis="y", color="#D8DDE3", linewidth=0.45)
    ax.legend(
        frameon=False,
        loc="lower left",
        bbox_to_anchor=(0.0, 0.02),
        ncol=2,
        handlelength=1.3,
        columnspacing=0.8,
        fontsize=6.5,
    )
    _panel_label(ax, "c")

    # D: built-gain agreement.
    ax = axes[1, 1]
    action_keys = (
        ("dynamic_world_observed", "dynamic_world_observed"),
        ("geospatial_kernel_worldcover_action", "geospatial_kernel"),
        ("random_worldcover_action", "random_allocation"),
    )
    for label_key, result_key in action_keys:
        values = []
        for row in worldcover["rows"]:
            if label_key == "dynamic_world_observed":
                item = row["built_gain_agreement"][result_key]
            else:
                item = row["worldcover_gain_count_action"][result_key]
            values.append(item["f1"] if "mean" not in item else item["mean"]["f1"])
        ax.plot(
            thresholds,
            values,
            marker="o",
            linewidth=1.5,
            markersize=4,
            color=COLORS[label_key],
            label=LABELS[label_key],
        )
    ax.set_title("Built-gain agreement", loc="left", fontweight="bold")
    ax.set_xlabel("WorldCover built fraction threshold")
    ax.set_ylabel("F1")
    ax.set_ylim(-0.002, 0.045)
    ax.set_xticks(thresholds)
    ax.grid(axis="y", color="#D8DDE3", linewidth=0.45)
    ax.legend(
        frameon=False,
        loc="lower right",
        bbox_to_anchor=(0.98, 0.02),
        ncol=1,
        handlelength=1.3,
        fontsize=6.5,
    )
    _panel_label(ax, "d")

    fig.legend(
        handles=[
            Line2D([0], [0], marker="o", color=COLORS[k], label=LABELS[k], linestyle="none")
            for k in ("geospatial_kernel", "random_allocation", "persistence")
        ],
        loc="upper center",
        bbox_to_anchor=(0.54, 0.985),
        ncol=3,
        frameon=False,
        handlelength=1.2,
        columnspacing=1.25,
    )

    fig.text(
        0.10,
        0.045,
        "Panels a–b: Kernel-only expanding-window backtest (2020→2021 through 2023→2024).\n"
        "Panels c–d: independent public-product diagnostic against ESA WorldCover; agreement is not official validation.",
        fontsize=7.1,
        color="#4A5560",
    )
    _write_source_data(rolling, uncertainty, worldcover)
    _save(fig)


if __name__ == "__main__":
    main()
