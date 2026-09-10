# Geospatial Kernel for Abu Dhabi Land-Cover Simulation and Planning

Research and reproducibility package for the manuscript **“Auditing constrained geospatial allocation under annual land-cover product uncertainty”** by Ning Zhou (Beijing Freedo Technology Co., Ltd.).

The repository contains the cleaned manuscript and LUP-oriented submission copy,
editable figures, benchmark scripts, public-data manifests and legacy audit
reports comparing:

- GeoSOS-derived FLUS-style ANN–CA console (author-modified build);
- Geospatial Kernel, the allocation core of a Geospatial World Model; and
- GeoFM-LDN (Geospatial Foundation-Model Latent Dynamics Network), the AlphaEarth latent-dynamics baseline.

The `docs/` directory contains internal capability-boundary and data-recovery
notes for project coordination; those files are not part of the journal
submission package.

## Scope and claim boundary

The benchmark uses two public annual land-cover products and proxy constraint data on a 100 m EPSG:32640 grid. Dynamic World covers 2017–2024; the ArcGIS-served Impact Observatory/Microsoft/Esri series covers 2017–2025 and retains native 10 m rasters for audit. Model execution remains at 100 m. Future maps are scenario stress tests, not official Abu Dhabi forecasts. They should not be interpreted as statutory residential, commercial, industrial, or cadastral land-use plans. The vector files are raster-cell transition polygons and are not legal parcels.

The repository deliberately excludes customer databases, credentials, private imagery and unrelated training caches. Derived rasters and vector packages required for the declared reruns are included or tracked with Git LFS; public-data lineage and checksums are retained under `benchmarks/abu_dhabi_land_use_v1/` and `benchmarks/abu_dhabi_land_use_v2/`.

The machine-readable reports retain the legacy internal identifier `paper58` for backward compatibility with the original runner and artifact paths. In the manuscript and all reader-facing labels, that implementation is called **GeoFM-LDN**. Current reruns write versioned report names, leaving legacy JSON lineage files immutable. The release planning objective set is v6: major-road distance, prior-built distance and connected-component density in the union of 2024 built and newly built cells; ecological conversion is diagnostic only.

This repository contains the benchmark protocol, public input bundle, model
runtimes/checkpoints, historical and planning prediction rasters, vector change
packages, mechanism controls and manuscript package. The strict multi-class
change FoM, persistence/minimum-change controls, spatial-block bootstrap with
paired model contrasts and the release planning objectives have been rerun.
Independent authoritative change-validation data are still not available. The
earlier matched-input FLUS failure was a relative-path configuration error;
corrected 13-, 19- and 25-feature diagnostics completed with absolute paths.
The 13-, 19- and 25-feature diagnostics are archived for seeds 31, 47 and 73.
The 25-feature mode is a platform-sensitive identity-leakage diagnostic: five
of six platform–seed runs collapsed to zero change. The 19-feature mode avoids
zero change but underfills demand. Neither mode is a headline estimator or a
paired model contrast.
The matched cross-product experiment uses expanding one-step windows, three
seeds, two zero models and 1,000-resample spatial-block intervals. Geospatial
Kernel leads all four Dynamic World windows but only the 2023 and 2024 matched
ArcGIS-served windows. This is product-pipeline dependence, not evidence that
either public label product is locally correct.
See [`manuscript/revision_after_LUP_review.md`](manuscript/revision_after_LUP_review.md)
for the evidence boundary.

## Start here

- Manuscript reading copy: [`manuscript/manuscript.pdf`](manuscript/manuscript.pdf)
- Landscape and Urban Planning author manuscript: [`manuscript/lup_submission.pdf`](manuscript/lup_submission.pdf)
- Manuscript source: [`manuscript/manuscript.md`](manuscript/manuscript.md)
- Reproduction protocol: [`benchmarks/abu_dhabi_land_use_v1/protocol.json`](benchmarks/abu_dhabi_land_use_v1/protocol.json)
- Benchmark instructions: [`benchmarks/abu_dhabi_land_use_v1/README.md`](benchmarks/abu_dhabi_land_use_v1/README.md)
- ArcGIS-served refresh and cross-product instructions: [`benchmarks/abu_dhabi_land_use_v2/README.md`](benchmarks/abu_dhabi_land_use_v2/README.md)
- Cross-product evidence summary: [`benchmarks/abu_dhabi_land_use_v2/results_arcgis_v2/paper_refresh/product_robustness_summary.md`](benchmarks/abu_dhabi_land_use_v2/results_arcgis_v2/paper_refresh/product_robustness_summary.md)
- Report lineage policy: [`benchmarks/abu_dhabi_land_use_v1/ARCHIVE_IMMUTABILITY.md`](benchmarks/abu_dhabi_land_use_v1/ARCHIVE_IMMUTABILITY.md)
- Planning delivery manifest: [`benchmarks/abu_dhabi_land_use_v1/planning_public_2025_2031_delivery_manifest_current.json`](benchmarks/abu_dhabi_land_use_v1/planning_public_2025_2031_delivery_manifest_current.json)
- Local data recovery and rerun record: [`docs/本机阿布扎比数据恢复与重算记录.md`](docs/本机阿布扎比数据恢复与重算记录.md)

## Reproduction

Run commands from the repository root. Some benchmark stages require external data access and optional model runtimes; the committed selected outputs can be inspected without rerunning those stages.

```bash
python benchmarks/abu_dhabi_land_use_v1/audit_inputs.py
python benchmarks/abu_dhabi_land_use_v1/audit_outputs.py
python benchmarks/abu_dhabi_land_use_v1/reproducibility_check.py
```

The v2 README gives the complete materialization and planning commands. Once
the downloaded inputs are present, the paper-refresh experiment is reproduced
with the two historical backtests followed by
`benchmarks/abu_dhabi_land_use_v2/analyze_product_robustness.py`.

The scripts document the canonical boundary, grid, class labels, constraints, scenario definitions, and validation contracts. See `protocol.json` before changing any input or output.

## Results

The `results/` directory contains earlier exported lineage files. The current
historical and planning reports are the versioned `_current` files under
`benchmarks/abu_dhabi_land_use_v1/`, generated from the released public-data
bundle. Historical/planning rasters, transition GeoPackages and mechanism
controls are included under that benchmark's `artifacts/` directory and are
described by the current delivery manifest.

The ArcGIS-served 2026–2031 ensembles and vector changes are under
`benchmarks/abu_dhabi_land_use_v2/results_arcgis_v2/`. The matched historical
reports, Figure 4 source data and Supplementary Table S6 are generated from the
two product-track reports and retain their hashes.

## Citation

For the ArcGIS-served refresh, cite the current version:

> Zhou, N. (2026). *Geospatial Kernel for Abu Dhabi Land-Cover Simulation and Planning* (v2.0.0). Zenodo. https://doi.org/10.5281/zenodo.22689057

The v2 DOI corresponds to GitHub tag `v2.0.0` at commit `77e2c59`. It identifies
the public-data benchmark source release, not the eventual journal article DOI
and not an authoritative Abu Dhabi land-use data release. The concept DOI for
all versions is `10.5281/zenodo.22663475`.

Large rasters, GeoPackages and model checkpoints are tracked with Git LFS in
the GitHub repository. The Zenodo v2 record currently contains GitHub's
automatically generated source ZIP; direct inspection confirmed that this ZIP
contains LFS pointer files rather than the hydrated large artifacts. A full
numerical rerun therefore requires checking out tag `v2.0.0`, running
`git lfs pull`, and passing both v2 manifest checks. See
[`docs/zenodo_v2_archival_audit.md`](docs/zenodo_v2_archival_audit.md).

## License and data attribution

Code is released under the MIT License. Public source data remain subject to their original terms. OpenStreetMap data are © OpenStreetMap contributors and licensed under the Open Data Commons Open Database License (ODbL).
