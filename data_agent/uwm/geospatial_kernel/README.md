# Geospatial Kernel runtime snapshot

`runtime.py` is a vendored, domain-neutral snapshot of the execution contract
used by the Abu Dhabi benchmark. It contains typed state and action records,
transition proposals, constraint projections, state writeback, rollout traces
and evidence provenance.

The Abu Dhabi adapter remains in
`benchmarks/abu_dhabi_land_use_v1/run_geospatial_kernel.py`; this package does
not include private customer data or model checkpoints. The snapshot is
included so that the benchmark scripts no longer depend on an absolute import
from the author's development checkout.
