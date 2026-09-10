# Abu Dhabi land-use v2: ArcGIS Sentinel-2 10 m source

This is an independent iteration of the Abu Dhabi public-data benchmark. The
v1 Dynamic World bundle is not overwritten. v2 uses the public ArcGIS Image
Server `Sentinel2_10m_LandCover` for annual categorical labels from 2017
through 2025, while retaining the native 10 m rasters and an aligned 100 m
model grid.

## What changed

- Temporal endpoint: 2024 → 2025 (the v1 label sequence stopped at 2024).
- Native label resolution: 10 m, exported in two tiles because the service
  limits an export dimension to 4000 pixels.
- Model grid: the existing EPSG:32640, 100 m, 475 × 360 contract. Source
  labels are first mapped to the six-class benchmark semantics and then
  aggregated by 10 × 10 majority vote among usable pixels.
- Drivers: 2025 VIIRS annual radiance and 2025 AlphaEarth annual embedding
  were materialized from Earth Engine. The older terrain and road layers are
  reused as explicitly declared static proxies.
- Models: GeoSOS-derived FLUS-style ANN–CA, Geospatial Kernel and a newly
  trained GeoFM-LDN checkpoint, each with seeds 31, 47 and 73.
- Scenarios: compact, ecological-priority and outward-growth; origin 2025;
  conditional projections 2026–2031.

## Important interpretation boundary

The ArcGIS service is a public global remote-sensing classification product
produced by Impact Observatory, Microsoft and Esri. It is not an Abu Dhabi
government statutory land-use, zoning, cadastral or development-permit
database. The v2 results therefore address freshness and product-resolution
robustness, not authoritative legal land-use prediction. Model rasters remain
100 m; native 10 m data are provided for audit and observed-change mapping.

## Reproduce

```bash
cd /Users/zhouning/abu-dhabi-geospatial-kernel-paper
./.venv-lup/bin/python benchmarks/abu_dhabi_land_use_v2/materialize_arcgis_sentinel2_landcover.py \
  --years 2017,2018,2019,2020,2021,2022,2023,2024,2025
./.venv-lup/bin/python benchmarks/abu_dhabi_land_use_v2/build_arcgis_bundle.py
./.venv-lup/bin/python benchmarks/abu_dhabi_land_use_v2/materialize_gee_2025_drivers.py \
  --products viirs,alphaearth
./.venv-lup/bin/python benchmarks/abu_dhabi_land_use_v2/train_arcgis_geofm_ldn.py \
  --seeds 31,47,73 --epochs 8 --device cpu
./.venv-lup/bin/python benchmarks/abu_dhabi_land_use_v2/run_planning_scenarios.py \
  --models geospatial_kernel,geosos_flus,paper58 --seeds 31,47,73 \
  --start-year 2026 --end-year 2031 \
  --output benchmarks/abu_dhabi_land_use_v2/artifacts/planning_arcgis_2026_2031 \
  --report benchmarks/abu_dhabi_land_use_v2/planning_scenario_report_arcgis_2026_2031.json
./.venv-lup/bin/python benchmarks/abu_dhabi_land_use_v2/analyze_arcgis_v2.py
./.venv-lup/bin/python benchmarks/abu_dhabi_land_use_v2/export_shapefiles_arcgis_v2.py
./.venv-lup/bin/python benchmarks/abu_dhabi_land_use_v2/export_native_10m_observed_change.py
./.venv-lup/bin/python benchmarks/abu_dhabi_land_use_v2/run_arcgis_historical_backtest.py \
  --output benchmarks/abu_dhabi_land_use_v2/artifacts/arcgis_v2_historical_backtest \
  --source-track arcgis --seeds 31,47,73 \
  --target-years 2021,2022,2023,2024,2025 --epochs 8 --batch-size 2 \
  --device cpu --bootstrap-resamples 1000
./.venv-lup/bin/python benchmarks/abu_dhabi_land_use_v2/run_arcgis_historical_backtest.py \
  --output benchmarks/abu_dhabi_land_use_v2/artifacts/dynamic_world_matched_backtest \
  --source-track dynamic_world --seeds 31,47,73 \
  --target-years 2021,2022,2023,2024 --epochs 8 --batch-size 2 \
  --device cpu --bootstrap-resamples 1000
./.venv-lup/bin/python benchmarks/abu_dhabi_land_use_v2/analyze_product_robustness.py
```

The service may change its mosaic catalog or availability. The materializer
records the service metadata, catalog records and SHA-256 hashes in
`artifacts/arcgis_sentinel2_landcover/manifest.json`. For a permanently
reproducible release, archive the downloaded rasters and manifest in a versioned
Zenodo record rather than relying only on the live ImageServer.

## Archived rerun and integrity gate

The v2 archive uses two separate manifests under `reproducibility/`:
`MANIFEST.json` freezes the materialized public inputs, model assets,
configuration and code required to rerun the experiment, whereas
`PUBLICATION_OUTPUTS.json` freezes the reports, Figure 4 source data/artwork and
the released raster/vector products. This distinction prevents a generated map
from being represented as an input while allowing the delivery set to be
checked independently.

```bash
./.venv-lup/bin/python benchmarks/abu_dhabi_land_use_v2/reproducibility/reproducibility_check.py
./.venv-lup/bin/python benchmarks/abu_dhabi_land_use_v2/reproducibility/reproduce.py --device cpu
```

The rerun command intentionally starts from the archived source tiles and
materialized public rasters. It does not re-query the live ArcGIS ImageServer or
Earth Engine, because a later live response would be a new experiment rather
than a reproducible rerun. The first command verifies both pre-existing
manifests; the second rebuilds the outputs and manifests and verifies the
resulting archive. It can take substantial time because it includes the two
three-seed historical backtests and 1,000-resample spatial bootstrap.

## Outputs

- Source manifest and native tiles:
  `artifacts/arcgis_sentinel2_landcover/`
- New shared bundle:
  `artifacts/bundle/`
- New model checkpoints:
  `artifacts/predictions/geofm_ldn_arcgis/`
- Three-model scenario rasters and run report:
  `artifacts/planning_arcgis_2026_2031/` and
  `planning_scenario_report_arcgis_2026_2031.json`
- Ensemble rasters, GeoPackages, Shapefiles and summary tables:
  `results_arcgis_v2/`
- Matched ArcGIS-served and Dynamic World historical reports:
  `artifacts/arcgis_v2_historical_backtest/report.json` and
  `artifacts/dynamic_world_matched_backtest/report.json`
- Paper-refresh tables and synchronized evidence:
  `results_arcgis_v2/paper_refresh/`
- Main Figure 4 and its source data:
  `../../figures/fig04_product_robustness.*` and
  `../../manuscript/source_data_fig04_product_robustness.csv`

The Shapefiles contain raster-cell transition polygons with source/target
classes and years; they are not legal parcels. The native observed 2024→2025
change layer is `vectors/arcgis_observed_2024_2025_native10m.gpkg`.

The matched experiment intentionally retains product-specific annual labels,
origin states, oracle totals, origin-year water/wetland masks and quality
semantics. It matches the boundary, grid, model implementations, seeds,
temporal firewall, evaluator and bootstrap. It is therefore a complete-product-
pipeline robustness test, not an isolated label substitution or a comparison
against authoritative truth.
