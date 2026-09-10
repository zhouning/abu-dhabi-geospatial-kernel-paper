#!/usr/bin/env python3
"""Compile auditable ArcGIS-v2 tables, ensemble rasters and change vectors."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import geopandas as gpd
import numpy as np
import rasterio
from rasterio.features import shapes
from shapely.geometry import shape

HERE = Path(__file__).resolve().parent
ARTIFACT_ROOT = HERE / "artifacts"
INPUT_ROOT = ARTIFACT_ROOT / "gee" / "land_cover"
PREDICTION_ROOT = ARTIFACT_ROOT / "planning_arcgis_2026_2031"
BUNDLE_ROOT = ARTIFACT_ROOT / "bundle"
YEARS = tuple(range(2026, 2032))
MODELS = ("geosos_flus", "geospatial_kernel", "paper58")
SCENARIOS = ("compact", "ecological_priority", "outward_growth")
CLASS_NAMES = {1: "water", 2: "woody_vegetation", 3: "low_vegetation", 4: "wetland", 5: "built", 6: "bare"}


def read(path: Path) -> tuple[np.ndarray, dict]:
    with rasterio.open(path) as dataset:
        return dataset.read(1), dataset.profile.copy()


def write(path: Path, data: np.ndarray, profile: dict, description: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    p = profile.copy()
    p.update(count=1, dtype="uint8", nodata=0, compress="deflate", tiled=True, blockxsize=256, blockysize=256)
    with rasterio.open(path, "w", **p) as dataset:
        dataset.write(data.astype(np.uint8), 1)
        dataset.set_band_description(1, description)


def ensemble(paths: list[Path], profile: dict) -> np.ndarray:
    arrays = [read(path)[0] for path in paths]
    stack = np.stack(arrays, axis=0)
    # Stable majority vote; ties resolve to the smallest class code.
    result = np.ones(stack.shape[1:], dtype=np.uint8)
    for value in range(1, 7):
        count = (stack == value).sum(axis=0)
        if value == 1:
            best = count
        else:
            replace = count > best
            result[replace] = value
            best[replace] = count[replace]
    result[stack.max(axis=0) == 0] = 0
    return result


def class_counts(array: np.ndarray, valid: np.ndarray) -> dict[str, int]:
    return {str(value): int(np.count_nonzero(valid & (array == value))) for value in range(1, 7)}


def make_vectors(origin: np.ndarray, target: np.ndarray, profile: dict, output_gpkg: Path, *, start_year: int, target_year: int) -> dict[str, int]:
    mask = (origin > 0) & (target > 0) & (origin != target)
    code = origin.astype(np.int16) * 10 + target.astype(np.int16)
    records = []
    with rasterio.Env():
        for geometry, value in shapes(code.astype(np.int16), mask=mask, transform=profile["transform"]):
            source, destination = divmod(int(value), 10)
            if source == destination or source not in CLASS_NAMES or destination not in CLASS_NAMES:
                continue
            geom = shape(geometry)
            records.append({"start_yr": start_year, "target_yr": target_year, "src_cls": source, "dst_cls": destination, "src_name": CLASS_NAMES[source], "dst_name": CLASS_NAMES[destination], "area_m2": float(geom.area), "geometry": geom})
    if records:
        gdf = gpd.GeoDataFrame(records, geometry="geometry", crs=profile["crs"])
    else:
        gdf = gpd.GeoDataFrame(columns=["start_yr", "target_yr", "src_cls", "dst_cls", "src_name", "dst_name", "area_m2", "geometry"], geometry="geometry", crs=profile["crs"])
    output_gpkg.parent.mkdir(parents=True, exist_ok=True)
    layer = f"y{target_year}"
    gdf.to_file(
        output_gpkg,
        layer=layer,
        driver="GPKG",
        engine="pyogrio",
        append=output_gpkg.exists(),
    )
    return {"polygon_count": int(len(gdf)), "changed_area_m2": float(gdf["area_m2"].sum()) if len(gdf) else 0.0}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=HERE / "results_arcgis_v2")
    args = parser.parse_args()
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    city, profile = read(ARTIFACT_ROOT / "abu_dhabi_city_100m_mask.tif")
    valid = city > 0
    states = {year: read(INPUT_ROOT / f"land_cover_{year}_100m.tif")[0] for year in range(2017, 2026)}
    source_summary = {
        "source": "ArcGIS Sentinel2_10m_LandCover",
        "native_years": list(range(2017, 2026)),
        "native_resolution_m": 10,
        "model_resolution_m": 100,
        "aggregation": "map source classes to canonical six classes, then 10x10 majority vote among usable pixels",
        "class_counts_100m": {str(year): class_counts(states[year], valid) for year in states},
    }
    old_states = {year: read(HERE.parent / "abu_dhabi_land_use_v1" / "artifacts/gee/land_cover" / f"land_cover_{year}_100m.tif")[0] for year in range(2017, 2025)}
    cross_product = {}
    for year in range(2017, 2025):
        joint = {}
        for old_value in range(1, 7):
            for new_value in range(1, 7):
                count = int(np.count_nonzero(valid & (old_states[year] == old_value) & (states[year] == new_value)))
                if count:
                    joint[f"{old_value}->{new_value}"] = count
        cross_product[str(year)] = joint
    source_summary["dynamic_world_cross_product_100m"] = cross_product
    (output / "source_comparison.json").write_text(json.dumps(source_summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    rows = []
    for model in MODELS:
        for scenario in SCENARIOS:
            ensemble_root = output / "ensembles" / model / scenario
            vector_path = output / "vectors" / f"{model}_{scenario}_changes_2025_2031.gpkg"
            if vector_path.exists():
                vector_path.unlink()
            origin = states[2025]
            for year in YEARS:
                paths = [PREDICTION_ROOT / model / scenario / f"seed_{seed}" / f"prediction_{year}.tif" for seed in (31, 47, 73)]
                pred = ensemble(paths, profile)
                pred[~valid] = 0
                out_raster = ensemble_root / f"prediction_{year}.tif"
                write(out_raster, pred, profile, f"{model}_{scenario}_ensemble_{year}")
                counts = class_counts(pred, valid)
                changed = int(np.count_nonzero(valid & (origin != pred)))
                vector = make_vectors(origin, pred, profile, vector_path, start_year=2025 if year == 2026 else year - 1, target_year=year)
                rows.append({"model": model, "scenario": scenario, "target_year": year, "prediction": str(out_raster.relative_to(HERE)), "counts": counts, "changed_cells_from_previous_year": changed, "change_polygons": str(vector_path.relative_to(HERE)), **vector})
                origin = pred
    report = {"schema": "gwm.abu_dhabi_land_use_v2_results.v1", "source": source_summary, "models": list(MODELS), "scenarios": list(SCENARIOS), "years": list(YEARS), "rows": rows, "claim_boundary": "ArcGIS is a public global remote-sensing land-cover product; it is not an authoritative Abu Dhabi statutory land-use database."}
    (output / "results_summary.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    lines = ["# Abu Dhabi land-use v2: ArcGIS Sentinel-2 10 m results", "", "The v2 run uses the public ArcGIS Sentinel2_10m_LandCover categorical product for 2017–2025. Native 10 m rasters are retained; the three models run on the existing aligned 100 m contract after canonical class mapping and 10×10 majority aggregation.", "", "## Source comparison", "", "| Year | ArcGIS built cells | Dynamic World built cells | ArcGIS valid cells |", "|---:|---:|---:|---:|"]
    for year in range(2017, 2025):
        lines.append(f"| {year} | {source_summary['class_counts_100m'][str(year)]['5']:,} | {class_counts(old_states[year], valid)['5']:,} | {sum(source_summary['class_counts_100m'][str(year)].values()):,} |")
    lines += ["", "## Scenario results", "", "| Model | Scenario | Year | Built cells | Changed cells from previous year | Change polygons |", "|---|---|---:|---:|---:|---:|"]
    for row in rows:
        lines.append(f"| {row['model']} | {row['scenario']} | {row['target_year']} | {row['counts']['5']:,} | {row['changed_cells_from_previous_year']:,} | {row['polygon_count']:,} |")
    lines += ["", "## Interpretation", "", "The ArcGIS source improves temporal coverage to 2025 and preserves a native 10 m audit layer. The released model predictions remain 100 m because the existing FLUS-style console and GeoFM-LDN contract were not silently changed to claim 10 m predictive accuracy. A future 10 m modelling release requires explicit 10 m retraining, neighbourhood-scale recalibration, and independent validation.", ""]
    (output / "results_summary.md").write_text("\n".join(lines), encoding="utf-8")
    print(json.dumps({"status": "complete", "output": str(output), "rows": len(rows)}))


if __name__ == "__main__":
    main()
