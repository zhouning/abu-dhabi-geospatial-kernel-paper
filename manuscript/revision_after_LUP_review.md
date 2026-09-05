# LUP review revision record

This internal record describes the fourth-round revision to the public-data
manuscript. It is not part of the submitted paper.

## Implemented in this revision

- Regenerated and synchronized the manuscript, Table 1, Table 2, figure
  captions, PDF and DOCX with the current reports produced from the released
  rasters: strict FoM is 0.1950 for Kernel in 2023 and 0.2520 in 2024.
- Deleted the obsolete `results/*_current.*` reports so that only the benchmark
  directory contains the current evidence files.
- Corrected report `evidence_mode` fields and made text byte counts canonical
  under LF normalization in the reproducibility manifest and gate. Generated
  output hashes now use the same text normalization.
- Disclosed that the locked macOS arm64 reference rerun is reproducible within
  its environment but a Windows Kernel rerun differs by approximately 1% of
  cells and roughly 0.001 strict FoM.
- Replaced prior planning objectives with the release v5 set: distance to major
  roads, distance to prior built cells, newly built component density and
  ecological-conversion rate. Vegetation gain and all-built component density
  are descriptive diagnostics only.
- Changed Pareto evaluation from a global nine-candidate comparison to a
  within-scenario comparison of the three model outputs; added three declared
  objective-set sensitivity variants.
- Renamed the reader-facing FLUS baseline to **FLUS-style ANN–CA console
  (untraceable build)** and retained `geosos_flus` solely as a compatibility
  identifier.
- Implemented a 25-feature matched-input FLUS mode. The supplied binary
  segfaulted before producing a valid probability surface, which is documented
  rather than represented as a completed experiment.
- Made high-confidence subset failure a principal finding: strict FoM is zero
  for all models in 2023 and reaches only 0.0188 at best in 2024.
- Regenerated Figures 1–5: repaired the Figure 1 action arrow/text, Figure 2
  panel spacing, Figure 3 objectives, and Figure 5 scale/north-arrow/overlay
  legibility.

## Objective-set history and interpretation

The planning objective set evolved in response to review. It was not
preregistered and is not called prespecified in the paper.

| Version | Objective set | Status |
|---|---|---|
| v1 | DTV, ecological conversion, neighbourhood, roads, prior-built distance, built gain, vegetation gain | Withdrawn: mixed feasibility and scenario/action quantities. |
| v2 | Road distance, prior-built distance, all-built component density, leapfrog rate | Not used for a released planning rerun. |
| v3 | Ecological conversion, road distance, leapfrog rate, built retirement | Withdrawn: outcomes were structurally problematic and comparison scope was unclear. |
| v4 | Road distance, prior-built distance, all-built component density, vegetation gain | Withdrawn: vegetation gain is scenario-supplied and all-built density can reward retirement. |
| v5 | Road distance, prior-built distance, newly built component density, ecological conversion | Current release objective set; evaluated within scenario and accompanied by sensitivity variants. |

The v5 frontier reports a trade-off rather than a winner. Across the three
scenarios, Kernel allocations are closer to roads and pre-existing built cells,
but have more newly built components than the FLUS-style control. GeoFM-LDN is
additionally non-dominated only for green-priority growth because it shares the
zero ecological-conversion result while offering intermediate fragmentation.

## Remaining limitations before a defensible LUP resubmission

1. There is no independent 2023–2024 built-area product or manually interpreted
   reference sample.
2. The FLUS-style console remains an untraceable macOS arm64 binary and cannot
   complete a matched-input run with the supplied build.
3. Authoritative planning, reclamation, infrastructure-capacity, irrigation and
   stakeholder data are unavailable. The maps are not official forecasts.
4. Add the archival DOI, repository URL and corresponding-author e-mail before
   submission.
