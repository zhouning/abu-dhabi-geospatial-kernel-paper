#!/usr/bin/env python3
"""Export auditable annual and baseline land-cover change polygons."""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import fiona
import numpy as np
import rasterio
from rasterio.features import shapes
from shapely.geometry import shape

HERE = Path(__file__).resolve().parent
BUNDLE_ROOT = HERE / "artifacts/bundle"
INPUT_ROOT = HERE / "artifacts/gee"
DEFAULT_COMPARISON_REPORT = HERE / "planning_comparison_report_public_2025_2031.json"
DEFAULT_OUTPUT_ROOT = HERE / "artifacts/planning_public_2025_2031/vector"
DEFAULT_MANIFEST = HERE / "planning_public_2025_2031_delivery_manifest.json"
CLASS_LABELS = {
    1: "water",
    2: "woody_vegetation",
    3: "low_vegetation",
    4: "wetland",
    5: "built",
    6: "bare",
}
SCHEMA = {
    "geometry": "Polygon",
    "properties": {
        "model": "str:32",
        "scenario": "str:32",
        "comparison": "str:16",
        "start_year": "int",
        "end_year": "int",
        "from_class": "int",
        "to_class": "int",
        "from_label": "str:32",
        "to_label": "str:32",
        "change_type": "str:80",
        "area_m2": "float",
        "area_ha": "float",
        "pixel_count": "int",
    },
}


def _read(path: Path) -> tuple[np.ndarray, dict[str, Any]]:
    with rasterio.open(path) as dataset:
        return dataset.read(1), dataset.profile.copy()


def _report_path(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(HERE.resolve()))
    except ValueError:
        return f"external/{path.name}"


def _resolve(path: str) -> Path:
    candidate = Path(path)
    return candidate if candidate.is_absolute() else HERE / candidate


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _grid_summary(profile: dict[str, Any]) -> dict[str, Any]:
    transform = profile["transform"]
    pixel_area = abs(transform.a * transform.e - transform.b * transform.d)
    return {
        "crs": str(profile["crs"]),
        "width": int(profile["width"]),
        "height": int(profile["height"]),
        "transform": list(transform)[:6],
        "pixel_area_m2": float(pixel_area),
    }


def _validate_state(
    state: np.ndarray,
    profile: dict[str, Any],
    *,
    reference: dict[str, Any],
    valid: np.ndarray,
    hard: np.ndarray,
    baseline: np.ndarray,
) -> dict[str, Any]:
    aligned = (
        profile["width"] == reference["width"]
        and profile["height"] == reference["height"]
        and profile["crs"] == reference["crs"]
        and profile["transform"] == reference["transform"]
    )
    invalid_class_pixels = int(
        np.count_nonzero(valid & ~np.isin(state, tuple(CLASS_LABELS)))
    )
    nonzero_outside_valid_pixels = int(np.count_nonzero(state[~valid]))
    hard_constraint_violation_pixels = int(
        np.count_nonzero(valid & hard & (state != baseline))
    )
    if not (
        aligned
        and invalid_class_pixels == 0
        and nonzero_outside_valid_pixels == 0
        and hard_constraint_violation_pixels == 0
    ):
        raise ValueError(
            "invalid_ensemble_raster:"
            f"aligned={aligned}:classes={invalid_class_pixels}:"
            f"outside={nonzero_outside_valid_pixels}:hard={hard_constraint_violation_pixels}"
        )
    return {
        "grid_aligned": aligned,
        "invalid_class_pixels": invalid_class_pixels,
        "nonzero_outside_valid_pixels": nonzero_outside_valid_pixels,
        "hard_constraint_violation_pixels": hard_constraint_violation_pixels,
        "class_counts": {
            str(class_id): int(np.count_nonzero(valid & (state == class_id)))
            for class_id in CLASS_LABELS
        },
    }


def _layer_name(comparison: str, start_year: int, end_year: int) -> str:
    prefix = "from" if comparison == "baseline" else "annual"
    return f"{prefix}_{start_year}_{end_year}" if comparison == "baseline" else f"{prefix}_{end_year}"


def _write_change_layer(
    *,
    package: Path,
    layer: str,
    model_id: str,
    scenario_id: str,
    comparison: str,
    start_year: int,
    end_year: int,
    start: np.ndarray,
    end: np.ndarray,
    valid: np.ndarray,
    profile: dict[str, Any],
) -> dict[str, Any]:
    if package.exists():
        raise FileExistsError(f"refusing_to_overwrite_vector_package:{package}")
    transform = profile["transform"]
    pixel_area = abs(transform.a * transform.e - transform.b * transform.d)
    changed = valid & (start != end)
    transitions = np.zeros(start.shape, dtype=np.uint8)
    transitions[changed] = start[changed] * 10 + end[changed]
    feature_count = 0
    feature_pixels = 0
    feature_area_m2 = 0.0
    package.parent.mkdir(parents=True, exist_ok=True)
    with fiona.open(
        package,
        mode="w",
        driver="GPKG",
        layer=layer,
        crs_wkt=profile["crs"].to_wkt(),
        schema=SCHEMA,
    ) as destination:
        for geometry, code in shapes(transitions, mask=changed, transform=transform):
            transition = int(code)
            from_class, to_class = divmod(transition, 10)
            if from_class not in CLASS_LABELS or to_class not in CLASS_LABELS:
                raise ValueError(f"unexpected_transition_code:{transition}")
            geometry_shape = shape(geometry)
            if geometry_shape.is_empty or not geometry_shape.is_valid:
                raise ValueError(f"invalid_generated_change_geometry:{layer}")
            area_m2 = float(geometry_shape.area)
            pixel_count = int(round(area_m2 / pixel_area))
            if pixel_count <= 0 or not np.isclose(area_m2, pixel_count * pixel_area):
                raise ValueError(f"unreconciled_polygon_area:{layer}:{area_m2}:{pixel_count}")
            destination.write(
                {
                    "geometry": geometry,
                    "properties": {
                        "model": model_id,
                        "scenario": scenario_id,
                        "comparison": comparison,
                        "start_year": start_year,
                        "end_year": end_year,
                        "from_class": from_class,
                        "to_class": to_class,
                        "from_label": CLASS_LABELS[from_class],
                        "to_label": CLASS_LABELS[to_class],
                        "change_type": (
                            f"{CLASS_LABELS[from_class]}_to_{CLASS_LABELS[to_class]}"
                        ),
                        "area_m2": area_m2,
                        "area_ha": area_m2 / 10_000.0,
                        "pixel_count": pixel_count,
                    },
                }
            )
            feature_count += 1
            feature_pixels += pixel_count
            feature_area_m2 += area_m2
    changed_pixels = int(changed.sum())
    if feature_pixels != changed_pixels:
        raise ValueError(
            f"polygon_pixel_count_mismatch:{layer}:{feature_pixels}:{changed_pixels}"
        )
    return {
        "layer": layer,
        "comparison": comparison,
        "start_year": start_year,
        "end_year": end_year,
        "changed_pixels": changed_pixels,
        "changed_area_m2": feature_area_m2,
        "feature_count": feature_count,
    }


def _append_change_layer(
    *,
    package: Path,
    layer: str,
    model_id: str,
    scenario_id: str,
    comparison: str,
    start_year: int,
    end_year: int,
    start: np.ndarray,
    end: np.ndarray,
    valid: np.ndarray,
    profile: dict[str, Any],
) -> dict[str, Any]:
    if not package.exists():
        return _write_change_layer(
            package=package,
            layer=layer,
            model_id=model_id,
            scenario_id=scenario_id,
            comparison=comparison,
            start_year=start_year,
            end_year=end_year,
            start=start,
            end=end,
            valid=valid,
            profile=profile,
        )
    transform = profile["transform"]
    pixel_area = abs(transform.a * transform.e - transform.b * transform.d)
    changed = valid & (start != end)
    transitions = np.zeros(start.shape, dtype=np.uint8)
    transitions[changed] = start[changed] * 10 + end[changed]
    feature_count = 0
    feature_pixels = 0
    feature_area_m2 = 0.0
    with fiona.open(
        package,
        mode="w",
        driver="GPKG",
        layer=layer,
        crs_wkt=profile["crs"].to_wkt(),
        schema=SCHEMA,
    ) as destination:
        for geometry, code in shapes(transitions, mask=changed, transform=transform):
            transition = int(code)
            from_class, to_class = divmod(transition, 10)
            geometry_shape = shape(geometry)
            if (
                from_class not in CLASS_LABELS
                or to_class not in CLASS_LABELS
                or geometry_shape.is_empty
                or not geometry_shape.is_valid
            ):
                raise ValueError(f"invalid_generated_change_feature:{layer}")
            area_m2 = float(geometry_shape.area)
            pixel_count = int(round(area_m2 / pixel_area))
            if pixel_count <= 0 or not np.isclose(area_m2, pixel_count * pixel_area):
                raise ValueError(f"unreconciled_polygon_area:{layer}:{area_m2}:{pixel_count}")
            destination.write(
                {
                    "geometry": geometry,
                    "properties": {
                        "model": model_id,
                        "scenario": scenario_id,
                        "comparison": comparison,
                        "start_year": start_year,
                        "end_year": end_year,
                        "from_class": from_class,
                        "to_class": to_class,
                        "from_label": CLASS_LABELS[from_class],
                        "to_label": CLASS_LABELS[to_class],
                        "change_type": (
                            f"{CLASS_LABELS[from_class]}_to_{CLASS_LABELS[to_class]}"
                        ),
                        "area_m2": area_m2,
                        "area_ha": area_m2 / 10_000.0,
                        "pixel_count": pixel_count,
                    },
                }
            )
            feature_count += 1
            feature_pixels += pixel_count
            feature_area_m2 += area_m2
    changed_pixels = int(changed.sum())
    if feature_pixels != changed_pixels:
        raise ValueError(
            f"polygon_pixel_count_mismatch:{layer}:{feature_pixels}:{changed_pixels}"
        )
    return {
        "layer": layer,
        "comparison": comparison,
        "start_year": start_year,
        "end_year": end_year,
        "changed_pixels": changed_pixels,
        "changed_area_m2": feature_area_m2,
        "feature_count": feature_count,
    }


def _audit_package(
    package: Path, *, expected_layers: list[dict[str, Any]], pixel_area: float
) -> None:
    actual_layers = set(fiona.listlayers(package))
    wanted_layers = {row["layer"] for row in expected_layers}
    if actual_layers != wanted_layers:
        raise ValueError(f"unexpected_vector_layers:{package}:{actual_layers}:{wanted_layers}")
    expected_by_layer = {row["layer"]: row for row in expected_layers}
    for layer in sorted(wanted_layers):
        pixels = 0
        features = 0
        with fiona.open(package, layer=layer) as source:
            if source.crs.to_epsg() != 32640:
                raise ValueError(f"unexpected_vector_crs:{package}:{layer}:{source.crs}")
            for feature in source:
                geometry_shape = shape(feature["geometry"])
                properties = feature["properties"]
                if geometry_shape.is_empty or not geometry_shape.is_valid or geometry_shape.area <= 0:
                    raise ValueError(f"invalid_exported_change_geometry:{package}:{layer}")
                count = int(properties["pixel_count"])
                area_m2 = float(properties["area_m2"])
                if count <= 0 or not np.isclose(area_m2, count * pixel_area):
                    raise ValueError(f"invalid_exported_change_area:{package}:{layer}")
                pixels += count
                features += 1
        expected = expected_by_layer[layer]
        if pixels != expected["changed_pixels"] or features != expected["feature_count"]:
            raise ValueError(f"vector_layer_audit_mismatch:{package}:{layer}")


def export(
    *,
    comparison_report: Path,
    output_root: Path,
    manifest_path: Path,
    delivery_years: tuple[int, ...],
    overwrite: bool = False,
) -> dict[str, Any]:
    report = json.loads(comparison_report.read_text(encoding="utf-8"))
    if report.get("status") != "complete":
        raise ValueError(f"comparison_report_not_complete:{report.get('status')}")
    target_years = {int(value) for value in report["target_years"]}
    if not delivery_years or not set(delivery_years).issubset(target_years):
        raise ValueError(f"invalid_delivery_years:{delivery_years}")
    baseline, reference = _read(INPUT_ROOT / "land_cover/land_cover_2024_100m.tif")
    valid, _ = _read(BUNDLE_ROOT / "common_valid_mask_100m.tif")
    hard, _ = _read(BUNDLE_ROOT / "hard_exclusion_2024_100m.tif")
    valid_mask = valid.astype(bool)
    hard_mask = hard.astype(bool)
    grid = _grid_summary(reference)
    if grid["crs"] != "EPSG:32640" or grid["pixel_area_m2"] <= 0:
        raise ValueError(f"unsupported_delivery_grid:{grid}")
    raster_artifacts = []
    vector_packages = []
    ensembles = report["ensembles"]
    for model_id, scenarios in ensembles.items():
        for scenario_id, years in scenarios.items():
            states: dict[int, np.ndarray] = {2024: baseline}
            profiles: dict[int, dict[str, Any]] = {2024: reference}
            for year in delivery_years:
                record = years[str(year)]
                path = _resolve(record["prediction_path"])
                state, profile = _read(path)
                checks = _validate_state(
                    state,
                    profile,
                    reference=reference,
                    valid=valid_mask,
                    hard=hard_mask,
                    baseline=baseline,
                )
                states[year] = state
                profiles[year] = profile
                raster_artifacts.append(
                    {
                        "model_id": model_id,
                        "scenario_id": scenario_id,
                        "year": year,
                        "path": _report_path(path),
                        "bytes": path.stat().st_size,
                        "sha256": _sha256(path),
                        **checks,
                    }
                )
            package = output_root / model_id / scenario_id / "changes.gpkg"
            if package.exists():
                if not overwrite:
                    raise FileExistsError(f"refusing_to_overwrite_vector_package:{package}")
                package.unlink()
                for sidecar in package.parent.glob(f"{package.stem}.*"):
                    if sidecar != package and sidecar.is_file():
                        sidecar.unlink()
            if overwrite and package.parent.exists():
                # The package is the only generated object in this directory;
                # remove stale layer sidecars before rebuilding it.
                for stale in package.parent.glob(f"{package.stem}.*"):
                    if stale.is_file():
                        stale.unlink()
            layers = []
            for year in delivery_years:
                layers.append(
                    _append_change_layer(
                        package=package,
                        layer=_layer_name("baseline", 2024, year),
                        model_id=model_id,
                        scenario_id=scenario_id,
                        comparison="baseline",
                        start_year=2024,
                        end_year=year,
                        start=baseline,
                        end=states[year],
                        valid=valid_mask,
                        profile=profiles[year],
                    )
                )
            for year in delivery_years:
                prior_year = year - 1
                if prior_year not in states:
                    prior_record = years[str(prior_year)]
                    states[prior_year], profiles[prior_year] = _read(
                        _resolve(prior_record["prediction_path"])
                    )
                layers.append(
                    _append_change_layer(
                        package=package,
                        layer=_layer_name("annual", prior_year, year),
                        model_id=model_id,
                        scenario_id=scenario_id,
                        comparison="annual",
                        start_year=prior_year,
                        end_year=year,
                        start=states[prior_year],
                        end=states[year],
                        valid=valid_mask,
                        profile=profiles[year],
                    )
                )
            _audit_package(
                package, expected_layers=layers, pixel_area=float(grid["pixel_area_m2"])
            )
            vector_packages.append(
                {
                    "model_id": model_id,
                    "scenario_id": scenario_id,
                    "path": _report_path(package),
                    "bytes": package.stat().st_size,
                    "sha256": _sha256(package),
                    "layers": layers,
                }
            )
    manifest = {
        "schema": "gwm.abu_dhabi_public_planning_delivery.v1",
        "created_at": datetime.now(UTC).isoformat(),
        "status": "PASS",
        "origin_year": 2024,
        "delivery_years": list(delivery_years),
        "comparison_report": _report_path(comparison_report),
        "grid": grid,
        "class_labels": {str(key): value for key, value in CLASS_LABELS.items()},
        "raster_artifact_count": len(raster_artifacts),
        "vector_package_count": len(vector_packages),
        "raster_artifacts": raster_artifacts,
        "vector_packages": vector_packages,
        "claim_boundary": [
            "Outputs are public-data scenario stress tests, not authoritative land-use forecasts.",
            "2031 demand targets are a documented extension of the prior annual scenario deltas.",
            "Vector polygons represent raster-cell transitions on the 100 m EPSG:32640 grid.",
        ],
    }
    manifest_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--comparison-report", type=Path, default=DEFAULT_COMPARISON_REPORT)
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--delivery-years", default="2027,2028,2029,2030,2031")
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()
    manifest = export(
        comparison_report=args.comparison_report,
        output_root=args.output_root,
        manifest_path=args.manifest,
        delivery_years=tuple(int(value) for value in args.delivery_years.split(",") if value),
        overwrite=args.overwrite,
    )
    print(
        json.dumps(
            {
                "status": manifest["status"],
                "rasters": manifest["raster_artifact_count"],
                "vector_packages": manifest["vector_package_count"],
            },
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
