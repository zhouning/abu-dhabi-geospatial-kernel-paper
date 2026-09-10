# Zenodo v2 release checklist

This checklist prepares a **new version** of the existing Abu Dhabi benchmark
record. It does not claim that the ArcGIS-served product is authoritative Abu
Dhabi land-use data; it archives the exact public-data experiment described in
the refreshed manuscript.

## Before creating the Zenodo version

1. In the repository root, use a fully hydrated Git LFS checkout. Do not use a
   GitHub-generated source ZIP, because it may contain only LFS pointer files.
2. Run the two checks below and retain their generated reports:

   ```bash
   ./.venv-lup/bin/python benchmarks/abu_dhabi_land_use_v2/reproducibility/build_reproducibility_manifest.py
   ./.venv-lup/bin/python benchmarks/abu_dhabi_land_use_v2/reproducibility/reproducibility_check.py \
     --output benchmarks/abu_dhabi_land_use_v2/reproducibility_check.json
   ```

   The result must be `PASS`.
3. Review `git status`, commit the refreshed v2 experiment, and create a new
   immutable Git tag such as `v2.0.0`. The tag must point to the same commit
   whose files are uploaded to Zenodo.
4. Do not include PostgreSQL credentials, customer databases, private imagery,
   client-only service endpoints or any other restricted material.

## Create the record

1. Open the existing Zenodo record whose concept DOI is
   `10.5281/zenodo.22663475` and choose **New version**. Do not edit the frozen
   v1.0.0 record.
2. Use the release title: *Geospatial Kernel for Abu Dhabi Land-Cover
   Simulation and Planning*.
3. Set version to `v2.0.0` (or the matching immutable Git tag), author to Ning
   Zhou, affiliation to Beijing Freedo Technology Co., Ltd., and upload date to
   the actual publication date.
4. Use a release description that states: the package contains a reproducible
   cross-public-product study using Dynamic World 2017–2024 and the
   ArcGIS-served Impact Observatory/Microsoft/Esri annual product 2017–2025;
   both are public land-cover products, model execution is 100 m, and the
   2026–2031 maps are conditional scenario stress tests rather than official
   forecasts or statutory land-use outputs.
5. Select the code license applicable to repository code (MIT). Preserve the
   original licence/attribution terms for every public input product; do not
   relabel their data as MIT.

## Required upload content

The release must contain all content referenced by both manifests, including:

- `benchmarks/abu_dhabi_land_use_v2/reproducibility/MANIFEST.json`,
  `PUBLICATION_OUTPUTS.json`, `SHA256SUMS`, `reproducibility_check.py` and
  `reproduce.py`;
- the archived ArcGIS source tiles, source manifest, aligned public rasters,
  source geometry, constraints and the Dynamic World inputs used by the matched
  track;
- the vendored FLUS executable, GeoFM-LDN checkpoints and all v2 runner code;
- the two historical backtest `report.json` files, cross-product result tables,
  Figure 4 source CSV/artwork, and Supplementary Table S6;
- the 2026–2031 ensemble rasters and annual/consolidated change GeoPackages and
  Shapefiles.

After upload, rerun `reproducibility_check.py` against the staged files, or
verify that Zenodo's deposited checksums match `SHA256SUMS`.

## After publishing

Zenodo will issue a new **version DOI**. Keep the concept DOI
`10.5281/zenodo.22663475` for the evolving record, but cite the newly issued
version DOI for this v2 experiment. Update the author-facing README, manuscript
data/code availability statement and title page with that exact DOI, rebuild
the PDF/DOCX package, then upload the blinded manuscript without the identifier
for double-anonymized review.
