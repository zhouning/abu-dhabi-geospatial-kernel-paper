# Geospatial Kernel in Abu Dhabi: manuscript package

This package contains a revised LUP-oriented research-article draft based on
the public-data Abu Dhabi Land-Use Benchmark V1. The manuscript evaluates
Geospatial Kernel as the state–action–constraint core of a Geospatial World
Model and compares it with a FLUS-style ANN–CA console (author-modified build) and
GeoFM-LDN.

## Main files

- `manuscript.pdf`: clean reading copy generated from the manuscript Markdown.
- `manuscript.docx`: editable Word copy.
- `manuscript.md`: clean manuscript source without author-facing editorial notes.
- `main.tex`: Nature-class LaTeX source generated from the clean manuscript.
- `main.pdf`: compiled LaTeX reading copy with recovered-data numerical results,
  regenerated Figures 1–5 and single-caption figure layout.
- `lup_submission.pdf`: LUP-oriented submission reading copy with repaired tables.
- `figures/`: Python/Matplotlib Nature-style figures in editable SVG/PDF and
  600-dpi PNG/TIFF formats.
- `paper_self_audit.md`: evidence and claim-boundary audit.
- `neighbourhood_weight_sensitivity.csv`: post-hoc sensitivity source data.
- `supplementary_table_S2_neighbourhood_weight_sensitivity.md`: synchronized
  strict-FoM Supplementary Table S2.
- `journal_recommendation.md`: target-journal recommendation and submission
  positioning.
- `submission_notes_zh.md`: Chinese hand-off notes and submission checklist.
- `landscape_urban_planning_compliance.md`: journal-specific submission check;
  the package is structurally aligned but scientifically blocked and is not
  Article type Ready.
- `response_to_LUP_review.md`: point-by-point revision and blocker record.
- `../benchmarks/abu_dhabi_land_use_v1/matched_input_review.md`: archived
  FLUS 13-, 19- and 25-feature input diagnostics and corrected command record.
  The 25-feature matched-input baseline covers seeds 31, 47 and 73; the
  13-feature identity-leakage run remains a seed-31 diagnostic.

The manuscript calls the latent-dynamics baseline **GeoFM-LDN** (Geospatial
Foundation-Model Latent Dynamics Network). Legacy machine-readable artifacts
retain the internal identifier `paper58` for compatibility with the original
runner and file paths.

## Evidence boundary

The historical benchmark uses public land-cover labels from 2017–2024 on a
100-m grid. The 2025–2031 maps are planner-supplied scenario stress tests with
2024 exogenous drivers frozen in time. They are not official Abu Dhabi forecasts
and do not infer statutory residential, commercial or industrial land use.

The released-data rerun supports a bounded implementation claim: Geospatial
Kernel is an auditable, constraint-preserving allocation core. Under the
unmatched public-data pipeline it has the largest strict one-step 2023
transition FoM, while GeoFM-LDN has the largest strict two-step 2024 open-loop
FoM; neither dominates both horizons. Within each 2031 scenario, the
FLUS-style control and Kernel are non-dominated; GeoFM-LDN is dominated after
the structural-zero ecological-conversion term is removed from the release
objectives. The release objectives are major-road distance, prior-built distance
and components in the combined 2024-built and newly built footprint. Ecological conversion
is retained as a diagnostic only. These are conditional pipeline and stress-test results,
not official Abu Dhabi forecasts.

## Before submission

1. Recheck the live LUP Guide for Authors immediately before upload, especially
   article-type limits, graphical-abstract status and artwork specifications.
2. Add an institutional correspondence e-mail when one is available; no e-mail
   is invented in this package.
3. Add the final public repository URL and archival DOI after release review.
4. Preserve the local recovered bundle or an equivalent external artifact
   package if full numerical reproduction is required.
5. Add independent built-area validation and authoritative local layers before
   presenting the outputs as client-facing planning evidence.
6. The manuscript intentionally contains no private database credentials.

The local recovered-data output audit passes 276 historical and planning
predictions with zero failures. A clean external checkout still needs the
large raster bundle and model runtimes to reproduce the numerical reports.
