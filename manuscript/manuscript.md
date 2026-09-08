## Abstract

Urban land-change models are often evaluated against annual labels whose reliability is not spatially uniform. We present an auditable protocol for testing constrained spatial allocation under that uncertainty, using Geospatial Kernel, the algorithmic core of a Geospatial World Model, as the focal execution layer. The Abu Dhabi public-data benchmark uses annual 100-m land-cover products from 2017–2024, three computational seeds, destination-correct multi-class change Figure of Merit (FoM), spatial-block bootstrap contrasts and explicit state–action–constraint traces. In the primary unmatched-pipeline test, strict FoM was 0.1961 for Geospatial Kernel, 0.1256 for a GeoSOS-derived FLUS-style ANN–CA console and 0.1619 for GeoFM-LDN in 2023; GeoFM-LDN led after recursive two-step rollout in 2024. A separate leakage-controlled expanding-window analysis, excluding the later road snapshot, gave Kernel FoM values of 0.2595, 0.0724, 0.2116 and 0.1816 for the four one-step targets from 2021 to 2024, exceeding a random minimum-change allocator in every window. However, an external-product diagnostic using ESA WorldCover 2020/2021 did not validate change location: Kernel built-gain F1 was 0 across four built-fraction thresholds, while Dynamic World-to-WorldCover built-gain F1 was only 0.0111–0.0192. The planning track is therefore reported as scenario stress testing, not official forecasting. The protocol's principal contribution is an inspectable proposal–projection–writeback boundary; the experiments support conditional allocation auditability, not verified prediction of Abu Dhabi's actual future.

## Highlights

- Geospatial Kernel separates transition proposals from constrained admission.
- Typed state–action–constraint traces make recursive updates auditable.
- Rolling-origin and spatial-block tests expose temporal variability.
- WorldCover disagreement bounds claims of real built-change prediction.
- Planning outputs are scenario stress tests, not statutory Abu Dhabi forecasts.

## Keywords

Geospatial World Model; land-cover change; constrained allocation; cellular automata; Abu Dhabi; scenario planning

## Introduction

Land-cover change is a spatial process. Development demand is expressed as a quantity, but its consequences depend on where each new cell is placed relative to roads, existing built areas, ecological features and other land-cover classes. This coupling matters for urban planning because two maps with the same total built area can imply very different infrastructure requirements and environmental pressures. Cellular-automata and suitability-based models have long provided a way to distribute land demand across a map, including CLUE-S, SLEUTH, Dinamica EGO, FLUS, local-attribute urban CA models and more recent patch-generating or deep-learning CA models (Verburg et al., 2002; Silva and Clarke, 2002; Soares-Filho et al., 2002; Lau and Kam, 2005; Liu et al., 2017; Liang et al., 2021). Global Earth-observation products now make it possible to construct annual, spatially aligned inputs for cities that lack a harmonized local data archive (Brown et al., 2022; Gorelick et al., 2017).

Validation studies have also shown that agreement in unchanged cells can mask poor allocation of actual change. Quantity and allocation disagreement, destination-specific transition scores and explicit calibration/validation protocols are therefore preferable to a single overall-accuracy number (Pontius et al., 2008; Pontius and Millones, 2011; van Vliet et al., 2011, 2016). This distinction is central here because the benchmark uses noisy annual labels and tests both one-step allocation and recursive rollout.

The main technical difficulty is not producing another categorical raster. It is keeping the semantics of a planning action separate from the learned transition tendency. A model may predict that a cell is likely to become built, yet the resulting map can still violate a water exclusion, miss the requested class totals or become inconsistent when the next year is simulated from the model's own output. These failure modes are particularly important when the model is used to compare scenarios rather than to reproduce one observed transition. Latent-dynamics approaches such as GeoFM-LDN can represent continuous geospatial state and condition transitions on demand, whereas traditional ANN-plus-cellular-automata systems combine suitability with explicit neighbourhood evolution. Neither design, by itself, guarantees that action semantics, hard constraints, state persistence and evidence provenance are visible at the same execution boundary.

We address this systems problem by studying Geospatial Kernel, the core transition layer of a Geospatial World Model (GWM). The Kernel represents one simulation step as a typed state, a typed action, a transition proposal, a constraint projection and a state writeback. The learned proposal remains domain-specific; the runtime contract is domain-neutral. For Abu Dhabi land-cover planning, the proposal is a six-class probability cube, and the projection allocates only mutable cells until the action's feasible class totals are reached. This separation makes the planning operation inspectable: a reviewer can distinguish what the transition model preferred from what the constraints admitted.

We evaluate this design in a controlled public-data benchmark rather than treating the benchmark as an official data release. All candidates consume the same 100-m grid, common valid mask, annual class-count actions, hard exclusions and evaluator. The historical track uses observed target counts to isolate spatial allocation skill from demand error. The planning track starts from the observed 2024 state and applies three planner-supplied actions: moderate growth, green-priority growth and high outward growth. Abu Dhabi Plan 2030 provides an institutional planning context for discussing urban structure, but the numerical actions in this benchmark are not calibrated to that plan or to an official population forecast (Abu Dhabi Urban Planning Council, 2007). We ask four questions: whether the Kernel execution contract is auditable, whether its allocation skill is competitive, whether it produces feasible and spatially distinct allocations and which conclusions survive label and parameter sensitivity.

The paper makes three bounded contributions. First, it gives a concrete state–action–constraint formulation for using a geospatial kernel as an algorithmic core rather than as an opaque end-to-end predictor. Second, it defines an evaluation protocol that combines confidence-filter retention, expanding-window temporal tests, zero-model controls and external-product disagreement rather than relying on one favourable split. Third, it turns future maps into explicit stress-test artefacts, including cumulative rasters and vectorized transition footprints, while preserving the distinction between public-data land cover and authoritative legal land use.

## Methods

### Portable audit protocol

The benchmark separates a reusable audit protocol from the Abu Dhabi adapter.
For any city or geospatial domain, the protocol requires: (i) a declared class
crosswalk and spatially stratified label-confidence tiers; (ii) persistence and
minimum-change zero models; (iii) destination-correct multi-class change FoM
with quantity and allocation diagnostics; (iv) spatial-block bootstrap intervals
and paired model contrasts on a frozen evaluation mask; (v) an explicit check for
structural-zero metrics before Pareto selection; (vi) a versioned objective table
with direction, units and interpretation; and (vii) a state–action–constraint
trace recording proposal, projection, hard-mask status and state writeback. The
protocol also requires every model/year/seed record to report the number of
predicted changed cells. A record with `predicted_change_pixels == 0` is marked
as a degenerate output and reviewed alongside structural-zero metrics; it cannot
by itself be interpreted as model superiority or real land-cover stability. The
protocol reports domain validity separately from execution completeness and
requires independent change validation before a categorical map is presented as
an observed land-use product. A structural-zero metric is flagged operationally
when its denominator is zero for every candidate under the declared action and
constraint rules; for exact-count allocation, a conversion rate is also a
structural zero when the protected/source rule makes the relevant source class
monotonically non-decreasing, so no eligible source cells can contribute to that
transition. Such a metric is reported descriptively and excluded from Pareto
selection.

### Abu Dhabi implementation: boundary, grid and temporal protocol

The study boundary is the polygon returned for OpenStreetMap relation R4479763, representing Abu Dhabi city. All rasters were aligned to a canonical 100-m grid in EPSG:32640 with 475 columns and 360 rows. A cell was included when its centre fell within the city polygon and when the common public-data mask indicated valid coverage. The benchmark profile records the source geometry, raster transform, dimensions and SHA-256 hashes. The effective evaluation mask contains 79,726 cells.

The observed sequence contains annual states for 2017–2024. Models were fit using the four transitions 2017→2018, 2018→2019, 2019→2020 and 2020→2021. A 2021→2022 transition was used for validation during model development. The historical test starts from 2022 and evaluates 2023 and 2024 in an open-loop rollout without observed-state writeback. The planning test starts from the observed 2024 state and recursively generates 2025–2031 under each scenario action.

An additional Geospatial Kernel analysis used four expanding one-step windows with origins in 2020–2023. For origin year $t$, training included only transitions whose target year was at or before $t$; the held-out $t+1$ label was prohibited from feature construction and fitting. The held-out target supplied its observed class counts to the oracle-demand allocator and was then used for evaluation. This design isolates spatial allocation conditional on known demand and is not an end-to-end demand forecast. Early folds locked only origin-year water and wetland cells and omitted the two road-distance features, because applying the 2021 WorldCover proxy or the later OpenStreetMap snapshot to earlier folds would introduce future information. The resulting rolling proposal has 23 features. A machine-tested temporal firewall records the last training target, prediction target and permitted target-year uses for every run.

### Public data and class semantics

Dynamic World V1 provides annual scene-argmax labels and mean top-class probabilities (Brown et al., 2022). The nine Dynamic World labels were crosswalked to six canonical classes: water (source 0), woody vegetation (1), low vegetation (2, 4 and 5), wetland (3), built (6) and bare (7). Source class 8 was excluded. The resulting label is explicitly treated as land cover. No residential, commercial or industrial category is inferred from the raster labels.

Annual 64-dimensional AlphaEarth embeddings were spatially averaged to the canonical grid and locally L2-normalized. Monthly VIIRS night-time-light radiance was averaged by year. Copernicus DEM supplied elevation and a finite-difference slope derivative. OpenStreetMap road geometries were rasterized into distance-to-road and distance-to-major-road surfaces. ESA WorldCover 2021 supplied public water and wetland/mangrove constraint proxies (Zanaga et al., 2022). All dynamic and static layers were checked for exact CRS, transform, width and height agreement.

For an external public-product diagnostic, the ESA WorldCover 2020 v1.0 and 2021 v2.0 built-up class (value 50) was converted to built fraction on each 100-m benchmark cell. Built presence was tested at fractions of 0.05, 0.10, 0.20 and 0.30. Built gain required a cell to cross from below to at or above the threshold; built loss used the reverse definition. Binary precision, recall, F1 and intersection over union were calculated for the Dynamic World transition and for the 2020-origin predictions. This is a product-agreement diagnostic, not ground-truth validation: the two WorldCover years use different product versions, WorldCover and Dynamic World both derive from Sentinel observations, and neither represents statutory Abu Dhabi land use.

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

The baseline was run through a GeoSOS-derived FLUS-style ANN–CA console (author-modified build; `paper-benchmark-flus-v1.1`) using seven continuous drivers: normalized row and column coordinates, elevation, slope, VIIRS radiance, distance to roads and distance to major roads. Its ANN suitability surface was passed to a cellular-automata allocation stage with the common class totals and public hard mask. The archived run used one 2021 training year, eight ANN hidden neurons, a 3 × 3 CA neighbourhood, neighbourhood strength 1.0, acceleration factor 0.1 and 1,000 iterations. Its frozen transition matrix protected water and wetland but did not prohibit built-to-non-built transitions. The algorithmic base is traceable to the GeoSOS team's public FLUS source release (Liu et al., 2017; geosimulation.cn); the accompanying source repository `FLUS_console_crossplatform` at commit `47e65b3` contains the author modifications used for this paper. Those modifications add `train`/`train-update` entry points and `FLUS_RANDOM_SEED` deterministic seeding for both ANN sampling and CA roulette draws, so the build is not the unmodified upstream executable. Version v1.1 changes only failure handling for invalid input reads; valid-input algorithmic paths and benchmark rasters are unchanged from v1. A 25-feature Kernel-matched input was then executed with absolute paths for seeds 31, 47 and 73 and is reported only as a platform-sensitive diagnostic. It shares the Kernel feature family, but not the learning target or projection semantics: the FLUS ANN estimates same-year label suitability $p(S_t\mid X_t)$, whereas the Kernel proposal is trained to estimate a next-state transition $p(S_{t+1}\mid S_t,X_t)$ before constrained projection. Matching features therefore does not match the training task. Two intermediate configurations were retained as mechanism diagnostics: 13 features (seven drivers plus current-class indicators) and 19 features (seven drivers plus neighbourhood fractions). The 25-feature run collapsed to zero change for macOS seeds 47 and 73 and for all three independent external Windows x86_64 verification runs; the remaining macOS seed-31 run is not used as a valid estimator. The external evidence is identified in Supplementary Table S3; its source rasters are not locally archived. The 19-feature mode produced changes for all three macOS seeds but underfilled the observed 4,500 and 8,464 changed cells in 2023 and 2024. Both modes are therefore diagnostic-only.

GeoFM-LDN (Geospatial Foundation-Model Latent Dynamics Network; the repository's former `paper58` path identifier) was implemented as a demand-conditioned residual latent-dynamics network on 64-channel AlphaEarth patches. Three 128-channel convolutions use dilation rates 1, 2 and 4, followed by a 1 × 1 projection to a 64-dimensional latent state. A 12-dimensional action vector (origin and target counts for six classes) is encoded by a two-layer MLP and broadcast across the patch before concatenation with the embedding. Group normalization and GELU activations are used in the residual blocks. A scikit-learn logistic-regression decoder maps the predicted latent embedding to six semantic classes. Training uses 64 × 64 patches, batch size 2, eight epochs, AdamW with learning rate $3\times10^{-4}$ and weight decay $10^{-4}$; the loss is the weighted sum of cosine embedding loss, 0.5 semantic cross-entropy, 0.1 demand-consistency loss and 0.2 hard-constraint consistency loss. The released checkpoints correspond to seeds 31, 47 and 73 and were trained in August 2026. The default reproduction loads these fixed checkpoints rather than retraining; the runner exposes retraining separately. Fixed checkpoints do not remove the decoding runtime boundary: categorical output still depends on the locked Torch and scikit-learn stack. Same-stack reproduction is the declared reference; no independent cross-stack GeoFM-LDN raster comparison is claimed, and changes between pre-lock and locked-environment outputs are not attributed to CPU architecture or to one library. During allocation, GeoFM-LDN directly calls the Geospatial Kernel `allocate_action` routine, so both methods share the same constrained projection and differ primarily in their proposal model. The comparison is therefore a proposal/pipeline comparison, not a comparison of two independent projection architectures. The name describes this benchmark implementation and does not attribute an external publication or performance claim.

The common evaluator computes actual class counts, normalized demand total variation, hard-mask violations, strict multi-class change FoM, binary change FoM, change F1, overall accuracy and macro-F1 for historical runs. The strict FoM counts a hit only when the predicted destination class equals the observed destination class; wrong destination changes are retained in the denominator. It also generates persistence and minimum-change zero controls, spatial-block bootstrap intervals and paired model-difference intervals for strict FoM, overall accuracy and macro-F1. For planning runs it additionally computes ecological conversion, new-built neighbourhood fraction, new-built component counts, the union of 2024 built and newly built components, all-final-built component counts, a 500-m leapfrog rate, distances to roads and prior built cells, infrastructure proxy distance and built retirement. Pareto membership is calculated within each scenario over three release objectives: major-road distance, prior-built distance and union-built component density. Ecological conversion is retained as a descriptive public-data pressure proxy because it is structurally zero for the two exact-count allocators and therefore has no discriminating power in their comparison. Vegetation gain is a scenario input and remains descriptive, not an objective.

### Scenario actions and uncertainty

The moderate-growth, green-priority-growth and high-outward-growth actions are stored in the tracked `planning_scenarios_public_2025_2031.json` manifest; the legacy `compact` path identifier is retained only for artifact compatibility. Each action supplies feasible class totals for 2025–2031. The 2031 totals are an explicit extension of the previous annual difference and are not derived from an official population, housing or infrastructure forecast. Future exogenous rasters are held at their 2024 values. The green-priority action is not a water-budget model. Each candidate is run at seeds 31, 47 and 73, and planning tables report arithmetic means and population standard deviations. No p-values are reported because the three seeds describe computational variability, not independent field samples. The primary Pareto comparison is within each scenario, contrasting the three models under the same action; a global nine-candidate frontier is retained only as lineage. Sensitivity variants remove or add objective dimensions on the same released rasters. The objective set evolved through four review-driven revisions and was not preregistered: v1 mixed feasibility, action and outcome terms; v2 was not released; v3 used structurally problematic outcomes; and v4 still included scenario-supplied vegetation gain and all-built fragmentation. The current release is v6: road access, prior-built distance and union-built component density. Ecological conversion is reported as a diagnostic rather than a Pareto objective because it is structurally zero for the exact-count Kernel and GeoFM-LDN allocations. We treat v6 as a release objective set rather than a prespecified planning preference, and treat its sensitivity results as robustness diagnostics.

### Change polygons and reproducibility

For each model–scenario pair, annual and cumulative differences from the 2024 raster are extracted as changed 100-m cells and dissolved into GeoPackage layers. The public delivery manifest covers 45 ensemble rasters for 2027–2031 and nine vector packages. The audit script reports `INCOMPLETE_INPUTS` or `FAIL` when source rasters, reports or vectors are absent; with the released public bundle, the input audit passed all alignment gates (with a Dynamic World label-noise warning) and the output audit passed 276 historical and planning predictions with zero failures. The vector layers preserve raster-cell geometry and should not be interpreted as cadastral parcels.

## Results

### A common benchmark separates allocation skill from demand assumptions

The benchmark covers the Abu Dhabi city polygon represented by OpenStreetMap relation R4479763. The canonical grid is a 475 × 360 lattice in EPSG:32640 at 100-m resolution. After the common coverage and alignment checks, 79,726 cells were used for scoring. Each cell represents 1 ha. Annual Dynamic World observations from 2017 to 2024 were harmonized to six land-cover classes: water, woody vegetation, low vegetation, wetland, built and bare. AlphaEarth annual embeddings, VIIRS night-time lights, Copernicus DEM derivatives and OpenStreetMap road distances supplied transition drivers. ESA WorldCover and public OpenStreetMap geometries supplied water, wetland and infrastructure exclusion proxies.

The comparison shared the canonical grid, origin states, target actions, hard masks and evaluator, but the public-data run was not information-balanced. The original FLUS-style control used seven continuous drivers in its external ANN suitability model, whereas Geospatial Kernel used 25 features including current-class indicators and neighbourhood proportions; GeoFM-LDN used AlphaEarth latent embeddings and the Kernel allocator. We therefore report the original result as an unmatched-input pipeline comparison, not evidence that one learner is intrinsically superior. The additional 25-feature FLUS run is a feature-space diagnostic only, because it still learns same-year suitability rather than next-state transitions and does not use the Kernel projection implementation. Across six platform–seed runs, five produced zero-change outputs through current-class identity leakage. The archived FLUS console is a Mach-O arm64 executable rebuilt from the public GeoSOS source base with the author-modified `train`/`train-update` entry points and `FLUS_RANDOM_SEED` seeding patch; its exact source is archived at `FLUS_console_crossplatform` commit `deb0a54`. It is not asserted to be bitwise equivalent to an unmodified upstream build. All headline and diagnostic runs used seeds 31, 47 and 73.

The execution trace makes the distinction between proposal and admission explicit. A Kernel step records the source state, action, probability-cube proposal, projected state, model identity, input evidence and next-state reference. The runtime checks that the action advances the source time and that the projected raster becomes the next state. This is the operational meaning of the Kernel in this study: not a claim that all GWM domains share the same learner, but a claim that they can share an auditable execution contract. The shared inputs and execution boundary are summarized in Fig. 1.

![Benchmark and Geospatial Kernel execution contract. Public annual land-cover, embedding, night-light, terrain and road layers are aligned to a common 100-m Abu Dhabi grid. The Kernel exposes a learned proposal, a constraint projection and a state writeback. The schematic describes a public-data benchmark and does not imply statutory planning boundaries.](figures/fig01_benchmark_contract.png){width=100%}

\FloatBarrier

### Historical and planning results

The historical track uses observed target class totals to isolate spatial
allocation from demand estimation. The primary metric is strict multi-class
change FoM: a hit requires the predicted destination class to equal the
observed destination class, while wrong destination changes remain in the
denominator (Pontius et al., 2008). Overall accuracy, macro-F1, change F1 and
binary FoM are secondary diagnostics. Uncertainty is estimated with an
8 × 8-pixel spatial-block bootstrap, and model contrasts are computed from the
same resampled blocks for each frozen seed. Persistence and random
minimum-change allocation are explicit zero-model controls.

The planning track starts from the observed 2024 state and applies three
synthetic class-count actions through 2031. The release objective set is version
6. It uses mean distance of new built cells to major roads, mean distance to
pre-existing built cells and connected components in the union of 2024 built and
newly built cells per 1,000 valid cells. These are public-data proxies. Ecological
conversion is retained as a descriptive diagnostic, not an objective, because it
is structurally zero for the two exact-count allocators. Vegetation gain is
excluded because it is supplied directly by the scenario action, and all-final-
built component density is reported only as a diagnostic because it can be
changed by built-cell retirement. No weighted composite score is used. Because
the objective set changed across the review rounds, we disclose the lineage: v1
included seven access, ecological, neighbourhood and gain terms; v2 proposed
roads, prior-built distance, fragmentation and leapfrog rate but was not run; v3
used ecological conversion, roads, leapfrog rate and built retirement; and v4
combined roads, prior-built distance, all-built fragmentation and vegetation
gain. The current v6 release replaces v5 after the review identified the
structural-zero ecological objective and the semantic inversion of new-only
fragmentation. Sensitivity sets are recomputed on the same rasters and reported
as robustness analyses, not as additional preregistered claims. These are
measurable public-data proxies rather than claims about welfare, equity or
statutory zoning.

The released public-data bundle supports a complete re-scoring of the current
historical rasters and a re-compilation of the 2025–2031 planning rasters. The
strict multi-class transition FoM (mean across three seeds) was 0.1256, 0.1961
and 0.1619 for the FLUS-style console, Geospatial Kernel and GeoFM-LDN in 2023,
and 0.1782, 0.2529 and 0.2708 in 2024, respectively. Under this unmatched
public-data pipeline, Geospatial Kernel had the largest 2023 value, whereas
GeoFM-LDN had the largest 2024 value after recursive two-step rollout; no
single model dominated both horizons. These rankings are conditional on the
different inputs, learners and shared evaluation projection.

**Table 1. Historical strict destination-change FoM.** Values are means across
three frozen computational seeds. The 25-feature FLUS run is excluded because
it is not a comparable estimator: five of six platform--seed runs collapsed to
zero change. Persistence (0.0000 in both years) and random minimum-change
allocation (0.0253 in 2023; 0.0605 in 2024) are explicit zero-model controls
and are plotted in Fig. 2.

| Target year | FLUS-style ANN-CA | Geospatial Kernel | GeoFM-LDN |
|:---|---:|---:|---:|
| 2023 (one-step) | 0.1256 | **0.1961** | 0.1619 |
| 2024 (two-step open-loop) | 0.1782 | 0.2529 | **0.2708** |

Spatial-block bootstrap model contrasts support these differences. For 2023,
Kernel minus the FLUS-style control was 0.0703 [0.0558, 0.0866] and GeoFM-LDN
minus Kernel was -0.0341 [-0.0479, -0.0209]. For 2024, GeoFM-LDN minus Kernel
was 0.0177 [0.0033, 0.0314]. These are conditional pipeline contrasts on public labels,
not independent-sample significance tests. The persistence control had higher
overall accuracy than every learned candidate (0.9436 in 2023 and 0.8938 in
2024), illustrating why change-specific metrics are necessary. Fig. 2 shows
the four historical metrics alongside the persistence and random minimum-change
controls; main-model bars use three-seed population standard deviations,
whereas the paired spatial-block intervals above are the uncertainty summaries
used for model contrasts. The 25- and 19-feature FLUS diagnostics are reported
in the machine-readable archive and Supplementary Table S3.

![Historical allocation skill. Strict destination-change FoM is the primary metric; change F1 is shown as a secondary diagnostic. Bars show mean plus or minus population standard deviation across the three frozen seeds. Persistence and random allocation are explicit zero-model controls.](figures/fig02_historical_validation.png){width=100%}

\FloatBarrier

An additional FLUS input-dimension analysis was also completed. The
25-feature run is not a valid point estimator: macOS seeds 47 and 73 and all
three independent external Windows x86_64 verification runs produced zero-change outputs,
whereas macOS seed 31 was the sole non-collapsed run. The six-run pattern is
therefore platform-sensitive and is retained as an identity-leakage diagnostic,
not as a Kernel contrast. The 19-feature diagnostic was run for all three macOS
seeds. Its strict FoM ranged from 0.1071 to 0.1617 in 2023 and from 0.0872 to
0.1386 in 2024; predicted changes ranged from 1,702 to 2,417 and from 1,805 to
2,499 cells, respectively, compared with 4,500 and 8,464 observed changes.
Demand total variation ranged from 0.0153 to 0.0305 in 2023 and from 0.0615 to
0.0767 in 2024. These results show why matching feature dimensions cannot make
the tasks equivalent: FLUS learns static suitability $p(S_t\mid X_t)$, while
the Kernel learns next-state transitions and then projects them against action
deficits and hard constraints.

The confidence sensitivity is a label-quality and selection-effect diagnostic,
not an independent validation set or a model-skill test. Requiring both the
origin and target Dynamic World mean top probability to exceed 0.5 retains only
25 of 4,500 observed changes (0.56%) in 2023 and 56 of 8,464 (0.66%) in 2024.
Strict FoM is 0.000 for all three models in 2023; in 2024 the means are 0.0040
for the FLUS-style console, 0.0055 for Geospatial Kernel and 0.0188 for
GeoFM-LDN. Screening only the confidence of the year immediately preceding the
target avoids filtering on target-year confidence, but still retains only 129
(2.87%) and 93 (1.10%) observed changes in 2023 and 2024, respectively. Its
2023 FoM values remain 0.000; its 2024 means are 0.0040, 0.0041 and 0.0120 for
the FLUS-style console, Kernel and GeoFM-LDN. The two filters therefore
describe label selection rather than establishing or rescuing model skill.
Dynamic World also reports built pixels increasing from 9,359 in 2022 to 15,598
in 2024 (67%), while the median one-year reversion fraction is 0.3611 and the
mean fraction of cells below confidence 0.5 is 0.5497. Test-year change counts
are approximately twice the training-transition counts. Because the same grid
cells recur across years and the Kernel includes coordinate features, a
training–test memory effect cannot be excluded; the reported scores should
therefore be interpreted as conditional agreement with the public product.

### Rolling-origin and external-product tests expose temporal and label dependence

The leakage-controlled expanding-window test produced mean Kernel strict FoM
values of 0.2595, 0.0724, 0.2116 and 0.1816 for the 2021, 2022, 2023 and 2024
one-step targets, respectively. The corresponding random minimum-change values
were 0.0524, 0.0048, 0.0200 and 0.0323; persistence produced no predicted
change and therefore zero strict FoM. Paired 8 × 8-cell spatial-block contrasts
between Kernel and each zero model excluded zero in every target year and each
of the three seeds. This result supports conditional spatial allocation under
Dynamic World labels, but the weak 2022 score shows substantial temporal
variation. Persistence also retained higher overall accuracy than Kernel in
2022–2024, whereas Kernel had higher overall accuracy only in 2021. The
change-specific and all-cell metrics therefore answer different questions.

The WorldCover comparison did not corroborate change location. Across built
fractions from 0.05 to 0.30, WorldCover contained 1,445–1,802 built-gain cells
and 1,408–1,506 built-loss cells. Dynamic World-to-WorldCover built-gain F1 was
only 0.0111–0.0192. Under the 2020→2021 Dynamic World oracle-demand action,
Kernel and the random allocator produced no built-gain cells, so their
WorldCover built-gain F1 was 0 at all thresholds and precision was undefined.
For 2021 built stock, Kernel F1 increased from 0.3518 to 0.3971 as the threshold
rose, but persistence was higher at every threshold (0.3886–0.4387). These
negative results indicate product-definition and temporal-label disagreement;
they do not identify which public product is correct. Fig. 3 reports the
rolling and external-product evidence together so that the zero-model advantage
and the absence of external change agreement cannot be separated in the claim.

![Rolling-origin robustness and external-product diagnostics. Panel a reports strict destination-change FoM for four leakage-controlled one-step targets; points show means and sample standard deviations across three computational seeds. Panel b reports Kernel-minus-baseline paired spatial-block contrasts; points are mean seed medians and whiskers span the minimum to maximum of seed-specific 95% intervals from 1,000 resamples of 8 × 8-cell blocks. Panels c and d compare 2021 built stock and 2020–2021 built gain with ESA WorldCover at four 100-m built-fraction thresholds. The WorldCover comparison is an external public-product diagnostic, not authoritative ground truth. Source data are provided in source_data_fig03_rolling_external_diagnostics.csv.](figures/fig03_rolling_external_diagnostics.png){width=100%}

\FloatBarrier

The reference reproduction environment is macOS arm64 with Python 3.11 and
scikit-learn 1.9.0. The archived Linux arm64 rerun uses Python 3.12 and
scikit-learn 1.8.0, so it measures a cross-stack boundary rather than an
architecture-only effect. Across six rasters (2023 and 2024 for each seed), it
differs from the current reference by 498–1,147 cells (0.62–1.44% of valid
cells), with strict-FoM deltas from -0.0023 to 0.0010. An author-controlled
GitHub Actions Ubuntu x86_64 rerun under Python 3.11.16 and scikit-learn 1.9.0
matched all six released categorical reference rasters exactly; its archived
audit is linked in Code availability. This is a scoped locked-stack regression
result, not universal bitwise identity. Independent external Windows FLUS
verification is documented with its provenance limitation in Supplementary
Table S3; its source rasters are not locally archived. The archived comparison
report records the exact paths and environment fields for the arm64 pair.

The planning compiler compares the three models within each of the three
scenarios. At 2031, the FLUS-style control has union-built component densities of
2.48–3.27 per 1,000 valid cells, the Kernel 2.92–4.28 and GeoFM-LDN 3.21–4.35.
The Kernel is closer to major roads and prior built cells, whereas the union
metric shows that this edge-filling pattern does not automatically imply lower
overall fragmentation than the FLUS-style allocations. Under the release
objective set, the within-scenario frontiers contain FLUS-style and Kernel
candidates in all three scenarios; GeoFM-LDN is dominated in each scenario.
In the preceding v5 formulation, GeoFM-LDN could appear non-dominated only
because its ecological-conversion value was the same structural zero as the
exact-count Kernel; that zero is not a model advantage. Ecological conversion
is therefore retained only as a diagnostic in v6. All sensitivity variants
retain the same FLUS-style/Kernel two-model frontier. These statements are
conditional on public proxy layers and synthetic actions, not model superiority
claims.
The corresponding objective profiles and diagnostic trade-offs are shown in
Fig. 4.

![Conditional planning objectives. The 2031 outcomes compare the three models under moderate-growth, green-priority-growth and high-outward-growth actions. Panels show the three release objectives: distance to major roads, distance to pre-existing built cells, and connected components in the combined 2024-built and newly built footprint. Black outlines indicate membership of the within-scenario Pareto frontier.](figures/fig04_planning_objectives.png){width=100%}

\FloatBarrier

**Table 2. 2031 within-scenario planning objectives.** Values are means across
three seeds. Road and pre-existing-built distances are in metres; components are
the number in the combined 2024-built and newly built footprint per 1,000 valid
cells. Ecological conversion is a descriptive fraction of new-built cells whose
origin was woody vegetation, low vegetation or wetland. Asterisks indicate the
primary within-scenario Pareto frontier.

| Scenario / model | Road (m) | Prior built (m) | Components / 1,000 | Ecology* | Frontier |
|:---|---:|---:|---:|---:|:---:|
| **Moderate** |  |  |  |  |  |
| FLUS-style ANN–CA | 446.1 | 231.6 | 3.035 | 0.0168 | * |
| Geospatial Kernel | 334.7 | 116.7 | 3.943 | 0.0000 | * |
| GeoFM-LDN | 475.9 | 239.7 | 4.056 | 0.0000 |  |
| **Green priority** |  |  |  |  |  |
| FLUS-style ANN–CA | 443.7 | 212.7 | 3.265 | 0.0177 | * |
| Geospatial Kernel | 323.1 | 111.0 | 4.277 | 0.0000 | * |
| GeoFM-LDN | 452.1 | 222.3 | 4.348 | 0.0000 |  |
| **High outward** |  |  |  |  |  |
| FLUS-style ANN–CA | 443.5 | 255.3 | 2.484 | 0.0131 | * |
| Geospatial Kernel | 365.5 | 139.8 | 2.923 | 0.0000 | * |
| GeoFM-LDN | 507.5 | 263.0 | 3.207 | 0.0000 |  |

### Sensitivity shows a stable but not fully explained neighbourhood contribution

The base Kernel allocation score adds a 7 × 7 target-class neighbourhood fraction with weight 0.35. The existing sensitivity and mechanism artefacts are retained as diagnostic controls; they do not identify a causal effect because the proposal features and allocator both contain spatial context. The neighbourhood term is therefore interpreted as evidence about the execution mechanism, not as an independently estimated planning preference. Fig. 5A shows focused proposal controls, and Fig. 5B reports the matched runtime controls.

In the post-hoc neighbourhood-weight sensitivity, mean strict FoM ranged from
0.19570 to 0.19609 in 2023 and from 0.25273 to 0.25304 in 2024; the complete
strict-evaluator scan is provided in Supplementary Table S2. These changes are small relative
to the model contrasts and are not interpreted causally. Objective-set
sensitivity on the planning rasters retained the FLUS-style and Kernel
candidates in all scenarios. GeoFM-LDN was dominated in all three scenarios
after the structurally zero ecological-conversion term was removed from the
release objectives.

### Mechanism controls separate learned proposal from runtime projection

Mechanism controls separate the learned proposal from runtime projection, hard
constraints and recursive writeback. They are not causal policy experiments.
Deleting the action reduces mean strict FoM by 0.1124 in 2023 and 0.1699 in
2024, whereas deleting the hard constraint increases it by 0.014 and 0.011,
respectively. The former is expected because the historical task supplies
oracle target counts; it shows that much of the measured skill belongs to the
action-conditioned allocator rather than to a demand forecast. The latter is
an important warning: allowing changes inside the exclusion mask can improve
agreement with noisy labels while violating the planning contract. The
controls therefore support an execution-level interpretation but do not prove
that either component causes an urban outcome.

![Mechanism controls. Panel A compares the full transition proposal with selected proposal controls. Panel B gives the strict destination-change FoM difference between matched runtime controls and the full Kernel. Bars show mean plus or minus population standard deviation across the three frozen seeds. The no-state-writeback control is undefined for the 2023 one-step target and is therefore shown only for 2024. These are execution diagnostics, not causal policy experiments.](figures/fig05_mechanism_ablation.png){width=100%}

\FloatBarrier

### Spatial footprints are scenario-conditioned, not parcel predictions

The 2031 majority-vote ensemble L1 demand errors were 8, 44 and 42 pixels for
the Kernel's moderate, green-priority and high-outward scenarios, respectively;
the corresponding GeoFM-LDN errors were 1,580, 1,524 and 1,148 pixels and the
FLUS-style errors were 2,504, 2,888 and 2,568 pixels. Seed-level projections
meet their feasible class totals, but majority voting can produce a different
raster and therefore a non-zero ensemble error. All 276 historical and planning
prediction records passed the raster audit. Fig. 6 uses the high-outward
scenario to make the spatial contrast legible; the complete nine-panel atlas is
provided as Fig. S1. These are raster-cell change footprints, not
parcel boundaries or statutory zoning maps.

![High-outward-growth spatial footprints. The observed 2024 state is compared with each model's 2031 majority-vote ensemble. Orange denotes cells newly built between 2024 and 2031; grey denotes cells already built in 2024. The map is a 100-m scenario stress-test product, not a cadastral or statutory land-use map.](figures/fig06_planning_maps_2031.png){width=100%}

\FloatBarrier

## Discussion

This study positions Geospatial Kernel as a candidate execution layer for constrained spatial reasoning and, more broadly, proposes an audit protocol for noisy annual labels. The defensible contribution is that a transition proposal and a planning admission rule can be represented and inspected separately. Under the unmatched public-data pipeline, Geospatial Kernel has the largest strict transition FoM at the one-step horizon, while GeoFM-LDN has the largest value after recursive two-step rollout. In the separate rolling analysis, Kernel exceeds both zero models in all four one-step windows, but its score varies from 0.0724 to 0.2595 after excluding the later road snapshot. The WorldCover diagnostic then shows that superiority relative to Dynamic World-based zero models does not transfer to externally defined built-gain locations. Confidence filtering, rolling-window stability and external-product agreement are different tests, and none substitutes for authoritative local validation. We therefore treat the planning frontier as conditional on public proxy objectives and synthetic actions.

The evidence remains bounded. The six classes are remote-sensing land cover, not
statutory residential, commercial or industrial land use. Dynamic World labels
show substantial annual uncertainty and apparent turnover; the available
2020–2021 WorldCover diagnostic conflicts with Dynamic World and is neither
fully independent nor authoritative, while no external 2023–2024 change
product or observed 2025–2031 labels was available. Public
roads, wetland and protected-area layers are proxies, future drivers are held at
2024, and the green-priority action has no water-budget constraint. The FLUS-style
control is an Apple-Silicon binary rebuilt from the public GeoSOS source base
with the author's `train`/`train-update` and deterministic-seeding patches; its
headline comparison uses seven drivers. The 25-feature run is a
platform-sensitive identity-leakage diagnostic: five of six platform–seed runs
collapsed to zero change, so the non-collapsed macOS seed-31 result is not used
as a comparative estimate.
These public-data stress tests therefore do
not establish causal planning effects or a validated Abu Dhabi forecast. An
authoritative deployment would replace public labels and masks with locally
approved land-use, infrastructure, ecological and development-demand records
while retaining the same execution contract.

## Data availability

The public-data benchmark manifests, protocols, reports and generated delivery artefacts are organized under `benchmarks/abu_dhabi_land_use_v1/` in the accompanying repository. The main evidence files are:

- `comparison_report_current.json` and `comparison_report_current.md` for historical metrics when a data-complete rerun is available;
- `planning_comparison_report_public_2025_2031_current.json` and its Markdown rendering for 2031 planning objectives;
- `planning_scenario_report_public_2025_2031_current.json` for per-seed rollout traces;
- `planning_public_2025_2031_delivery_manifest_current.json` for raster and vector delivery;
- `output_audit.json` for the current raster audit; `output_audit_reproducible.json` is a compatibility copy produced by the same run;
- `artifacts/rolling_backtest/report.json` and `paired_spatial_uncertainty.json` for the four leakage-controlled one-step windows;
- `supplementary_table_S5_rolling_external_diagnostics.md` for the synchronized rolling and external-product table;
- `artifacts/external_validation/worldcover/` for frozen WorldCover built-fraction inputs, hashes and the external-product diagnostic;
- the data-audit, protocol and source-input manifests for data provenance;
- The released bundle includes the aligned 2017–2024 public rasters, historical and rolling-origin prediction rasters, frozen WorldCover built-fraction rasters, 2025–2031 planning rasters, nine GeoPackages of dissolved change footprints, model checkpoints and the SHA-256 manifest. Text hashes use canonical LF line endings, and the byte-length check applies the same normalization on text records, so a Windows checkout with `core.autocrlf=true` can pass the manifest gate. The locked macOS arm64 execution environment remains the reference for model outputs. An archived arm64 Linux rerun of the six historical Kernel rasters differed from the macOS reference by 498–1,147 cells (0.62%–1.44%), with strict-FoM deltas from -0.0023 to +0.0010; these cross-stack differences are quantified rather than treated as categorical identity. An author-controlled GitHub Actions Ubuntu x86_64 rerun of all six rasters under the resolved lock had zero categorical differences; the repository-stored CI audit is in `artifacts/cross_platform` at commit `e06a997`, and the workflow is versioned under `.github/workflows/`. Independent external Windows evidence remains separately labelled for FLUS because the corresponding rasters are not archived locally. No private database address, credential or client-only service is included. Authoritative Abu Dhabi land-use and independent reference data remain outside this study.

## Code availability

The analysis scripts, a vendored Geospatial Kernel runtime snapshot, benchmark protocol, model runners and figure-generation code are maintained in the accompanying repository. Principal entry points are listed separately to keep the manuscript readable:

- `run_geospatial_kernel.py` for the Kernel historical run;
- `run_rolling_backtest.py` and `run_rolling_uncertainty.py` for the expanding-window experiment and paired spatial-block intervals;
- `materialize_worldcover_validation.py` for frozen WorldCover inputs;
- `run_worldcover_external_diagnostic.py` for the agreement diagnostic;
- the vendored `geospatial_kernel/runtime.py` snapshot;
- `render_nature_figures.py` and `render_rolling_validation_figure.py` for publication artwork;
- `source_data_fig03_rolling_external_diagnostics.csv` for the quantitative source data behind Fig. 3.
- `reproducibility/reproduce.py` for the end-to-end rerun;
- `reproducibility_check.py` and `audit_outputs.py` for fail-closed integrity checks.

GeoFM-LDN source and the three fixed checkpoints are included in the benchmark
external and prediction-artifact directories.
Earlier internal reference outputs, produced before the dependency lock was
completed, could not be regenerated under the resolved environment and were
superseded by the locked-environment rerun reported here. Historical strict-FoM
differences were at approximately the 0.001 level; discrete multi-year planning
ensemble demand errors changed more substantially and are reported here only
from the locked-environment rerun. The prior outputs remain Git-history lineage,
not current evidence.
The vendored FLUS executable is a macOS arm64 binary rebuilt from the GeoSOS
public FLUS source base. The author-modified source, including `train-update`
and `FLUS_RANDOM_SEED`, is archived at
the public FLUS source repository, tag `paper-benchmark-flus-v1.1` at commit
`47e65b3`
(the GeoSOS source release and Liu et al. (2017) are cited above). Rebuilding
the preceding v1 commit (`deb0a54`) on macOS arm64 produced SHA-256
`9839ce50950442d4ef49e4d2129a1ba27735e1955c2d4975ae51067c1c3c9964`,
identical to the vendored executable. Version v1.1 changes only invalid-input
failure handling and leaves valid-input algorithmic paths unchanged; the
normal-output equivalence check is archived with the source release.
The tagged author-modified source can also be built on Linux and Windows using
the repository instructions. `FLUS_RANDOM_SEED` guarantees determinism only
within a platform and build environment because ANN sampling and CA roulette
draws use platform-defined C `rand()`/`srand()` streams. Independent external
Windows FLUS verification, including the seven-driver cross-platform difference
and the 25-feature zero-change outcome, is documented with its provenance
limitation in Supplementary Table S3. Windows execution requires the benchmark
and working directories to use pure ASCII paths; saving configuration files as
UTF-8 alone does not repair GDAL path decoding. A compatible local build is required to
execute the FLUS track outside macOS arm64 and will produce a different random
stream. The macOS binary SHA statement is an author self-check. As an
upstream-only fallback, the public FLUS CA source can be paired with an open
Python ANN implementation, but the unmodified upstream CA uses time seeding
rather than `FLUS_RANDOM_SEED`. The corresponding-author e-mail is
`zhouning@freedotech.com`; an archival DOI should be added after a persistent
public release is created.

## Declarations

**Funding.** No external funding was received for this study.

**Competing interests.** Ning Zhou is employed by Beijing Freedo Technology Co., Ltd., which develops geospatial-world-model software. The author declares no other competing financial or personal interests.

**CRediT author statement.** Ning Zhou: Conceptualization, methodology, software, data curation, formal analysis, visualization, writing—original draft, writing—review and editing.

**Acknowledgements.** The author thanks the anonymous reviewers for independent technical verification and constructive methodological comments.

**Ethics statement.** Not applicable; the study used geospatial raster, vector and derived public-data products and did not involve human or animal participants.

## References

Abu Dhabi Urban Planning Council. (2007). Plan Abu Dhabi 2030: urban structure framework plan. Abu Dhabi, United Arab Emirates.

Brown, C. F., et al. (2022). Dynamic World, near real-time global 10 m land use land cover mapping. *Scientific Data*, 9, 251. https://doi.org/10.1038/s41597-022-01307-4

Burton, E. (2000). The compact city: just or just compact? A preliminary analysis. *Urban Studies*, 37, 1969–2006. https://doi.org/10.1080/00420980050162184

Gorelick, N., et al. (2017). Google Earth Engine: planetary-scale geospatial analysis for everyone. *Remote Sensing of Environment*, 202, 18–27. https://doi.org/10.1016/j.rse.2017.06.031

Lau, K. H., & Kam, B. H. (2005). A cellular automata model for urban land-use simulation. *Environment and Planning B: Planning and Design*, 32, 247–263. https://doi.org/10.1068/b31110

Liang, X., et al. (2021). A patch-generating land use simulation model integrating multisource data for urban growth simulation. *Landscape and Urban Planning*, 214, 104157. https://doi.org/10.1016/j.landurbplan.2021.104157

Liu, X., et al. (2017). A future land use simulation model (FLUS) for simulating multiple land use scenarios by coupling human and natural effects. *Landscape and Urban Planning*, 168, 94–116. https://doi.org/10.1016/j.landurbplan.2017.09.019

GeoSOS team, Sun Yat-sen University. (n.d.). FLUS source code for non-commercial academic research. http://www.geosimulation.cn/FLUS-source-code.html (accessed 6 September 2026).

OpenStreetMap contributors. (2026). OpenStreetMap data, Abu Dhabi relation R4479763 and Geofabrik GCC extract, accessed 31 July 2026. https://www.openstreetmap.org

Pontius, R. G., Jr., Boersma, W., Castella, J.-C., et al. (2008). Comparing the input, output, and validation maps for several models of land change. *The Annals of Regional Science*, 42, 11–37. DOI: 10.1007/s00168-007-0138-2

Pontius, R. G., Jr., & Millones, M. (2011). Death to Kappa: birth of quantity disagreement and allocation disagreement for accuracy assessment. *International Journal of Remote Sensing*, 32, 4407–4429. DOI: 10.1080/01431161.2011.552923

Silva, E. A., & Clarke, K. C. (2002). Calibration of the SLEUTH urban growth model for Lisbon and Porto, Portugal. *Computers, Environment and Urban Systems*, 26, 525–552. https://doi.org/10.1016/S0198-9715(01)00017-8

Soares-Filho, B. S., Cerqueira, G. C., & Pennachin, C. L. (2002). DINAMICA—a stochastic cellular automata model designed to simulate the landscape dynamics in an Amazonian colonization frontier. *Ecological Modelling*, 154, 217–235. https://doi.org/10.1016/S0304-3800(02)00059-5

van Vliet, J., Bregt, A. K., Rietveld, P., & Verburg, P. H. (2011). Modeling land-use change with cellular automata: Issues and recommendations. *Journal of Land Use Science*, 6, 247–265. https://doi.org/10.1080/1747423X.2011.562018

van Vliet, J., Bregt, A. K., Brown, D. G., van Delden, H., Heckbert, S., & Verburg, P. H. (2016). A review of current calibration and validation practices in land-change modeling. *Environmental Modelling & Software*, 82, 174–182. https://doi.org/10.1016/j.envsoft.2016.04.017

Verburg, P. H., et al. (2002). Modeling the spatial dynamics of regional land use: the CLUE-S model. *Environmental Management*, 30, 391–405. https://doi.org/10.1007/s00267-002-2631-x

Zanaga, D., et al. (2022). ESA WorldCover 10 m 2021 v200. Zenodo. https://doi.org/10.5281/zenodo.7254221

## Supplementary information outline

- **Supplementary Note 1:** Complete data crosswalk, quality metrics and public/proxy status.
- **Supplementary Note 2:** Kernel runtime schemas, audit fields and adapter boundary.
- **Supplementary Table S1:** Full 2025–2031 model–scenario objective matrix with per-seed values.
- **Supplementary Table S2:** Neighbourhood-weight sensitivity at 0, 0.175, 0.35 and 0.7 (see `supplementary_table_S2_neighbourhood_weight_sensitivity.md`).
- **Supplementary Table S3:** FLUS 13-, 19- and 25-feature diagnostics, platform boundary and demand-underfill evidence (see `supplementary_table_S3_flus_feature_diagnostics.md`).
- **Supplementary Table S4:** Raster and vector delivery audit, hashes and layer counts.
- **Supplementary Table S5:** Rolling-origin and WorldCover external-product diagnostics (see `supplementary_table_S5_rolling_external_diagnostics.md`).
- **Fig. S1:** Full 3-scenarios × 3-model 2031 new-built footprint atlas (`figures/figS01_planning_atlas_2031.*`).
- **Fig. S2:** Dynamic World confidence and high-confidence change sensitivity (`figures/figS02_input_label_quality.*`).
- **Fig. S3:** Historical maps and change-error maps for 2024 (`figures/figS03_historical_2024_maps_and_errors.*`).
- **Fig. S4:** Driver layers and experiment design in English (`figures/figS04_driver_layers_and_experiment_design.*`).

---
