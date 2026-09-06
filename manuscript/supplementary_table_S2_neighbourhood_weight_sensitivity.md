# Supplementary Table S2. Strict neighbourhood-weight sensitivity

Values are means across seeds 31, 47 and 73 under the destination-correct
strict multi-class change Figure of Merit evaluator. This is a post-hoc
robustness diagnostic, not a causal estimate of the neighbourhood term.

| Target year | Neighbourhood weight λ | Mean strict FoM | Population SD |
|---:|---:|---:|---:|
| 2023 | 0.000 | 0.19597783 | 0.00172388 |
| 2023 | 0.175 | 0.19534963 | 0.00218323 |
| 2023 | 0.350 | 0.19503564 | 0.00230604 |
| 2023 | 0.700 | 0.19472257 | 0.00262389 |
| 2024 | 0.000 | 0.25280145 | 0.00020075 |
| 2024 | 0.175 | 0.25283626 | 0.00060536 |
| 2024 | 0.350 | 0.25203762 | 0.00031882 |
| 2024 | 0.700 | 0.25129586 | 0.00111658 |

Machine-readable seed-level values are provided in
`../benchmarks/abu_dhabi_land_use_v1/artifacts/mechanism_ablations/neighbourhood_weight_sensitivity_report.json`.
