# Geospatial Kernel for Abu Dhabi Land-Cover Simulation and Planning

Research and reproducibility package for the manuscript **“An auditable geospatial kernel for constraint-preserving land-cover simulation and planning stress tests in Abu Dhabi”** by Ning Zhou (Beijing Freedo Technology Co., Ltd.).

The repository contains the cleaned manuscript and LUP-oriented submission copy,
editable figures, benchmark scripts, public-data manifests and legacy audit
reports comparing:

- GeoSOS-FLUS;
- Geospatial Kernel, the allocation core of a Geospatial World Model; and
- GeoFM-LDN (Geospatial Foundation-Model Latent Dynamics Network), the AlphaEarth latent-dynamics baseline.

## Scope and claim boundary

The benchmark uses public land-cover and proxy constraint data on a 100 m EPSG:32640 grid. Future maps are scenario stress tests, not official Abu Dhabi forecasts. They should not be interpreted as statutory residential, commercial, industrial, or cadastral land-use plans. The vector files are raster-cell transition polygons and are not legal parcels.

The repository deliberately excludes customer databases, credentials, private imagery, large raw downloads, and intermediate training caches. The public-data lineage and checksums are retained in the manifests under `benchmarks/abu_dhabi_land_use_v1/`.

The machine-readable reports retain the legacy internal identifier `paper58` for backward compatibility with the original runner and artifact paths. In the manuscript and all reader-facing labels, that implementation is called **GeoFM-LDN**. Current reruns write versioned report names, leaving legacy JSON lineage files immutable.

This repository contains the benchmark protocol and the manuscript package.
The strict multi-class change FoM, persistence/minimum-change controls,
spatial-block bootstrap with paired model contrasts and independent morphology
objective code have been rerun against the complete public-data bundle recovered
from the companion local GIS workspace. Large rasters and model runtimes remain
external to Git; independent authoritative change-validation data are still not
available. See [`manuscript/revision_after_LUP_review.md`](manuscript/revision_after_LUP_review.md)
for the evidence boundary.

## Start here

- Manuscript reading copy: [`manuscript/manuscript.pdf`](manuscript/manuscript.pdf)
- Landscape and Urban Planning copy: [`manuscript/lup_submission.pdf`](manuscript/lup_submission.pdf)
- Manuscript source: [`manuscript/manuscript.md`](manuscript/manuscript.md)
- Reproduction protocol: [`benchmarks/abu_dhabi_land_use_v1/protocol.json`](benchmarks/abu_dhabi_land_use_v1/protocol.json)
- Benchmark instructions: [`benchmarks/abu_dhabi_land_use_v1/README.md`](benchmarks/abu_dhabi_land_use_v1/README.md)
- Report lineage policy: [`benchmarks/abu_dhabi_land_use_v1/ARCHIVE_IMMUTABILITY.md`](benchmarks/abu_dhabi_land_use_v1/ARCHIVE_IMMUTABILITY.md)
- Planning delivery manifest: [`results/planning_public_2025_2031_delivery_manifest.json`](results/planning_public_2025_2031_delivery_manifest.json)
- Local data recovery and rerun record: [`docs/本机阿布扎比数据恢复与重算记录.md`](docs/本机阿布扎比数据恢复与重算记录.md)

## Reproduction

Run commands from the repository root. Some benchmark stages require external data access and optional model runtimes; the committed selected outputs can be inspected without rerunning those stages.

```bash
python benchmarks/abu_dhabi_land_use_v1/audit_inputs.py
python benchmarks/abu_dhabi_land_use_v1/audit_outputs.py
python benchmarks/abu_dhabi_land_use_v1/reproducibility_check.py
```

The scripts document the canonical boundary, grid, class labels, constraints, scenario definitions, and validation contracts. See `protocol.json` before changing any input or output.

## Results

Historical and planning comparison reports are in `results/` and the benchmark
directory. The current reports are generated from the recovered public-data
bundle; selected ensemble rasters and transition GeoPackages remain external
artifacts under `benchmarks/abu_dhabi_land_use_v1/artifacts/` and are described
by the delivery manifests.

## Citation

Until the manuscript is accepted and archived, cite the repository commit and manuscript author. A versioned DOI and final citation will be added after publication.

## License and data attribution

Code is released under the MIT License. Public source data remain subject to their original terms. OpenStreetMap data are © OpenStreetMap contributors and licensed under the Open Data Commons Open Database License (ODbL).
