# Abu Dhabi 三模型土地覆盖历史模拟比较

生成时间：2026-09-06T15:01:46.195231+00:00

同一 100 m 网格、需求动作、硬约束和评价器下的三随机种子均值；严格 FoM 与两个零模型均已列出。区间采用 8×8 像元空间块 bootstrap，并提供同一空间块上的模型差值区间。

| 年份 | 模型 | change FoM | change F1 | OA | macro-F1 | demand TV |
|---:|---|---:|---:|---:|---:|---:|
| 2023 | GeoSOS-derived FLUS-style ANN–CA console (author-modified build) | 0.1256 | 0.2273 | 0.9183 | 0.8441 | 0.00283 |
| 2023 | Geospatial Kernel | 0.1950 | 0.3321 | 0.9361 | 0.8498 | 0.00000 |
| 2023 | GeoFM-LDN | 0.1616 | 0.2857 | 0.9316 | 0.8457 | 0.00000 |
| 2023 | Persistence zero model | 0.0000 | 0.0000 | 0.9436 | 0.8684 | 0.03880 |
| 2023 | Random minimum-change zero model | 0.0253 | 0.0543 | 0.9097 | 0.8303 | 0.00000 |
| 2024 | GeoSOS-derived FLUS-style ANN–CA console (author-modified build) | 0.1782 | 0.3071 | 0.8595 | 0.7483 | 0.00538 |
| 2024 | Geospatial Kernel | 0.2520 | 0.4122 | 0.8861 | 0.7665 | 0.00000 |
| 2024 | GeoFM-LDN | 0.2708 | 0.4347 | 0.8905 | 0.7693 | 0.00000 |
| 2024 | Persistence zero model | 0.0000 | 0.0000 | 0.8938 | 0.7907 | 0.08572 |
| 2024 | Random minimum-change zero model | 0.0605 | 0.1249 | 0.8310 | 0.7300 | 0.00000 |

## Matched-input FLUS baseline

The 25-feature FLUS run shares the Kernel feature family but not its next-state training target or projection semantics. Three seeds were run; seeds 47 and 73 collapsed to zero-change outputs because current-class one-hot inputs leak the same-year label target. Only seed 31 is retained as the valid matched-input point comparison.

| 年份 | FLUS matched-input strict FoM (seed 31) | Kernel − matched-input raw point contrast | Within-seed block-bootstrap median |
|---:|---:|---:|---:|
| 2023 | 0.1320 | 0.0599 | 0.0595 |
| 2024 | 0.1960 | 0.0558 | 0.0558 |

## 当前结论

- 2023 单步和 2024 两步开环均同时报告严格多类别 FoM 与旧二值 FoM。
- 持久性与随机可行分配是预先声明的零模型，不得从主模型表中省略。
- 模型比较应读取 JSON 中的 pairwise_bootstrap_95ci，而不是比较两个边际区间是否重叠。
- 高置信度标签子集上的 FoM 若较低，必须保留 Dynamic World 标签噪声警告。
- 这是历史条件分配结果，不是未来政策预测，也不是因果效应证据。
