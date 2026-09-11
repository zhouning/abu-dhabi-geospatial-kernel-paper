# ArcGIS and Dynamic World product-robustness analysis

This is a whole-public-product-pipeline robustness experiment on the frozen Abu Dhabi city research boundary. It is not validation against authoritative local land-use truth.

## Same-year product agreement

| Year | All-class agreement | Built IoU | Dynamic World built (km²) | ArcGIS built (km²) |
|---:|---:|---:|---:|---:|
| 2017 | 0.735 | 0.394 | 91.05 | 217.25 |
| 2018 | 0.711 | 0.333 | 75.82 | 217.34 |
| 2019 | 0.702 | 0.350 | 89.07 | 243.03 |
| 2020 | 0.745 | 0.419 | 96.42 | 214.29 |
| 2021 | 0.732 | 0.376 | 85.53 | 216.07 |
| 2022 | 0.655 | 0.320 | 93.59 | 282.14 |
| 2023 | 0.651 | 0.375 | 121.21 | 312.88 |
| 2024 | 0.667 | 0.449 | 155.98 | 335.57 |

## Matched one-step model rankings

| Product | Target | Rank 1 | Rank 2 | Rank 3 |
|---|---:|---|---|---|
| arcgis | 2021 | FLUS-style ANN–CA (0.062) | GeoFM-LDN (0.031) | Geospatial Kernel (0.015) |
| arcgis | 2022 | GeoFM-LDN (0.449) | Geospatial Kernel (0.278) | FLUS-style ANN–CA (0.223) |
| arcgis | 2023 | Geospatial Kernel (0.162) | GeoFM-LDN (0.156) | FLUS-style ANN–CA (0.102) |
| arcgis | 2024 | Geospatial Kernel (0.167) | GeoFM-LDN (0.131) | FLUS-style ANN–CA (0.120) |
| arcgis | 2025 | FLUS-style ANN–CA (0.073) | GeoFM-LDN (0.065) | Geospatial Kernel (0.058) |
| dynamic_world | 2021 | Geospatial Kernel (0.259) | GeoFM-LDN (0.247) | FLUS-style ANN–CA (0.163) |
| dynamic_world | 2022 | Geospatial Kernel (0.072) | FLUS-style ANN–CA (0.062) | GeoFM-LDN (0.058) |
| dynamic_world | 2023 | Geospatial Kernel (0.212) | GeoFM-LDN (0.166) | FLUS-style ANN–CA (0.115) |
| dynamic_world | 2024 | Geospatial Kernel (0.182) | GeoFM-LDN (0.166) | FLUS-style ANN–CA (0.097) |

## Planning frontier sensitivity

The planning comparison is conditional on each product-specific origin state and the same released public proxy objectives. Frontier membership is not a forecast-accuracy ranking, and stable membership does not imply unchanged objective trade-offs.

| Scenario | Dynamic World v1 frontier | ArcGIS v2 frontier |
|---|---|---|
| Moderate growth | geosos_flus:compact, geospatial_kernel:compact | geosos_flus:compact, geospatial_kernel:compact |
| Green-priority growth | geosos_flus:ecological_priority, geospatial_kernel:ecological_priority | geosos_flus:ecological_priority, geospatial_kernel:ecological_priority |
| High outward growth | geosos_flus:outward_growth, geospatial_kernel:outward_growth | geosos_flus:outward_growth, geospatial_kernel:outward_growth |

## Interpretation boundary

- Native source pixels are 10 m, but all model comparisons use the frozen 100 m contract.
- Product-native quality terms are retained: Dynamic World maximum temporal-mean probability (a quality proxy) and ArcGIS 100 m majority fraction. The comparison therefore tests complete public-product pipelines rather than an isolated label effect.
- Origin states, oracle actions and origin-year water/wetland masks are product specific; all other protocol settings are matched.
- Oracle target class counts isolate spatial allocation; they are not a deployable demand forecast.
- Differences between product tracks quantify label-product dependence, not which product is correct.
- The 2026-2031 maps remain conditional scenario stress tests until authoritative local validation is available.
