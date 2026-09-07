# Supplementary Table S2. Strict neighbourhood-weight sensitivity

Values are means across seeds 31, 47 and 73 under the destination-correct
strict multi-class change Figure of Merit evaluator. This is a post-hoc
robustness diagnostic, not a causal estimate of the neighbourhood term.

| Target year | Neighbourhood weight λ | Mean strict FoM | Population SD |
|---:|---:|---:|---:|
| 2023 | 0.000 | 0.19570436 | 0.00171387 |
| 2023 | 0.175 | 0.19609294 | 0.00176310 |
| 2023 | 0.350 | 0.19608163 | 0.00141267 |
| 2023 | 0.700 | 0.19577652 | 0.00133722 |
| 2024 | 0.000 | 0.25304391 | 0.00139858 |
| 2024 | 0.175 | 0.25296735 | 0.00100364 |
| 2024 | 0.350 | 0.25294629 | 0.00083516 |
| 2024 | 0.700 | 0.25273342 | 0.00118025 |

Machine-readable seed-level values are provided in
`../benchmarks/abu_dhabi_land_use_v1/artifacts/mechanism_ablations/neighbourhood_weight_sensitivity_report.json`.
