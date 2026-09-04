# Landscape and Urban Planning submission check

Checked: 4 September 2026

Target journal: *Landscape and Urban Planning* (Elsevier, ISSN 0169-2046)

## Scope and article structure

| Requirement | Status | Check |
|---|---|---|
| Article type | Structurally suitable; scientifically blocked | The draft is positioned as a research article / algorithmic benchmark, but it must not be marked submission-ready until the missing reruns and independent validation are completed. |
| Title | Ready | Descriptive title identifies the method and planning use without claiming an official forecast. |
| Author and affiliation | Ready | Ning Zhou; Beijing Freedo Technology Co., Ltd. |
| Corresponding author | Needs portal entry | Name is present, but the submission system should receive a valid institutional e-mail and full correspondence address. |
| Abstract | Draft-ready; portal confirmation required | 205 words by whitespace count. Confirm the live LUP guide and any structured abstract fields immediately before submission. |
| Highlights | Draft-ready | Four bullets are supplied; each is below 85 characters, including spaces. They describe a blocked revision rather than completed model-ranking evidence. |
| Keywords | Ready | Six searchable terms are supplied: Geospatial World Model, land-cover change, constrained allocation, cellular automata, Abu Dhabi and scenario planning. |
| Graphical abstract | Confirm in portal | No separate graphical abstract is included. The journal's current article-type setting should determine whether it is required or optional. Figure 1 can be adapted if requested. |
| Main sections | Structurally compliant; scientifically blocked | The Markdown source follows Introduction–Methods–Results–Discussion order. Final copy-edit, template checks and the required reruns remain. |

## Tables, figures and artwork

| Requirement | Status | Check |
|---|---|---|
| Editable tables | Ready | Tables remain Markdown/LaTeX text tables rather than raster images. Table 2 was split into 2a and 2b to preserve readability. |
| Table width | Ready | The LUP reading copy uses a 1.7 pt column separation and scriptsize long tables; visual QA confirms no clipped last columns or overlapping cells. |
| Table notes | Ready | Units, DTV, ecological-proxy semantics, compactness and Pareto interpretation are stated immediately before the relevant tables. |
| Figure files | Partial | Figure 1 has been redrawn and exported as editable SVG/PDF plus 600-dpi PNG/TIFF. Figures 2–5 remain legacy outputs pending the strict-metric and raster rerun. |
| Figure captions | Not submission-ready | Captions explicitly label Figures 2–5 as legacy/pending rerun. They must be regenerated from the strict-metric, audited raster bundle before submission. |
| Arrow alignment | Ready for Figure 1 | Figure 1 arrows terminate at the implemented projection stage and were visually checked after redrawing. |
| Separate upload | Submission step | Upload each figure as a separate file if Editorial Manager requests individual artwork; keep the combined PDF only as a reading copy. |
| Artwork technical limits | Confirm in portal | Elsevier commonly distinguishes line art, grayscale and colour resolution and accepts TIFF/EPS/PDF/JPEG variants. Confirm the live LUP artwork page before upload. |

## Declarations and reproducibility

| Requirement | Status | Check |
|---|---|---|
| Data availability | Blocked | Public-data manifests and provenance files are identified, but the complete raster bundle is not in the reviewed checkout; the current output audit is `INCOMPLETE_INPUTS` with eight failures. |
| Code availability | Blocked | A runtime snapshot is vendored, but GeoFM-LDN source/checkpoint, the FLUS environment/version, complete generated inputs and a public release DOI remain outstanding. |
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
- Historical ranking is explicitly marked as a legacy binary-FoM result pending strict multi-class rerun; persistence is disclosed and no universal ranking is claimed.
- Figure 2–5 source assets are fail-closed: the renderer refuses to issue a new-looking figure when legacy reports or required rasters are detected.
- Change polygons are dissolved 100-m raster-cell footprints, not cadastral parcels.
- No client database credentials or private service endpoints are present in the manuscript package.

## Files for hand-off

- `lup_submission.pdf`: LUP-oriented reading PDF with repaired table widths and
  explicit legacy-result warnings; not a final resubmission PDF.
- `manuscript.pdf`: clean Pandoc reading PDF.
- `manuscript.docx`: editable Word copy.
- `manuscript.md`: source manuscript.
- `figures/`: individual figure artwork in SVG/PDF/PNG/TIFF.
- `landscape_urban_planning_compliance.md`: this report.
- `response_to_LUP_review.md`: point-by-point response and unresolved blockers.

The package is therefore a transparent revision record, not an Article type
Ready submission package. A final LUP resubmission requires the missing
artifacts, matched-input baseline, independent 2023–2024 change validation,
strict-metric/bootstrap rerun and regenerated figures/tables.
