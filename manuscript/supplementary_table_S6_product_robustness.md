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

ArcGIS report SHA-256: `d80d2e8ca640686a27cec24cba2ec178dd40ec654ec5f3fd3a63a12c0eb2bcbd`.

Dynamic World report SHA-256: `bce1043f8478288aff2b5808f3b5521c139c47e265d12a465f928379ff2f7fe8`.
