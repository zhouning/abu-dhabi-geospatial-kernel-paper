# Self-audit for the Geospatial Kernel Abu Dhabi manuscript (legacy checklist)

> **Archive notice:** This checklist predates the recovered-data rerun. The
> unchecked items below are historical blockers and do not describe the current
> revision status. Use `manuscript/paper_self_audit.md` for the current audit.

This historical checklist predates the recovered-data rerun. Use
`manuscript/paper_self_audit.md` for the current evidence status; the current
machine-readable checks are `reproducibility_check.json` and
`output_audit_reproducible.json`.

## Evidence integrity

- [ ] Historical numbers have been regenerated with strict multi-class FoM, spatial-block bootstrap and paired model-difference intervals (blocked until the raster bundle is restored).
- [ ] 2031 planning numbers have been regenerated with the revised independent objective set (blocked until the raster bundle is restored).
- [x] 2027–2031 Geospatial Kernel trajectory numbers match the planning aggregate.
- [ ] The versioned output audit covers the same run as the 45-raster public delivery (the earlier 240-raster audit is a separate 2025–2030 run).
- [x] The nine vector packages and their raster-cell semantics are described without calling them parcels.
- [x] Public data sources and the six-class crosswalk are traceable to the manifests and protocol.
- [x] The neighbourhood-weight sensitivity values are recorded in `neighbourhood_weight_sensitivity.csv` and are described as post-hoc sensitivity, not mechanism proof.

## Claim boundaries

- [x] The manuscript uses “land cover” for the six remote-sensing classes and reserves “land use” for the limitation and deployment discussion.
- [x] The manuscript says that scenario outputs are planner-supplied stress tests, not forecasts.
- [x] The manuscript says that public OSM/WorldCover layers are proxies, not statutory planning or ecological layers.
- [x] The manuscript identifies the GeoFM-LDN 2024 two-step result as a legacy binary-FoM continuity snapshot and withholds any current ranking until strict FoM/bootstrap reruns.
- [x] The manuscript avoids causal language for actions, neighbourhood terms, state writeback and constraints.
- [x] No private database IP, port, username, password or client-only ArcGIS endpoint is included.

## LUP writing checks

- [x] Abstract follows context → gap → approach → quantitative result → implication → boundary.
- [x] Introduction uses a field-scale funnel and states the unresolved systems problem before the contribution.
- [x] Results separate observations from interpretation.
- [x] Discussion names failure modes and unresolved controls.
- [x] Methods include state, action, proposal, projection, features, hyperparameters and evaluation tracks.
- [x] The manuscript no longer contains a Nature-specific broad-audience summary paragraph.
- [x] No unsupported “first”, “unprecedented”, “proves” or universal-performance claims are used.
- [ ] Current PNG figure labels are not yet fully English or vector-ready; redraw before external submission.

## Remaining blockers before submission

1. Regenerate the protocol-required persistence, random-feasible, Markov/CA, action-deleted, action-shuffled, constraint-deleted and spatial-driver-shuffled controls with the strict evaluator.
2. Run an allocator-matched comparison to separate the learned transition proposal from the projection implementation.
3. Add a 30-m or multi-resolution sensitivity analysis if the target journal requires scale robustness.
4. Replace public labels and proxy constraints with authoritative local data before presenting outputs as client-facing planning evidence.
5. The final public repository URL and archival DOI are recorded in the
   submission package: https://github.com/zhouning/abu-dhabi-geospatial-kernel-paper
   and https://doi.org/10.5281/zenodo.22663476. Corresponding-author e-mail,
   author and affiliation metadata are also present.

## Reviewer-risk posture

The strongest defensible version is an algorithmic benchmark and conditional planning study. The manuscript should not be submitted as a validated forecast of Abu Dhabi's legal land-use change until the missing authoritative inputs and negative controls are addressed.
