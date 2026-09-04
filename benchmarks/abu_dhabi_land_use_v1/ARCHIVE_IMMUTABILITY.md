# Report lineage and immutable archives

The JSON files without a `_current` suffix are retained as legacy lineage
records. They are not evidence for the revised protocol and must not be
edited in place. A data-complete rerun writes versioned files by default:

- `comparison_report_current.json` and `comparison_report_current.md`;
- `planning_scenario_report_public_2025_2031_current.json`;
- `planning_comparison_report_public_2025_2031_current.json` and its Markdown
  rendering.

The output audit prefers these versioned reports when they exist and falls
back to the legacy paths only to report a blocked/stale state. A release
should additionally record SHA-256 hashes, the exact input manifest, model
versions and the command line used to create the versioned report. Status
annotations belong in a sidecar or a new versioned report; the `created_at`,
paths and payload of an archived report are not rewritten.
