# V2 archive and rerun contract

The v2 experiment is reproducible from the materialized inputs in this
repository or a Zenodo archive created from a fully hydrated Git LFS checkout.
It is not reproduced by downloading current pixels from the live ArcGIS
ImageServer: the service catalog can change after the experiment date.

`MANIFEST.json` freezes public input rasters, source tiles, model assets,
configuration and code. `PUBLICATION_OUTPUTS.json` freezes the cited reports,
Figure 4 source data/artwork, and delivered 2026–2031 rasters and change
GeoPackages/Shapefiles. `SHA256SUMS` contains both record sets. Text files use
canonical LF line endings; all binary files use raw bytes.

From the repository root, run:

```bash
python benchmarks/abu_dhabi_land_use_v2/reproducibility/reproducibility_check.py
python benchmarks/abu_dhabi_land_use_v2/reproducibility/reproduce.py --device cpu
```

The second command may take substantial time because it retrains GeoFM-LDN and
runs nine historical windows with 1,000 spatial-block bootstrap resamples. It
first validates the *pre-rerun* archive, recreates outputs, rebuilds the
manifests and validates the resulting archive. It does not require an Earth
Engine credential or live ArcGIS service access when the archived source tiles
and public inputs are present.

The v2 Zenodo release must include all Git LFS objects referenced by both
manifests. A GitHub-generated source ZIP that contains LFS pointer files is
not a complete numerical-reproduction archive.
