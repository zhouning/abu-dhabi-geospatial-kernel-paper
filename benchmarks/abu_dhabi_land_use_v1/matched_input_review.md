# FLUS matched-input diagnostic archive

This archive addresses the reviewer request to test whether the supplied
FLUS-style console fails because of the number of ANN drivers. The first
attempt used relative paths in the generated configuration and returned
`read config file error!!!`; it did not provide evidence of a segmentation
fault. The corrected runs use absolute paths and preserve the console's
stdout/stderr logs, configuration files and reports.

The corrected 13-, 19- and 25-feature diagnostics use seeds 31, 47 and 73. All
runs use the supplied macOS arm64 binary, the 2021 training year, the same 2022
driver year and the same CA protocol as the headline control.
The feature modes are:

| Mode | Features | 2023 strict FoM | 2024 strict FoM | Output |
|---|---:|---:|---:|---|
| `baseline_plus_onehot` | 13 (7 drivers + 6 current-class indicators) | 0.0000 | 0.0000 | `artifacts/predictions/flus_7_plus_onehot_abs/report.json` |
| `baseline_plus_neighborhood` | 19 (7 drivers + 12 3×3/7×7 neighbourhood fractions) | 0.1071–0.1617 (3 seeds) | 0.0872–0.1386 (3 seeds) | `artifacts/predictions/flus_7_plus_neighbourhood_abs/report.json` |
| `matched_kernel` | 25 (6 one-hot + 12 neighbourhood + 7 continuous, Kernel order) | 0.0000–0.1320 (macOS; diagnostic only) | 0.0000–0.1960 (macOS; diagnostic only) | `artifacts/predictions/flus_matched_inputs_abs/report.json` |

The 25-feature values are a platform-sensitive diagnostic, not a replacement for
the original seven-driver headline control. Across the six platform–seed runs,
five collapsed to zero-change outputs through current-class identity leakage:
macOS seeds 47 and 73 and all three reviewer-provided Windows x86_64 seeds.
The non-collapsed macOS seed-31 result is therefore not treated as a valid point
estimate or paired interval. The feature family is matched, but the learning
target is not: FLUS estimates same-year suitability from the current label,
whereas the Kernel estimates next-state transitions before constraint
projection. The 19-feature diagnostic produces changes for all three macOS
seeds, but predicted changes remain below the observed 4,500 and 8,464 cells in
2023 and 2024, respectively. These are mechanism and failure-mode diagnostics,
not evidence of a no-change process or a comparable estimator.

The full command pattern is:

```bash
python benchmarks/abu_dhabi_land_use_v1/run_geosos_flus.py \
  --binary "$REPO/benchmarks/abu_dhabi_land_use_v1/vendor/flus_console" \
  --seeds 31,47,73 \
  --output "$REPO/benchmarks/abu_dhabi_land_use_v1/artifacts/predictions/flus_matched_inputs_abs" \
  --feature-mode matched_kernel
```

Replace the output directory and feature mode with the two intermediate rows
above. Each `work/seed_<seed>/ann/flus_ann.log` records the command, working
directory, `FLUS_RANDOM_SEED`, return code, stdout and stderr. The corrected
25-feature run returned code 0 for all three seeds, wrote
`target_probability.tif` in each seed directory, and produced valid 2023 and
2024 rasters. The archive therefore supports the narrower conclusion that the
previous failure was a path/configuration problem, while preserving the
methodological boundary between matched feature inputs and matched learning
targets.
