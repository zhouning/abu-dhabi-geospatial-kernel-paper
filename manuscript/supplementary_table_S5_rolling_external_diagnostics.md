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
and built gain between 2020 and 2021. The original Dynamic World-count gain
comparison is structural-zero because Dynamic World built count decreases;
the count-controlled rows use the WorldCover gain count as the action and are
the informative allocation comparison. All comparisons remain external
public-product agreement diagnostics, not authoritative ground-truth validation.
For the two count-controlled action columns, `±` is the three-seed sample SD.

| Built fraction threshold | WorldCover built gain cells | Dynamic World built-gain F1 | Dynamic World 2020 same-year stock F1 | Dynamic World 2021 same-year stock F1 | Kernel 2021 built-stock F1 | Persistence 2021 built-stock F1 | Kernel built-gain F1 (structural-zero) | Kernel F1 (WorldCover-count action, mean ± SD) | Random F1 (WorldCover-count action, mean ± SD) |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 0.05 | 1,802 | 0.0111 | 0.3908 | 0.3501 | 0.3518 | 0.3886 | 0.0000 | 0.0157 ± 0.0008 | 0.0268 ± 0.0058 |
| 0.10 | 1,566 | 0.0135 | 0.3998 | 0.3603 | 0.3625 | 0.4003 | 0.0000 | 0.0228 ± 0.0007 | 0.0277 ± 0.0036 |
| 0.20 | 1,445 | 0.0188 | 0.4186 | 0.3780 | 0.3814 | 0.4209 | 0.0000 | 0.0268 ± 0.0011 | 0.0251 ± 0.0011 |
| 0.30 | 1,511 | 0.0192 | 0.4334 | 0.3924 | 0.3971 | 0.4387 | 0.0000 | 0.0397 ± 0.0007 | 0.0251 ± 0.0075 |

Kernel was below random at 0.05, the 0.10–0.20 differences were not
distinguishable from three-seed variation, and only the 0.30 result was clearly
above random. The low-threshold deficit is consistent with WorldCover cells
that barely exceed 5% built fraction, including sparse or road-edge structure
that Dynamic World does not consistently label as built.

The rolling 2023 row is a one-step forecast with 23 features and training
through 2022, whereas the headline 2023 result uses 25 features and training
through 2021. Rolling 2024 is also one-step, while headline 2024 is a two-step
open-loop rollout; these rows are not directly comparable point estimates.

Source data and machine-readable details are provided in
`artifacts/rolling_backtest/report.json`,
`artifacts/rolling_backtest/paired_spatial_uncertainty.json` and
`artifacts/external_validation/worldcover/diagnostic.json`.
