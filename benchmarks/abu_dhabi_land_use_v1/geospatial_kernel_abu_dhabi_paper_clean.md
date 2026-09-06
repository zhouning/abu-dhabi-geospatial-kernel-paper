# Archived pre-review draft

> **Archive notice:** This file is retained for historical provenance only. Its
> legacy numbers, objective definitions and pre-review wording are not current
> evidence. Use `manuscript/manuscript.md`, the versioned `_current` reports and
> `manuscript/response_to_LUP_review.md` for the fifth-round revision.

This file is retained for provenance only and is not the revised manuscript or
an inferential results record. Use `manuscript/manuscript.md` and
`manuscript/response_to_LUP_review.md` for the post-review version. Its legacy
binary metrics and seven-objective Pareto table must not be reused.

The current release also corrects the former matched-input interpretation: the
relative-path attempt returned a console configuration error, while corrected
absolute-path 13-, 19- and 25-feature diagnostics completed for seed 31. See
`matched_input_review.md` for the archived evidence.

# Geospatial Kernel: a state–action–constraint core for urban land-cover planning

**An Abu Dhabi benchmark with conditional multi-year scenario analysis**

**Authors:** To be completed

**Manuscript status:** Nature-style research-article draft based on the public-data Abu Dhabi Land-Use Benchmark V1. This document is not an official Abu Dhabi planning forecast.

## Abstract

Urban land-change models are increasingly used to test how development demand could be distributed across space. Their practical value depends on more than pixel-level classification: a planning model must respond to explicit actions, preserve hard exclusions and carry its own state into the next simulated year. Here we study Geospatial Kernel, the algorithmic core of a Geospatial World Model, as a state–action–constraint transition system for urban land-cover planning. We evaluate it against GeoSOS-FLUS and GeoFM-LDN on a common Abu Dhabi benchmark comprising annual public land-cover products from 2017 to 2024, a 100-m grid and three random seeds. In conditional historical allocation tests, Geospatial Kernel achieved the highest change Figure of Merit (FoM) for 2023 (0.2004, compared with 0.1283 for GeoSOS-FLUS and 0.1670 for GeoFM-LDN), whereas GeoFM-LDN achieved the highest FoM for the two-step 2024 open-loop target (0.2778, compared with 0.2606 for Geospatial Kernel). This horizon dependence argues against a universal model ranking. In planner-supplied 2025–2031 stress tests, Geospatial Kernel exactly met class-count actions, preserved all hard exclusions and placed all three scenarios on the Pareto frontier under the frozen public-data objectives. At 2031, new built cells had neighbourhood compactness of 0.833–0.855 and mean distances of 323–365 m to major roads and 111–140 m to pre-existing built cells. These results support Geospatial Kernel as an auditable allocation core for conditional planning experiments. They do not establish legal land use, policy causality or the actual future of Abu Dhabi, because the benchmark uses noisy public land-cover labels, proxy constraints, frozen future drivers and synthetic scenario actions.

## Summary paragraph for nonspecialists

Cities change through many small decisions: where new buildings are permitted, which open areas are protected and how new development connects to existing infrastructure. A useful spatial model therefore has to keep track of both the current map and the action that is being tested. It must also refuse allocations that violate protected areas or the requested amount of each land-cover class. Existing models often combine these tasks in a single simulation step, which makes it difficult to audit why a cell changed or to reproduce a multi-year rollout. Here we examine Geospatial Kernel, the state–action–constraint core of a Geospatial World Model, in Abu Dhabi using public satellite-derived land-cover products and open road data. The Kernel was not the best model at every historical horizon, but it produced exact, constraint-preserving allocations and more compact, road-accessible planning patterns under three controlled growth scenarios. The resulting maps and change polygons are useful as transparent stress tests. They should not be read as official land-use forecasts until authoritative local land-use, planning and infrastructure data are available.

## Introduction

Land-cover change is a spatial process. Development demand is expressed as a quantity, but its consequences depend on where each new cell is placed relative to roads, existing built areas, ecological features and other land-cover classes. This coupling matters for urban planning because two maps with the same total built area can imply very different infrastructure requirements and environmental pressures. Cellular-automata and suitability-based models have long provided a way to distribute land demand across a map, and the FLUS family is a prominent example of a model that combines a suitability surface with neighbourhood-based allocation [1]. Global Earth-observation products now make it possible to construct annual, spatially aligned inputs for cities that lack a harmonized local data archive [2,3].

The main technical difficulty is not producing another categorical raster. It is keeping the semantics of a planning action separate from the learned transition tendency. A model may predict that a cell is likely to become built, yet the resulting map can still violate a water exclusion, miss the requested class totals or become inconsistent when the next year is simulated from the model's own output. These failure modes are particularly important when the model is used to compare scenarios rather than to reproduce one observed transition. Latent-dynamics approaches such as GeoFM-LDN can represent continuous geospatial state and condition transitions on demand, whereas traditional ANN-plus-cellular-automata systems such as GeoSOS-FLUS combine suitability with explicit neighbourhood evolution. Neither design, by itself, guarantees that action semantics, hard constraints, state persistence and evidence provenance are visible at the same execution boundary.

We address this systems problem by studying Geospatial Kernel, the core transition layer of a Geospatial World Model (GWM). The Kernel represents one simulation step as a typed state, a typed action, a transition proposal, a constraint projection and a state writeback. The learned proposal remains domain-specific; the runtime contract is domain-neutral. For Abu Dhabi land-cover planning, the proposal is a six-class probability cube, and the projection allocates only mutable cells until the action's feasible class totals are reached. This separation makes the planning operation inspectable: a reviewer can distinguish what the transition model preferred from what the constraints admitted.

We evaluate this design in a controlled public-data benchmark rather than treating the benchmark as an official data release. All candidates consume the same 100-m grid, common valid mask, annual class-count actions, hard exclusions and evaluator. The historical track uses observed target counts to isolate spatial allocation skill from demand error. The planning track starts from the observed 2024 state and applies three planner-supplied actions: compact growth, ecological priority and outward growth. We ask four questions: whether the Kernel execution contract is auditable, whether its allocation skill is competitive, whether it produces preferable feasible planning allocations and which conclusions survive label and parameter sensitivity.

The paper makes three bounded contributions. First, it gives a concrete state–action–constraint formulation for using a geospatial kernel as an algorithmic core rather than as an opaque end-to-end predictor. Second, it reports a fair, multi-horizon comparison with GeoSOS-FLUS and GeoFM-LDN, including a case in which the Kernel does not win. Third, it turns the future maps into explicit stress-test artefacts, including cumulative rasters and vectorized transition footprints, while preserving the distinction between public-data land cover and authoritative legal land use.

## Results

### A common benchmark separates allocation skill from demand assumptions

The benchmark covers the Abu Dhabi city polygon represented by OpenStreetMap relation R4479763. The canonical grid is a 475 × 360 lattice in EPSG:32640 at 100-m resolution. After the common coverage and alignment checks, 79,726 cells were used for scoring. Each cell represents 1 ha. Annual Dynamic World observations from 2017 to 2024 were harmonized to six land-cover classes: water, woody vegetation, low vegetation, wetland, built and bare. AlphaEarth annual embeddings, VIIRS night-time lights, Copernicus DEM derivatives and OpenStreetMap road distances supplied transition drivers. ESA WorldCover and public OpenStreetMap geometries supplied water, wetland and infrastructure exclusion proxies.

The comparison was designed so that differences in model output could not be attributed to different grids or target totals. GeoSOS-FLUS received the same continuous drivers and used an external ANN suitability model followed by cellular-automata allocation. GeoFM-LDN used demand-conditioned latent dynamics on the annual AlphaEarth embeddings, a semantic decoder and the constrained allocation interface. Geospatial Kernel used the same target action records and hard masks, but separated a learned per-cell transition proposal from a runtime constraint projection. All models were run with seeds 31, 47 and 73. The output audit accepted 240 prediction rasters, including 54 planning ensembles and 162 planning seed rasters, with no grid, class or hard-constraint failures.

The execution trace makes the distinction between proposal and admission explicit. A Kernel step records the source state, action, probability-cube proposal, projected state, model identity, input evidence and next-state reference. The runtime checks that the action advances the source time and that the projected raster becomes the next state. This is the operational meaning of the Kernel in this study: not a claim that all GWM domains share the same learner, but a claim that they can share an auditable execution contract.

### Historical performance is competitive but horizon-dependent

The historical track used observed target class totals. This choice removes one source of uncertainty, demand estimation, and tests how each model allocates the requested changes in space. The primary metric was change FoM, which measures the overlap between observed and simulated changes while accounting for false alarms and misses [4]. Change F1, overall accuracy and macro-F1 were secondary metrics. Values below are means with population standard deviations over the three seeds.

**Table 1 | Historical conditional allocation performance.** The 2023 target is a one-step prediction from 2022. The 2024 target is reached by a two-step open-loop rollout from 2022 without observed-state writeback. Demand total variation is the normalized class-count mismatch.

| Target year | Model | Change FoM | Change F1 | Overall accuracy | Macro-F1 | Demand total variation |
|---:|---|---:|---:|---:|---:|---:|
| 2023 | GeoSOS-FLUS | 0.1283 ± 0.0043 | 0.2273 ± 0.0068 | 0.9183 ± 0.0008 | 0.8441 ± 0.0034 | 0.002835 |
| 2023 | Geospatial Kernel | **0.2004 ± 0.0018** | **0.3338 ± 0.0026** | **0.9362 ± 0.0002** | **0.8499 ± 0.0003** | 0.000000 |
| 2023 | GeoFM-LDN | 0.1670 ± 0.0039 | 0.2862 ± 0.0058 | 0.9316 ± 0.0005 | 0.8457 ± 0.0006 | 0.000000 |
| 2024 | GeoSOS-FLUS | 0.1815 ± 0.0125 | 0.3071 ± 0.0180 | 0.8595 ± 0.0030 | 0.7483 ± 0.0062 | 0.005381 |
| 2024 | Geospatial Kernel | 0.2606 ± 0.0006 | 0.4134 ± 0.0008 | 0.8863 ± 0.0002 | 0.7670 ± 0.0004 | 0.000000 |
| 2024 | GeoFM-LDN | **0.2778 ± 0.0061** | **0.4348 ± 0.0074** | **0.8905 ± 0.0014** | **0.7693 ± 0.0011** | 0.000000 |

Geospatial Kernel improved change FoM over GeoSOS-FLUS by 0.0721 in 2023 and 0.0790 in 2024. GeoFM-LDN improved over GeoSOS-FLUS by 0.0388 and 0.0963, respectively. The ranking changed at the longer horizon: Geospatial Kernel was strongest for the 2023 one-step target, while GeoFM-LDN was strongest for the 2024 two-step target. The result is scientifically useful precisely because it prevents an over-general conclusion. Geospatial Kernel was competitive in historical allocation, but its advantage in this benchmark is not a universal claim about future prediction accuracy.

The reliability subset tells a second, less favourable story about the data. Dynamic World mean top-probability was below 0.5 for approximately 51.0% of valid cells in 2017 and 61.3% in 2024. When both origin and target cells were required to exceed 0.5, all models retained high static agreement but the change FoM became much lower because few high-confidence cells were labelled as changed. We therefore report the full-grid metric as the primary result and use the reliability subset only as a diagnostic of label volatility.

### Constraint projection produces feasible and spatially distinct planning allocations

The planning track starts from the observed 2024 state and rolls forward to 2031. It uses three declared actions. Compact growth adds 500 built and 50 green cells per year. Ecological priority adds 350 built and 150 green cells per year. Outward growth adds 1,000 built and 25 green cells per year. The 2031 targets extend the 2029–2030 annual differences and are marked as scenario targets. Exogenous drivers are held at their 2024 values, so the exercise is a controlled stress test rather than a forecast.

**Table 2 | 2031 planning objective components.** Values are three-seed means; compactness is the fraction of eight neighbouring cells that are built around a new built cell. Distances are measured in metres. “Built gain” is net built-cell change relative to 2024; “retired” counts cells that were built in 2024 and are not built in 2031. Pareto membership is conditional on the declared objective directions and public-data proxy constraints.

| Model | Scenario | Demand TV | Ecological conversion rate | New-built compactness | Distance to major road (m) | Distance to prior built (m) | Built gain (cells) | Retired built (cells) | Green gain (cells) | Pareto |
|---|---|---:|---:|---:|---:|---:|---:|---:|:---:|
| GeoSOS-FLUS | Compact | 0.00068 | 1.68% | 0.7618 ± 0.0231 | 446.1 ± 39.5 | 231.6 ± 21.3 | 3,500 | 3,436 | 296 | no |
| GeoSOS-FLUS | Ecological priority | 0.00528 | 1.77% | 0.7687 ± 0.0291 | 443.7 ± 35.9 | 212.7 ± 11.4 | 2,450 | 3,632 | 629 | no |
| GeoSOS-FLUS | Outward growth | 0.00045 | 1.31% | 0.8000 ± 0.0196 | 443.5 ± 37.2 | 255.3 ± 27.8 | 7,000 | 2,724 | 139 | no |
| Geospatial Kernel | Compact | 0.00000 | 0.00% | **0.8410 ± 0.0045** | **334.7 ± 13.4** | **116.7 ± 1.2** | 3,500 | 0 | 350 | **yes** |
| Geospatial Kernel | Ecological priority | 0.00000 | 0.00% | **0.8332 ± 0.0068** | **323.1 ± 19.5** | **111.0 ± 0.5** | 2,450 | 0 | 1,050 | **yes** |
| Geospatial Kernel | Outward growth | 0.00000 | 0.00% | **0.8545 ± 0.0047** | **365.5 ± 5.3** | **139.8 ± 1.5** | 7,000 | 0 | 175 | **yes** |
| GeoFM-LDN | Compact | 0.00000 | 0.00% | 0.7676 ± 0.0170 | 475.9 ± 35.7 | 239.7 ± 44.6 | 3,500 | 0 | 350 | no |
| GeoFM-LDN | Ecological priority | 0.00000 | 0.00% | 0.7506 ± 0.0174 | 452.1 ± 22.0 | 222.3 ± 19.8 | 2,450 | 0 | 1,050 | no |
| GeoFM-LDN | Outward growth | 0.00000 | 0.00% | 0.8117 ± 0.0236 | 507.5 ± 56.4 | 263.0 ± 71.8 | 7,000 | 0 | 175 | no |

All three Geospatial Kernel candidates were on the Pareto frontier under the frozen objective set. In the compact scenario, for example, the Kernel placed new built cells closer to major roads than either baseline and produced a higher neighbourhood compactness. The same ordering held for ecological priority and outward growth. The ecological conversion rate was zero for the Kernel and GeoFM-LDN because the projected allocations avoided conversion of the declared vegetation-origin cells in the public-data constraint system; GeoSOS-FLUS converted 1.31–1.77% of its new built cells from ecological proxy classes. These values are proxy outcomes, not estimates of statutory ecological impact.

The built-retirement contrast is also visible in the maps. GeoSOS-FLUS reclassified approximately 2,724–3,632 cells that were built in 2024 while allocating new built cells elsewhere. Geospatial Kernel and GeoFM-LDN retained the prior built class under the same scenario target counts. This difference is a model behaviour under the frozen transition matrix, not evidence that either approach reproduces actual redevelopment or demolition.

### Five-year trajectories and vectorized change footprints

The Geospatial Kernel trajectories from 2027 to 2031 show how the action changes the spatial configuration as demand accumulates. In the compact scenario, net built gain increases from 1,500 cells (15 km²) in 2027 to 3,500 cells (35 km²) in 2031, while green gain increases from 150 to 350 cells (1.5–3.5 km²). Ecological priority reaches 2,450 built cells (24.5 km²) and 1,050 green cells (10.5 km²) by 2031. Outward growth reaches 7,000 built cells (70 km²) and 175 green cells (1.75 km²). The corresponding new-built compactness rises from 0.776–0.795 in 2027 to 0.833–0.855 in 2031. Mean distance to pre-existing built cells remains lower than for the baselines, although it increases as the outward action expands.

**Table 3 | Geospatial Kernel trajectory under the three scenario actions.** Values are three-seed means. Built and green gains are cumulative net changes relative to 2024.

| Scenario | Year | Built gain (cells) | Green gain (cells) | Compactness | Distance to major road (m) | Distance to prior built (m) |
|---|---:|---:|---:|---:|---:|---:|
| Compact | 2027 | 1,500 | 150 | 0.7913 | 320.5 | 102.9 |
| Compact | 2028 | 2,000 | 200 | 0.8067 | 324.5 | 105.6 |
| Compact | 2029 | 2,500 | 250 | 0.8217 | 327.0 | 108.8 |
| Compact | 2030 | 3,000 | 300 | 0.8318 | 331.7 | 112.5 |
| Compact | 2031 | 3,500 | 350 | 0.8410 | 334.7 | 116.7 |
| Ecological priority | 2027 | 1,050 | 450 | 0.7757 | 313.3 | 102.0 |
| Ecological priority | 2028 | 1,400 | 600 | 0.8003 | 314.3 | 103.8 |
| Ecological priority | 2029 | 1,750 | 750 | 0.8141 | 316.2 | 106.3 |
| Ecological priority | 2030 | 2,100 | 900 | 0.8229 | 319.5 | 108.5 |
| Ecological priority | 2031 | 2,450 | 1,050 | 0.8332 | 323.1 | 111.0 |
| Outward growth | 2027 | 3,000 | 75 | 0.7948 | 341.5 | 107.7 |
| Outward growth | 2028 | 4,000 | 100 | 0.8147 | 348.2 | 114.9 |
| Outward growth | 2029 | 5,000 | 125 | 0.8304 | 354.4 | 123.0 |
| Outward growth | 2030 | 6,000 | 150 | 0.8444 | 359.5 | 131.5 |
| Outward growth | 2031 | 7,000 | 175 | 0.8545 | 365.5 | 139.8 |

For delivery, each model and scenario has an ensemble raster for each year 2027–2031 and a vector package containing annual and cumulative transition layers. The nine GeoPackage packages contain polygons formed by dissolving changed 100-m cells; they are therefore raster-cell transition footprints rather than parcel boundaries. This distinction matters for downstream planning because the polygons can support visual review and overlay analysis, but they do not represent cadastral lots or legally approved projects.

### Sensitivity shows a stable but not fully explained neighbourhood contribution

The historical version of this file reported an earlier binary-FoM sensitivity scan. That scan is retained for provenance only and must not be labelled strict FoM. The current strict multi-class scan is archived in `neighbourhood_weight_sensitivity.csv` and `artifacts/mechanism_ablations/neighbourhood_weight_sensitivity_report.json`; see the revised manuscript for interpretation.

## Discussion

This study positions Geospatial Kernel at the level where a Geospatial World Model becomes usable for constrained spatial reasoning. The key result is not that one classifier wins every temporal test. It is that the transition proposal and the planning admission rule can be represented separately, inspected separately and evaluated under the same action and constraint contract. In Abu Dhabi, this design produced exact target counts, zero hard-constraint violations and spatial allocations that were more compact and closer to major roads and prior built cells than the two baselines under the declared 2031 objective set.

The historical results place that planning result in context. Geospatial Kernel had the strongest one-step 2023 allocation score, but GeoFM-LDN had the strongest 2024 two-step open-loop score. A model that performs well at one horizon can lose its advantage when its own output becomes the next input. The appropriate conclusion is therefore task-specific: Geospatial Kernel is promising as a constrained allocation core, whereas GeoFM-LDN may be competitive for longer-horizon latent-state evolution in this public-data experiment. The benchmark does not support selecting one model as the universally most accurate future predictor.

The spatial objective differences are consistent with the design of the Kernel projection. The score compares the learned probability of a target class with that of the current class and adds local support from the target-class neighbourhood. The projection then resolves deficits and excesses while refusing mutable changes inside the hard mask. This makes it natural for the Kernel to retain existing built cells and to fill target classes near already compatible neighbourhoods. Yet the same interpretation remains provisional. GeoFM-LDN uses a shared constrained allocation interface in the benchmark, and GeoSOS-FLUS uses a different cellular-automata implementation. Allocator-matched ablations are needed to determine how much of the planning gap arises from the learned proposal and how much from the projection implementation.

Several limitations define the boundary of the present evidence. The six classes are remote-sensing land cover, not statutory residential, commercial or industrial land use. Dynamic World labels show substantial annual uncertainty and apparent turnover, and the public road, wetland and protected-area layers are proxies rather than Abu Dhabi planning records. Future drivers are frozen at 2024, no observed 2025–2031 labels exist for validation and the scenario targets are synthetic planner-supplied actions. The three-seed summaries quantify stochastic variation but are not population-level uncertainty intervals. Finally, the required negative controls have not yet been completed, so the paper does not attribute the observed gains to action conditioning, state writeback, neighbourhood context or hard constraints as isolated mechanisms.

These limitations also indicate a practical path to deployment. An authoritative version would replace the Dynamic World class raster with a locally validated land-use/land-cover crosswalk, replace public proxy masks with statutory water, ecological, airport, port and growth-boundary layers, and supply approved development demand and infrastructure capacities. The Kernel contract can remain unchanged while those domain inputs are upgraded. This separation is useful for governance: a new data source changes the evidence attached to a transition, rather than silently changing the meaning of the execution trace.

## Methods

### Study boundary, grid and temporal protocol

The study boundary is the polygon returned for OpenStreetMap relation R4479763, representing Abu Dhabi city. All rasters were aligned to a canonical 100-m grid in EPSG:32640 with 475 columns and 360 rows. A cell was included when its centre fell within the city polygon and when the common public-data mask indicated valid coverage. The benchmark profile records the source geometry, raster transform, dimensions and SHA-256 hashes. The effective evaluation mask contains 79,726 cells.

The observed sequence contains annual states for 2017–2024. Models were fit using the four transitions 2017→2018, 2018→2019, 2019→2020 and 2020→2021. A 2021→2022 transition was used for validation during model development. The historical test starts from 2022 and evaluates 2023 and 2024 in an open-loop rollout without observed-state writeback. The planning test starts from the observed 2024 state and recursively generates 2025–2031 under each scenario action.

### Public data and class semantics

Dynamic World V1 provides annual scene-argmax labels and mean top-class probabilities [2]. The nine Dynamic World labels were crosswalked to six canonical classes: water (source 0), woody vegetation (1), low vegetation (2, 4 and 5), wetland (3), built (6) and bare (7). Source class 8 was excluded. The resulting label is explicitly treated as land cover. No residential, commercial or industrial category is inferred from the raster labels.

Annual 64-dimensional AlphaEarth embeddings were spatially averaged to the canonical grid and locally L2-normalized. Monthly VIIRS night-time-light radiance was averaged by year. Copernicus DEM supplied elevation and a finite-difference slope derivative. OpenStreetMap road geometries were rasterized into distance-to-road and distance-to-major-road surfaces. ESA WorldCover 2021 supplied public water and wetland/mangrove constraint proxies [5]. All dynamic and static layers were checked for exact CRS, transform, width and height agreement.

### Geospatial Kernel state, action and transition proposal

Let $S_t(i)$ denote the six-class state at valid cell $i$, $A_t$ the action for the interval $t\rightarrow t+1$, and $X_t$ the aligned driver layers. The Kernel separates a proposal from a projection:

$$
Q_t(i,c)=p_\theta\big(c\mid x_i(S_t,X_t)\big),
\qquad
S_{t+1}=\Pi_{\mathcal C,A_t}(Q_t,S_t).
$$

The feature vector $x_i$ contains 25 values: six one-hot current-class indicators; twelve neighbourhood proportions, comprising 3 × 3 and 7 × 7 windows for each of the six classes; and seven continuous variables, namely normalized row and column coordinates, clipped elevation, clipped slope, log-transformed VIIRS radiance, log distance to roads and log distance to major roads. A histogram gradient-boosting classifier estimates the six-class probability vector. It uses learning rate 0.08, 120 iterations, at most 31 leaf nodes, minimum leaf size 40 and L2 regularization 1.0.

Training samples combine all changed valid cells and a 20% random sample of stable valid cells in each fit transition. The sample weight is the product of a change emphasis, $1+5\mathbf{1}(S_t\ne S_{t+1})$, and a confidence factor, $0.5+\min(r_t,r_{t+1})$, where $r$ is the Dynamic World mean top probability. The target years 2023 and 2024 are not used during fitting or model selection. Across the three seeds, each fitted model used 71,892–72,202 pixel rows and all six classes.

### Constraint projection and state writeback

For a mutable source cell $i$ of class $s$ and target class $c$, the base allocation score is

$$
q_{i,s\rightarrow c}=\log p_\theta(c\mid x_i)-\log p_\theta(s\mid x_i)+\lambda\rho^{(7)}_{i,c},
$$

where $\rho^{(7)}_{i,c}$ is the 7 × 7 fraction of neighbouring cells currently in class $c$, and $\lambda=0.35$. The algorithm computes class deficits and excesses from the action's feasible target counts, ranks all admissible source–target candidates by $q$, and changes cells in descending order until all deficits and excesses are zero. Permanent water and the protected wetland/ecological mask are held fixed. If the counts cannot be satisfied without changing a hard-exclusion cell, the step fails closed rather than silently violating the action.

The projected raster is written as the next `KernelState`. Every step records a state reference, action evidence, model version, parameter reference, projection status and diagnostic counts. The runtime checks domain identity, source-time consistency and action time advancement. This execution contract is the Geospatial Kernel's algorithmic contribution; the Abu Dhabi adapter supplies the land-cover-specific features, learner and constraint masks.

### Baselines and common evaluator

GeoSOS-FLUS was run through the external FLUS console using seven continuous drivers: coordinates, elevation, slope, VIIRS radiance, distance to roads and distance to major roads. Its ANN suitability surface was passed to a cellular-automata allocation stage with the common class totals and public hard mask.

GeoFM-LDN was trained as a demand-conditioned latent-dynamics network on AlphaEarth embeddings. A logistic semantic decoder maps the predicted embedding to six class probabilities, and the constrained allocation step converts those probabilities to a categorical raster. The latent and categorical states are both recursively carried into the next year. GeoFM-LDN is treated as an internal benchmark implementation in this manuscript; no external publication or performance claim is attributed to the name.

The common evaluator computes actual class counts, normalized demand total variation, hard-mask violations, change FoM, change F1, overall accuracy and macro-F1 for historical runs. For planning runs it additionally computes ecological conversion, new-built neighbourhood compactness, component counts, distances to roads and prior built cells, infrastructure proxy distance and built retirement. Pareto membership is calculated over seven declared objective directions: minimize demand total variation, ecological conversion, major-road distance and prior-built distance; maximize compactness, built gain and green gain.

### Scenario actions and uncertainty

The compact, ecological-priority and outward-growth actions are stored in `planning_scenarios_public_2025_2031.json`. Each action supplies feasible class totals for 2025–2031. The 2031 totals are an explicit extension of the previous annual difference and are not derived from an official population, housing or infrastructure forecast. Future exogenous rasters are held at their 2024 values. Each candidate is run at seeds 31, 47 and 73, and planning tables report arithmetic means and population standard deviations. No p-values are reported because the three seeds describe computational variability, not independent field samples.

### Change polygons and reproducibility

For each model–scenario pair, annual and cumulative differences from the 2024 raster are extracted as changed 100-m cells and dissolved into GeoPackage layers. The output manifest covers 45 ensemble rasters for 2027–2031 and nine vector packages. Every published raster passed the grid, class, nodata and hard-constraint audit. The vector layers preserve the raster-cell geometry and should not be interpreted as cadastral parcels.

## Data and code availability

The public-data benchmark manifests, protocols, scripts, reports and generated delivery artefacts are organized under `benchmarks/abu_dhabi_land_use_v1/` in the accompanying repository. The main evidence files are:

- `comparison_report.json` and `comparison_report.md` for historical metrics;
- `planning_comparison_report_public_2025_2031.json` and its Markdown rendering for 2031 planning objectives;
- `planning_scenario_report_public_2025_2031.json` for per-seed rollout traces;
- `planning_public_2025_2031_delivery_manifest.json` for raster and vector delivery;
- `output_audit.json` for the 240-raster audit;
- `data_audit.json`, `protocol.json`, `gee_input_manifest.json` and `osm_input_manifest.json` for data provenance;
- `run_geospatial_kernel.py` and `data_agent/uwm/geospatial_kernel/runtime.py` for the Kernel adapter and runtime contract.

Large raster files are tracked through repository-relative paths and SHA-256 manifests rather than embedded in this manuscript. A public repository URL and archival DOI should be added after the authors complete release review. No private database address, credential or client-only service is required to reproduce the public-data benchmark.

## References

1. Liu, X. et al. A future land use simulation model (FLUS) for simulating multiple land use scenarios by coupling human and natural effects. *Landscape and Urban Planning* **168**, 94–116 (2017). https://doi.org/10.1016/j.landurbplan.2017.09.019
2. Brown, C. F. et al. Dynamic World, Near real-time global 10 m land use land cover mapping. *Scientific Data* **9**, 251 (2022). https://doi.org/10.1038/s41597-022-01307-4
3. Gorelick, N. et al. Google Earth Engine: Planetary-scale geospatial analysis for everyone. *Remote Sensing of Environment* **202**, 18–27 (2017). https://doi.org/10.1016/j.rse.2017.06.031
4. Pontius, R. G. Jr & Millones, M. Death to Kappa: birth of quantity disagreement and allocation disagreement for accuracy assessment. *International Journal of Remote Sensing* **32**, 4407–4429 (2011). https://doi.org/10.1080/01431161.2011.552923
5. Zanaga, D. et al. ESA WorldCover 10 m 2021 v200. Zenodo (2022). https://doi.org/10.5281/zenodo.7254221
6. OpenStreetMap contributors. OpenStreetMap data, Abu Dhabi relation R4479763 and Geofabrik GCC extract, accessed 31 July 2026. https://www.openstreetmap.org

## Figure legends

![Figure 1 draft asset: benchmark and experiment design](figures/fig04_experiment_design.png)

**Figure 1 | Benchmark and Geospatial Kernel execution contract.** Public annual land-cover, embedding, night-light, terrain and road layers are aligned to a common 100-m Abu Dhabi grid. Each model receives the same state, action and hard exclusions. The Geospatial Kernel makes the transition proposal, constraint projection and state writeback explicit. Historical allocation, open-loop rollout and planning tracks are evaluated by one audit contract. The current draft asset is `fig04_experiment_design.png`; its Chinese labels must be translated or redrawn before submission.

![Figure 2 draft asset: historical validation](figures/fig07_historical_metrics.png)

**Figure 2 | Historical validation across horizons.** Change FoM, change F1, overall accuracy and macro-F1 for the 2023 one-step target and 2024 two-step open-loop target. Bars or points show three-seed means; error bars should show population standard deviations. The key comparison is the horizon-dependent ranking: Geospatial Kernel leads in 2023, whereas GeoFM-LDN leads in 2024. Draft asset: `fig07_historical_metrics.png`.

![Figure 3 draft asset: conditional planning objectives](figures/fig08_planning_metrics.png)

**Figure 3 | Conditional planning objective comparison at 2031.** Objective components for compact, ecological-priority and outward-growth actions. Lower is preferred for demand total variation, ecological conversion and distances; higher is preferred for compactness, built gain and green gain. The Geospatial Kernel candidates are on the frozen Pareto frontier. Draft asset: `fig08_planning_metrics.png`.

![Figure 4 draft asset: spatial allocations and change footprints](../abu_dhabi_land_use_v1/planning_2030_comparison.png)

**Figure 4 | Spatial allocations and change footprints.** Three rows show compact, ecological-priority and outward-growth actions; columns show GeoSOS-FLUS, Geospatial Kernel and GeoFM-LDN. Colours distinguish retained water/wetland, retained vegetation, new built cells, retired built cells and bare/other cells. The map is an ensemble or majority raster at 2030 in the current draft. Draft asset: `planning_2030_comparison.png`. The public vector packages contain annual and cumulative transition layers for 2027–2031.

## Supplementary information outline

- **Supplementary Note 1:** Complete data crosswalk, quality metrics and public/proxy status.
- **Supplementary Note 2:** Kernel runtime schemas, audit fields and adapter boundary.
- **Supplementary Table S1:** Full 2025–2031 model–scenario objective matrix with per-seed values.
- **Supplementary Table S2:** Neighbourhood-weight sensitivity at 0, 0.175, 0.35 and 0.7.
- **Supplementary Table S3:** Raster and vector delivery audit, hashes and layer counts.
- **Supplementary Figure S1:** Dynamic World confidence and high-confidence change sensitivity.
- **Supplementary Figure S2:** Historical maps and change-error maps for 2024.
- **Supplementary Figure S3:** Driver layers and experiment design in English.

---
