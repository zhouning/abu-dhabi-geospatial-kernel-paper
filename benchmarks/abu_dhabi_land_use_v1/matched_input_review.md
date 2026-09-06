# FLUS matched-input diagnostic archive

This archive addresses the reviewer request to test whether the supplied
FLUS-style console fails because of the number of ANN drivers. The first
attempt used relative paths in the generated configuration and returned
`read config file error!!!`; it did not provide evidence of a segmentation
fault. The corrected runs use absolute paths and preserve the console's
stdout/stderr logs, configuration files and reports.

The corrected 25-feature matched-input baseline uses seeds 31, 47 and 73. The
intermediate 13- and 19-feature diagnostics remain archived for seed 31. All
runs use the supplied macOS arm64 binary, the 2021 training year, the same 2022
driver year and the same CA protocol as the headline control.
The feature modes are:

| Mode | Features | 2023 strict FoM | 2024 strict FoM | Output |
|---|---:|---:|---:|---|
| `baseline_plus_onehot` | 13 (7 drivers + 6 current-class indicators) | 0.0000 | 0.0000 | `artifacts/predictions/flus_7_plus_onehot_abs/report.json` |
| `baseline_plus_neighborhood` | 19 (7 drivers + 12 3×3/7×7 neighbourhood fractions) | 0.1371 | 0.1149 | `artifacts/predictions/flus_7_plus_neighbourhood_abs/report.json` |
| `matched_kernel` | 25 (6 one-hot + 12 neighbourhood + 7 continuous, Kernel order) | 0.0440 (three-seed mean) | 0.0653 (three-seed mean) | `artifacts/predictions/flus_matched_inputs_abs/report.json` |

The 25-feature values are a separate matched-input baseline, not a replacement
for the original seven-driver headline control. The feature family is matched,
but the learning target is not: FLUS estimates same-year suitability from the
current label, whereas the Kernel estimates next-state transitions before
constraint projection. The 13-feature run is especially degenerate because the
current-class indicators expose the same label used as the ANN target. Its ANN
RMSE is approximately $1.6\times10^{-5}$, and the resulting CA changes zero
pixels. This is identity leakage, not evidence of a no-change process.

The full command pattern is:

```bash
python benchmarks/abu_dhabi_land_use_v1/run_geosos_flus.py \
  --binary "$REPO/benchmarks/abu_dhabi_land_use_v1/vendor/flus_console" \
  --seeds 31,47,73 \
  --output "$REPO/benchmarks/abu_dhabi_land_use_v1/artifacts/predictions/flus_matched_inputs_abs" \
  --feature-mode matched_kernel
```

Replace the output directory and feature mode with the two intermediate rows
above. Each `work/seed_31/ann/flus_ann.log` records the command, working
directory, `FLUS_RANDOM_SEED`, return code, stdout and stderr. The corrected
25-feature run returned code 0 for all three seeds, wrote
`target_probability.tif` in each seed directory, and produced valid 2023 and
2024 rasters. The archive therefore supports the narrower conclusion that the
previous failure was a path/configuration problem, while preserving the
methodological boundary between matched feature inputs and matched learning
targets.
