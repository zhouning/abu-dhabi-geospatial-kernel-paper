# Supplementary Table S6. Cross-product historical robustness

All values use the frozen Abu Dhabi city 100-m grid. Strict destination-change FoM values are means across seeds 31, 47 and 73. Each expanding-window fold fits only observations available through its origin year; the target label supplies oracle class totals and evaluation only. Dynamic World and the ArcGIS-served Impact Observatory/Microsoft/Esri series retain their product-native label and aggregation-quality semantics, so this is a whole-product-pipeline robustness test rather than an isolated label substitution. Neither product is authoritative local land-use truth.

| Product | Target | Observed change (%) | One-year reversion (%) | Random | FLUS-style | Kernel | GeoFM-LDN |
|---|---:|---:|---:|---:|---:|---:|---:|
| Dynamic World | 2021 | 3.05 | 38.90 | 0.0492 | 0.1627 | 0.2595 | 0.2469 |
| Dynamic World | 2022 | 3.45 | 33.31 | 0.0056 | 0.0618 | 0.0724 | 0.0584 |
| Dynamic World | 2023 | 5.65 | 10.39 | 0.0217 | 0.1150 | 0.2116 | 0.1663 |
| Dynamic World | 2024 | 6.24 | n/a | 0.0312 | 0.0967 | 0.1816 | 0.1661 |
| ArcGIS-served IO/MS/Esri | 2021 | 4.06 | 42.61 | 0.0020 | 0.0625 | 0.0154 | 0.0314 |
| ArcGIS-served IO/MS/Esri | 2022 | 10.59 | 5.53 | 0.0923 | 0.2227 | 0.2775 | 0.4488 |
| ArcGIS-served IO/MS/Esri | 2023 | 6.07 | 20.47 | 0.0471 | 0.1016 | 0.1619 | 0.1561 |
| ArcGIS-served IO/MS/Esri | 2024 | 5.26 | 28.26 | 0.0406 | 0.1197 | 0.1674 | 0.1312 |
| ArcGIS-served IO/MS/Esri | 2025 | 4.50 | n/a | 0.0090 | 0.0731 | 0.0579 | 0.0654 |

## Matched product-difference sensitivity

Intervals are ArcGIS-served minus Dynamic World mean strict FoM for the four paired targets. The 2022 target follows the documented 2021–2022 ArcGIS class-composition break, so the right-hand interval isolates the remaining folds rather than treating its sign as ordinary product variation. A negative value means lower agreement with the ArcGIS-served product under the product-specific pipeline; it does not identify which product is correct.

| Model | All matched targets | All-target interval | Excluding 2022 | Excluding-2022 interval | Direction excluding 2022 |
|---|---|---:|---|---:|---|
| FLUS-style ANN–CA | 2021,2022,2023,2024 | -0.100 to +0.161 | 2021,2023,2024 | -0.100 to +0.023 | mixed remaining folds |
| Geospatial Kernel | 2021,2022,2023,2024 | -0.244 to +0.205 | 2021,2023,2024 | -0.244 to -0.014 | negative in every remaining fold |
| GeoFM-LDN | 2021,2022,2023,2024 | -0.215 to +0.390 | 2021,2023,2024 | -0.215 to -0.010 | negative in every remaining fold |

Same-year agreement between the two harmonized products is reported below. A 100-m cell contributes only where both products have a usable canonical label.

| Year | All-class agreement | Built-class IoU | Dynamic World built (km2) | ArcGIS-served built (km2) |
|---:|---:|---:|---:|---:|
| 2017 | 0.7346 | 0.3938 | 91.05 | 217.25 |
| 2018 | 0.7114 | 0.3328 | 75.82 | 217.34 |
| 2019 | 0.7015 | 0.3501 | 89.07 | 243.03 |
| 2020 | 0.7451 | 0.4193 | 96.42 | 214.29 |
| 2021 | 0.7324 | 0.3765 | 85.53 | 216.07 |
| 2022 | 0.6553 | 0.3200 | 93.59 | 282.14 |
| 2023 | 0.6514 | 0.3750 | 121.21 | 312.88 |
| 2024 | 0.6674 | 0.4494 | 155.98 | 335.57 |

## Product-native annual class stocks

Counts below use each product's own city-valid 100-m state layer, rather than the smaller pairwise common-coverage mask. They describe mapped class prevalence, not verified land-cover change or land-use truth.

| Product | Year | Valid cells | Water | Woody vegetation | Low vegetation | Wetland | Built | Bare |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Dynamic World | 2017 | 79760 | 15390 | 440 | 388 | 974 | 9105 | 53463 |
| Dynamic World | 2018 | 79769 | 14851 | 311 | 363 | 918 | 7582 | 55744 |
| Dynamic World | 2019 | 79759 | 15334 | 440 | 432 | 1009 | 8907 | 53637 |
| Dynamic World | 2020 | 79761 | 15567 | 544 | 480 | 1014 | 9642 | 52514 |
| Dynamic World | 2021 | 79747 | 15534 | 534 | 468 | 1016 | 8553 | 53642 |
| Dynamic World | 2022 | 79765 | 15438 | 496 | 471 | 1011 | 9359 | 52990 |
| Dynamic World | 2023 | 79750 | 15987 | 688 | 461 | 1096 | 12121 | 49397 |
| Dynamic World | 2024 | 79749 | 16062 | 917 | 408 | 1000 | 15598 | 45764 |
| ArcGIS-served IO/MS/Esri | 2017 | 79775 | 20281 | 265 | 2211 | 615 | 21725 | 34678 |
| ArcGIS-served IO/MS/Esri | 2018 | 79775 | 20419 | 262 | 2287 | 484 | 21734 | 34589 |
| ArcGIS-served IO/MS/Esri | 2019 | 79775 | 20226 | 288 | 2333 | 648 | 24303 | 31977 |
| ArcGIS-served IO/MS/Esri | 2020 | 79775 | 20021 | 273 | 2429 | 850 | 21429 | 34773 |
| ArcGIS-served IO/MS/Esri | 2021 | 79775 | 20035 | 293 | 2526 | 792 | 21608 | 34521 |
| ArcGIS-served IO/MS/Esri | 2022 | 79775 | 20423 | 88 | 2739 | 490 | 28214 | 27821 |
| ArcGIS-served IO/MS/Esri | 2023 | 79775 | 21168 | 22 | 2585 | 24 | 31288 | 24688 |
| ArcGIS-served IO/MS/Esri | 2024 | 79775 | 21193 | 16 | 2581 | 20 | 33557 | 22408 |
| ArcGIS-served IO/MS/Esri | 2025 | 79775 | 21180 | 2 | 2694 | 17 | 32731 | 23151 |

The ArcGIS-served sequence has a material class-composition discontinuity: built rises from 21,608 cells in 2021 to 28,214 in 2022, while bare falls from 34,521 to 27,821; woody vegetation and wetland later approach zero. The upstream Living Atlas item does not publish annual model-version identifiers, so this table cannot assign a cause. It is therefore evidence of a product-series break, not evidence that these mapped transitions occurred on the ground.

The full annual 6 x 6 Dynamic World-to-ArcGIS class matrix is supplied as `results_arcgis_v2/paper_refresh/cross_product_class_matrix.csv`. Its rows use the pairwise common-coverage grid; zeros are retained so every annual matrix is explicit.

## Rangeland crosswalk sensitivity

The source service names raw class 11 `Rangeland`. The frozen benchmark maps it to low vegetation. The counterfactual below maps only raw class 11 to bare before the identical 10 x 10 majority aggregation. No model was refit, so this is a label-aggregation sensitivity, not a historical-skill or planning-rank sensitivity.

| Year | Raw rangeland 10-m pixels | Changed 100-m labels | Baseline low vegetation | Alternate low vegetation | Baseline bare | Alternate bare |
|---:|---:|---:|---:|---:|---:|---:|
| 2017 | 233306 | 2265 | 2211 | 23 | 34678 | 36937 |
| 2018 | 242279 | 2346 | 2287 | 16 | 34589 | 36928 |
| 2019 | 247521 | 2384 | 2333 | 16 | 31977 | 34355 |
| 2020 | 257835 | 2484 | 2429 | 12 | 34773 | 37248 |
| 2021 | 268400 | 2589 | 2526 | 12 | 34521 | 37102 |
| 2022 | 289017 | 2792 | 2739 | 24 | 27821 | 30605 |
| 2023 | 275034 | 2652 | 2585 | 15 | 24688 | 27325 |
| 2024 | 272030 | 2653 | 2581 | 15 | 22408 | 25052 |
| 2025 | 282750 | 2754 | 2694 | 21 | 23151 | 25891 |

ArcGIS report SHA-256 (LF-normalized text): `d80d2e8ca640686a27cec24cba2ec178dd40ec654ec5f3fd3a63a12c0eb2bcbd`.

Dynamic World report SHA-256 (LF-normalized text): `bce1043f8478288aff2b5808f3b5521c139c47e265d12a465f928379ff2f7fe8`.
