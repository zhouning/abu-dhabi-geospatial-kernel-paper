# LUP review revision record

This file records how the public-data manuscript responds to the review dated
2026-09-04. It is an internal revision record, not part of the submitted
manuscript.

## Implemented in this revision

The third-round corrections are implemented in the source tree. The complete
public raster bundle, model source/checkpoints, historical and planning output
rasters, change GeoPackages and mechanism-control report are included in the
public release path; authoritative local validation data remain unavailable.

- Replaced independent-pixel bootstrap with an 8 × 8-pixel spatial-block
  bootstrap and added paired model-difference intervals using the same sampled
  blocks for both predictions.
- Replaced the global random permutation control with a score-independent
  minimum-change allocation that preserves compatible cells, changes only
  source excesses to target deficits, and preserves hard masks and exact
  feasible totals.
- Removed hard-coded model-ranking statements from `compile_comparison.py`;
  interpretation text is generated from computed strict FoM values.
- Froze a non-redundant planning objective set before recompilation: major-road
  distance, prior-built distance, built components per 1,000 valid cells and
  green-cell gain. Ecological conversion, 500-m leapfrog rate and built
  retirement remain descriptive diagnostics.
- Corrected the planning runner to import the vendored runtime module directly
  and added a repository-level `requirements.txt`.
- Removed legacy numerical tables, stale figure citations and peer-review
  process language from the formal manuscript source. Legacy files remain in
  the repository only as lineage artefacts.

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
- Added `random_feasible_allocation`, spatial-block bootstrap and paired model
  difference intervals to the shared evaluator.
- Changed the primary change metric to a strict multi-class FoM: a hit requires
  the correct observed destination class; wrong destination changes remain in
  the denominator. The earlier binary FoM remains a secondary diagnostic.
- Added persistence and random minimum-change zero-model outputs to the comparison
  compiler.
- Replaced the circular/structural planning objective set with four frozen,
  non-redundant objectives: major-road accessibility, distance to prior built
  cells (compactness), built components per 1,000 valid cells (fragmentation)
  and green-cell gain (an opposing ecological-balance direction). Ecological
  conversion, 500-m leapfrog rate, built retirement and demand error remain
  descriptive diagnostics because some are structural zeros under exact-count
  projection.
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
- Changed compiler defaults to versioned `*_current.json`/Markdown outputs so
  new runs do not overwrite legacy report lineage; the audit prefers the
  versioned files when present and falls back to legacy files only to report a
  blocked status.
- Added all historical prediction rasters, planning seed/ensemble rasters,
  nine vector change packages and the mechanism-ablation report to the release
  manifest; large binary files use Git LFS where needed.
- Changed input hashes so text files are normalized to LF before SHA-256,
  making the manifest stable under Windows `core.autocrlf=true`.
- Expanded the manuscript with the GeoFM-LDN architecture and fixed-checkpoint
  protocol, high-confidence Dynamic World diagnostics, ensemble demand errors,
  FLUS binary boundary and the action/constraint ablation interpretation.

## Remaining limitations before a defensible LUP resubmission

1. No independent 2023–2024 built-area product or manually interpreted sample
   is available. This is mandatory for validating whether Dynamic World label
   changes represent real Abu Dhabi expansion.
2. The released FLUS console is a macOS arm64 binary; its original source/version
   and a matched-input rerun are not archived. A fair baseline comparison still
   requires a compatible build or a deliberately limited claim.
3. Authoritative planning, reclamation, infrastructure-capacity and irrigation
   data are still unavailable. The 2025–2031 maps must remain stress tests,
   not official land-use forecasts.
4. An archival DOI and corresponding-author e-mail should be added to the
   submission metadata.

## Rerun command sequence used for the current reports

With the local input bundle and model artifacts available, run:

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

The current numerical tables, figures and LUP submission PDF were reissued
after the strict reports and output audit completed. The public bundle now
contains the historical/planning rasters, vector packages, mechanism report,
GeoFM-LDN source and checkpoints. Independent change validation, a
matched-input FLUS comparison, a compatible non-macOS FLUS build and a public
DOI remain recommended before claiming a validated Abu Dhabi forecast.
