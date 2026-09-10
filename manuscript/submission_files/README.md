# Editorial Manager upload package

The working revision includes the allocation-limit analysis and conditional
paired-interval interpretation described in `../revision_2026_09_10_zh.md`.
Supplementary Table S7 must accompany this revision. This working manuscript
is newer than the published v2.0.0 DOI; verify the separate working manifests
before using it as a submission package.

Use the files below for the five required upload categories shown by the
Landscape and Urban Planning submission system.

| System category | Recommended file | Alternative |
|---|---|---|
| Highlights | `highlights.pdf` | `highlights.docx` |
| Cover letter | `cover_letter.pdf` | `cover_letter.docx` |
| Title page with author details | `title_page.pdf` | `title_page.docx` |
| Manuscript without author details | `manuscript_anonymous.pdf` | `manuscript_anonymous.docx` |
| Abstract | `abstract.pdf` | `abstract.docx` |

The anonymous manuscript intentionally withholds author names, affiliation,
contact information, repository identifiers and archival DOI. These details
are supplied through the separate title page and Editorial Manager metadata.
Do not upload `manuscript.md`, `manuscript_pandoc.tex`, the review-response
file or internal database information as submission files.

The author-facing title page cites the published v2 Zenodo source release,
https://doi.org/10.5281/zenodo.22689057. The anonymous manuscript continues to
withhold repository and DOI identifiers for double-anonymized review. The
Zenodo-generated ZIP contains Git LFS pointers, so a full numerical rerun also
requires the hydrated LFS objects from GitHub tag `v2.0.0` and successful v2
manifest checks.

Main figures, if requested as separate artwork, are in the parent `figures/`
directory. Supplementary figures are also in that directory and should be
uploaded under the system's supplementary-material category.
