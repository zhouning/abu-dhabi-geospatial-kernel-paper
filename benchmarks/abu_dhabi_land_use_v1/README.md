# Abu Dhabi Land-Use Benchmark V1

This directory is the single execution boundary for comparing GeoSOS-FLUS,
the GWM Geospatial Kernel and GeoFM-LDN (Geospatial Foundation-Model Latent
Dynamics Network) on Abu Dhabi city land-cover simulation and constrained
planning optimization.

The comparison is valid only when every candidate consumes the same canonical
grid, origin state, action, hard constraints and driver versions, and writes a
prediction accepted by `contract.validate_prediction`.

## Frozen scope

- Boundary: OpenStreetMap relation `R4479763` (Abu Dhabi city).
- Grid: `EPSG:32640`, 100 m, aligned to the 100 m UTM lattice.
- Observations: annual 2017-2024 states.
- Historical fit: transitions ending no later than 2021.
- Validation: 2021 to 2022.
- Test: open-loop rollout from 2022 to 2023 and 2024.
- Scenario origin: 2024; conditional annual rollout through 2031.
- Semantics: six-class land cover, not cadastral residential/commercial use.

`protocol.json` is authoritative. It separates oracle-demand allocation skill,
end-to-end rollout and planning optimization so that demand error cannot be
mistaken for spatial allocation error.

## Materialize the boundary and grid

```bash
python benchmarks/abu_dhabi_land_use_v1/fetch_boundary.py \
  --proxy http://127.0.0.1:7897
python benchmarks/abu_dhabi_land_use_v1/prepare_grid.py
```

The generated `boundary_manifest.json` and `grid_profile.json` retain source
and artifact hashes. Released raster/vector artifacts are validated by the
output audit; the input manifest uses raw hashes for binaries and LF-normalized
hashes for text files.

## Execute the three candidates

Historical conditional allocation (strict multi-class FoM and zero controls are
compiled by the comparison step):

```bash
python benchmarks/abu_dhabi_land_use_v1/run_geosos_flus.py
python benchmarks/abu_dhabi_land_use_v1/run_geospatial_kernel.py
# Provide the external GeoFM-LDN runner through GEOFM_LDN_RUNNER when available.
GEOFM_LDN_RUNNER=/path/to/geofm_ldn/experiments/abu_dhabi/run_paper58_abu_dhabi.py \
  python benchmarks/abu_dhabi_land_use_v1/run_planning_scenarios.py --models geofm_ldn
python benchmarks/abu_dhabi_land_use_v1/compile_comparison.py
```

The compiler writes `comparison_report_current.json` and
`comparison_report_current.md` by default, leaving the legacy
`comparison_report.json` untouched. The planning runner/compiler similarly
write `planning_scenario_report_public_2025_2031_current.json` and
`planning_comparison_report_public_2025_2031_current.json` by default.

Conditional 2025-2031 scenarios and independent morphology comparison:

```bash
python benchmarks/abu_dhabi_land_use_v1/run_planning_scenarios.py
python benchmarks/abu_dhabi_land_use_v1/compile_planning.py
python benchmarks/abu_dhabi_land_use_v1/audit_outputs.py
```

`run_planning_scenarios.py` invokes the real external FLUS console, trains the
explicit Geospatial Kernel and loads GeoFM-LDN checkpoints. All candidates
start from the observed 2024 state and receive the same annual demand and hard
constraints. Future exogenous raster drivers are held at their known 2024
values; GeoFM-LDN recursively writes back its predicted latent state.

## Exact reproducibility

The repository contains the public-data bundle needed for a clean checkout:
the 2017--2024 land-cover, quality, VIIRS, AlphaEarth, terrain and WorldCover
rasters; the OSM road-accessibility raster; the allocation and constraint
bundle; the three GeoFM-LDN checkpoints; the vendored GeoFM-LDN runner; the
tested macOS arm64 FLUS console; historical and planning prediction rasters;
change GeoPackages; and mechanism-control outputs. Raw OSM PBF is excluded
because it duplicates the released road-accessibility derivative.

The exact Python pins are in
`reproducibility/requirements.lock.txt`; platform and seed policy are in
`reproducibility/environment.json`. `reproducibility/MANIFEST.json` and
`reproducibility/SHA256SUMS` cover every declared input, model asset and source
file. The fail-closed gate is:

```bash
python benchmarks/abu_dhabi_land_use_v1/reproducibility_check.py
```

After installing the lock file in Python 3.11, a complete rerun is:

```bash
python benchmarks/abu_dhabi_land_use_v1/reproducibility/reproduce.py --device cpu
```

It regenerates the historical model rasters, the 2025--2031 three-model
scenarios, strict comparison reports, mechanism controls, 45 ensemble rasters,
9 multi-layer GeoPackages, the output audit and publication figures. The
reference run completed with 276 audited predictions and zero failures. The
vendored FLUS executable is macOS arm64; on another operating system provide
an explicitly built compatible binary with `run_geosos_flus.py --binary`.

The default rerun uses the declared GeoFM-LDN checkpoints so that model assets
remain immutable. The full training path remains available by invoking the
vendored runner without `--use-checkpoints`.

## Current result status

The immutable historical and planning JSON files are retained as legacy
lineage. Current versioned reports are generated from the recovered local
public-data bundle and use the strict multi-class FoM, spatial-block bootstrap
and revised independent planning objective set. The earlier 240-raster audit
belongs to a separate 2025–2030 run and is not an audit of the public
2025–2031 delivery.

The code needed for the revised analysis is present, including paired
model-difference intervals and a score-independent minimum-change null. The
resulting ranking and Pareto membership are conditional pipeline comparisons.
The original FLUS run used a different feature set and frozen console defaults,
so intrinsic model superiority should not be inferred without a matched-input
rerun. Independent authoritative 2023–2024 change validation is still not
available.

All substantive findings remain conditional on Dynamic World labels, public
OSM/WorldCover proxy constraints and planner-supplied scenario demand. They do
not predict actual Abu Dhabi policy or establish causal planning effects.
