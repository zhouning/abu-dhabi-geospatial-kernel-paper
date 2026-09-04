# Response to the LUP review

This document records the revision state after the 4 September 2026 review. It
is an internal response draft, not a cover letter. Numerical claims are not
reissued when the raster and checkpoint artifacts needed to recompute them are
absent.

## Major comments

| Review concern | Revision made | Remaining status |
|---|---|---|
| Contribution was framed mainly as a software contract | The Introduction and Discussion now define the Kernel as a conditional land-cover allocation core and explicitly limit the contribution to an auditable execution boundary. | A planning-science contribution still requires independent, authoritative Abu Dhabi data. |
| FLUS received fewer features and was run with frozen defaults | The manuscript calls the comparison a pipeline comparison, records the FLUS configuration in `protocol.json`, and removes intrinsic-superiority language. | A matched-input FLUS rerun remains required. |
| GeoFM-LDN implementation was underspecified and not archived | The manuscript names the architecture and states that it is an internal benchmark implementation; the reproducibility check now reports the missing checkpoint and source explicitly. | Source, checkpoint, training details and selection log must be released or the model must be removed from the comparison. |
| Planning objectives were circular or structurally zero | The revised planning code uses major-road distance, prior-built distance, built-component density and 500-m leapfrog rate as the only Pareto objectives. Demand, ecological conversion, neighbourhood fraction and net gains are descriptive outcomes. | The revised compiler must be rerun from the planning rasters. |
| Built-component counts were omitted | `planning_metrics` now reports component count and normalizes component density by valid cells; the manuscript and figure script reserve a panel for it. | Final values cannot be reported without the raster bundle. |
| Dynamic World label noise and persistence baseline were hidden | The manuscript discusses label volatility, names the persistence and random-feasible controls, and uses strict multi-class FoM as the prespecified primary metric. | Strict FoM, bootstrap intervals and high-confidence sensitivity must be recomputed. |
| FoM definition was binary rather than destination-specific | `shared.py` now counts a hit only when the predicted destination class equals the observed destination class and retains wrong destination changes in the denominator. The old binary FoM is retained only as a secondary diagnostic. | No strict numerical result is claimed until rerun. |
| Reclamation and fixed-water treatment were underreported | `protocol.json` now records the feasible-target projection and its effect on observed target totals; the manuscript states that fixed-water constraints exclude reclamation changes from the current skill test. | A coastline/reclamation sensitivity analysis is still needed. |
| Ablations did not support the original causal interpretation | The Discussion now treats action deletion, state-writeback deletion, allocator matching and constraint deletion as mechanism controls rather than causal experiments. | The complete ablation report must be regenerated with the revised evaluator. |
| The earlier Pareto claim was too strong | The claim that all Kernel candidates occupy the Pareto frontier is withdrawn. Legacy JSON files are marked as stale or withdrawn and the current compiler writes an explicit objective version. | New frontier membership awaits a rerun. |
| Outputs and audit files mixed 2025–2030 and 2025–2031 runs | The public 2025–2031 scenario/report paths are now the defaults; the audit reads the public scenario report and fails closed when the bundle is absent. | Existing 240-raster PASS record is retained only as historical lineage, not current evidence. |
| Reproducibility claims were too strong | The runtime snapshot is vendored, a reproducibility check distinguishes code/manifests/generated inputs/external dependencies, and Data/Code Availability state the missing artifacts. | Public repository release, DOI, GeoFM-LDN artifacts and complete input bundle remain required. |

## Structure, figures and reporting

- The manuscript is now ordered Introduction → Methods → Results → Discussion,
  followed by availability, declarations and references.
- Figure 1 was redrawn with the action arrow terminating at the projection
  stage, where the current implementation actually applies the action. State
  variables use math-text subscripts and the output is written to the tracked
  `figures/` directory.
- Figure 2 reserves explicit visual encodings for persistence and random-feasible
  controls. It must be regenerated after the strict-metric run.
- Figure 3 reserves independent morphology diagnostics and no longer treats
  compactness as a Pareto objective.
- Figure 5 includes a scale bar, north arrow and transition outlines; the
  panels remain unusable for quantitative interpretation until the ensemble
  rasters are restored.
- The manuscript no longer presents the old compactness/Pareto tables as final
  evidence. The retained numbers are clearly labelled legacy artifacts pending
  recomputation.

## Blocking items before resubmission

1. Restore the aligned 2017–2024 raster inputs, masks and all model predictions.
2. Release or archive GeoFM-LDN source, checkpoint and training metadata, and
   record the FLUS software version and complete parameters.
3. Run the strict FoM, persistence/random controls, paired-pixel bootstrap,
   matched-input FLUS experiment and revised planning compiler.
4. Validate 2023–2024 built change with an independent product or a documented
   manual sample, including a sensitivity analysis for fixed-water/reclamation
   treatment.
5. Regenerate Figures 2–5, Tables 1–3 and the PDF/DOCX only after those checks
   pass; then add the public repository URL, DOI and corresponding-author
   e-mail.
