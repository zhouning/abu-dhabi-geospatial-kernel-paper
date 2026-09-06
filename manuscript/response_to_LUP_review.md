# Response to the sixth-round LUP review

This is an internal point-by-point response draft for the review dated 5
September 2026. It records what the repository now supports and what remains
outside the evidence boundary. The manuscript remains a public-data benchmark
and scenario-stress-test study, not an official Abu Dhabi land-use forecast.

## Sixth-round minor revisions

| ID | Review concern | Revision made | Evidence / remaining boundary |
|---|---|---|---|
| R6.1 | Integrated raster-demand errors in the manuscript were stale | Corrected the 2031 ensemble errors to Kernel 60/68/86 and GeoFM-LDN 1,596/1,536/1,174. `reproduce.py` now reads the current planning report and fails closed if these manuscript values drift. | Values are sourced from `planning_comparison_report_public_2025_2031_current.json`; majority-vote ensembles can still differ from seed-level exact-count outputs. |
| R6.2 | Manifest was generated before the final code changes | Added final manifest generation and a final gate to the end of the reproduction flow; current and compatibility audit outputs are regenerated before hashing. | A clean checkout still requires the declared public inputs and model assets; the FLUS binary remains host-specific. |
| R6.3 | 25-feature matched-input FLUS was only run for seed 31 | Re-ran seeds 31, 47 and 73, added the matched-input baseline summaries to the historical comparison and computed paired Kernel-minus-matched-input spatial-block intervals. | Matching features does not match the learning target or projection semantics. |
| R6.4 | 13-feature result was not mechanistically explained | Methods and Discussion now describe same-year current-class identity leakage, near-zero ANN RMSE and the resulting no-change CA output. | This is a diagnostic of a mismatched static-suitability task, not evidence that the Kernel or FLUS should predict no change. |
| R6.5 | Cross-platform claim omitted architecture and x86_64 limitation | Linux report now records `platform.machine()` as arm64; manuscript states the comparison is same-architecture and discloses earlier x86_64 differences as not independently characterised. | The result is not a universal bitwise-identity claim. |
| R6.6 | `output_audit.json` was described as legacy | The current run writes `output_audit.json` and copies it to `output_audit_reproducible.json` for compatibility; the manuscript and README now use the current-file wording. | Both files are generated from the same audit invocation. |

## Fifth-round major comments

| ID | Review concern | Revision made | Evidence / remaining boundary |
|---|---|---|---|
| R5.1 | Neighbourhood-weight values were old binary FoM but labelled strict FoM | Recomputed the complete weight scan at 0, 0.175, 0.35 and 0.7 with the strict destination-correct multi-class evaluator. The manuscript now reports 0.19598–0.19472 for 2023 and 0.25280–0.25130 for 2024 and points to Supplementary Table S2. | Seed-level values and the full report are in `artifacts/mechanism_ablations/neighbourhood_weight_sensitivity_report.json` and the synchronized CSV files. This remains a post-hoc diagnostic, not a causal estimate. |
| R5.2 | Ecological conversion created a structural-zero Pareto advantage | Removed ecological conversion from the release objective set v6. It remains a descriptive public-data pressure proxy. The manuscript explicitly states that GeoFM-LDN's former non-dominated status was a structural-zero artefact and that it is dominated after removal. | The release objective set is road distance, prior-built distance and union-built component density; membership remains conditional on public proxies and synthetic actions. |
| R5.3 | New-only component count had the wrong fragmentation semantics | Recomputed the planning metrics from the connected components of the union of 2024 built cells and newly built cells. Table 2, Figure 3 and the objective-set sensitivity now use this metric; no model rerun was required because this is raster post-processing. | The former new-only component count is retained only as a diagnostic field in the machine-readable reports. |
| R5.4 | Matched-input FLUS failure lacked evidence | Archived the relative-path command and `read config file error!!!` output, explicitly withdrawing the earlier SIGSEGV interpretation. Corrected absolute-path 13-, 19- and 25-feature runs completed; the 25-feature run now covers seeds 31, 47 and 73 and is included as a separate matched-input baseline. | Matching feature inputs does not match the FLUS same-year suitability target to the Kernel next-state transition target; the original three-seed seven-driver run remains the unmatched control. |
| R5.5 | Cross-platform differences were quoted from the reviewer | Performed an author-run Linux comparison of the six released Kernel rasters (three seeds × two target years). All categorical arrays matched the macOS reference and all strict-FoM deltas were zero. | `artifacts/cross_platform/linux_vs_macos_kernel_comparison.json` records the exact paths and evaluator values; this does not guarantee identity for arbitrary numerical stacks. |
| R5.6 | Windows gate returned BLOCKED for a non-executable host-specific binary | Changed the gate to report a present but non-executable FLUS binary as `warning_not_executable`; public-input and hash integrity can now pass on such a host while the execution limitation remains visible. | A compatible FLUS build is still required to execute the FLUS baseline on another operating system. |
| R5.7 | Audit protocol was mixed with the Abu Dhabi adapter | Added a separate `Portable audit protocol` subsection covering label confidence tiers, zero models, strict FoM, block bootstrap, structural-zero detection, objective versioning and state–action–constraint traces. The Abu Dhabi implementation follows as a separate adapter description. | Independent authoritative change validation remains unavailable, so the protocol is demonstrated for execution auditability rather than claimed as a validated Abu Dhabi forecast. |

## Fifth-round minor comments

| ID | Review concern | Revision made |
|---|---|---|
| R5.m1 | Figure 3 was not cited in the main text | The planning-results subsection now cites Fig. 3 immediately after the objective and frontier interpretation. |
| R5.m2 | Figure 2 and Figure 3 legends/titles overlapped | Both figures were regenerated and inspected in the final PDF. The legends no longer cover panel titles, and the Figure 2 panel-C spacing is repaired. |
| R5.m3 | Figure 2 error bars were seed SDs despite a bootstrap claim | The caption and Results now state exactly that bars use three-seed population SDs; paired spatial-block bootstrap intervals are reported separately in text, Table 1 discussion and the machine-readable report. |
| R5.m4 | Figure 5 scale and change overlays were difficult to read | The figure was regenerated with a legible 2-km scale bar, north arrows and more distinct built/new-built colours. |
| R5.m5 | Results still said “recovered public-data bundle” | Replaced this with “released public-data bundle.” |
| R5.m6 | The Abstract did not qualify the FLUS build at first mention | The first Abstract mention now reads “FLUS-style ANN–CA console (untraceable build).” |
| R5.m7 | Scenario-design limitations were dispersed | The Discussion now consolidates the lack of official demand basis, irrigation/water budget, reclamation authority, infrastructure capacity and stakeholder input within the public-data scenario-stress-test boundary. |

## Fourth-round major comments

| Review concern | Revision made | Remaining boundary |
|---|---|---|
| Manuscript, tables and PDFs used older numbers | All numerical statements, Table 1, Table 2 and regenerated PDFs now read the current reports. Strict FoM is 0.1256/0.1950/0.1616 in 2023 and 0.1782/0.2520/0.2708 in 2024 for the FLUS-style control, Kernel and GeoFM-LDN, respectively. The obsolete `results/*_current.*` copies were removed. | The canonical current evidence remains under `benchmarks/abu_dhabi_land_use_v1/`; older unversioned reports remain lineage only. |
| `evidence_mode` and report metadata were stale | The historical compiler records `current_evaluator_on_current_reproduced_prediction_rasters`; the planning compiler records its corresponding current-planning mode. The manuscript and availability statements name the current files. | None beyond the stated public-data and locked-environment limits. |
| Kernel was not bitwise identical across platforms | We reran Geospatial Kernel in a Linux container with the same source, inputs and seeds 31, 47 and 73. Across six historical rasters (2023 and 2024 for each seed), the author-run comparison found zero differing categorical cells and zero strict-FoM delta. The exact paths and evaluator outputs are archived in `artifacts/cross_platform/linux_vs_macos_kernel_comparison.json`. | This is a measured result for the released macOS/Linux pair, not a universal bitwise-identity guarantee across arbitrary BLAS, compiler or library versions. |
| Planning objectives were repeatedly called frozen and contained a scenario input | The paper discloses the four-round objective-set history as a limitation. The release objective set is major-road distance, prior-built distance and **union-built** component density. Ecological conversion is now descriptive only, and vegetation gain remains descriptive. | Objective selection remains a post-hoc analytical choice, not a preregistered planning preference. |
| Fragmentation allowed built retirement to benefit FLUS | Fragmentation is now calculated from the union of 2024 built cells and newly built cells. This avoids both the semantic inversion of new-only components and the influence of model-specific built retirement. The former new-only metric is retained only as a diagnostic. | The revised metric is a post-processing change on the released rasters; no model rerun is required. |
| Pareto mixed scenario selection with model behaviour | The primary frontier compares the three models within each scenario. FLUS-style and Kernel candidates are non-dominated in all three scenarios; GeoFM-LDN is dominated after the structural-zero ecological-conversion term is removed. The global nine-candidate frontier is retained only as lineage. | Pareto membership is conditional on public proxy layers and synthetic scenario actions. |
| Objective sensitivity was qualitative | The strict evaluator was rerun at weights 0, 0.175, 0.35 and 0.7. Mean strict FoM ranges from 0.19598 to 0.19472 in 2023 and 0.25280 to 0.25130 in 2024; the full table and seed-level report are archived. All declared objective-set sensitivity variants retain the FLUS-style/Kernel structure. | These are robustness diagnostics on released rasters, not independent planning samples. |
| FLUS was called GeoSOS-FLUS despite no traceable source | All reader-facing labels now use **FLUS-style ANN–CA console (untraceable build)**. The text does not claim equivalence to Liu et al. (2017); the internal `geosos_flus` identifier remains only for artifact compatibility. | Its source commit cannot be recovered from the supplied Mach-O binary. |
| Matched-input FLUS was not attempted | The earlier failure is now identified as a relative-path configuration error (`read config file error`), not a verified segmentation fault. With absolute paths, the supplied Mach-O arm64 console completed the 25-feature matched-input run for seeds 31, 47 and 73 and wrote valid probability surfaces plus 2023/2024 predictions. Two intermediate configurations (13 features: seven drivers plus current-class indicators; 19 features: seven drivers plus neighbourhood fractions) remain archived as diagnostics. Commands, configurations, logs and reports are archived under the corresponding `artifacts/predictions/` directories. | The headline comparison remains the original three-seed seven-driver FLUS-style control; the matched-input baseline is reported separately because matching features does not match the FLUS same-year suitability target to the Kernel next-state transition target or projection semantics. |
| Windows reproducibility gate failed after CRLF conversion | The manifest builder now records canonical LF byte lengths for text files, and the gate applies the same normalization to its byte check. Generated-output hashes are schema v2 and also use LF-normalized text bytes/hashes. A present but non-executable host-specific FLUS binary is now reported as `warning_not_executable`; it no longer blocks the public-input integrity PASS. | Raw binaries and rasters still require exact raw bytes, and a compatible FLUS build remains necessary to execute that baseline on another OS. |
| High-confidence subset was only a diagnostic | The title, Abstract, Results and Discussion now center the high-confidence result: all models score 0.000 strict FoM in 2023 and the 2024 maximum is 0.0188. The paper is framed as an audit protocol under noisy annual labels rather than a claim of validated model superiority. | An independent 2023–2024 change product or documented manual reference sample is still absent. |

## Figures, tables and artefacts

- Table 1 reports regenerated historical FoM values and the paired model
  contrasts: Kernel minus FLUS-style is 0.0692 [0.0546, 0.0859] in 2023;
  GeoFM-LDN minus Kernel is -0.0333 [-0.0478, -0.0201] in 2023 and 0.0184
  [0.0046, 0.0321] in 2024.
- Table 2 reports all nine 2031 model–scenario candidates, their three release
  objectives, and within-scenario frontier membership.
- Figure 1 was redrawn so that the action arrow terminates at constraint
  projection, and its aligned-state text stays inside the box.
- Figure 2 panel spacing was repaired. Bars retain three-seed population SDs;
  paired spatial-block bootstrap intervals are reported in the table/text and
  machine-readable report rather than incorrectly drawn as seed SDs.
- Figure 3 uses union-built component density as the third release objective;
  ecological conversion and vegetation gain are explicitly labelled diagnostics.
- Figure 5 now has a legible scale bar, north arrows and more distinct built
  versus newly built overlays.

## Remaining limitations before resubmission

1. Independent authoritative 2023–2024 change validation, or a documented
   manual reference sample, is necessary to validate whether Dynamic World
   changes represent real Abu Dhabi land-cover change.
2. The FLUS-style binary is a macOS arm64 executable with no recoverable source
   provenance. Its seven-driver run remains the headline unmatched control;
   the 25-feature runs are reported as a separate matched-input baseline but do
   not make the learning tasks or projection semantics equivalent.
3. Authoritative planning, reclamation, infrastructure-capacity, irrigation and
   stakeholder data are unavailable. The 2025–2031 maps must remain scenario
   stress tests, not statutory land-use forecasts.
4. Add an archival DOI, public repository URL and corresponding-author e-mail
   before formal submission.
