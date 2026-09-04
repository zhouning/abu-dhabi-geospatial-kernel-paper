# Geospatial Kernel in Abu Dhabi: manuscript package

This package contains a revised LUP-oriented research-article draft based on
the public-data Abu Dhabi Land-Use Benchmark V1. The manuscript evaluates
Geospatial Kernel as the state–action–constraint core of a Geospatial World
Model and compares it with GeoSOS-FLUS and GeoFM-LDN.

## Main files

- `manuscript.pdf`: clean reading copy generated from the manuscript Markdown.
- `manuscript.docx`: editable Word copy.
- `manuscript.md`: clean manuscript source without author-facing editorial notes.
- `main.tex`: Nature-class LaTeX source generated from the clean manuscript.
- `main.pdf`: compiled LaTeX reading copy; Figures 2–5 are legacy plots pending
  the strict-metric/raster rerun, while Figure 1 has been redrawn.
- `lup_submission.pdf`: LUP-oriented submission reading copy with repaired tables.
- `figures/`: Python/Matplotlib Nature-style figures in editable SVG/PDF and
  600-dpi PNG/TIFF formats.
- `paper_self_audit.md`: evidence and claim-boundary audit.
- `neighbourhood_weight_sensitivity.csv`: post-hoc sensitivity source data.
- `journal_recommendation.md`: target-journal recommendation and submission
  positioning.
- `submission_notes_zh.md`: Chinese hand-off notes and submission checklist.
- `landscape_urban_planning_compliance.md`: journal-specific submission check;
  the package is structurally aligned but scientifically blocked and is not
  Article type Ready.
- `response_to_LUP_review.md`: point-by-point revision and blocker record.

The manuscript calls the latent-dynamics baseline **GeoFM-LDN** (Geospatial
Foundation-Model Latent Dynamics Network). Legacy machine-readable artifacts
retain the internal identifier `paper58` for compatibility with the original
runner and file paths.

## Evidence boundary

The historical benchmark uses public land-cover labels from 2017–2024 on a
100-m grid. The 2025–2031 maps are planner-supplied scenario stress tests with
2024 exogenous drivers frozen in time. They are not official Abu Dhabi forecasts
and do not infer statutory residential, commercial or industrial land use.

The results support only a bounded implementation claim: Geospatial Kernel is
an auditable, constraint-preserving allocation core. The earlier
Pareto-frontier claim is withdrawn pending rerun with independent morphology
objectives. GeoFM-LDN was stronger on the legacy 2024 two-step open-loop
historical target, but that is a withdrawn binary-FoM continuity result. All
quantitative rankings must be regenerated with strict multi-class FoM, zero
models, spatial-block bootstrap and paired model-difference intervals.

## Before submission

1. Recheck the live LUP Guide for Authors immediately before upload, especially
   article-type limits, graphical-abstract status and artwork specifications.
2. Add an institutional correspondence e-mail when one is available; no e-mail
   is invented in this package.
3. Add the final public repository URL and archival DOI after release review.
4. Restore the complete public raster bundle, GeoFM-LDN checkpoint and FLUS
   environment, then rerun all metrics and figures.
5. Add independent built-area validation and authoritative local layers before
   presenting the outputs as client-facing planning evidence.
6. The manuscript intentionally contains no private database credentials.

The current output audit is `INCOMPLETE_INPUTS` (eight failures), and the
figure renderer fails closed when it detects legacy reports. Existing Figures
2–5 and numerical tables are retained for lineage only and are not
submission-ready.
