#!/usr/bin/env python3
"""Freeze ESA WorldCover built fractions for an external-product diagnostic."""

from __future__ import annotations

import argparse
import json
import time
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import rasterio

try:
    from .materialize_gee_inputs import (
        DEFAULT_BOUNDARY,
        DEFAULT_CITY_MASK,
        DEFAULT_GRID_PROFILE,
        NODATA_FLOAT,
        _rewrite_raster,
        artifact,
        download_image,
        expected_grid,
        load_geometry,
        sha256_file,
        validate_raster,
    )
except ImportError:
    from materialize_gee_inputs import (  # type: ignore
        DEFAULT_BOUNDARY,
        DEFAULT_CITY_MASK,
        DEFAULT_GRID_PROFILE,
        NODATA_FLOAT,
        _rewrite_raster,
        artifact,
        download_image,
        expected_grid,
        load_geometry,
        sha256_file,
        validate_raster,
    )


HERE = Path(__file__).resolve().parent
DEFAULT_OUTPUT = HERE / "artifacts/external_validation/worldcover"
DEFAULT_MANIFEST = DEFAULT_OUTPUT / "input_manifest.json"
ASSETS = {
    2020: "ESA/WorldCover/v100/2020",
    2021: "ESA/WorldCover/v200/2021",
}


def materialize(
    *,
    project: str,
    boundary_path: Path,
    grid_profile_path: Path,
    city_mask_path: Path,
    output_root: Path,
    manifest_path: Path,
) -> dict[str, Any]:
    boundary_path = boundary_path.resolve()
    grid_profile_path = grid_profile_path.resolve()
    city_mask_path = city_mask_path.resolve()
    output_root = output_root.resolve()
    manifest_path = manifest_path.resolve()
    import ee

    ee.Initialize(project=project)
    grid = expected_grid(grid_profile_path)
    validate_raster(city_mask_path, grid, band_count=1)
    with rasterio.open(city_mask_path) as dataset:
        city_mask = dataset.read(1).astype(bool)
    geometry = ee.Geometry(
        load_geometry(boundary_path), proj="EPSG:4326", geodesic=False
    )
    started = time.perf_counter()
    records: list[dict[str, Any]] = []
    for year, asset_id in ASSETS.items():
        worldcover = ee.Image(asset_id).select("Map")
        built_fraction = (
            worldcover.eq(50)
            .rename("built_fraction")
            .reduceResolution(reducer=ee.Reducer.mean(), maxPixels=1024)
            .clip(geometry)
            .unmask(NODATA_FLOAT)
            .toFloat()
        )
        output_path = output_root / f"worldcover_{year}_built_fraction_100m.tif"
        download_image(
            built_fraction,
            output_path=output_path,
            grid=grid,
            name=f"abu_dhabi_worldcover_{year}_built_fraction_100m",
            band_count=1,
        )
        _rewrite_raster(
            output_path,
            dtype="float32",
            nodata=NODATA_FLOAT,
            descriptions=("worldcover_built_fraction",),
            city_mask=city_mask,
        )
        records.append(
            artifact(
                output_path,
                role="external_worldcover_built_fraction",
                source_year=year,
                source_asset=asset_id,
            )
        )
        print(f"worldcover_external:{year}:complete", flush=True)
    manifest = {
        "schema": "gwm.abu_dhabi_worldcover_validation_inputs.v1",
        "benchmark_id": "abu-dhabi-land-use-v1",
        "created_at": datetime.now(UTC).isoformat(),
        "status": "complete",
        "earth_engine_project": project,
        "grid_profile_sha256": sha256_file(grid_profile_path),
        "boundary_sha256": sha256_file(boundary_path),
        "source_assets": {str(year): asset for year, asset in ASSETS.items()},
        "source_class": {"value": 50, "name": "built-up"},
        "derivation": (
            "Per-cell indicator(Map == 50), aggregated to the frozen 100 m "
            "grid with Earth Engine reduceResolution(mean, maxPixels=1024)."
        ),
        "interpretation": "independent_public_product_diagnostic_not_ground_truth",
        "known_confounds": [
            "WorldCover 2020 v1.0 and 2021 v2.0 are different product versions.",
            "Both WorldCover and Dynamic World ultimately use Sentinel observations.",
            "Neither product is authoritative Abu Dhabi land-use data.",
        ],
        "artifacts": records,
        "wall_seconds": time.perf_counter() - started,
    }
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project", default="ee-zn19860115")
    parser.add_argument("--boundary", type=Path, default=DEFAULT_BOUNDARY)
    parser.add_argument("--grid-profile", type=Path, default=DEFAULT_GRID_PROFILE)
    parser.add_argument("--city-mask", type=Path, default=DEFAULT_CITY_MASK)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    args = parser.parse_args()
    report = materialize(
        project=args.project,
        boundary_path=args.boundary,
        grid_profile_path=args.grid_profile,
        city_mask_path=args.city_mask,
        output_root=args.output,
        manifest_path=args.manifest,
    )
    print(json.dumps({"status": report["status"], "artifacts": len(report["artifacts"])}))


if __name__ == "__main__":
    main()
