# LUP review revision record

This internal record describes the seventh-round revision to the public-data
manuscript. It is not part of the submitted paper.

## Implemented in this revision

- Corrected FLUS provenance: the algorithmic base is the public GeoSOS source;
  the bundled console is an author-modified build archived in
  `FLUS_console_crossplatform` at commit `deb0a54`. The source adds
  `train`/`train-update` entry points and `FLUS_RANDOM_SEED` deterministic
  seeding, and `NOTICE` now records those differences.
- Replaced the 25-feature three-seed matched-input mean and paired interval with
  the valid seed-31 point comparison (0.1320 / 0.1960 FoM; 0.0599 / 0.0558
  Kernel-minus-matched contrasts). Seeds 47 and 73 are reported as explicit
  zero-change identity-leakage degeneracies.
- Added compiler-level zero-change diagnostics and automatic archiving of the
  matched-input ANN logs for seeds 31, 47 and 73, including RMSE and return-code
  metadata. Updated Figure 2 to show the seed-31 diagnostic and revised the
  portable audit protocol accordingly.

- Regenerated and synchronized the manuscript, Table 1, Table 2, figure
  captions, PDF and DOCX with the current reports produced from the released
  rasters: strict FoM is 0.1950 for Kernel in 2023 and 0.2520 in 2024.
- Deleted the obsolete `results/*_current.*` reports so that only the benchmark
  directory contains the current evidence files.
- Corrected report `evidence_mode` fields and made text byte counts canonical
  under LF normalization in the reproducibility manifest and gate. Generated
  output hashes now use the same text normalization.
- Added an author-run Linux comparison of six Kernel historical rasters (three
  seeds × two target years). The categorical arrays were identical to the
  macOS reference rasters and strict-FoM deltas were zero; the comparison JSON
  records the paths and evaluator outputs without generalising to all stacks.
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
- Implemented 13-feature, 19-feature and 25-feature matched-input FLUS modes.
  The earlier failure was a relative-path configuration error. Corrected
  absolute-path 25-feature runs completed for seeds 31, 47 and 73 and are
  reported as a separate matched-input baseline; the 13- and 19-feature runs
  remain seed-31 mechanism diagnostics.
- Made high-confidence subset failure a principal finding: strict FoM is zero
  for all models in 2023 and reaches only 0.0188 at best in 2024.
- Regenerated Figures 1–5: repaired the Figure 1 action arrow/text, Figure 2
  panel spacing, Figure 3 objective labels and legend spacing, and Figure 5
  scale/north-arrow/overlay legibility.
- Corrected the 2031 integrated raster-demand errors to Kernel 60/68/86 and
  GeoFM-LDN 1,596/1,536/1,174, with a reproduction-time manuscript/report
  consistency check.
- Extended the 25-feature matched-input FLUS baseline to seeds 31, 47 and 73;
  added paired Kernel-minus-matched-input spatial-block intervals and explained
  the 13-feature identity-leakage mechanism.
- Recorded the archived Linux runner architecture (arm64), disclosed that the
  author-run comparison is same-architecture, and retained the earlier x86_64
  difference as an uncharacterised cross-architecture limitation.
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
   modifications archived at commit `deb0a54`. The 25-feature matched-input run
   is reported separately because matching
   feature inputs does not match the learning target or projection semantics;
   the headline comparison remains the original three-seed seven-driver
   control.
3. Authoritative planning, reclamation, infrastructure-capacity, irrigation and
   stakeholder data are unavailable. The maps are not official forecasts.
4. Add the archival DOI, repository URL and corresponding-author e-mail before
   submission.
