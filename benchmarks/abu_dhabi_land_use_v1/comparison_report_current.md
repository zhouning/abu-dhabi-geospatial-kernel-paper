# Abu Dhabi 三模型土地覆盖历史模拟比较

生成时间：2026-09-07T10:25:34.947571+00:00

同一 100 m 网格、需求动作、硬约束和评价器下的三随机种子均值；严格 FoM 与两个零模型均已列出。区间采用 8×8 像元空间块 bootstrap，并提供同一空间块上的模型差值区间。

| 年份 | 模型 | change FoM | change F1 | OA | macro-F1 | demand TV |
|---:|---|---:|---:|---:|---:|---:|
| 2023 | GeoSOS-derived FLUS-style ANN–CA console (author-modified build) | 0.1256 | 0.2273 | 0.9183 | 0.8441 | 0.00283 |
| 2023 | Geospatial Kernel | 0.1961 | 0.3338 | 0.9362 | 0.8499 | 0.00000 |
| 2023 | GeoFM-LDN | 0.1619 | 0.2862 | 0.9316 | 0.8457 | 0.00000 |
| 2023 | Persistence zero model | 0.0000 | 0.0000 | 0.9436 | 0.8684 | 0.03880 |
| 2023 | Random minimum-change zero model | 0.0253 | 0.0543 | 0.9097 | 0.8303 | 0.00000 |
| 2024 | GeoSOS-derived FLUS-style ANN–CA console (author-modified build) | 0.1782 | 0.3071 | 0.8595 | 0.7483 | 0.00538 |
| 2024 | Geospatial Kernel | 0.2529 | 0.4134 | 0.8863 | 0.7670 | 0.00000 |
| 2024 | GeoFM-LDN | 0.2708 | 0.4348 | 0.8905 | 0.7693 | 0.00000 |
| 2024 | Persistence zero model | 0.0000 | 0.0000 | 0.8938 | 0.7907 | 0.08572 |
| 2024 | Random minimum-change zero model | 0.0605 | 0.1249 | 0.8310 | 0.7300 | 0.00000 |

## FLUS feature diagnostics

The 25-feature run shares the Kernel feature family but not its next-state target or projection semantics. It is not a comparable estimator: five of six platform-seed runs collapsed to zero change, including every independent external Windows x86_64 run. The non-collapsed macOS seed-31 result is retained only as a platform-sensitive diagnostic.

| 年份 | 19-feature FoM range | Predicted change range | Observed change | Demand TV range |
|---:|---:|---:|---:|---:|
| 2023 | 0.1071–0.1617 | 1,702–2,417 | 4,500 | 0.0153–0.0305 |
| 2024 | 0.0872–0.1386 | 1,805–2,499 | 8,464 | 0.0615–0.0767 |

## Label-quality diagnostics

The confidence filters below are diagnostics of annual-product quality and selection effects, not independent validation sets or model-skill tests.

| Target year | Full-grid observed changes | Dual-year retained changes | Dual-year retention | Preceding-year-only retained changes | Preceding-year-only retention | Preceding-year-only FoM (FLUS / Kernel / GeoFM-LDN) |
|---:|---:|---:|---:|---:|---:|---:|
| 2023 | 4,500 | 25 | 0.56% | 129 | 2.87% | 0.0000 / 0.0000 / 0.0000 |
| 2024 | 8,464 | 56 | 0.66% | 93 | 1.10% | 0.0040 / 0.0041 / 0.0120 |

## 当前结论

- 2023 单步和 2024 两步开环均同时报告严格多类别 FoM 与旧二值 FoM。
- 持久性与随机可行分配是预先声明的零模型，不得从主模型表中省略。
- 模型比较应读取 JSON 中的 pairwise_bootstrap_95ci，而不是比较两个边际区间是否重叠。
- 置信度筛选会改变被评分的观测变化组成，因此仅作为标签质量与选择效应诊断。
- 这是历史条件分配结果，不是未来政策预测，也不是因果效应证据。
