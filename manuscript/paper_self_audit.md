# Self-audit for the Geospatial Kernel Abu Dhabi manuscript

## Evidence integrity

- [x] Historical numbers have been regenerated with the strict multi-class FoM, spatial-block bootstrap and paired model contrasts.
- [x] 2031 planning numbers have been regenerated with the revised independent objective set.
- [x] 2027–2031 Geospatial Kernel trajectory numbers match the planning aggregate.
- [x] The versioned output audit covers the same run as the 45-raster public delivery (the earlier 240-raster audit is a separate 2025–2030 run).
- [x] The nine vector packages and their raster-cell semantics are described without calling them parcels.
- [x] Public data sources and the six-class crosswalk are traceable to the manifests and protocol.
- [x] The neighbourhood-weight sensitivity values are recorded in `neighbourhood_weight_sensitivity.csv` and are described as post-hoc sensitivity, not mechanism proof.
- [x] Proposal, runtime, allocator-matched morphology and hard-constraint controls are available for the current evaluator; causal attribution is not claimed.
- [x] The matched Dynamic World and ArcGIS-served backtests use the same boundary, 100-m grid, models, seeds, temporal firewall, oracle-action rule, evaluator and 1,000-resample spatial bootstrap.
- [x] The product-specific state, action, hard-mask and quality semantics are explicitly retained and described as whole-product-pipeline dependence rather than an isolated label effect.
- [x] Figure 4 includes source data for all four panels; Supplementary Table S6 records the complete result and SHA-256 values of both backtest reports.
- [x] The v2 rerun contract separates immutable inputs/assets/code from cited outputs: `reproducibility/MANIFEST.json` and `reproducibility/PUBLICATION_OUTPUTS.json` are independently verified by `reproducibility_check.py`.

## Claim boundaries

- [x] The manuscript uses “land cover” for the six remote-sensing classes and reserves “land use” for the limitation and deployment discussion.
- [x] The manuscript says that scenario outputs are planner-supplied stress tests, not forecasts.
- [x] The manuscript says that public OSM/WorldCover layers are proxies, not statutory planning or ecological layers.
- [x] The manuscript reports the regenerated strict-FoM ranking and states that it is a conditional pipeline comparison.
- [x] The manuscript does not claim that the ArcGIS-served 10-m product is authoritative or that the model produces 10-m predictions.
- [x] The manuscript states that Kernel leads all four Dynamic World windows but only two of four matched ArcGIS-served windows; no universal learned-model rank is claimed.
- [x] The manuscript avoids causal language for actions, neighbourhood terms, state writeback and constraints.
- [x] No private database IP, port, username, password or client-only ArcGIS endpoint is included.

## LUP writing checks

- [x] Abstract follows context → gap → approach → quantitative result → implication → boundary.
- [x] Introduction uses a field-scale funnel and states the unresolved systems problem before the contribution.
- [x] Results separate observations from interpretation.
- [x] Discussion names failure modes and qualifies the completed controls as non-causal public-data stress tests.
- [x] Methods include state, action, proposal, projection, features, hyperparameters and evaluation tracks.
- [x] The manuscript no longer contains a Nature-specific broad-audience summary paragraph.
- [x] No unsupported “first”, “unprecedented”, “proves” or universal-performance claims are used.
- [x] Main figures are Python/Matplotlib outputs with English labels, editable SVG/PDF text and 600-dpi PNG/TIFF exports.

## Remaining blockers before submission

1. The Markdown source now follows the LUP Introduction–Methods–Results–Discussion structure; final template and portal checks remain.
2. The corresponding-author e-mail is set to `zhouning@freedotech.com`; confirm any full correspondence-address field in the submission portal.
3. Add a 30-m or multi-resolution sensitivity analysis if the target journal requires scale robustness.
4. Replace public labels and proxy constraints with authoritative local data before presenting outputs as client-facing planning evidence.
5. The public repository URL and archival DOI are recorded: Zenodo
   `10.5281/zenodo.22663476`, GitHub tag `v1.0.0`, commit `2cbd2d3`.
6. Preserve or publish an external copy of the public raster bundle if full numerical reproduction is required, and add an independent change-validation product when available.
7. Create and publish a new Zenodo version containing the ArcGIS-served v2 inputs, cross-product reports, Figure 4 source data, Supplementary Table S6 and both v2 integrity manifests. The current v1.0.0 DOI predates this refresh and must not be presented as its archival record.

## Reviewer-risk posture

The strongest defensible version is an algorithmic benchmark and conditional planning study with a cross-public-product robustness result. The manuscript should not be submitted as a validated forecast of Abu Dhabi's legal land-use change until the missing authoritative inputs and independent validation are addressed. It also should not be submitted as a fully archived reproducible refresh until the v2 Zenodo record is published.
