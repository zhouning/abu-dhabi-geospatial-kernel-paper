#!/usr/bin/env python3
"""Materialize the public ArcGIS Sentinel-2 10 m annual land-cover service.

The released Dynamic World inputs remain immutable.  This script writes an
independent ArcGIS-derived input bundle, retaining native 10 m rasters and a
100 m majority-vote model grid aligned with ``grid_profile.json``.  The
service is a categorical land-cover product (not raw imagery), so the
resulting canonical labels are explicitly documented as a second public
remote-sensing product rather than authoritative statutory land use.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import tempfile
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import numpy as np
import geopandas as gpd
import rasterio
import requests
from affine import Affine
from rasterio.features import rasterize

HERE = Path(__file__).resolve().parent
DEFAULT_GRID = HERE / "grid_profile.json"
DEFAULT_BOUNDARY = HERE / "source/abu_dhabi_city_osm_r4479763.geojson"
DEFAULT_OUTPUT = HERE / "artifacts/arcgis_sentinel2_landcover"
SERVICE_URL = (
    "https://ic.imagery1.arcgis.com/arcgis/rest/services/"
    "Sentinel2_10m_LandCover/ImageServer"
)
YEARS = tuple(range(2017, 2026))
RAW_CLASSES = (1, 2, 4, 5, 7, 8, 9, 10, 11)
# Service value -> benchmark value.  0 is nodata/excluded (cloud and snow).
CANONICAL_MAP = {1: 1, 2: 2, 4: 4, 5: 3, 7: 5, 8: 6, 11: 3, 9: 0, 10: 0}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_geometry(path: Path) -> dict[str, Any]:
    boundary = gpd.read_file(path)
    if boundary.empty:
        raise ValueError("boundary_is_empty")
    if boundary.crs is None:
        raise ValueError("boundary_crs_missing")
    boundary = boundary.to_crs("EPSG:32640")
    geometry = boundary.geometry.union_all()
    if geometry.is_empty or not geometry.is_valid:
        raise ValueError("boundary_geometry_invalid")
    return geometry.__geo_interface__


def load_grid(path: Path) -> dict[str, Any]:
    profile = json.loads(path.read_text(encoding="utf-8"))
    return {
        "crs": str(profile["crs"]),
        "width": int(profile["width"]),
        "height": int(profile["height"]),
        "transform": Affine.from_gdal(*profile["transform_gdal"]),
        "bounds": [float(v) for v in profile["bounds"]],
        "resolution_m": int(profile["resolution_m"]),
    }


def request_json(session: requests.Session, url: str, params: dict[str, Any]) -> dict[str, Any]:
    response = session.get(url, params=params, timeout=180)
    response.raise_for_status()
    payload = response.json()
    if "error" in payload:
        raise RuntimeError(f"arcgis_error:{payload['error']}")
    return payload


def catalog(session: requests.Session) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    service = request_json(session, SERVICE_URL, {"f": "json"})
    query = request_json(
        session,
        f"{SERVICE_URL}/query",
        {
            "f": "json",
            "where": "1=1",
            "outFields": "OBJECTID,Name,Year,MinPS,MaxPS",
            "returnGeometry": "false",
            "orderByFields": "Year ASC",
        },
    )
    records = [row["attributes"] for row in query.get("features", [])]
    by_year = {int(row["Year"]): row for row in records if row.get("Year") is not None}
    missing = sorted(set(YEARS) - set(by_year))
    if missing:
        raise RuntimeError(f"arcgis_years_missing:{missing}")
    return service, [by_year[year] for year in YEARS]


def native_grid(grid: dict[str, Any]) -> dict[str, Any]:
    minx, miny, maxx, maxy = grid["bounds"]
    resolution = 10
    width = int(round((maxx - minx) / resolution))
    height = int(round((maxy - miny) / resolution))
    if width * resolution != int(round(maxx - minx)):
        raise ValueError("canonical_bounds_not_aligned_to_10m")
    if height * resolution != int(round(maxy - miny)):
        raise ValueError("canonical_bounds_not_aligned_to_10m")
    return {
        "crs": grid["crs"],
        "width": width,
        "height": height,
        "resolution_m": resolution,
        "transform": Affine(resolution, 0, minx, 0, -resolution, maxy),
        "bounds": [minx, miny, maxx, maxy],
    }


def city_mask(geometry: dict[str, Any], grid: dict[str, Any]) -> np.ndarray:
    return rasterize(
        [(geometry, 1)],
        out_shape=(grid["height"], grid["width"]),
        transform=grid["transform"],
        fill=0,
        all_touched=False,
        dtype="uint8",
    ).astype(bool)


def _write_bytes(path: Path, content: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(prefix=f".{path.name}.", dir=path.parent, delete=False) as handle:
        temporary = Path(handle.name)
        handle.write(content)
    os.replace(temporary, path)


def manifest_path(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(HERE.resolve()))
    except ValueError:
        return str(path.resolve())


def export_tile(
    session: requests.Session,
    *,
    year: int,
    bbox: tuple[float, float, float, float],
    width: int,
    height: int,
    output: Path,
) -> None:
    mosaic_rule = json.dumps(
        {
            "where": f"Year={year}",
            "mosaicMethod": "esriMosaicAttribute",
            "sortField": "Year",
            "ascending": True,
        },
        separators=(",", ":"),
    )
    params = {
        "f": "image",
        "format": "tiff",
        "bbox": ",".join(f"{value:.3f}" for value in bbox),
        "bboxSR": "32640",
        "imageSR": "32640",
        "size": f"{width},{height}",
        "mosaicRule": mosaic_rule,
        "interpolation": "RSP_NearestNeighbor",
    }
    if output.is_file():
        return
    response = session.get(f"{SERVICE_URL}/exportImage", params=params, timeout=900)
    response.raise_for_status()
    if response.headers.get("content-type", "").lower().startswith("application/json"):
        raise RuntimeError(f"arcgis_export_json:{response.text[:500]}")
    _write_bytes(output, response.content)


def validate_native(path: Path, grid: dict[str, Any]) -> None:
    with rasterio.open(path) as dataset:
        if dataset.width != grid["width"] or dataset.height != grid["height"]:
            raise ValueError(f"native_shape_mismatch:{path}:{dataset.shape}")
        if dataset.crs is None or dataset.crs.to_string() != grid["crs"]:
            raise ValueError(f"native_crs_mismatch:{path}:{dataset.crs}")
        if not dataset.transform.almost_equals(grid["transform"], precision=1e-6):
            raise ValueError(f"native_transform_mismatch:{path}:{dataset.transform}")


def write_native_mosaic(
    year: int,
    *,
    tile_paths: list[Path],
    output: Path,
    grid: dict[str, Any],
    mask: np.ndarray,
) -> dict[str, Any]:
    arrays: list[np.ndarray] = []
    profiles: list[dict[str, Any]] = []
    for path in tile_paths:
        with rasterio.open(path) as source:
            arrays.append(source.read(1))
            profiles.append(source.profile.copy())
    # Tiles are exported west-to-east with exactly matching north/south rows.
    if len(arrays) != 2:
        raise ValueError("expected_two_native_tiles")
    data = np.concatenate(arrays, axis=1).astype(np.uint8, copy=False)
    if data.shape != (grid["height"], grid["width"]):
        raise ValueError(f"native_mosaic_shape_mismatch:{data.shape}:{grid['height'], grid['width']}")
    data[~mask] = 0
    profile = profiles[0]
    profile.update(
        driver="GTiff",
        width=grid["width"],
        height=grid["height"],
        count=1,
        dtype="uint8",
        crs=grid["crs"],
        transform=grid["transform"],
        nodata=0,
        compress="deflate",
        predictor=2,
        tiled=True,
        blockxsize=256,
        blockysize=256,
    )
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = output.with_suffix(f".partial.{os.getpid()}.tif")
    with rasterio.open(temporary, "w", **profile) as target:
        target.write(data, 1)
        target.set_band_description(1, "arcgis_sentinel2_landcover_raw_10m")
    os.replace(temporary, output)
    return {"year": year, "path": manifest_path(output), "sha256": sha256_file(output), "shape": list(data.shape)}


def aggregate_100m(
    native_path: Path,
    *,
    output_root: Path,
    year: int,
    canonical_grid: dict[str, Any],
    city_100m: np.ndarray,
) -> list[dict[str, Any]]:
    with rasterio.open(native_path) as source:
        raw = source.read(1)
        reference = source.profile.copy()
    h, w = canonical_grid["height"], canonical_grid["width"]
    if raw.shape != (h * 10, w * 10):
        raise ValueError(f"native_expected_10x_shape:{raw.shape}:{h,w}")
    blocks = raw.reshape(h, 10, w, 10)
    raw_counts = np.stack(
        [(blocks == value).sum(axis=(1, 3)) for value in RAW_CLASSES], axis=0
    )
    winner_index = raw_counts.argmax(axis=0)
    majority_raw = np.asarray(RAW_CLASSES, dtype=np.uint8)[winner_index]
    canonical_native = np.zeros_like(raw, dtype=np.uint8)
    for source_value, target_value in CANONICAL_MAP.items():
        canonical_native[raw == source_value] = target_value
    canonical_blocks = canonical_native.reshape(h, 10, w, 10)
    canonical_classes = np.arange(1, 7, dtype=np.uint8)
    canonical_counts = np.stack(
        [(canonical_blocks == value).sum(axis=(1, 3)) for value in canonical_classes], axis=0
    )
    canonical = canonical_classes[canonical_counts.argmax(axis=0)]
    source_count = (canonical_blocks > 0).sum(axis=(1, 3)).astype(np.float32)
    majority_fraction = np.divide(
        canonical_counts.max(axis=0),
        source_count,
        out=np.zeros_like(source_count, dtype=np.float32),
        where=source_count > 0,
    )
    canonical[source_count == 0] = 0
    canonical[~city_100m] = 0
    majority_raw[~city_100m] = 0
    majority_fraction[~city_100m] = -32768.0
    source_count[~city_100m] = -32768.0
    profile = reference.copy()
    profile.update(
        driver="GTiff",
        width=w,
        height=h,
        crs=canonical_grid["crs"],
        transform=canonical_grid["transform"],
        nodata=0,
        compress="deflate",
        predictor=2,
        tiled=True,
        blockxsize=256,
        blockysize=256,
    )
    records = []
    canonical_path = output_root / "land_cover" / f"land_cover_{year}_100m.tif"
    raw_path = output_root / "land_cover_raw" / f"land_cover_raw_{year}_100m.tif"
    quality_path = output_root / "land_cover" / f"land_cover_quality_{year}_100m.tif"
    for path, values, dtype, nodata, description in (
        (canonical_path, canonical, "uint8", 0, "canonical_land_cover_arcgis"),
        (raw_path, majority_raw, "uint8", 0, "arcgis_majority_raw_class"),
    ):
        path.parent.mkdir(parents=True, exist_ok=True)
        temporary = path.with_suffix(f".partial.{os.getpid()}.tif")
        p = profile.copy()
        p.update(dtype=dtype, count=1, nodata=nodata)
        with rasterio.open(temporary, "w", **p) as target:
            target.write(values.astype(np.uint8), 1)
            target.set_band_description(1, description)
        os.replace(temporary, path)
        records.append({"year": year, "path": manifest_path(path), "sha256": sha256_file(path)})
    quality_path.parent.mkdir(parents=True, exist_ok=True)
    temporary = quality_path.with_suffix(f".partial.{os.getpid()}.tif")
    p = profile.copy()
    p.update(dtype="float32", count=2, nodata=-32768.0)
    with rasterio.open(temporary, "w", **p) as target:
        target.write(majority_fraction, 1)
        target.write(source_count, 2)
        target.set_band_description(1, "majority_fraction_10m_source_pixels")
        target.set_band_description(2, "source_pixel_count")
    os.replace(temporary, quality_path)
    records.append({"year": year, "path": manifest_path(quality_path), "sha256": sha256_file(quality_path)})
    return records


def materialize(*, output_root: Path, years: tuple[int, ...], timeout: int = 900) -> dict[str, Any]:
    grid = load_grid(DEFAULT_GRID)
    native = native_grid(grid)
    geometry = load_geometry(DEFAULT_BOUNDARY)
    mask_10m = city_mask(geometry, native)
    mask_100m = city_mask(geometry, grid)
    output_root = output_root.resolve()
    output_root.mkdir(parents=True, exist_ok=True)
    session = requests.Session()
    session.headers.update({"User-Agent": "abu-dhabi-land-use-v2/1.0 (research reproducibility)"})
    service, records = catalog(session)
    result: dict[str, Any] = {
        "schema": "gwm.arcgis_sentinel2_landcover_materialization.v1",
        "created_at": datetime.now(UTC).isoformat(),
        "service_url": SERVICE_URL,
        "service_name": service.get("name"),
        "service_description": service.get("description"),
        "copyright_text": service.get("copyrightText"),
        "license_info": service.get("licenseInfo"),
        "service_metadata": {
            "band_count": service.get("bandCount"),
            "pixel_type": service.get("pixelType"),
            "pixel_size_x": service.get("pixelSizeX"),
            "pixel_size_y": service.get("pixelSizeY"),
            "spatial_reference": service.get("spatialReference"),
            "allow_copy": service.get("allowCopy"),
            "allow_analysis": service.get("allowAnalysis"),
            "max_image_width": service.get("maxImageWidth"),
            "max_image_height": service.get("maxImageHeight"),
            "time_info": service.get("timeInfo"),
        },
        "catalog": records,
        "years": list(years),
        "source_classes": {str(k): v for k, v in CANONICAL_MAP.items()},
        "native_grid": {
            "crs": native["crs"],
            "width": native["width"],
            "height": native["height"],
            "resolution_m": native["resolution_m"],
            "bounds": native["bounds"],
            "aggregation_to_100m": (
                "map source classes to the six-class benchmark system, then 10x10 "
                "majority vote among usable pixels; ties choose the smallest canonical code"
            ),
        },
        "canonical_grid": {
            "crs": grid["crs"],
            "width": grid["width"],
            "height": grid["height"],
            "resolution_m": grid["resolution_m"],
        },
        "artifacts": [],
    }
    for year in years:
        west, south, east, north = native["bounds"]
        split = west + 40000.0
        tile_specs = [
            (west, south, split, north, 4000, native["height"]),
            (split, south, east, north, native["width"] - 4000, native["height"]),
        ]
        tile_paths = []
        for index, (xmin, ymin, xmax, ymax, width, height) in enumerate(tile_specs, start=1):
            tile_path = output_root / "tiles" / str(year) / f"tile_{index}.tif"
            export_tile(
                session,
                year=year,
                bbox=(xmin, ymin, xmax, ymax),
                width=width,
                height=height,
                output=tile_path,
            )
            validate_native(tile_path, {**native, "width": width, "bounds": [xmin, ymin, xmax, ymax], "transform": Affine(10, 0, xmin, 0, -10, ymax)})
            tile_paths.append(tile_path)
        native_path = output_root / "native" / f"arcgis_sentinel2_landcover_{year}_10m.tif"
        native_record = write_native_mosaic(
            year,
            tile_paths=tile_paths,
            output=native_path,
            grid=native,
            mask=mask_10m,
        )
        model_records = aggregate_100m(
            native_path,
            output_root=output_root,
            year=year,
            canonical_grid=grid,
            city_100m=mask_100m,
        )
        result["artifacts"].append({"year": year, "native": native_record, "model_grid": model_records})
        print(f"arcgis_sentinel2:{year}:complete", flush=True)
    manifest_path = output_root / "manifest.json"
    manifest_path.write_text(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--years", default=",".join(str(year) for year in YEARS))
    args = parser.parse_args()
    years = tuple(int(value) for value in args.years.split(",") if value.strip())
    unknown = sorted(set(years) - set(YEARS))
    if unknown:
        raise ValueError(f"years_outside_arcgis_catalog:{unknown}")
    result = materialize(output_root=args.output, years=years)
    print(json.dumps({"status": "complete", "years": result["years"], "output": str(args.output.resolve())}))


if __name__ == "__main__":
    main()
