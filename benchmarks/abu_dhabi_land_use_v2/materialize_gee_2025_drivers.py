#!/usr/bin/env python3
"""Materialize 2025 AlphaEarth and VIIRS drivers for the ArcGIS v2 bundle."""

from __future__ import annotations

import importlib.util
from pathlib import Path

HERE = Path(__file__).resolve().parent
SOURCE = HERE.parent / "abu_dhabi_land_use_v1" / "materialize_gee_inputs.py"
spec = importlib.util.spec_from_file_location("materialize_v1", SOURCE)
if spec is None or spec.loader is None:
    raise ImportError(SOURCE)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def main() -> None:
    import argparse
    import json
    import numpy as np
    import rasterio
    import ee

    parser = argparse.ArgumentParser()
    parser.add_argument("--project", default="ee-zn19860115")
    parser.add_argument("--products", default="viirs,alphaearth")
    parser.add_argument("--alphaearth-chunk-size", type=int, default=8)
    args = parser.parse_args()
    ee.Initialize(project=args.project)
    # Use the frozen boundary through Earth Engine's GeoJSON constructor.
    boundary = json.loads((HERE / "source/abu_dhabi_city_osm_r4479763.geojson").read_text())
    geometry = ee.Geometry(boundary["features"][0]["geometry"])
    grid = module.expected_grid(HERE / "grid_profile.json")
    city_mask = rasterio.open(HERE / "artifacts/abu_dhabi_city_100m_mask.tif").read(1).astype(bool)
    output = HERE / "artifacts/gee"
    output.mkdir(parents=True, exist_ok=True)
    module.HERE = HERE
    records = []
    if "viirs" in args.products.split(","):
        records.extend(module.materialize_viirs(ee, geometry, years=(2025,), output_root=output, grid=grid, city_mask=city_mask))
    if "alphaearth" in args.products.split(","):
        records.extend(module.materialize_alphaearth(ee, geometry, city_mask_path=HERE / "artifacts/abu_dhabi_city_100m_mask.tif", years=(2025,), output_root=output, grid=grid, chunk_size=args.alphaearth_chunk_size))
    print(json.dumps({"status": "complete", "artifacts": records}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
