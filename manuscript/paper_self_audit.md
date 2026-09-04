# Self-audit for the Geospatial Kernel Abu Dhabi manuscript

## Evidence integrity

- [x] Historical numbers match `comparison_report.json` means and population standard deviations over seeds 31, 47 and 73.
- [x] 2031 planning numbers match `planning_comparison_report_public_2025_2031.json`.
- [x] 2027–2031 Geospatial Kernel trajectory numbers match the planning aggregate.
- [x] The 240-raster audit and 45-raster delivery counts match `output_audit.json` and `planning_public_2025_2031_delivery_manifest.json`.
- [x] The nine vector packages and their raster-cell semantics are described without calling them parcels.
- [x] Public data sources and the six-class crosswalk are traceable to the manifests and protocol.
- [x] The neighbourhood-weight sensitivity values are recorded in `neighbourhood_weight_sensitivity.csv` and are described as post-hoc sensitivity, not mechanism proof.
- [x] Proposal, runtime, planning-morphology and hard-constraint controls are reported from `artifacts/mechanism_ablations/report.json`.

## Claim boundaries

- [x] The manuscript uses “land cover” for the six remote-sensing classes and reserves “land use” for the limitation and deployment discussion.
- [x] The manuscript says that scenario outputs are planner-supplied stress tests, not forecasts.
- [x] The manuscript says that public OSM/WorldCover layers are proxies, not statutory planning or ecological layers.
- [x] The manuscript reports that GeoFM-LDN wins the 2024 two-step historical FoM, so Geospatial Kernel is not presented as universally best.
- [x] The manuscript avoids causal language for actions, neighbourhood terms, state writeback and constraints.
- [x] No private database IP, port, username, password or client-only ArcGIS endpoint is included.

## Nature-style writing checks

- [x] Abstract follows context → gap → approach → quantitative result → implication → boundary.
- [x] Introduction uses a field-scale funnel and states the unresolved systems problem before the contribution.
- [x] Results separate observations from interpretation.
- [x] Discussion names failure modes and qualifies the completed controls as non-causal public-data stress tests.
- [x] Methods include state, action, proposal, projection, features, hyperparameters and evaluation tracks.
- [x] The manuscript has a broad-audience summary paragraph.
- [x] No unsupported “first”, “unprecedented”, “proves” or universal-performance claims are used.
- [x] Main figures are Python/Matplotlib outputs with English labels, editable SVG/PDF text and 600-dpi PNG/TIFF exports.

## Remaining blockers before submission

1. Confirm the target journal and adapt the manuscript to its current author guide.
2. Add an institutional correspondence e-mail when one is available; no e-mail is invented in this package.
3. Add a 30-m or multi-resolution sensitivity analysis if the target journal requires scale robustness.
4. Replace public labels and proxy constraints with authoritative local data before presenting outputs as client-facing planning evidence.
5. Add the final public repository URL and archival DOI after release review.

## Reviewer-risk posture

The strongest defensible version is an algorithmic benchmark and conditional planning study. The manuscript should not be submitted as a validated forecast of Abu Dhabi's legal land-use change until the missing authoritative inputs and negative controls are addressed.
