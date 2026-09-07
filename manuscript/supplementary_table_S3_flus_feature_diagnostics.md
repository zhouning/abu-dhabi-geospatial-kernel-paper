# Supplementary Table S3. FLUS feature-expansion diagnostics

These diagnostics use the author-modified FLUS console with the released
public-data benchmark. They are not comparable headline estimators because they
retain the FLUS same-year suitability target and cellular-automata allocation
semantics rather than the Geospatial Kernel next-state transition and projection
contract.

| Configuration | Archive / evidence platform | Seeds | 2023 strict FoM | 2024 strict FoM | 2023 predicted changes | 2024 predicted changes | 2023 demand TV | 2024 demand TV | Interpretation |
|---|---|---|---:|---:|---:|---:|---:|---:|---|
| Seven drivers + current-class one-hot (13 features) | macOS arm64 | 31, 47, 73 | 0.0000 | 0.0000 | 0 | 0 | 0.0388 | 0.0857 | Same-year class identity leakage; zero-change diagnostic. |
| Seven drivers + neighbourhood fractions (19 features) | macOS arm64 | 31, 47, 73 | 0.1071–0.1617 | 0.0872–0.1386 | 1,702–2,417 | 1,805–2,499 | 0.0153–0.0305 | 0.0615–0.0767 | Partial demand underfill. Observed changes: 4,500 (2023) and 8,464 (2024). |
| Kernel-order feature family (25 features) | macOS arm64 | 31, 47, 73 | 0.0000–0.1320 | 0.0000–0.1960 | 0–2,948 | 0–6,462 | 0.0023–0.0388 | 0.0052–0.0857 | Seeds 47 and 73 collapsed. Seed 31 is diagnostic only. |
| Kernel-order feature family (25 features) | independent external Windows x86_64 verification | 31, 47, 73 | 0.0000 | 0.0000 | 0 | 0 | 0.0388 | 0.0857 | All three seeds collapsed; evidence was reported during anonymous peer review and source rasters are not locally archived. |

The 25-feature mode collapsed in five of six platform–seed runs. The sole
non-collapsed macOS seed-31 result is not reported as a point estimate or as a
Kernel-minus-FLUS paired contrast. `FLUS_RANDOM_SEED` produces deterministic
runs within a fixed platform and build environment, but the console uses C
`rand()`/`srand()` in both ANN sampling and CA roulette draws. The random stream
therefore differs across platform runtimes.

The independent external Windows x86_64 verification also found the
seven-driver control to differ from the macOS output by approximately 2–4% of
valid categorical cells. These external Windows observations are reported here
for the platform-boundary diagnosis only. Their source rasters and logs are not
part of the repository, so they are not used as author-run primary evidence or
as a model-comparison point estimate.
