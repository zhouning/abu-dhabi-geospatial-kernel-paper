# LUP review revision record

This file records how the public-data manuscript responds to the review dated
2026-09-04. It is an internal revision record, not part of the submitted
manuscript.

## Implemented in this revision

- Replaced the Nature-style nonspecialist summary and removed the explicit
  Nature-style status label.
- Shortened the abstract to below 250 words and added the strict-metric and
  independent-validation caveats.
- Changed the prose from a universal model ranking to a conditional pipeline
  comparison because FLUS originally used seven drivers while the Kernel used
  25 state/neighbourhood/context features.
- Added a vendored `data_agent/uwm/geospatial_kernel/runtime.py` snapshot so
  the benchmark no longer imports the runtime from an absolute development
  checkout.
- Added `random_feasible_allocation` and `paired_pixel_bootstrap_ci` to the
  shared evaluator.
- Changed the primary change metric to a strict multi-class FoM: a hit requires
  the correct observed destination class; wrong destination changes remain in
  the denominator. The earlier binary FoM remains a secondary diagnostic.
- Added persistence and random-feasible zero-model outputs to the comparison
  compiler.
- Replaced the circular/structural planning objective set with four diagnostics:
  major-road distance, prior-built distance, built component density and a
  500-m leapfrog rate. Demand totals, ecological conversion and net gains are
  descriptive outcomes only.
- Added a tracked 2025–2031 scenario manifest and changed planning defaults to
  the public 2031 run. The legacy `compact` path ID is retained only for file
  compatibility and is labelled moderate growth.
- Corrected built-component density to use valid-cell normalization, so it is
  not mechanically confounded with the scenario's built-cell total.
- Made the output audit version-aware and fail closed with
  `INCOMPLETE_INPUTS` when source rasters or reports are absent.
- Added literature on CLUE-S, SLEUTH, DINAMICA, FLUS, PLUS, model validation,
  compact-city morphology and the Abu Dhabi Plan 2030 context.
- Corrected the Figure 1 action arrow: the implemented proposal does not read
  the action; the action is applied at constraint projection.
- Added a scale bar, north arrow and transition outlines to the map-rendering
  script.

## Still blocked before a defensible LUP resubmission

1. The current checkout does not contain the complete `artifacts/gee`,
   `artifacts/bundle` or historical prediction rasters. The strict FoM,
   bootstrap intervals, revised morphology metrics and all figures therefore
   cannot be regenerated here.
2. The GeoFM-LDN source code and checkpoint are not in this repository.
3. The external FLUS console, version and matched-input rerun are not
   archived. A fair baseline comparison still requires either a matched-input
   rerun or a deliberately limited claim.
4. No independent 2023–2024 built-area product or manually interpreted sample
   is available. This is mandatory for validating whether Dynamic World label
   changes represent real Abu Dhabi expansion.
5. The GitHub repository is private and has no DOI. The author must provide a
   working corresponding-author email, public release URL and archival DOI.
6. Authoritative planning, reclamation, infrastructure-capacity and irrigation
   data are still unavailable. The 2025–2031 maps must remain stress tests,
   not official land-use forecasts.

## Required rerun command sequence

After restoring the input bundle and model artifacts, run:

```bash
python benchmarks/abu_dhabi_land_use_v1/run_geosos_flus.py
python benchmarks/abu_dhabi_land_use_v1/run_geospatial_kernel.py
python benchmarks/abu_dhabi_land_use_v1/compile_comparison.py
python benchmarks/abu_dhabi_land_use_v1/run_planning_scenarios.py
python benchmarks/abu_dhabi_land_use_v1/compile_planning.py
python benchmarks/abu_dhabi_land_use_v1/audit_outputs.py
python benchmarks/abu_dhabi_land_use_v1/run_mechanism_ablations.py
python benchmarks/abu_dhabi_land_use_v1/reproducibility_check.py
```

Only after these commands complete and an independent change-validation layer
is added should the numerical tables, figures and LUP submission PDF be
reissued.
