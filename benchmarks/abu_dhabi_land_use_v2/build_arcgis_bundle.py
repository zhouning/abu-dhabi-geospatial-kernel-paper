#!/usr/bin/env python3
"""Build the v2 shared action/constraint bundle from ArcGIS annual labels.

The v1 public proxy bundle is used only to recover its explicitly declared
static exclusion component.  Dynamic World water/wetland pixels are removed
from that component before ArcGIS water/wetland labels are added, preventing a
silent reuse of v1 class semantics.
"""

from __future__ import annotations

import hashlib
import json
import os
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import numpy as np
import rasterio

from shared import CLASSES, class_counts, feasible_target_counts

HERE = Path(__file__).resolve().parent
V1 = HERE.parent / "abu_dhabi_land_use_v1"
INPUT_ROOT = HERE / "artifacts/gee"
V1_INPUT_ROOT = V1 / "artifacts/gee"
V1_BUNDLE = V1 / "artifacts/bundle"
CITY_MASK = HERE / "artifacts/abu_dhabi_city_100m_mask.tif"
OUTPUT = HERE / "artifacts/bundle"
YEARS = tuple(range(2017, 2026))


def read(path: Path) -> tuple[np.ndarray, dict[str, Any]]:
    with rasterio.open(path) as dataset:
        return dataset.read(), dataset.profile.copy()


def write(path: Path, data: np.ndarray, profile: dict[str, Any], descriptions: tuple[str, ...], *, nodata: int | float = 0) -> None:
    values = data if data.ndim == 3 else data[None, ...]
    p = profile.copy()
    p.update(count=values.shape[0], dtype=str(values.dtype), nodata=nodata, compress="deflate", tiled=True, blockxsize=256, blockysize=256)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(f".partial.{os.getpid()}.tif")
    with rasterio.open(temporary, "w", **p) as target:
        target.write(values)
        for index, description in enumerate(descriptions, start=1):
            target.set_band_description(index, description)
    os.replace(temporary, path)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def scenario_counts(origin: dict[int, int], *, built_gain: int, green_gain: int, years: tuple[int, ...]) -> dict[str, dict[str, int]]:
    current = dict(origin)
    result: dict[str, dict[str, int]] = {}
    for year in years:
        built_gain = min(built_gain, max(0, current[6]))
        current[6] -= built_gain
        current[5] += built_gain
        green_gain = min(green_gain, max(0, current[6]))
        current[6] -= green_gain
        current[3] += green_gain
        result[str(year)] = {str(key): int(value) for key, value in current.items()}
    return result


def main() -> None:
    city_data, reference = read(CITY_MASK)
    city = city_data[0].astype(bool)
    states = {year: read(INPUT_ROOT / "land_cover" / f"land_cover_{year}_100m.tif")[0][0] for year in YEARS}
    qualities = {year: read(INPUT_ROOT / "land_cover" / f"land_cover_quality_{year}_100m.tif")[0] for year in YEARS}
    v1_states = {year: read(V1_INPUT_ROOT / "land_cover" / f"land_cover_{year}_100m.tif")[0][0] for year in range(2017, 2025)}
    old_hard_2022 = read(V1_BUNDLE / "hard_exclusion_2022_100m.tif")[0][0].astype(bool)
    old_hard_2024 = read(V1_BUNDLE / "hard_exclusion_2024_100m.tif")[0][0].astype(bool)
    static_2022 = old_hard_2022 & ~np.isin(v1_states[2022], (1, 4))
    static_2024 = old_hard_2024 & ~np.isin(v1_states[2024], (1, 4))
    common = city.copy()
    for state in states.values():
        common &= np.isin(state, CLASSES)
    hard = {}
    for year, static in ((2022, static_2022), (2023, static_2024), (2024, static_2024), (2025, static_2024)):
        mask = common & (static | np.isin(states[year], (1, 4)))
        hard[year] = mask
        write(OUTPUT / f"hard_exclusion_{year}_100m.tif", mask.astype(np.uint8), reference, ("hard_exclusion_arcgis_v2",))
    write(OUTPUT / "common_valid_mask_100m.tif", common.astype(np.uint8), reference, ("common_valid_2017_2025_arcgis",))

    actions = []
    for start_year, target_year in ((2023, 2024), (2024, 2025)):
        desired = class_counts(states[target_year], common)
        hard_origin = hard[2023]
        feasible = feasible_target_counts(desired, origin_state=states[2023], valid_mask=common, hard_exclusion_mask=hard_origin)
        reliability = common & (qualities[start_year][0] >= 0.5) & (qualities[target_year][0] >= 0.5)
        reliability_path = OUTPUT / f"reliability_{start_year}_{target_year}_100m.tif"
        write(reliability_path, reliability.astype(np.uint8), reference, ("arcgis_majority_fraction_ge_0_5_both_years",))
        actions.append({
            "schema": "gwm.land_use_demand_action.v2",
            "action_id": f"oracle_allocation_arcgis_{start_year}_{target_year}",
            "source": "observed_arcgis_allocation",
            "start_year": start_year,
            "target_year": target_year,
            "desired_observed_counts": {str(key): int(value) for key, value in desired.items()},
            "feasible_target_counts": {str(key): int(value) for key, value in feasible.items()},
            "hard_exclusion_origin_year": 2023,
            "reliability_mask": str(reliability_path.relative_to(HERE)),
            "model_may_read_reliability_mask": False,
        })
    (OUTPUT / "allocation_actions.json").write_text(json.dumps({"schema": "gwm.land_use_actions.v2", "actions": actions}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    origin_counts = class_counts(states[2025], common)
    specs = {"compact": (500, 50), "ecological_priority": (350, 150), "outward_growth": (1000, 25)}
    scenarios = []
    years = tuple(range(2026, 2032))
    for scenario_id, (built_gain, green_gain) in specs.items():
        scenarios.append({"schema": "gwm.land_use_scenario.v2", "scenario_id": scenario_id, "target_counts_by_year": scenario_counts(origin_counts, built_gain=built_gain, green_gain=green_gain, years=years)})
    scenario_payload = {"schema": "gwm.land_use_scenarios.v2", "origin_year": 2025, "target_years": list(years), "source_state": "arcgis_sentinel2_landcover_2025_100m", "scenarios": scenarios}
    (HERE / "planning_scenarios_arcgis_2025_2031.json").write_text(json.dumps(scenario_payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    manifest = {
        "schema": "gwm.abu_dhabi_land_use_v2_bundle.v1",
        "created_at": datetime.now(UTC).isoformat(),
        "input_source": "ArcGIS Sentinel2_10m_LandCover",
        "observed_years": list(YEARS),
        "canonical_resolution_m": 100,
        "common_valid_pixel_count": int(common.sum()),
        "hard_exclusion_pixel_counts": {str(year): int(mask.sum()) for year, mask in hard.items()},
        "static_exclusion_recovered_from": "v1 hard masks minus v1 Dynamic World water/wetland labels",
        "artifacts": {str(path.relative_to(HERE)): sha256(path) for path in sorted(OUTPUT.glob("*.tif"))},
    }
    (HERE / "bundle_manifest_arcgis.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
