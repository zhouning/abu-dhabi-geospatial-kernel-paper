# Landscape and Urban Planning submission check

Checked: 11 September 2026

Target journal: *Landscape and Urban Planning* (Elsevier, ISSN 0169-2046)

## Scope and article structure

| Requirement | Status | Check |
|---|---|---|
| Article type | Conventional author manuscript; portal confirmation required | The draft is positioned as a research article / algorithmic benchmark. It uses a clean single-column `article` wrapper because no official LUP template was available locally. Public-data reruns are complete; independent authoritative change validation remains absent. |
| Title | Ready | Descriptive title identifies the method and planning use without claiming an official forecast. |
| Author and affiliation | Ready | Ning Zhou; Beijing Freedo Technology Co., Ltd. |
| Corresponding author | Partially ready; portal address still required | Ning Zhou; `zhouning@freedotech.com`, Beijing, China, and ORCID `0009-0002-5647-7388` are listed on the title page. Enter the author's confirmed full postal correspondence address in Editorial Manager before upload. |
| Abstract | Draft-ready; portal confirmation required | 244 words by whitespace count. It reports cross-product label dependence, isolates the 2022 product-series-break target, and preserves the 100-m/non-authoritative boundary. Confirm the live LUP guide and any structured abstract fields immediately before submission. |
| Highlights | Draft-ready | Five bullets are supplied; each is below 85 characters, including spaces. They describe the completed public-data benchmark and its evidence boundary. |
| Keywords | Ready | Six searchable terms are supplied: Geospatial World Model, land-cover change, constrained allocation, cellular automata, Abu Dhabi and scenario planning. |
| Graphical abstract | Confirm in portal | No separate graphical abstract is included. The journal's current article-type setting should determine whether it is required or optional. Figure 1 can be adapted if requested. |
| Main sections | Structurally compliant | The Markdown source follows Introduction–Methods–Results–Discussion–Conclusions order. Main figures 1–7 are embedded at their first evidentiary discussion; Fig. S1–S4 are supplied as separate diagnostic supplements. Final copy-edit and portal checks remain. |

## Tables, figures and artwork

| Requirement | Status | Check |
|---|---|---|
| Editable tables | Ready | The historical score table is numbered and captioned in the manuscript source; it remains a Markdown/LaTeX text table rather than a raster image. |
| Table width | Ready with residual copy-edit checks | Tables are editable LaTeX text and fit the A4 author-manuscript width. Long code-like paths were shortened in the reader-facing prose; the machine-readable paths remain in the repository. |
| Table notes | Ready | Units, DTV, ecological-proxy semantics, compactness and Pareto interpretation are stated immediately before the relevant tables. |
| Figure files | Ready for technical review | The repository tracks editable SVG/PDF and 600-dpi PNG for Figures 1–7 and Fig. S1–S4. The same deterministic renderers also emit 600-dpi TIFF upload copies, which are intentionally not versioned as large binaries. Figure 4 is generated from the paired product reports and its source CSV covers every panel. |
| Figure captions | Ready for scientific review | Captions describe current public-data results and retain the conditional-proxy boundary. Figure 4's overall title and explanatory footer were moved from artwork into its caption; panel titles remain in the artwork. |
| Arrow alignment | Ready for Figure 1 | Figure 1 was redrawn on one coordinate system; all arrows terminate on the intended boxes and were checked after PDF embedding. |
| Separate upload | Submission step | Upload each figure as a separate file if Editorial Manager requests individual artwork; keep the combined PDF only as a reading copy. |
| Artwork technical limits | Confirm in portal | Elsevier commonly distinguishes line art, grayscale and colour resolution and accepts TIFF/EPS/PDF/JPEG variants. Confirm the live LUP artwork page before upload. |

## Declarations and reproducibility

| Requirement | Status | Check |
|---|---|---|
| Data availability | Versioned source release; LFS caveat | The v2 source release is published at https://doi.org/10.5281/zenodo.22689057 with immutable-input and publication-output manifests plus a fail-closed verifier. Its GitHub-generated ZIP contains LFS pointers, so hydrated large artifacts must be fetched from tag `v2.0.0` for a full numerical rerun. Authoritative local validation data remain unavailable. |
| Code availability | Ready | Runtime, evaluators, GeoFM-LDN source/checkpoints and the macOS arm64 FLUS executable are versioned at tag `v2.0.0`; large LFS-tracked files require `git lfs pull`. |
| CRediT statement | Ready | Ning Zhou is credited for conceptualization, methodology, software, curation, analysis, visualization and writing. |
| Funding | Ready | No external funding statement included. |
| Competing interests | Updated | Employment by the software company is disclosed; this should be checked against the portal's structured declaration field. |
| Acknowledgements | Ready | The manuscript acknowledges anonymous reviewers' independent technical verification and methodological comments; no funding or private data contribution is implied. |
| Ethics statement | Ready | Not applicable statement included for geospatial public-data work. |
| Generative-AI declaration | Ready | The author declares use of OpenAI Codex for language editing, code review and document formatting, with author review and responsibility. |
| Author contributions / declarations placement | Confirm in portal | Keep these as separate submission fields if Editorial Manager asks for structured metadata in addition to the manuscript text. |

## References and submission metadata

- References now use author–year citations and include core land-change models, validation literature and planning-context sources. Run the final bibliography through the journal's reference-style check if the portal provides one.
- A cover letter is normally supplied as a separate submission item. It should state that the manuscript is original, is not under consideration elsewhere and is an algorithmic public-data stress test rather than an official Abu Dhabi forecast.
- Add continuous line numbers only if the live LUP submission system requests them; the current reading PDF is intentionally clean and unnumbered.
- Confirm article-type-specific word limits, graphical-abstract status, artwork specifications and required declarations against the live Guide for Authors immediately before upload. ScienceDirect's web guide was Cloudflare-protected during this check, so no unverified journal-specific limit is presented as definitive.

## Scientific content checks

- The six classes are labelled as remote-sensing **land cover**, not legal residential, commercial or industrial land use.
- The Dynamic World 2025--2031 and ArcGIS-served 2026--2031 outputs are planner-supplied scenario stress tests with drivers frozen at their respective final observed years, not official forecasts.
- OSM and ESA WorldCover layers are described as public proxy constraints, not statutory planning red lines.
- Historical ranking is based on the regenerated strict multi-class FoM, spatial-block intervals and paired model contrasts; the matched-product result explicitly shows that no universal ranking is supported.
- Figures 1–7 and Fig. S1–S4 are embedded at their first evidentiary discussion. Figure 4 is a four-panel product-robustness figure with source data, an explicit ArcGIS-series-break marker and no overlapping label/title geometry.
- Change polygons are dissolved 100-m raster-cell footprints, not cadastral parcels.
- No client database credentials or private service endpoints are present in the manuscript package.

## Files for hand-off

- `lup_submission.pdf`: conventional single-column LUP-oriented author manuscript with inline figures.
- `manuscript.pdf`: clean Pandoc reading PDF.
- `manuscript.docx`: editable Word copy.
- `manuscript.md`: source manuscript.
- `figures/`: tracked individual artwork in SVG/PDF/PNG; regenerate 600-dpi TIFF upload copies from the versioned renderers when the portal requests them.
- `landscape_urban_planning_compliance.md`: this report.
- `response_to_LUP_review.md`: point-by-point response and unresolved blockers.

The package is a conditional Article-type draft. The current PDF is not an
official Elsevier production template; it is a readable, conventional initial-
submission author manuscript. Before submission, publish a post-revision tag
and self-contained archive containing hydrated Git LFS objects, then replace the
working-revision archival statement with that DOI. An independent local
change-validation layer is still unavailable.
The supplied FLUS build is GeoSOS-derived. Its valid-input binary provenance is
commit `deb0a54`; the retained fail-closed source release is
`FLUS_console_crossplatform` tag `paper-benchmark-flus-v1.1` at commit
`47e65b3`. The 25-feature run is platform sensitive and cannot replace
the primary three-seed comparison.
