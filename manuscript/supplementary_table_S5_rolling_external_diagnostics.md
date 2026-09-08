# Supplementary Table S5 | Rolling-origin and external-product diagnostics

The rolling-origin rows use one-step expanding-window Geospatial Kernel fits
with observed target class totals supplied only to the oracle-demand allocator.
The leakage-controlled fits use 23 features and omit the later road snapshot
from every fold. Values are means across seeds 31, 47 and 73; `±` is the sample standard
deviation across those three computational seeds. The spatial-block intervals
are paired contrasts from 1,000 resamples of 8 × 8 cells (800 m × 800 m).

| Target year | Kernel strict FoM | Random strict FoM | Persistence strict FoM | Kernel − random 95% interval range across seeds | Kernel − persistence 95% interval range across seeds |
|---:|---:|---:|---:|---:|---:|
| 2021 | 0.2595 ± 0.0046 | 0.0524 ± 0.0069 | 0.0000 | [0.1704, 0.2529] | [0.2247, 0.3001] |
| 2022 | 0.0724 ± 0.0020 | 0.0048 ± 0.0016 | 0.0000 | [0.0543, 0.0812] | [0.0572, 0.0873] |
| 2023 | 0.2116 ± 0.0042 | 0.0200 ± 0.0005 | 0.0000 | [0.1686, 0.2126] | [0.1873, 0.2334] |
| 2024 | 0.1816 ± 0.0022 | 0.0323 ± 0.0013 | 0.0000 | [0.1317, 0.1658] | [0.1624, 0.1989] |

WorldCover 2020 v1.0 and 2021 v2.0 built-fraction thresholds were 0.05,
0.10, 0.20 and 0.30. The values below are F1 scores for built stock in 2021
and built gain between 2020 and 2021. The comparison is an external public-
product agreement diagnostic, not authoritative ground-truth validation.

| Built fraction threshold | WorldCover built gain cells | Dynamic World built-gain F1 | Kernel built-stock F1 | Persistence built-stock F1 | Kernel built-gain F1 |
|---:|---:|---:|---:|---:|---:|
| 0.05 | 1,802 | 0.0111 | 0.3518 | 0.3886 | 0.0000 |
| 0.10 | 1,566 | 0.0135 | 0.3625 | 0.4003 | 0.0000 |
| 0.20 | 1,445 | 0.0188 | 0.3814 | 0.4209 | 0.0000 |
| 0.30 | 1,511 | 0.0192 | 0.3971 | 0.4387 | 0.0000 |

Source data and machine-readable details are provided in
`artifacts/rolling_backtest/report.json`,
`artifacts/rolling_backtest/paired_spatial_uncertainty.json` and
`artifacts/external_validation/worldcover/diagnostic.json`.
