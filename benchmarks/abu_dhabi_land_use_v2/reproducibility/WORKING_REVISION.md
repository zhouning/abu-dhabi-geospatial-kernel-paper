# Working revision and published archive

The published v2.0.0 DOI and Git tag retain their original content. This working
revision adds a report-derived net-change limit analysis, exposes seed-specific
paired intervals, archives the 27 per-seed 2031 ArcGIS planning states read by
the cross-product compiler, and revises the manuscript. It does not retrain
models or replace historical or planning prediction rasters. Do not attribute
the working revision to the published DOI as if it were already archived there.

The 10 September 2026 reference revision specifies the Dynamic World temporal
reducers and quality statistic, distinguishes the VIIRS monthly input from the
cited annual product, identifies Copernicus GLO-30 as a DSM, and links OSM and
ArcGIS citations to the stored source manifests. These are documentation
corrections, not new validation results or changes to the numerical pipeline.
See `manuscript/reference_revision_2026_09_10_zh.md` for the citation audit scope
and unresolved source checks.

The accompanying consistency repair also updates generated report metadata and
supplementary quality-proxy labels to the same Dynamic World definition. It does
not alter rasters, model fitting, predictions, or reported metric values.

From the repository root, generate the supplementary analysis:

```sh
python benchmarks/abu_dhabi_land_use_v2/analyze_allocation_limits.py
```

Check the declared working revision (verification never updates hashes):

```sh
python benchmarks/abu_dhabi_land_use_v2/reproducibility/reproducibility_check.py --working
```

The generator is deterministic: it emits LF-delimited CSV, Markdown and JSON
files and fixed 12-decimal derived floats. After a normal regeneration of an
already frozen working revision, the four CSV/JSON outputs and Supplementary
Table S7 must remain unchanged in Git after LF normalization. Run `git diff
--check` and inspect the five generated paths before rebuilding a manifest.

Maintainers may deliberately freeze a new working revision after reviewing changes:

```sh
python benchmarks/abu_dhabi_land_use_v2/reproducibility/build_reproducibility_manifest.py --working
```

The manifests under `working/` are distinct from the published manifests one
directory above. CSV, TSV, GeoJSON and SVG use LF-normalized text hashes in the
working revision; binary raster and model hashes remain raw byte hashes. The
working publication-output manifest explicitly includes the 27 per-seed 2031
ArcGIS planning rasters required by `analyze_product_robustness.py`, so Fig. 4,
Supplementary Table S1 and Supplementary Table S6 can be recreated without an
end-to-end simulation. The published manifests are preserved, including their
original hash conventions. For exact published-release verification, use a
separate checkout of `v2.0.0`, retrieve Git LFS objects and preserve LF line
endings (`git -c core.autocrlf=false checkout v2.0.0`). Do not regenerate its
manifests to conceal differences. Default checking against the published
manifests on this edited branch is expected to fail.

PDF and Word builds require Pandoc, the Python package `python-docx`, and XeLaTeX. Tectonic is also supported by
setting `MANUSCRIPT_TEX_ENGINE=tectonic`. Set `MANUSCRIPT_FONT` to an installed
font (for example Arial on Windows) for the short submission documents, then run
`python manuscript/build_submission_package.py`.

An integrity PASS verifies the declared files only. It does not validate land
cover against independent reference samples, establish operational forecasts,
or demonstrate a gross-transition allocator or constraint-preserving ensemble.
