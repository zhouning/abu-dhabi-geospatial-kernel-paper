# Response to the LUP review

This document records the revision state after the 4 September 2026 review. It
is an internal response draft, not a cover letter. The complete public-data
bundle and model artifacts are now released in the repository and re-evaluated
under one frozen protocol; authoritative local change-validation data remain
unavailable.

The current code is fail-closed: it repairs the evaluation design and removes
pre-written conclusions. Current versioned reports
and figures now use the released current rasters rather than immutable legacy reports.

## Major comments

| Review concern | Revision made | Remaining status |
|---|---|---|
| Contribution was framed mainly as a software contract | The Introduction and Discussion now define the Kernel as a conditional land-cover allocation core and explicitly limit the contribution to an auditable execution boundary. | A planning-science contribution still requires independent, authoritative Abu Dhabi data. |
| FLUS received fewer features and was run with frozen defaults | The manuscript calls the comparison a pipeline comparison, records the FLUS configuration in `protocol.json`, and removes intrinsic-superiority language. | A matched-input FLUS rerun remains required. |
| GeoFM-LDN implementation was underspecified and not archived | The manuscript now documents the residual dilated CNN, 12-dimensional action encoder, latent dimension, loss, optimizer, patch/batch/epoch settings, checkpoint mode and shared `allocate_action` projection. Source and three checkpoints are released. | Retraining remains optional; default reproduction loads fixed August 2026 checkpoints. |
| Planning objectives were circular or structurally zero | The objective set was frozen before recompilation to major-road distance, prior-built distance, built components per 1,000 valid cells and green-cell gain. Ecological conversion, leapfrog rate and built retirement are descriptive diagnostics. | Recompiled; six of nine candidates are non-dominated (all FLUS and Kernel scenarios). Kernel's fragmentation disadvantage is reported explicitly. |
| Built-component counts were omitted | `planning_metrics` reports component density and the compiler/figure include it as a frozen fragmentation objective. | Recomputed from the released planning rasters; Kernel has 2.92–4.28 components per 1,000 valid cells versus 0.92–1.23 for FLUS. |
| Dynamic World label noise and persistence baseline were hidden | The manuscript discusses label volatility, names persistence and minimum-change controls, and uses strict multi-class FoM as the prespecified primary metric. | Recomputed; the input audit reports 0.5497 mean fraction below confidence 0.5 and 0.3611 median one-year reversion. |
| FoM definition was binary rather than destination-specific | `shared.py` now counts a hit only when the predicted destination class equals the observed destination class and retains wrong destination changes in the denominator. The old binary FoM is retained only as a secondary diagnostic. | Recomputed with strict multi-class FoM and spatial-block intervals. |
| Reclamation and fixed-water treatment were underreported | `protocol.json` now records the feasible-target projection and its effect on observed target totals; the manuscript states that fixed-water constraints exclude reclamation changes from the current skill test. | A coastline/reclamation sensitivity analysis is still needed. |
| Ablations did not support the original causal interpretation | The Discussion now treats action deletion, state-writeback deletion, allocator matching and constraint deletion as mechanism controls rather than causal experiments. | The released report shows action deletion lowers FoM by 0.114/0.171, while constraint deletion raises it by 0.014/0.011 for 2023/2024. |
| The earlier Pareto claim was too strong | The claim that all Kernel candidates occupy the Pareto frontier is withdrawn. Legacy JSON files remain immutable and the current compiler writes an explicit objective version. | Recompiled; six of nine candidates are non-dominated under the frozen balanced objective set. |
| Outputs and audit files mixed 2025–2030 and 2025–2031 runs | The public 2025–2031 scenario/report paths are now the defaults; the audit reads the public scenario report and fails closed when the bundle is absent. | Current `_current` reports and the reproducible output audit are the manuscript evidence; older reports are lineage only. |
| Bootstrap treated autocorrelated pixels as independent | `shared.py` now samples spatial blocks and records block size/count; `paired_model_difference_bootstrap_ci` computes model-A minus model-B intervals from the same resampled blocks. | Recomputed with 8×8 blocks and paired contrasts. |
| Random baseline rewrote stable pixels | `random_feasible_allocation` now preserves compatible mutable cells and randomly pairs only source excesses with target deficits under oracle counts. | Recomputed and included as the random minimum-change control. |
| Compiler embedded uncomputed rankings | `compile_comparison.py` now generates interpretation statements from computed summaries and never writes a ranking before data validation. | The compiler still fails closed when reports or inputs are stale/missing. |
| Formal manuscript included review-process and withdrawn legacy tables | The manuscript source now reports the protocol and evidence boundary without peer-review status language; legacy numerical tables and figures are withheld from the formal text. | A data-complete rerun is still required before submission. |
| Reproducibility claims were too strong | The runtime snapshot, public input bundle, historical/planning rasters, vectors, mechanism report, GeoFM-LDN source/checkpoints and FLUS binary are released. Manifest hashes normalize text line endings for Windows. | Independent authoritative validation, matched-input FLUS and a compatible non-macOS FLUS build remain outside this release. |

## Structure, figures and reporting

- The manuscript is now ordered Introduction → Methods → Results → Discussion,
  followed by availability, declarations and references.
- Figure 1 was redrawn with the action arrow terminating at the projection
  stage, where the current implementation actually applies the action. State
  variables use math-text subscripts and the output is written to the tracked
  `figures/` directory.
- Figure 2 includes explicit visual encodings for persistence and random minimum-change
  controls and was regenerated after the strict-metric run.
- Figure 3 separates the four frozen Pareto objectives from two descriptive
  diagnostics and marks non-dominated candidates; fragmentation is now a target.
- Figure 5 includes a scale bar, north arrow and transition outlines from the
  released ensemble rasters.
- The manuscript no longer presents the old compactness/Pareto tables as final
  evidence; current tables are generated from the revised compiler.

## Remaining limitations before resubmission

1. A matched-input FLUS experiment remains recommended; the released FLUS
   console is a macOS arm64 binary and its original source/version cannot be
   rebuilt from this repository.
2. Validate 2023–2024 built change with an independent product or a documented
   manual sample, including a sensitivity analysis for fixed-water/reclamation
   treatment.
3. Figures 2–5 and the PDF/DOCX have been regenerated. Add the archival DOI and
   corresponding-author e-mail to the submission metadata.
