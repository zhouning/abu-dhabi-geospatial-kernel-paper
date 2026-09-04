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
and artifact hashes. Large raster artifacts remain local; their hashes and
lineage records are the reproducibility interface.

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

## Current result status

The checked-in historical and planning JSON files are legacy artifacts. They
predate the strict multi-class FoM, paired-pixel bootstrap and revised
independent morphology objective set; their metadata now marks them as
`stale_artifact_not_for_inference` or `withdrawn_pending_public_2025_2031_rerun`.
The earlier 240-raster audit belongs to a separate 2025–2030 run and is not an
audit of the public 2025–2031 delivery.

The code needed for the revised analysis is present, but the current checkout
does not contain the complete raster bundle, GeoFM-LDN checkpoint or an
independent 2023–2024 built-area validation layer. Therefore no revised model
ranking, bootstrap interval or Pareto frontier is claimed here. The original
FLUS run also used a different feature set and frozen console defaults; a
matched-input rerun is required before intrinsic model superiority is inferred.

All substantive findings remain conditional on Dynamic World labels, public
OSM/WorldCover proxy constraints and planner-supplied scenario demand. They do
not predict actual Abu Dhabi policy or establish causal planning effects.
