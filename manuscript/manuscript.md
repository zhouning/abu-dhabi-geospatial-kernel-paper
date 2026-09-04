# Geospatial Kernel: a state–action–constraint core for urban land-cover planning

**An Abu Dhabi benchmark with conditional multi-year scenario analysis**

**Author:** Ning Zhou  
**Affiliation:** Beijing Freedo Technology Co., Ltd.  
**Corresponding author:** Ning Zhou

This study is not an official Abu Dhabi planning forecast. Correspondence: Ning Zhou, Beijing Freedo Technology Co., Ltd.

## Abstract

Urban land-change models test how development demand may be distributed across space. Their planning value depends on explicit actions, hard constraints and consistent multi-year state transitions. We examine Geospatial Kernel, the algorithmic core of a Geospatial World Model, as an auditable state–action–constraint transition system for urban land-cover allocation. The Abu Dhabi benchmark specifies annual public land-cover products from 2017–2024, a 100-m grid, three computational seeds, destination-correct multi-class change Figure of Merit, persistence and minimum-change controls, spatial-block bootstrap intervals, and a planning objective set spanning ecological conversion, accessibility, leapfrog morphology and built-state stability. The implementation contribution is an inspectable proposal–projection–writeback execution boundary with fail-closed data and output audits. The current checkout is intentionally evidence-limited: the aligned raster bundle, GeoFM-LDN checkpoint, FLUS runtime and independent change-validation layer are not available, so no numerical ranking, Pareto frontier or Abu Dhabi forecast is claimed. The benchmark defines the analyses required for a defensible data-complete study and keeps public land-cover stress tests separate from authoritative statutory land use.

## Highlights

- Geospatial Kernel separates transition proposals from constraint projection.
- The execution contract separates learned proposals from constrained admission.
- Spatial-block uncertainty and paired model contrasts are prespecified.
- Four planning dimensions are reported without a weighted composite score.
- Public-data scenarios are stress tests, not statutory Abu Dhabi forecasts.

## Keywords

Geospatial World Model; land-cover change; constrained allocation; cellular automata; Abu Dhabi; scenario planning

## Introduction

Land-cover change is a spatial process. Development demand is expressed as a quantity, but its consequences depend on where each new cell is placed relative to roads, existing built areas, ecological features and other land-cover classes. This coupling matters for urban planning because two maps with the same total built area can imply very different infrastructure requirements and environmental pressures. Cellular-automata and suitability-based models have long provided a way to distribute land demand across a map, including CLUE-S, SLEUTH, Dinamica EGO, FLUS, local-attribute urban CA models and more recent patch-generating or deep-learning CA models (Verburg et al., 2002; Silva and Clarke, 2002; Soares-Filho et al., 2002; Lau and Kam, 2005; Liu et al., 2017; Liang et al., 2021). Global Earth-observation products now make it possible to construct annual, spatially aligned inputs for cities that lack a harmonized local data archive (Brown et al., 2022; Gorelick et al., 2017).

Validation studies have also shown that agreement in unchanged cells can mask poor allocation of actual change. Quantity and allocation disagreement, destination-specific transition scores and explicit calibration/validation protocols are therefore preferable to a single overall-accuracy number (Pontius et al., 2008; Pontius and Millones, 2011; van Vliet et al., 2011, 2016). This distinction is central here because the benchmark uses noisy annual labels and tests both one-step allocation and recursive rollout.

The main technical difficulty is not producing another categorical raster. It is keeping the semantics of a planning action separate from the learned transition tendency. A model may predict that a cell is likely to become built, yet the resulting map can still violate a water exclusion, miss the requested class totals or become inconsistent when the next year is simulated from the model's own output. These failure modes are particularly important when the model is used to compare scenarios rather than to reproduce one observed transition. Latent-dynamics approaches such as GeoFM-LDN can represent continuous geospatial state and condition transitions on demand, whereas traditional ANN-plus-cellular-automata systems such as GeoSOS-FLUS combine suitability with explicit neighbourhood evolution. Neither design, by itself, guarantees that action semantics, hard constraints, state persistence and evidence provenance are visible at the same execution boundary.

We address this systems problem by studying Geospatial Kernel, the core transition layer of a Geospatial World Model (GWM). The Kernel represents one simulation step as a typed state, a typed action, a transition proposal, a constraint projection and a state writeback. The learned proposal remains domain-specific; the runtime contract is domain-neutral. For Abu Dhabi land-cover planning, the proposal is a six-class probability cube, and the projection allocates only mutable cells until the action's feasible class totals are reached. This separation makes the planning operation inspectable: a reviewer can distinguish what the transition model preferred from what the constraints admitted.

We evaluate this design in a controlled public-data benchmark rather than treating the benchmark as an official data release. All candidates consume the same 100-m grid, common valid mask, annual class-count actions, hard exclusions and evaluator. The historical track uses observed target counts to isolate spatial allocation skill from demand error. The planning track starts from the observed 2024 state and applies three planner-supplied actions: moderate growth, green-priority growth and high outward growth. Abu Dhabi Plan 2030 provides an institutional planning context for discussing urban structure, but the numerical actions in this benchmark are not calibrated to that plan or to an official population forecast (Abu Dhabi Urban Planning Council, 2007). We ask four questions: whether the Kernel execution contract is auditable, whether its allocation skill is competitive, whether it produces feasible and spatially distinct allocations and which conclusions survive label and parameter sensitivity.

The paper makes three bounded contributions. First, it gives a concrete state–action–constraint formulation for using a geospatial kernel as an algorithmic core rather than as an opaque end-to-end predictor. Second, it reports a multi-horizon pipeline comparison with GeoSOS-FLUS and GeoFM-LDN, including a case in which the Kernel does not win, while making the input imbalance explicit. Third, it turns the future maps into explicit stress-test artefacts, including cumulative rasters and vectorized transition footprints, while preserving the distinction between public-data land cover and authoritative legal land use.

## Methods

### Study boundary, grid and temporal protocol

The study boundary is the polygon returned for OpenStreetMap relation R4479763, representing Abu Dhabi city. All rasters were aligned to a canonical 100-m grid in EPSG:32640 with 475 columns and 360 rows. A cell was included when its centre fell within the city polygon and when the common public-data mask indicated valid coverage. The benchmark profile records the source geometry, raster transform, dimensions and SHA-256 hashes. The effective evaluation mask contains 79,726 cells.

The observed sequence contains annual states for 2017–2024. Models were fit using the four transitions 2017→2018, 2018→2019, 2019→2020 and 2020→2021. A 2021→2022 transition was used for validation during model development. The historical test starts from 2022 and evaluates 2023 and 2024 in an open-loop rollout without observed-state writeback. The planning test starts from the observed 2024 state and recursively generates 2025–2031 under each scenario action.

### Public data and class semantics

Dynamic World V1 provides annual scene-argmax labels and mean top-class probabilities (Brown et al., 2022). The nine Dynamic World labels were crosswalked to six canonical classes: water (source 0), woody vegetation (1), low vegetation (2, 4 and 5), wetland (3), built (6) and bare (7). Source class 8 was excluded. The resulting label is explicitly treated as land cover. No residential, commercial or industrial category is inferred from the raster labels.

Annual 64-dimensional AlphaEarth embeddings were spatially averaged to the canonical grid and locally L2-normalized. Monthly VIIRS night-time-light radiance was averaged by year. Copernicus DEM supplied elevation and a finite-difference slope derivative. OpenStreetMap road geometries were rasterized into distance-to-road and distance-to-major-road surfaces. ESA WorldCover 2021 supplied public water and wetland/mangrove constraint proxies (Zanaga et al., 2022). All dynamic and static layers were checked for exact CRS, transform, width and height agreement.

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

GeoSOS-FLUS was run through the external FLUS console using seven continuous drivers: normalized row and column coordinates, elevation, slope, VIIRS radiance, distance to roads and distance to major roads. Its ANN suitability surface was passed to a cellular-automata allocation stage with the common class totals and public hard mask. The archived run used one 2021 training year, eight ANN hidden neurons, a 3 × 3 CA neighbourhood, neighbourhood strength 1.0, acceleration factor 0.1 and 1,000 iterations. Its frozen transition matrix protected water and wetland but did not prohibit built-to-non-built transitions; this configuration is recorded as a baseline limitation rather than a calibrated Abu Dhabi model.

GeoFM-LDN (Geospatial Foundation-Model Latent Dynamics Network) was trained as a demand-conditioned latent-dynamics network on AlphaEarth embeddings. A logistic semantic decoder maps the predicted embedding to six class probabilities, and the constrained allocation step converts those probabilities to a categorical raster. The latent and categorical states are both recursively carried into the next year. GeoFM-LDN is an internal benchmark implementation in this manuscript; the name describes its architecture and does not attribute an external publication or performance claim.

The common evaluator computes actual class counts, normalized demand total variation, hard-mask violations, strict multi-class change FoM, binary change FoM, change F1, overall accuracy and macro-F1 for historical runs. The strict FoM counts a hit only when the predicted destination class equals the observed destination class; wrong destination changes are retained in the denominator. It also generates persistence and minimum-change zero controls, spatial-block bootstrap intervals and paired model-difference intervals for strict FoM, overall accuracy and macro-F1. For planning runs it additionally computes ecological conversion, new-built neighbourhood fraction, built component counts, built components per 1,000 valid pixels, a 500-m leapfrog rate, distances to roads and prior built cells, infrastructure proxy distance and built retirement. Pareto membership is calculated over four distinct dimensions: ecological conversion proxy, major-road accessibility, leapfrog morphology and built-state stability.

### Scenario actions and uncertainty

The moderate-growth, green-priority-growth and high-outward-growth actions are stored in the tracked `planning_scenarios_public_2025_2031.json` manifest; the legacy `compact` path identifier is retained only for artifact compatibility. Each action supplies feasible class totals for 2025–2031. The 2031 totals are an explicit extension of the previous annual difference and are not derived from an official population, housing or infrastructure forecast. Future exogenous rasters are held at their 2024 values. The green-priority action is not a water-budget model. Each candidate is run at seeds 31, 47 and 73, and planning tables report arithmetic means and population standard deviations. No p-values are reported because the three seeds describe computational variability, not independent field samples.

### Change polygons and reproducibility

For each model–scenario pair, annual and cumulative differences from the 2024 raster are extracted as changed 100-m cells and dissolved into GeoPackage layers. The public delivery manifest covers 45 ensemble rasters for 2027–2031 and nine vector packages. The audit script now reports `INCOMPLETE_INPUTS` or `FAIL` when source rasters, reports or vectors are absent; a PASS cannot be inferred from a stale audit file. The vector layers preserve raster-cell geometry and should not be interpreted as cadastral parcels.

## Results

### A common benchmark separates allocation skill from demand assumptions

The benchmark covers the Abu Dhabi city polygon represented by OpenStreetMap relation R4479763. The canonical grid is a 475 × 360 lattice in EPSG:32640 at 100-m resolution. After the common coverage and alignment checks, 79,726 cells were used for scoring. Each cell represents 1 ha. Annual Dynamic World observations from 2017 to 2024 were harmonized to six land-cover classes: water, woody vegetation, low vegetation, wetland, built and bare. AlphaEarth annual embeddings, VIIRS night-time lights, Copernicus DEM derivatives and OpenStreetMap road distances supplied transition drivers. ESA WorldCover and public OpenStreetMap geometries supplied water, wetland and infrastructure exclusion proxies.

The comparison shared the canonical grid, origin states, target actions, hard masks and evaluator, but the original public-data run was not information-balanced. GeoSOS-FLUS used seven continuous drivers in its external ANN suitability model, whereas Geospatial Kernel used 25 features including current-class indicators and neighbourhood proportions; GeoFM-LDN used AlphaEarth latent embeddings. We therefore treat the historical ranking as a pipeline comparison, not evidence that one learner is intrinsically superior. A matched-input FLUS rerun is required before making model-level superiority claims. All models used seeds 31, 47 and 73. The earlier output audit reported 240 seed and ensemble rasters for a separate 2025–2030 run; the public 2025–2031 delivery is a separate artifact set and must be audited separately.

The execution trace makes the distinction between proposal and admission explicit. A Kernel step records the source state, action, probability-cube proposal, projected state, model identity, input evidence and next-state reference. The runtime checks that the action advances the source time and that the projected raster becomes the next state. This is the operational meaning of the Kernel in this study: not a claim that all GWM domains share the same learner, but a claim that they can share an auditable execution contract. The shared inputs and execution boundary are summarized in Fig. 1.

### Results status and prespecified reporting

The historical track uses observed target class totals to isolate spatial
allocation from demand estimation. The primary metric is strict multi-class
change FoM: a hit requires the predicted destination class to equal the
observed destination class, while wrong destination changes remain in the
denominator (Pontius et al., 2008). Overall accuracy, macro-F1, change F1 and
binary FoM are secondary diagnostics. Uncertainty is estimated with an
8 × 8-pixel spatial-block bootstrap, and model contrasts are computed from the
same resampled blocks for each frozen seed. Persistence and random
minimum-change allocation are prespecified controls.

The planning track starts from the observed 2024 state and applies three
synthetic class-count actions through 2031. The four Pareto dimensions are
ecological conversion rate (a public proxy), mean distance of new built cells
to major roads, 500-m leapfrog rate and removed built pixels. Built-component
density, prior-built distance, demand error and neighbourhood fraction remain
descriptive diagnostics. No weighted composite score is used.

No numerical result is reported in this version because the checkout lacks the
aligned 2017–2024 raster bundle, current model predictions, GeoFM-LDN
checkpoint, FLUS runtime and independent 2023–2024 change-validation layer.
The compiler and audit scripts fail closed when any of these inputs are absent;
they cannot emit a model ranking, confidence interval, Pareto frontier or
future forecast from the legacy artefacts. Once the data-complete run is
available, the numerical tables and figures should be generated directly from
the versioned reports and their hashes, with no manual transcription.

### Sensitivity shows a stable but not fully explained neighbourhood contribution

The base Kernel allocation score adds a 7 × 7 target-class neighbourhood fraction with weight 0.35. A future data-complete run will vary this weight under the same spatial-block uncertainty procedure. Because the neighbourhood fraction appears in both the proposal features and the allocation score, it remains a descriptive diagnostic rather than a standalone compactness objective.

### Mechanism controls separate learned proposal from runtime projection

Mechanism controls are specified to separate the learned proposal from runtime
projection, hard constraints and recursive writeback. They are not causal
policy experiments. A data-complete run will report each control with the
strict evaluator, spatial-block intervals and a matched-input baseline; no
legacy ablation number is carried into the present manuscript.

## Discussion

This study positions Geospatial Kernel as a candidate execution layer for constrained spatial reasoning. The defensible contribution is that a transition proposal and a planning admission rule can be represented and inspected separately. The repository currently supports protocol and code review, but it does not contain the aligned rasters and model artifacts required to re-audit numerical outputs. We therefore make no quantitative superiority or compactness claim.

The proposed mechanism is explicit: the score compares the learned probability of a target class with that of the current class and adds local support from the target-class neighbourhood. The projection then resolves deficits and excesses while refusing mutable changes inside the hard mask. This can preserve existing built cells when demand is non-decreasing, but that outcome is a structural consequence of the projection and should not be interpreted as evidence of redevelopment realism. Allocator-matched controls are required before attributing morphology to the learned proposal.

Several limitations define the boundary of the present evidence. The six classes are remote-sensing land cover, not statutory residential, commercial or industrial land use. Dynamic World labels show substantial annual uncertainty and apparent turnover, and the public road, wetland and protected-area layers are proxies rather than Abu Dhabi planning records. Future drivers are frozen at 2024, no observed 2025–2031 labels exist for validation and the scenario targets are synthetic planner-supplied actions. The three-seed summaries quantify stochastic variation but are not population-level uncertainty intervals. The completed controls are public-data stress tests with matched seeds rather than randomized interventions on real planning decisions, and several variants alter more than one implementation detail at a time. We therefore report them as evidence consistent with the execution contract rather than as causal attribution.

These limitations also indicate a practical path to deployment. An authoritative version would replace the Dynamic World class raster with a locally validated land-use/land-cover crosswalk, replace public proxy masks with statutory water, ecological, airport, port and growth-boundary layers, and supply approved development demand and infrastructure capacities. The Kernel contract can remain unchanged while those domain inputs are upgraded. This separation is useful for governance: a new data source changes the evidence attached to a transition, rather than silently changing the meaning of the execution trace.

## Data availability

The public-data benchmark manifests, protocols, reports and generated delivery artefacts are organized under `benchmarks/abu_dhabi_land_use_v1/` in the accompanying repository. The main evidence files are:

- `comparison_report_current.json` and `comparison_report_current.md` for historical metrics when a data-complete rerun is available;
- `planning_comparison_report_public_2025_2031_current.json` and its Markdown rendering for 2031 planning objectives;
- `planning_scenario_report_public_2025_2031_current.json` for per-seed rollout traces;
- `planning_public_2025_2031_delivery_manifest.json` for raster and vector delivery;
- `output_audit.json` for the versioned raster audit; the revised audit does not treat the earlier 240-raster 2025–2030 record as evidence for the separate 2025–2031 delivery;
- `data_audit.json`, `protocol.json`, `gee_input_manifest.json` and `osm_input_manifest.json` for data provenance;
- Large raster files are tracked through repository-relative paths and SHA-256 manifests rather than embedded in this manuscript. The present checkout does not contain the complete `artifacts/gee`, `artifacts/bundle` or historical prediction rasters, so the experiment cannot be rerun from this repository alone. No private database address, credential or client-only service is required for the intended public-data benchmark, but the missing artifacts must be restored before a reproducibility claim is made.

## Code availability

The analysis scripts, a vendored Geospatial Kernel runtime snapshot, benchmark protocol and figure-generation code are maintained in the accompanying repository. Principal entry points are listed separately to keep the manuscript readable:

- `run_geospatial_kernel.py` for the Kernel historical run;
- `data_agent/uwm/geospatial_kernel/runtime.py` for the vendored runtime snapshot;
- `render_nature_figures.py` for publication artwork.

GeoFM-LDN code and checkpoints are not included in this repository and remain a reproducibility blocker. A public release URL, archival DOI and corresponding-author e-mail should be added at submission.

## Declarations

**Funding.** No external funding was received for this study.

**Competing interests.** Ning Zhou is employed by Beijing Freedo Technology Co., Ltd., which develops geospatial-world-model software. The author declares no other competing financial or personal interests.

**CRediT author statement.** Ning Zhou: Conceptualization, methodology, software, data curation, formal analysis, visualization, writing—original draft, writing—review and editing.

**Acknowledgements.** None.

**Ethics statement.** Not applicable; the study used geospatial raster, vector and derived public-data products and did not involve human or animal participants.

## References

Abu Dhabi Urban Planning Council. (2007). Plan Abu Dhabi 2030: urban structure framework plan. Abu Dhabi, United Arab Emirates.

Brown, C. F., et al. (2022). Dynamic World, near real-time global 10 m land use land cover mapping. *Scientific Data*, 9, 251. https://doi.org/10.1038/s41597-022-01307-4

Burton, E. (2000). The compact city: just or just compact? A preliminary analysis. *Urban Studies*, 37, 1969–2006. https://doi.org/10.1080/00420980050162184

Gorelick, N., et al. (2017). Google Earth Engine: planetary-scale geospatial analysis for everyone. *Remote Sensing of Environment*, 202, 18–27. https://doi.org/10.1016/j.rse.2017.06.031

Lau, K. H., & Kam, B. H. (2005). A cellular automata model for urban land-use simulation. *Environment and Planning B: Planning and Design*, 32, 247–263. https://doi.org/10.1068/b31110

Liang, X., et al. (2021). A patch-generating land use simulation model integrating multisource data for urban growth simulation. *Landscape and Urban Planning*, 214, 104157. https://doi.org/10.1016/j.landurbplan.2021.104157

Liu, X., et al. (2017). A future land use simulation model (FLUS) for simulating multiple land use scenarios by coupling human and natural effects. *Landscape and Urban Planning*, 168, 94–116. https://doi.org/10.1016/j.landurbplan.2017.09.019

OpenStreetMap contributors. (2026). OpenStreetMap data, Abu Dhabi relation R4479763 and Geofabrik GCC extract, accessed 31 July 2026. https://www.openstreetmap.org

Pontius, R. G., Jr., Boersma, W., Castella, J.-C., et al. (2008). Comparing the input, output, and validation maps for several models of land change. *The Annals of Regional Science*, 42, 11–37. DOI: 10.1007/s00168-007-0138-2

Pontius, R. G., Jr., & Millones, M. (2011). Death to Kappa: birth of quantity disagreement and allocation disagreement for accuracy assessment. *International Journal of Remote Sensing*, 32, 4407–4429. DOI: 10.1080/01431161.2011.552923

Silva, E. A., & Clarke, K. C. (2002). Calibration of the SLEUTH urban growth model for Lisbon and Porto, Portugal. *Computers, Environment and Urban Systems*, 26, 525–552. https://doi.org/10.1016/S0198-9715(01)00017-8

Soares-Filho, B. S., Cerqueira, G. C., & Pennachin, C. L. (2002). DINAMICA—a stochastic cellular automata model designed to simulate the landscape dynamics in an Amazonian colonization frontier. *Ecological Modelling*, 154, 217–235. https://doi.org/10.1016/S0304-3800(02)00059-5

van Vliet, J., Bregt, A. K., Rietveld, P., & Verburg, P. H. (2011). Modeling land-use change with cellular automata: Issues and recommendations. *Journal of Land Use Science*, 6, 247–265. https://doi.org/10.1080/1747423X.2011.562018

van Vliet, J., Bregt, A. K., Brown, D. G., van Delden, H., Heckbert, S., & Verburg, P. H. (2016). A review of current calibration and validation practices in land-change modeling. *Environmental Modelling & Software*, 82, 174–182. https://doi.org/10.1016/j.envsoft.2016.04.017

Verburg, P. H., et al. (2002). Modeling the spatial dynamics of regional land use: the CLUE-S model. *Environmental Management*, 30, 391–405. https://doi.org/10.1007/s00267-002-2631-x

Zanaga, D., et al. (2022). ESA WorldCover 10 m 2021 v200. Zenodo. https://doi.org/10.5281/zenodo.7254221

## Figure legends

![Figure 1: benchmark and execution contract](figures/fig01_benchmark_contract.png)

**Figure 1 | Benchmark and Geospatial Kernel execution contract.** Public annual land-cover, embedding, night-light, terrain and road layers are aligned to a common 100-m Abu Dhabi grid. Each model receives the same state, action and public proxy exclusions. The Geospatial Kernel exposes a learned proposal, constraint projection and state writeback. Historical, open-loop and planning tracks use one audit contract. The schematic does not imply statutory planning boundaries.

Figures 2–5 are intentionally withheld from the formal manuscript until the
strict evaluator, spatial-block uncertainty, matched-input baseline and
independent change validation have been run. Existing image files remain in
the repository as non-inferential lineage artefacts and are not cited here.

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
