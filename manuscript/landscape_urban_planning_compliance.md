# Landscape and Urban Planning submission check

Checked: 6 September 2026

Target journal: *Landscape and Urban Planning* (Elsevier, ISSN 0169-2046)

## Scope and article structure

| Requirement | Status | Check |
|---|---|---|
| Article type | Structurally suitable; conditional evidence | The draft is positioned as a research article / algorithmic benchmark. Public-data reruns are complete; independent authoritative change validation remains absent. The supplied FLUS binary is a GeoSOS-derived author-modified build. The 25-feature mode is a platform-sensitive identity-leakage diagnostic, and the 19-feature mode underfills demand; the primary comparison remains the seven-driver unmatched control. |
| Title | Ready | Descriptive title identifies the method and planning use without claiming an official forecast. |
| Author and affiliation | Ready | Ning Zhou; Beijing Freedo Technology Co., Ltd. |
| Corresponding author | Ready in manuscript; confirm portal address field | Ning Zhou; `zhouning@freedotech.com` is listed in the manuscript. Confirm any full correspondence-address field required by Editorial Manager before upload. |
| Abstract | Draft-ready; portal confirmation required | 206 words by whitespace count. Confirm the live LUP guide and any structured abstract fields immediately before submission. |
| Highlights | Draft-ready | Four bullets are supplied; each is below 85 characters, including spaces. They describe the completed public-data benchmark and its evidence boundary. |
| Keywords | Ready | Six searchable terms are supplied: Geospatial World Model, land-cover change, constrained allocation, cellular automata, Abu Dhabi and scenario planning. |
| Graphical abstract | Confirm in portal | No separate graphical abstract is included. The journal's current article-type setting should determine whether it is required or optional. Figure 1 can be adapted if requested. |
| Main sections | Structurally compliant | The Markdown source follows Introduction–Methods–Results–Discussion order. Final copy-edit and portal checks remain. |

## Tables, figures and artwork

| Requirement | Status | Check |
|---|---|---|
| Editable tables | Ready | The historical score table is numbered and captioned in the manuscript source; it remains a Markdown/LaTeX text table rather than a raster image. |
| Table width | Ready | The LUP reading copy uses a 0.9 pt column separation and scriptsize long tables; visual QA of the latest PDF confirms no clipped last columns or overlapping cells. |
| Table notes | Ready | Units, DTV, ecological-proxy semantics, compactness and Pareto interpretation are stated immediately before the relevant tables. |
| Figure files | Ready for technical review | Figures 1–5 were regenerated from the current strict-metric and planning reports as editable SVG/PDF plus 600-dpi PNG/TIFF. |
| Figure captions | Ready for scientific review | Captions describe current public-data results and retain the conditional-proxy boundary; duplicate auto-captions were removed from the latest reading PDF. |
| Arrow alignment | Ready for Figure 1 | Figure 1 arrows terminate at the implemented projection stage and were visually checked after redrawing. |
| Separate upload | Submission step | Upload each figure as a separate file if Editorial Manager requests individual artwork; keep the combined PDF only as a reading copy. |
| Artwork technical limits | Confirm in portal | Elsevier commonly distinguishes line art, grayscale and colour resolution and accepts TIFF/EPS/PDF/JPEG variants. Confirm the live LUP artwork page before upload. |

## Declarations and reproducibility

| Requirement | Status | Check |
|---|---|---|
| Data availability | Conditional | The complete public bundle, generated rasters, vectors and mechanism controls are included or tracked with Git LFS and pass the input/output audits; authoritative local validation data are unavailable. The author-run Linux/macOS Kernel comparison and FLUS feature diagnostics are archived with commands and reports. Reviewer-provided Windows figures are provenance-labelled external verification because their rasters are not locally archived. |
| Code availability | Conditional | Runtime, evaluators, GeoFM-LDN source/checkpoints and the macOS arm64 FLUS executable are included; a compatible, traceable FLUS build is required for an information-matched comparison, and a DOI is not yet provided. |
| CRediT statement | Ready | Ning Zhou is credited for conceptualization, methodology, software, curation, analysis, visualization and writing. |
| Funding | Ready | No external funding statement included. |
| Competing interests | Updated | Employment by the software company is disclosed; this should be checked against the portal's structured declaration field. |
| Acknowledgements | Ready | Explicit `None` statement included. |
| Ethics statement | Ready | Not applicable statement included for geospatial public-data work. |
| Author contributions / declarations placement | Confirm in portal | Keep these as separate submission fields if Editorial Manager asks for structured metadata in addition to the manuscript text. |

## References and submission metadata

- References now use author–year citations and include core land-change models, validation literature and planning-context sources. Run the final bibliography through the journal's reference-style check if the portal provides one.
- A cover letter is normally supplied as a separate submission item. It should state that the manuscript is original, is not under consideration elsewhere and is an algorithmic public-data stress test rather than an official Abu Dhabi forecast.
- Add continuous line numbers only if the live LUP submission system requests them; the current reading PDF is intentionally clean and unnumbered.
- Confirm article-type-specific word limits, graphical-abstract status, artwork specifications and required declarations against the live Guide for Authors immediately before upload. ScienceDirect's web guide was Cloudflare-protected during this check, so no unverified journal-specific limit is presented as definitive.

## Scientific content checks

- The six classes are labelled as remote-sensing **land cover**, not legal residential, commercial or industrial land use.
- The 2025--2031 outputs are planner-supplied scenario stress tests with exogenous drivers frozen at 2024, not official forecasts.
- OSM and ESA WorldCover layers are described as public proxy constraints, not statutory planning red lines.
- Historical ranking is based on the regenerated strict multi-class FoM, spatial-block intervals and paired model contrasts; persistence is disclosed and no universal ranking is claimed.
- Figures 2–5 were regenerated from versioned current reports; the renderer still fails closed on stale reports.
- Change polygons are dissolved 100-m raster-cell footprints, not cadastral parcels.
- No client database credentials or private service endpoints are present in the manuscript package.

## Files for hand-off

- `lup_submission.pdf`: LUP-oriented reading PDF with repaired table widths.
- `manuscript.pdf`: clean Pandoc reading PDF.
- `manuscript.docx`: editable Word copy.
- `manuscript.md`: source manuscript.
- `figures/`: individual figure artwork in SVG/PDF/PNG/TIFF.
- `landscape_urban_planning_compliance.md`: this report.
- `response_to_LUP_review.md`: point-by-point response and unresolved blockers.

The package is a conditional Article-type draft. Before submission, add the
public release URL/DOI and an independent 2023–2024 change-validation layer.
The supplied FLUS build is GeoSOS-derived
and its author modifications are archived at `FLUS_console_crossplatform`
commit `deb0a54`. The 25-feature run is platform sensitive and cannot replace
the primary three-seed comparison.
