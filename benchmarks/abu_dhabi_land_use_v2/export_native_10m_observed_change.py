#!/usr/bin/env python3
"""Export the observed 2024→2025 ArcGIS change layer at native 10 m."""

from __future__ import annotations

from pathlib import Path

import geopandas as gpd
import rasterio
from rasterio.features import shapes
from shapely.geometry import shape

HERE = Path(__file__).resolve().parent
ROOT = HERE / "artifacts/arcgis_sentinel2_landcover/native"
OUTPUT = HERE / "results_arcgis_v2/vectors/arcgis_observed_2024_2025_native10m.gpkg"


def main() -> None:
    with rasterio.open(ROOT / "arcgis_sentinel2_landcover_2024_10m.tif") as src:
        origin = src.read(1)
        profile = src.profile.copy()
    with rasterio.open(ROOT / "arcgis_sentinel2_landcover_2025_10m.tif") as src:
        target = src.read(1)
    mask = (origin > 0) & (target > 0) & (origin != target)
    code = origin.astype("int16") * 100 + target.astype("int16")
    records = []
    for geom_json, value in shapes(code, mask=mask, transform=profile["transform"]):
        source, destination = divmod(int(value), 100)
        geom = shape(geom_json)
        records.append({"start_yr": 2024, "target_yr": 2025, "src_cls": source, "dst_cls": destination, "area_m2": float(geom.area), "geometry": geom})
    gdf = gpd.GeoDataFrame(records, geometry="geometry", crs=profile["crs"])
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    gdf.to_file(OUTPUT, layer="native10m", driver="GPKG", engine="pyogrio")
    print({"path": str(OUTPUT), "polygon_count": len(gdf), "changed_area_m2": float(gdf.area.sum())})


if __name__ == "__main__":
    main()
