# Zenodo v2 archival audit

Audit date: 2026-09-10

## Published identity

- Version DOI: `10.5281/zenodo.22689057`
- Concept DOI: `10.5281/zenodo.22663475`
- Zenodo version: `v2.0.0`
- GitHub tag: `v2.0.0`
- Git commit: `77e2c59a42e7520819973c34e32bc446a78fcbc3`
- Publication state returned by the Zenodo API: `published`

## Deposited-file check

The Zenodo API reported one deposited file:

`zhouning/abu-dhabi-geospatial-kernel-paper-v2.0.0.zip`

Its reported size was 30,161,890 bytes and MD5 checksum was
`abc6f3068521ef83b87b6b20da444147`. Direct inspection of the downloaded ZIP
showed that Git LFS-tracked files are pointer records rather than hydrated
binary objects. For example, tracked TIFF entries were 129 bytes and began
with `version https://git-lfs.github.com/spec/v1`.

## Reproduction consequence

The DOI is the persistent identifier for the exact v2 source release, but its
current ZIP is not sufficient by itself for a full numerical rerun. Use:

```bash
git clone https://github.com/zhouning/abu-dhabi-geospatial-kernel-paper.git
cd abu-dhabi-geospatial-kernel-paper
git checkout v2.0.0
git lfs pull
./.venv-lup/bin/python benchmarks/abu_dhabi_land_use_v2/reproducibility/reproducibility_check.py
```

Both `MANIFEST.json` and `PUBLICATION_OUTPUTS.json` must pass before rerunning
the experiment. A future Zenodo version should upload a fully hydrated release
bundle directly if self-contained DOI-only reproduction is required.

## Tag verification

On 2026-09-10, an isolated checkout of Git tag `v2.0.0` was hydrated with 767
Git LFS objects (about 590 MB) and passed `reproducibility_check.py`: 170
immutable-input records, 181 publication-output records, and all three core
reports were `PASS`/`complete`. DOI references were necessarily committed to
`main` after Zenodo minted the identifier; those post-release metadata edits are
not part of the immutable tag and should not be used as the manifest-verification
target.

This audit does not change the scientific data boundary: the two input tracks
are public land-cover products, model execution is at 100 m, and the 2026-2031
outputs are conditional scenario stress tests rather than official Abu Dhabi
land-use forecasts.
