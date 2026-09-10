# Supplementary Table S7. Net-change limits and conditional model contrasts

Derived from frozen three-seed expanding-window reports; no models were refit. Origin counts are recovered from persistence outputs on the same evaluation mask. M is half the L1 difference between origin and feasible target class totals. O is observed gross change. For strict destination-change FoM, hits cannot exceed min(M,O), and the union contains at least max(M,O) cells, hence FoM <= min(M,O)/max(M,O). This loose count-only upper bound is not necessarily attainable: destination, hard-mask and spatial restrictions can lower the achievable maximum. Feasible counts may differ from observed counts. The bound is not a corrected skill score or a validation reference.

| Product | Target | Observed changes O | Feasible moves M | Count-only FoM upper bound | Kernel FoM |
|---|---:|---:|---:|---:|---:|
| Dynamic World | 2021 | 2429 | 1115 | 0.4590 | 0.2595 |
| Dynamic World | 2022 | 2749 | 793 | 0.2885 | 0.0724 |
| Dynamic World | 2023 | 4500 | 3080 | 0.6844 | 0.2116 |
| Dynamic World | 2024 | 4972 | 3696 | 0.7434 | 0.1816 |
| ArcGIS | 2021 | 3241 | 278 | 0.0858 | 0.0154 |
| ArcGIS | 2022 | 8446 | 6864 | 0.8127 | 0.2775 |
| ArcGIS | 2023 | 4846 | 3223 | 0.6651 | 0.1619 |
| ArcGIS | 2024 | 4197 | 2281 | 0.5435 | 0.1674 |
| ArcGIS | 2025 | 3587 | 849 | 0.2367 | 0.0579 |

## Seed-specific paired spatial-block intervals

Each interval uses the archived 1,000 shared resamples of 8 × 8 cells. Seeds are computational replicates, not independent field samples. Intervals are conditional on each product, fold, seed and mask; no pooled confidence interval or multiple-comparison adjustment is claimed. An interval containing zero does not establish equivalence. Block-size sensitivity and spatial transfer remain untested.

| Product | Target | Contrast | Seed | Median | Lower 95% | Upper 95% | Direction |
|---|---:|---|---:|---:|---:|---:|---|
| Dynamic World | 2021 | Kernel minus FLUS-style | 31 | 0.1057 | 0.0810 | 0.1286 | positive |
| Dynamic World | 2021 | Kernel minus FLUS-style | 47 | 0.0993 | 0.0764 | 0.1235 | positive |
| Dynamic World | 2021 | Kernel minus FLUS-style | 73 | 0.0841 | 0.0616 | 0.1090 | positive |
| Dynamic World | 2021 | GeoFM-LDN minus Kernel | 31 | -0.0249 | -0.0456 | -0.0044 | negative |
| Dynamic World | 2021 | GeoFM-LDN minus Kernel | 47 | -0.0028 | -0.0210 | 0.0177 | includes_zero |
| Dynamic World | 2021 | GeoFM-LDN minus Kernel | 73 | -0.0103 | -0.0290 | 0.0077 | includes_zero |
| Dynamic World | 2022 | Kernel minus FLUS-style | 31 | 0.0088 | -0.0010 | 0.0180 | includes_zero |
| Dynamic World | 2022 | Kernel minus FLUS-style | 47 | 0.0137 | 0.0037 | 0.0248 | positive |
| Dynamic World | 2022 | Kernel minus FLUS-style | 73 | 0.0093 | 0.0002 | 0.0196 | positive |
| Dynamic World | 2022 | GeoFM-LDN minus Kernel | 31 | -0.0178 | -0.0279 | -0.0079 | negative |
| Dynamic World | 2022 | GeoFM-LDN minus Kernel | 47 | -0.0131 | -0.0245 | -0.0022 | negative |
| Dynamic World | 2022 | GeoFM-LDN minus Kernel | 73 | -0.0109 | -0.0214 | -0.0014 | negative |
| Dynamic World | 2023 | Kernel minus FLUS-style | 31 | 0.0987 | 0.0844 | 0.1138 | positive |
| Dynamic World | 2023 | Kernel minus FLUS-style | 47 | 0.0488 | 0.0375 | 0.0599 | positive |
| Dynamic World | 2023 | Kernel minus FLUS-style | 73 | 0.1411 | 0.1253 | 0.1592 | positive |
| Dynamic World | 2023 | GeoFM-LDN minus Kernel | 31 | -0.0420 | -0.0568 | -0.0272 | negative |
| Dynamic World | 2023 | GeoFM-LDN minus Kernel | 47 | -0.0449 | -0.0613 | -0.0289 | negative |
| Dynamic World | 2023 | GeoFM-LDN minus Kernel | 73 | -0.0478 | -0.0637 | -0.0318 | negative |
| Dynamic World | 2024 | Kernel minus FLUS-style | 31 | 0.1107 | 0.0964 | 0.1267 | positive |
| Dynamic World | 2024 | Kernel minus FLUS-style | 47 | 0.0806 | 0.0602 | 0.0997 | positive |
| Dynamic World | 2024 | Kernel minus FLUS-style | 73 | 0.0627 | 0.0491 | 0.0773 | positive |
| Dynamic World | 2024 | GeoFM-LDN minus Kernel | 31 | -0.0170 | -0.0280 | -0.0053 | negative |
| Dynamic World | 2024 | GeoFM-LDN minus Kernel | 47 | -0.0095 | -0.0213 | 0.0030 | includes_zero |
| Dynamic World | 2024 | GeoFM-LDN minus Kernel | 73 | -0.0197 | -0.0320 | -0.0078 | negative |
| ArcGIS | 2021 | Kernel minus FLUS-style | 31 | -0.0698 | -0.0866 | -0.0543 | negative |
| ArcGIS | 2021 | Kernel minus FLUS-style | 47 | -0.0179 | -0.0282 | -0.0059 | negative |
| ArcGIS | 2021 | Kernel minus FLUS-style | 73 | -0.0536 | -0.0671 | -0.0411 | negative |
| ArcGIS | 2021 | GeoFM-LDN minus Kernel | 31 | 0.0173 | 0.0031 | 0.0371 | positive |
| ArcGIS | 2021 | GeoFM-LDN minus Kernel | 47 | 0.0157 | 0.0001 | 0.0399 | positive |
| ArcGIS | 2021 | GeoFM-LDN minus Kernel | 73 | 0.0131 | -0.0010 | 0.0306 | includes_zero |
| ArcGIS | 2022 | Kernel minus FLUS-style | 31 | 0.1537 | 0.1269 | 0.1799 | positive |
| ArcGIS | 2022 | Kernel minus FLUS-style | 47 | -0.0145 | -0.0487 | 0.0181 | includes_zero |
| ArcGIS | 2022 | Kernel minus FLUS-style | 73 | 0.0257 | -0.0134 | 0.0669 | includes_zero |
| ArcGIS | 2022 | GeoFM-LDN minus Kernel | 31 | 0.1588 | 0.1266 | 0.1947 | positive |
| ArcGIS | 2022 | GeoFM-LDN minus Kernel | 47 | 0.1743 | 0.1391 | 0.2084 | positive |
| ArcGIS | 2022 | GeoFM-LDN minus Kernel | 73 | 0.1783 | 0.1418 | 0.2121 | positive |
| ArcGIS | 2023 | Kernel minus FLUS-style | 31 | 0.0596 | 0.0429 | 0.0761 | positive |
| ArcGIS | 2023 | Kernel minus FLUS-style | 47 | 0.0451 | 0.0315 | 0.0590 | positive |
| ArcGIS | 2023 | Kernel minus FLUS-style | 73 | 0.0759 | 0.0495 | 0.1001 | positive |
| ArcGIS | 2023 | GeoFM-LDN minus Kernel | 31 | -0.0020 | -0.0222 | 0.0182 | includes_zero |
| ArcGIS | 2023 | GeoFM-LDN minus Kernel | 47 | -0.0102 | -0.0299 | 0.0078 | includes_zero |
| ArcGIS | 2023 | GeoFM-LDN minus Kernel | 73 | -0.0049 | -0.0249 | 0.0144 | includes_zero |
| ArcGIS | 2024 | Kernel minus FLUS-style | 31 | 0.0502 | 0.0299 | 0.0722 | positive |
| ArcGIS | 2024 | Kernel minus FLUS-style | 47 | 0.0435 | 0.0209 | 0.0637 | positive |
| ArcGIS | 2024 | Kernel minus FLUS-style | 73 | 0.0492 | 0.0286 | 0.0707 | positive |
| ArcGIS | 2024 | GeoFM-LDN minus Kernel | 31 | -0.0461 | -0.0705 | -0.0215 | negative |
| ArcGIS | 2024 | GeoFM-LDN minus Kernel | 47 | -0.0125 | -0.0407 | 0.0127 | includes_zero |
| ArcGIS | 2024 | GeoFM-LDN minus Kernel | 73 | -0.0495 | -0.0756 | -0.0233 | negative |
| ArcGIS | 2025 | Kernel minus FLUS-style | 31 | -0.0053 | -0.0173 | 0.0073 | includes_zero |
| ArcGIS | 2025 | Kernel minus FLUS-style | 47 | 0.0095 | -0.0054 | 0.0262 | includes_zero |
| ArcGIS | 2025 | Kernel minus FLUS-style | 73 | -0.0492 | -0.0669 | -0.0323 | negative |
| ArcGIS | 2025 | GeoFM-LDN minus Kernel | 31 | 0.0020 | -0.0143 | 0.0189 | includes_zero |
| ArcGIS | 2025 | GeoFM-LDN minus Kernel | 47 | 0.0020 | -0.0130 | 0.0174 | includes_zero |
| ArcGIS | 2025 | GeoFM-LDN minus Kernel | 73 | 0.0172 | 0.0003 | 0.0362 | positive |
