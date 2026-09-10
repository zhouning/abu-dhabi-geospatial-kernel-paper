# Working revision and published archive

The published v2.0.0 DOI and Git tag retain their original content. This working
revision adds a report-derived net-change limit analysis, exposes seed-specific
paired intervals, and revises the manuscript. It does not retrain models or
replace historical or planning prediction rasters. Do not attribute the working
revision to the published DOI as if it were already archived there.

From the repository root, generate the supplementary analysis:

```sh
python benchmarks/abu_dhabi_land_use_v2/analyze_allocation_limits.py
```

Check the declared working revision (verification never updates hashes):

```sh
python benchmarks/abu_dhabi_land_use_v2/reproducibility/reproducibility_check.py --working
```

The generator is deterministic: it emits LF-delimited CSV files and fixed
12-decimal derived floats. After a normal regeneration of an already frozen
working revision, the three CSV/JSON outputs and Supplementary Table S7 must
remain unchanged in Git. Run `git diff --check` and inspect the four generated
paths before rebuilding a manifest.

Maintainers may deliberately freeze a new working revision after reviewing changes:

```sh
python benchmarks/abu_dhabi_land_use_v2/reproducibility/build_reproducibility_manifest.py --working
```

The manifests under `working/` are distinct from the published manifests one
directory above. CSV, TSV, GeoJSON and SVG use LF-normalized text hashes in the
working revision; binary raster and model hashes remain raw byte hashes. The
published manifests are preserved, including their original hash conventions.
For exact published-release verification, use a separate checkout of `v2.0.0`,
retrieve Git LFS objects and preserve LF line endings. Do not regenerate its
manifests to conceal differences. Default checking against the published
manifests on this edited branch is expected to fail.

PDF and Word builds require Pandoc, the Python package `python-docx`, and XeLaTeX. Tectonic is also supported by
setting `MANUSCRIPT_TEX_ENGINE=tectonic`. Set `MANUSCRIPT_FONT` to an installed
font (for example Arial on Windows) for the short submission documents, then run
`python manuscript/build_submission_package.py`.

An integrity PASS verifies the declared files only. It does not validate land
cover against independent reference samples, establish operational forecasts,
or demonstrate a gross-transition allocator or constraint-preserving ensemble.
