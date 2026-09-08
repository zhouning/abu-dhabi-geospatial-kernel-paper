# LUP review revision record

This internal record describes the eighth-round revision to the public-data
manuscript. It is not part of the submitted paper.

## Eighth-round implementation

- Removed the 25-feature FLUS result from Table 1 and Figure 2. It is no
  longer called a valid seed-31 point comparison or used in a paired Kernel
  contrast. Five of six platform–seed runs collapsed to zero change, including
  all three reviewer-provided Windows x86_64 runs.
- Rebuilt the comparison schema around `matched_input_diagnostic` and
  `neighbourhood_input_diagnostic`. The 19-feature result now reports all three
  macOS seeds, including FoM, change-count and demand-total-variation ranges.
- Added Supplementary Table S3 for the 13-, 19- and 25-feature diagnostics,
  including the provenance-labelled Windows results and the C `rand()`/`srand()`
  platform-random-stream boundary.
- Updated the FLUS console to fail closed with exit code 3 after unreadable
  training, update or simulation input. The Windows pure-ASCII path limitation,
  same-platform-only seed determinism, and author-self-check status of the
  macOS binary SHA are documented in source and manuscript materials.
- Recorded reviewer-provided x86_64 Kernel and FLUS checks as external
  verification. No local Windows or x86_64 Linux raster output is represented
  as author-run reproduction.
- Replaced the incomplete 14-package requirement list with a fully resolved
  50-package lock and reran the complete benchmark in a clean Python 3.11
  environment. The current reports, figures and manuscript use the values that
  this environment reproduces; repeated Kernel runs are byte-identical.

## Prior implementation

- Corrected FLUS provenance: the algorithmic base is the public GeoSOS source;
  the bundled console is an author-modified build archived in
  `FLUS_console_crossplatform` at commit `deb0a54`. The source adds
  `train`/`train-update` entry points and `FLUS_RANDOM_SEED` deterministic
  seeding, and `NOTICE` now records those differences.
- The prior seed-31 point-comparison treatment was superseded in the eighth
  round after cross-platform verification. The 25-feature mode is now retained
  solely as a platform-sensitive identity-leakage diagnostic.
- Added compiler-level zero-change diagnostics and automatic archiving of the
  matched-input ANN logs for seeds 31, 47 and 73, including RMSE and return-code
  metadata. The portable audit protocol was revised accordingly; Figure 2 no
  longer displays the diagnostic as a comparable model bar.

- Regenerated and synchronized the manuscript, Table 1, Table 2, figure
  captions, PDF and DOCX with the current reports produced from the released
  rasters: strict FoM is 0.1961 for Kernel in 2023 and 0.2529 in 2024.
- Deleted the obsolete `results/*_current.*` reports so that only the benchmark
  directory contains the current evidence files.
- Corrected report `evidence_mode` fields and made text byte counts canonical
  under LF normalization in the reproducibility manifest and gate. Generated
  output hashes now use the same text normalization.
- Updated the archived Linux comparison of six Kernel historical rasters (three
  seeds × two target years). Its Python 3.12/scikit-learn 1.8 stack differs
  from the current macOS Python 3.11/scikit-learn 1.9 reference by 498–1,147
  cells (0.62–1.44%) and strict-FoM deltas from −0.0023 to 0.0010; the
  comparison JSON records the paths and evaluator outputs without treating this
  as an architecture-only effect.
- Replaced prior planning objectives with the release v6 set: distance to major
  roads, distance to prior built cells and connected-component density in the
  union of 2024 built and newly built cells. Ecological conversion and
  vegetation gain are descriptive diagnostics only.
- Changed Pareto evaluation from a global nine-candidate comparison to a
  within-scenario comparison of the three model outputs; added three declared
  objective-set sensitivity variants.
- Renamed the reader-facing FLUS baseline to **FLUS-style ANN–CA console
  (author-modified build)** and retained `geosos_flus` solely as a compatibility
  identifier.
- Implemented 13-feature, 19-feature and 25-feature FLUS feature diagnostics.
  The earlier failure was a relative-path configuration error. Corrected
  absolute-path feature runs completed for seeds 31, 47 and 73. The 25-feature
  diagnostic is platform sensitive, and the 19-feature diagnostic underfills
  demand; neither is a headline estimator.
- Made high-confidence subset failure a principal finding: strict FoM is zero
  for all models in 2023 and reaches only 0.0188 at best in 2024.
- Regenerated Figures 1–5: repaired the Figure 1 action arrow/text, Figure 2
  panel spacing, Figure 3 objective labels and legend spacing, and Figure 5
  scale/north-arrow/overlay legibility.
- Corrected the 2031 integrated raster-demand errors to Kernel 8/44/42 and
  GeoFM-LDN 1,580/1,524/1,148, with a reproduction-time manuscript/report
  consistency check.
- Extended every FLUS feature diagnostic to seeds 31, 47 and 73 and explained
  the 13-feature identity-leakage mechanism. The former paired
  Kernel-minus-matched-input interval is withdrawn.
- Recorded the archived Linux runner architecture (arm64) and dependency stack,
  and quantified its difference from the current macOS reference. The reviewer
  Windows evidence remains external and is not relabelled as a local replay.
- Made `output_audit.json` the current audit file and retained
  `output_audit_reproducible.json` only as a compatibility copy. The manifest is
  now rebuilt as the final reproduction step.

## Objective-set history and interpretation

The planning objective set evolved in response to review. It was not
preregistered and is not called prespecified in the paper.

| Version | Objective set | Status |
|---|---|---|
| v1 | DTV, ecological conversion, neighbourhood, roads, prior-built distance, built gain, vegetation gain | Withdrawn: mixed feasibility and scenario/action quantities. |
| v2 | Road distance, prior-built distance, all-built component density, leapfrog rate | Not used for a released planning rerun. |
| v3 | Ecological conversion, road distance, leapfrog rate, built retirement | Withdrawn: outcomes were structurally problematic and comparison scope was unclear. |
| v4 | Road distance, prior-built distance, all-built component density, vegetation gain | Withdrawn: vegetation gain is scenario-supplied and all-built density can reward retirement. |
| v5 | Road distance, prior-built distance, newly built component density, ecological conversion | Superseded: ecological conversion was structurally zero for exact-count allocators and new-only fragmentation had the wrong planning semantics. |
| v6 | Road distance, prior-built distance, union-built component density | Current release objective set; evaluated within scenario and accompanied by strict-FoM and objective-set sensitivity variants. |

The v6 frontier reports a trade-off rather than a winner. Across the three
scenarios, Kernel allocations are closer to roads and pre-existing built cells,
but the union-built morphology metric does not make them uniformly less
fragmented than the FLUS-style control. GeoFM-LDN is dominated in all three
scenarios once the structurally zero ecological-conversion term is removed from
the release objectives. Ecological conversion remains a reported diagnostic.

## Remaining limitations before a defensible LUP resubmission

1. There is no independent 2023–2024 built-area product or manually interpreted
   reference sample.
2. The FLUS-style console is a GeoSOS-derived macOS arm64 binary with author
   modifications archived at commit `deb0a54`. The 25-feature run is a
   platform-sensitive identity-leakage diagnostic. Matching feature inputs does
   not match the learning target or projection semantics; the headline
   comparison remains the original three-seed seven-driver control.
3. Authoritative planning, reclamation, infrastructure-capacity, irrigation and
   stakeholder data are unavailable. The maps are not official forecasts.
4. The archival DOI and final public repository URL are now included in the
   manuscript package; the DOI is `10.5281/zenodo.22663476`.
