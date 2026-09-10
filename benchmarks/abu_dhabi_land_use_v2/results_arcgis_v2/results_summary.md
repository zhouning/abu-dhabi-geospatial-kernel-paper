# Abu Dhabi land-use v2: ArcGIS Sentinel-2 10 m results

The v2 run uses the public ArcGIS Sentinel2_10m_LandCover categorical product for 2017–2025. Native 10 m rasters are retained; the three models run on the existing aligned 100 m contract after canonical class mapping and 10×10 majority aggregation.

## Source comparison

| Year | ArcGIS built cells | Dynamic World built cells | ArcGIS valid cells |
|---:|---:|---:|---:|
| 2017 | 21,725 | 9,105 | 79,775 |
| 2018 | 21,734 | 7,582 | 79,775 |
| 2019 | 24,303 | 8,907 | 79,775 |
| 2020 | 21,429 | 9,642 | 79,775 |
| 2021 | 21,608 | 8,553 | 79,775 |
| 2022 | 28,214 | 9,359 | 79,775 |
| 2023 | 31,288 | 12,121 | 79,775 |
| 2024 | 33,557 | 15,598 | 79,775 |

## Scenario results

| Model | Scenario | Year | Built cells | Changed cells from previous year | Change polygons |
|---|---|---:|---:|---:|---:|
| geosos_flus | compact | 2026 | 33,407 | 1,957 | 1,081 |
| geosos_flus | compact | 2027 | 33,890 | 1,867 | 1,026 |
| geosos_flus | compact | 2028 | 34,307 | 1,604 | 958 |
| geosos_flus | compact | 2029 | 34,707 | 1,318 | 915 |
| geosos_flus | compact | 2030 | 35,209 | 1,289 | 891 |
| geosos_flus | compact | 2031 | 35,634 | 1,116 | 783 |
| geosos_flus | ecological_priority | 2026 | 33,254 | 1,896 | 1,063 |
| geosos_flus | ecological_priority | 2027 | 33,611 | 1,831 | 1,054 |
| geosos_flus | ecological_priority | 2028 | 33,947 | 1,643 | 934 |
| geosos_flus | ecological_priority | 2029 | 34,194 | 1,383 | 912 |
| geosos_flus | ecological_priority | 2030 | 34,475 | 1,235 | 864 |
| geosos_flus | ecological_priority | 2031 | 34,793 | 1,089 | 765 |
| geosos_flus | outward_growth | 2026 | 33,830 | 2,329 | 1,123 |
| geosos_flus | outward_growth | 2027 | 34,827 | 2,286 | 1,163 |
| geosos_flus | outward_growth | 2028 | 35,771 | 1,927 | 1,051 |
| geosos_flus | outward_growth | 2029 | 36,736 | 1,733 | 1,005 |
| geosos_flus | outward_growth | 2030 | 37,688 | 1,565 | 899 |
| geosos_flus | outward_growth | 2031 | 38,660 | 1,467 | 777 |
| geospatial_kernel | compact | 2026 | 33,220 | 532 | 400 |
| geospatial_kernel | compact | 2027 | 33,719 | 543 | 426 |
| geospatial_kernel | compact | 2028 | 34,220 | 550 | 430 |
| geospatial_kernel | compact | 2029 | 34,718 | 547 | 418 |
| geospatial_kernel | compact | 2030 | 35,228 | 562 | 441 |
| geospatial_kernel | compact | 2031 | 35,711 | 525 | 414 |
| geospatial_kernel | ecological_priority | 2026 | 33,067 | 476 | 374 |
| geospatial_kernel | ecological_priority | 2027 | 33,403 | 483 | 396 |
| geospatial_kernel | ecological_priority | 2028 | 33,771 | 507 | 408 |
| geospatial_kernel | ecological_priority | 2029 | 34,131 | 495 | 400 |
| geospatial_kernel | ecological_priority | 2030 | 34,478 | 503 | 412 |
| geospatial_kernel | ecological_priority | 2031 | 34,799 | 471 | 388 |
| geospatial_kernel | outward_growth | 2026 | 33,727 | 1,018 | 692 |
| geospatial_kernel | outward_growth | 2027 | 34,726 | 1,021 | 680 |
| geospatial_kernel | outward_growth | 2028 | 35,714 | 1,012 | 674 |
| geospatial_kernel | outward_growth | 2029 | 36,730 | 1,043 | 660 |
| geospatial_kernel | outward_growth | 2030 | 37,747 | 1,040 | 620 |
| geospatial_kernel | outward_growth | 2031 | 38,750 | 1,028 | 604 |
| paper58 | compact | 2026 | 33,205 | 518 | 236 |
| paper58 | compact | 2027 | 33,667 | 502 | 219 |
| paper58 | compact | 2028 | 34,079 | 446 | 281 |
| paper58 | compact | 2029 | 34,572 | 540 | 281 |
| paper58 | compact | 2030 | 35,033 | 523 | 301 |
| paper58 | compact | 2031 | 35,455 | 485 | 285 |
| paper58 | ecological_priority | 2026 | 33,040 | 453 | 252 |
| paper58 | ecological_priority | 2027 | 33,380 | 457 | 195 |
| paper58 | ecological_priority | 2028 | 33,652 | 386 | 247 |
| paper58 | ecological_priority | 2029 | 33,969 | 453 | 297 |
| paper58 | ecological_priority | 2030 | 34,287 | 499 | 288 |
| paper58 | ecological_priority | 2031 | 34,583 | 470 | 297 |
| paper58 | outward_growth | 2026 | 33,711 | 1,000 | 366 |
| paper58 | outward_growth | 2027 | 34,613 | 920 | 431 |
| paper58 | outward_growth | 2028 | 35,600 | 1,005 | 490 |
| paper58 | outward_growth | 2029 | 36,512 | 940 | 436 |
| paper58 | outward_growth | 2030 | 37,463 | 989 | 414 |
| paper58 | outward_growth | 2031 | 38,480 | 1,047 | 350 |

## Interpretation

The ArcGIS source improves temporal coverage to 2025 and preserves a native 10 m audit layer. The released model predictions remain 100 m because the existing FLUS-style console and GeoFM-LDN contract were not silently changed to claim 10 m predictive accuracy. A future 10 m modelling release requires explicit 10 m retraining, neighbourhood-scale recalibration, and independent validation.
