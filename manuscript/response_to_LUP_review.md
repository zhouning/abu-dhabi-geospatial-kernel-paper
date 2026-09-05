# Response to the LUP review

This is an internal point-by-point response draft for the review dated 5
September 2026. It records what the repository now supports and what remains
outside the evidence boundary. The manuscript remains a public-data benchmark
and scenario-stress-test study, not an official Abu Dhabi land-use forecast.

## Fourth-round major comments

| Review concern | Revision made | Remaining boundary |
|---|---|---|
| Manuscript, tables and PDFs used older numbers | All numerical statements, Table 1, Table 2 and regenerated PDFs now read the current reports. Strict FoM is 0.1256/0.1950/0.1616 in 2023 and 0.1782/0.2520/0.2708 in 2024 for the FLUS-style control, Kernel and GeoFM-LDN, respectively. The obsolete `results/*_current.*` copies were removed. | The canonical current evidence remains under `benchmarks/abu_dhabi_land_use_v1/`; older unversioned reports remain lineage only. |
| `evidence_mode` and report metadata were stale | The historical compiler records `current_evaluator_on_current_reproduced_prediction_rasters`; the planning compiler records its corresponding current-planning mode. The manuscript and availability statements name the current files. | None beyond the stated public-data and locked-environment limits. |
| Kernel was not bitwise identical across platforms | Methods, Results and Data availability now disclose the macOS arm64/Python 3.11/scikit-learn 1.9.0 reference environment. A Windows rerun differs by about 498–592 cells per seed in 2023 and 1,005–1,147 in 2024, approximately 1% of valid cells and about 0.001 strict FoM. The reported paired spatial-block intervals are wider and preserve the reported rankings. | The manifest verifies declared files cross-platform; it does not claim cross-platform bitwise identity of the histogram-gradient learner. |
| Planning objectives were repeatedly called frozen and contained a scenario input | The paper discloses the four-round objective-set history as a limitation. The release objective set is major-road distance, prior-built distance, **newly built** component density and ecological-conversion rate. Vegetation gain is now descriptive only. | Objective selection remains a post-hoc analytical choice, not a preregistered planning preference. |
| Fragmentation allowed built retirement to benefit FLUS | Fragmentation is calculated from newly built cells, not all final built cells. Existing built retirement remains a descriptive model-behaviour diagnostic and is not used to reward a candidate on the frontier. | No fixed-exit counterfactual has been added because it would require a distinct rerun protocol. |
| Pareto mixed scenario selection with model behaviour | The primary frontier compares the three models within each scenario. FLUS-style and Kernel candidates are non-dominated in all three scenarios; GeoFM-LDN is additionally non-dominated in green-priority growth. The global nine-candidate frontier is retained only as lineage. | Pareto membership is conditional on public proxy layers and synthetic scenario actions. |
| Objective sensitivity was qualitative | The Results now state the numerical neighbourhood sensitivity: mean strict FoM changes 0.19997 to 0.20042 in 2023 and 0.26079 to 0.26034 in 2024 across weights 0–0.7. All three declared objective-set sensitivity variants retain the FLUS-style/Kernel structure; GeoFM-LDN remains additionally non-dominated only in green-priority growth when ecological conversion is included. | These are robustness diagnostics on released rasters, not independent planning samples. |
| FLUS was called GeoSOS-FLUS despite no traceable source | All reader-facing labels now use **FLUS-style ANN–CA console (untraceable build)**. The text does not claim equivalence to Liu et al. (2017); the internal `geosos_flus` identifier remains only for artifact compatibility. | Its source commit cannot be recovered from the supplied Mach-O binary. |
| Matched-input FLUS was not attempted | `run_geosos_flus.py` now constructs the 25 Kernel-matched features and exposes `--feature-mode matched_kernel`. The documented run with seed 31 terminated with SIGSEGV in the supplied Mach-O arm64 binary before writing a valid probability surface. It is reported as a blocked binary limitation, not a completed comparison. | A reproducibly sourced, compatible FLUS implementation is needed for an information-matched comparator. |
| Windows reproducibility gate failed after CRLF conversion | The manifest builder now records canonical LF byte lengths for text files, and the gate applies the same normalization to its byte check. Generated-output hashes are schema v2 and also use LF-normalized text bytes/hashes. | Raw binaries and rasters still require exact raw bytes, as intended. |
| High-confidence subset was only a diagnostic | The title, Abstract, Results and Discussion now center the high-confidence result: all models score 0.000 strict FoM in 2023 and the 2024 maximum is 0.0188. The paper is framed as an audit protocol under noisy annual labels rather than a claim of validated model superiority. | An independent 2023–2024 change product or documented manual reference sample is still absent. |

## Figures, tables and artefacts

- Table 1 reports regenerated historical FoM values and the paired model
  contrasts: Kernel minus FLUS-style is 0.0692 [0.0546, 0.0859] in 2023;
  GeoFM-LDN minus Kernel is -0.0333 [-0.0478, -0.0201] in 2023 and 0.0184
  [0.0046, 0.0321] in 2024.
- Table 2 reports all nine 2031 model–scenario candidates, their four release
  objectives, and within-scenario frontier membership.
- Figure 1 was redrawn so that the action arrow terminates at constraint
  projection, and its aligned-state text stays inside the box.
- Figure 2 panel spacing was repaired. Bars retain three-seed population SDs;
  paired spatial-block bootstrap intervals are reported in the table/text and
  machine-readable report rather than incorrectly drawn as seed SDs.
- Figure 3 uses newly built component density and ecological conversion as the
  four release objectives. Vegetation gain is explicitly labelled diagnostic.
- Figure 5 now has a legible scale bar, north arrows and more distinct built
  versus newly built overlays.

## Remaining limitations before resubmission

1. Independent authoritative 2023–2024 change validation, or a documented
   manual reference sample, is necessary to validate whether Dynamic World
   changes represent real Abu Dhabi land-cover change.
2. The FLUS-style binary is a macOS arm64 executable with no recoverable source
   provenance. Its 25-feature run is blocked by a segmentation fault, so the
   comparison remains explicitly unmatched.
3. Authoritative planning, reclamation, infrastructure-capacity, irrigation and
   stakeholder data are unavailable. The 2025–2031 maps must remain scenario
   stress tests, not statutory land-use forecasts.
4. Add an archival DOI, public repository URL and corresponding-author e-mail
   before formal submission.
