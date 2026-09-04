# Landscape and Urban Planning submission check

Checked: 4 September 2026

Target journal: *Landscape and Urban Planning* (Elsevier, ISSN 0169-2046)

## Scope and article structure

| Requirement | Status | Check |
|---|---|---|
| Article type | Ready | Draft is positioned as a research article / algorithmic benchmark, not a short communication or review. |
| Title | Ready | Descriptive title identifies the method and planning use without claiming an official forecast. |
| Author and affiliation | Ready | Ning Zhou; Beijing Freedo Technology Co., Ltd. |
| Corresponding author | Needs portal entry | Name is present, but the submission system should receive a valid institutional e-mail and full correspondence address. |
| Abstract | Ready with portal confirmation | 244 words. This is within the 250-word limit commonly used by Elsevier research articles; confirm the current LUP guide at submission. |
| Highlights | Ready | Four bullets are supplied; each is below 85 characters, including spaces. |
| Keywords | Ready | Six searchable terms are supplied: Geospatial World Model, land-cover change, constrained allocation, cellular automata, Abu Dhabi and scenario planning. |
| Graphical abstract | Confirm in portal | No separate graphical abstract is included. The journal's current article-type setting should determine whether it is required or optional. Figure 1 can be adapted if requested. |
| Main sections | Ready | Introduction, Results, Discussion and Methods are present, followed by availability, declarations, references and figure legends. |

## Tables, figures and artwork

| Requirement | Status | Check |
|---|---|---|
| Editable tables | Ready | Tables remain Markdown/LaTeX text tables rather than raster images. Table 2 was split into 2a and 2b to preserve readability. |
| Table width | Ready | The LUP reading copy uses a 1.7 pt column separation and scriptsize long tables; visual QA confirms no clipped last columns or overlapping cells. |
| Table notes | Ready | Units, DTV, ecological-proxy semantics, compactness and Pareto interpretation are stated immediately before the relevant tables. |
| Figure files | Ready | Each main figure is available as editable SVG/PDF plus 600-dpi PNG/TIFF in `figures/`. |
| Figure captions | Ready | Captions identify panels, metrics, seeds, units and the public-data interpretation boundary. |
| Arrow alignment | Ready | Figure 1 arrows were redrawn as explicit patch endpoints and visually checked in the final PDF. |
| Separate upload | Submission step | Upload each figure as a separate file if Editorial Manager requests individual artwork; keep the combined PDF only as a reading copy. |
| Artwork technical limits | Confirm in portal | Elsevier commonly distinguishes line art, grayscale and colour resolution and accepts TIFF/EPS/PDF/JPEG variants. Confirm the live LUP artwork page before upload. |

## Declarations and reproducibility

| Requirement | Status | Check |
|---|---|---|
| Data availability | Ready | Public-data manifests, provenance files, audit reports and generated delivery artefacts are identified. |
| Code availability | Ready with release step | Runtime, benchmark and figure scripts are identified. Add the final public repository URL and archival DOI before submission. |
| CRediT statement | Ready | Ning Zhou is credited for conceptualization, methodology, software, curation, analysis, visualization and writing. |
| Funding | Ready | No external funding statement included. |
| Competing interests | Ready | No competing financial or personal interests statement included. |
| Acknowledgements | Ready | Explicit `None` statement included. |
| Ethics statement | Ready | Not applicable statement included for geospatial public-data work. |
| Author contributions / declarations placement | Confirm in portal | Keep these as separate submission fields if Editorial Manager asks for structured metadata in addition to the manuscript text. |

## References and submission metadata

- References use a numbered, author--year--journal--DOI presentation consistent with the current draft. Run the final bibliography through the journal's reference-style check if the portal provides one.
- A cover letter is normally supplied as a separate submission item. It should state that the manuscript is original, is not under consideration elsewhere and is an algorithmic public-data stress test rather than an official Abu Dhabi forecast.
- Add continuous line numbers only if the live LUP submission system requests them; the current reading PDF is intentionally clean and unnumbered.
- Confirm article-type-specific word limits, graphical-abstract status, artwork specifications and required declarations against the live Guide for Authors immediately before upload. ScienceDirect's web guide was Cloudflare-protected during this check, so no unverified journal-specific limit is presented as definitive.

## Scientific content checks

- The six classes are labelled as remote-sensing **land cover**, not legal residential, commercial or industrial land use.
- The 2025--2031 outputs are planner-supplied scenario stress tests with exogenous drivers frozen at 2024, not official forecasts.
- OSM and ESA WorldCover layers are described as public proxy constraints, not statutory planning red lines.
- Historical ranking is reported by horizon: Geospatial Kernel leads the 2023 one-step test, while GeoFM-LDN leads the 2024 two-step open-loop test.
- Change polygons are dissolved 100-m raster-cell footprints, not cadastral parcels.
- No client database credentials or private service endpoints are present in the manuscript package.

## Files for hand-off

- `lup_submission.pdf`: LUP-oriented reading PDF with repaired tables.
- `manuscript.pdf`: clean Pandoc reading PDF.
- `manuscript.docx`: editable Word copy.
- `manuscript.md`: source manuscript.
- `figures/`: individual figure artwork in SVG/PDF/PNG/TIFF.
- `landscape_urban_planning_compliance.md`: this report.

