#!/usr/bin/env python3
"""Export v2 GeoPackage change layers as one Shapefile per model/scenario."""

from __future__ import annotations

from pathlib import Path

import geopandas as gpd
import pandas as pd

HERE = Path(__file__).resolve().parent
VECTOR_ROOT = HERE / "results_arcgis_v2" / "vectors"
OUTPUT_ROOT = VECTOR_ROOT / "shapefiles"
MODELS = ("geosos_flus", "geospatial_kernel", "paper58")
SCENARIOS = ("compact", "ecological_priority", "outward_growth")


def main() -> None:
    OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)
    for model in MODELS:
        for scenario in SCENARIOS:
            source = VECTOR_ROOT / f"{model}_{scenario}_changes_2025_2031.gpkg"
            layers = gpd.list_layers(source)
            frames = []
            for name in layers["name"].tolist():
                frame = gpd.read_file(source, layer=name)
                frames.append(frame)
            merged = gpd.GeoDataFrame(pd.concat(frames, ignore_index=True), crs=frames[0].crs)
            output = OUTPUT_ROOT / f"{model}_{scenario}_changes_2025_2031.shp"
            merged.to_file(output, driver="ESRI Shapefile", engine="pyogrio")
            print(f"shapefile:{output.name}:{len(merged)}", flush=True)


if __name__ == "__main__":
    main()
