## Abstract

Public land-cover products are increasingly used where authoritative local time series are unavailable, but product choice and within-product discontinuities can alter apparent urban change and model rankings. We present an auditable protocol for constrained spatial allocation using Geospatial Kernel, the algorithmic core of a Geospatial World Model, as the focal execution layer. Two annual 10-m products for Abu Dhabi city, Google Dynamic World (2017–2024) and an ArcGIS-served Impact Observatory/Microsoft/Esri series (2017–2025), were harmonized to the same 100-m, six-class modelling contract. Leakage-controlled expanding-window tests compared a FLUS-style ANN–CA, Geospatial Kernel, GeoFM-LDN, persistence and random minimum-change allocation using three seeds and 1,000 spatial-block bootstrap resamples. The target year supplied oracle class totals and evaluation labels only. In 2024, the ArcGIS-served series mapped 335.57 km² as built versus 155.98 km² in Dynamic World; built-class intersection over union was 0.449. Its built class also rose by 30.6% between 2021 and 2022 while wetland and woody classes later nearly disappeared, an unreconciled series break. Kernel had the highest mean FoM in four Dynamic World targets and two matched ArcGIS-served targets; these numerical ranks did not uniformly imply paired-interval separation. Net-change allocation imposed product-specific count-only FoM upper bounds of 0.086–0.813 only for exact minimum-change allocators. Kernel's ArcGIS-minus-Dynamic World strict change Figure of Merit ranged from -0.244 to +0.205. The product-specific 2031 frontiers retained FLUS-style and Kernel candidates in all scenarios, but their objective trade-offs changed. The results support an inspectable proposal–projection–writeback boundary while showing that comparative skill is label-product dependent. Neither product is authoritative local land-use truth, model outputs remain 100 m, and the 2026–2031 maps are conditional stress tests rather than official forecasts.

## Highlights

- Cross-product backtests expose product dependence and a series discontinuity.
- Numerical rankings depend on product and conditional paired uncertainty.
- Proposal–projection–writeback traces preserve allocation auditability.
- Net-change allocation restricts exact minimum-change scores, not CA scores.
- The 2026–2031 maps remain 100-m stress tests, not statutory forecasts.

## Keywords

Geospatial World Model; land-cover change; constrained allocation; cellular automata; Abu Dhabi; scenario planning

## Introduction

Land-cover change is a spatial process. Development demand is expressed as a quantity, but its consequences depend on where each new cell is placed relative to roads, existing built areas, ecological features and other land-cover classes. This coupling matters for urban planning because two maps with the same total built area can imply very different infrastructure requirements and environmental pressures. Cellular-automata and suitability-based models have long provided a way to distribute land demand across a map, including CLUE-S, SLEUTH, Dinamica EGO, FLUS, local-attribute urban CA models and more recent patch-generating or deep-learning CA models (Verburg et al., 2002; Silva and Clarke, 2002; Soares-Filho et al., 2002; Lau and Kam, 2005; Liu et al., 2017; Liang et al., 2021). Global Earth-observation products now make it possible to construct annual, spatially aligned inputs for cities that lack a harmonized local data archive (Brown et al., 2022; Gorelick et al., 2017).

Validation studies have also shown that agreement in unchanged cells can mask poor allocation of actual change. Quantity and allocation disagreement, destination-specific transition scores and explicit calibration/validation protocols are therefore preferable to a single overall-accuracy number (Pontius et al., 2008; Pontius and Millones, 2011; van Vliet et al., 2011, 2016). This distinction is central here because the benchmark uses noisy annual labels and tests both one-step allocation and recursive rollout.

The main technical difficulty is not producing another categorical raster. It is keeping the semantics of a planning action separate from the learned transition tendency. A model may predict that a cell is likely to become built, yet the resulting map can still violate a water exclusion, miss the requested class totals or become inconsistent when the next year is simulated from the model's own output. These failure modes are particularly important when the model is used to compare scenarios rather than to reproduce one observed transition. Latent-dynamics approaches such as GeoFM-LDN can represent continuous geospatial state and condition transitions on demand, whereas traditional ANN-plus-cellular-automata systems combine suitability with explicit neighbourhood evolution. Neither design, by itself, guarantees that action semantics, hard constraints, state persistence and evidence provenance are visible at the same execution boundary.

We address this systems problem by studying Geospatial Kernel, the core transition layer of a Geospatial World Model (GWM). The Kernel represents one simulation step as a typed state, a typed action, a transition proposal, a constraint projection and a state writeback. The learned proposal remains domain-specific; the runtime contract is domain-neutral. For Abu Dhabi land-cover planning, the proposal is a six-class probability cube, and the projection allocates only mutable cells until the action's feasible class totals are reached. This separation makes the planning operation inspectable: a reviewer can distinguish what the transition model preferred from what the constraints admitted.

We evaluate this design in a controlled public-data benchmark rather than treating the benchmark as an official data release. All candidates consume the same 100-m grid, annual class-count actions, hard exclusions and evaluator. The historical track uses observed target counts to isolate spatial allocation skill from demand error. A matched protocol is run separately on Dynamic World and on an ArcGIS-served annual product so that dependence on the complete label-product pipeline is visible. The original planning track starts from the 2024 Dynamic World state; the refreshed track starts from the 2025 ArcGIS-served state. Both apply three planner-supplied actions: moderate growth, green-priority growth and high outward growth. Abu Dhabi Plan 2030 provides an institutional planning context for discussing urban structure, but the numerical actions are not calibrated to that plan or to an official population forecast (Abu Dhabi Urban Planning Council, 2007). We ask four questions: whether the Kernel execution contract is auditable, whether its allocation skill is competitive, whether comparative conclusions survive a change of land-cover product and whether the candidates produce feasible, spatially distinct scenario allocations.

The paper makes three bounded contributions. First, it gives a concrete state–action–constraint formulation for using a geospatial kernel as an algorithmic core rather than as an opaque end-to-end predictor. Second, it defines an evaluation protocol that combines expanding-window temporal tests, zero-model controls, spatial bootstrap contrasts and a whole-product-pipeline replication rather than relying on one favourable split. Third, it turns future maps into explicit stress-test artefacts, including cumulative rasters and vectorized transition footprints, while preserving the distinction between public-data land cover and authoritative legal land use.

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

The study boundary is the polygon returned for OpenStreetMap relation R4479763, representing Abu Dhabi city (OpenStreetMap contributors, 2026). All rasters were aligned to a canonical 100-m grid in EPSG:32640 with 475 columns and 360 rows. A cell was included when its centre fell within the city polygon and when the common public-data mask indicated valid coverage. The benchmark profile records the source geometry, raster transform, dimensions and SHA-256 hashes. The effective evaluation mask contains 79,726 cells.

The original Dynamic World sequence contains annual states for 2017–2024. Models were fit using the four transitions 2017→2018, 2018→2019, 2019→2020 and 2020→2021. A 2021→2022 transition was used for validation during model development. The original historical test starts from 2022 and evaluates 2023 and 2024 in an open-loop rollout without observed-state writeback. Its planning test starts from the observed 2024 state and recursively generates 2025–2031. The refreshed product track adds a separate annual sequence for 2017–2025, starts planning from its observed 2025 state and generates 2026–2031.

The leakage-controlled analysis used expanding one-step windows with origins in 2020–2023 for both products and an additional 2024 origin for the ArcGIS-served series. For origin year $t$, training included only observations available at or before $t$; the held-out $t+1$ label was prohibited from feature construction, model fitting and GeoFM-LDN epoch selection. The target supplied only observed class totals for oracle allocation, evaluation labels and the common-coverage mask. This design isolates spatial allocation conditional on known demand and is not an end-to-end demand forecast. Each fold locked origin-year water and wetland cells and omitted the two road-distance features, because the available OpenStreetMap snapshot was accessed in 2026. Kernel consequently used 23 features and the FLUS-style track used the remaining five continuous drivers. A machine-tested temporal firewall records permitted target-year uses for every model, seed and fold. The two product tracks match the boundary, 100-m grid, model implementations, seeds, target-year protocol, oracle-action rule, evaluator and 1,000-resample 8 × 8-cell spatial bootstrap. Annual labels, origin states, oracle totals, origin water/wetland masks and quality semantics remain product specific; the experiment therefore tests the complete public-product pipelines rather than an isolated label substitution. The original 2023–2024 headline comparison is less strict because it uses the later road snapshot and remains a secondary unmatched-pipeline result.

The random minimum-change controls are deterministic within each analysis but
not a shared cross-table estimator: the rolling-origin diagnostic derives its
stream from the declared seed plus origin year × 1,000, whereas the matched
product analysis uses the declared seed plus target year × 1,000. Their values
therefore serve as local zero controls in Supplementary Tables S5 and S6,
respectively, and are not compared numerically across those tables.

### Public data and class semantics

Dynamic World V1 supplies scene-level class probabilities and maximum-probability labels (Brown et al., 2022). We constructed annual labels by taking the temporal mode of the available scene labels before class crosswalking and export to the modelling grid. Annual composition is a processing choice of this study, not an official annual Dynamic World product. At each source pixel, the quality statistic is $r_y=\max_c[|T_y|^{-1}\sum_{j\in T_y}p_{j,c}]$, where $T_y$ denotes valid scenes in year $y$ and $c$ indexes the nine source classes. Thus the operation is maximum of temporal mean probabilities, not temporal mean of scene-wise maxima; its maximizing class need not equal the annual modal label. The archived band name `mean_top_probability` is retained for compatibility. This statistic is a weighting proxy, not a calibrated probability that the annual label is correct. The nine Dynamic World labels were crosswalked to six canonical classes: water (source 0), woody vegetation (1), low vegetation (2, 4 and 5), wetland (3), built (6) and bare (7). Source class 8 was excluded.

The second sequence was materialized from the public ArcGIS ImageServer `Sentinel2_10m_LandCover`, whose metadata attributes the global annual series to Impact Observatory, Microsoft and Esri (Impact Observatory et al., n.d.). The study by Karra et al. (2021) describes the classification lineage; it does not independently validate every annual layer or subsequent service revision. The associated Living Atlas item states that its 2018–2025 layers use a more complete image collection and cautions that 2017 may be less accurate (Esri, 2026). It does not disclose annual model-version identifiers. The materialization manifest, created on 9 September 2026, records the service URL, temporal extent, class mapping and SHA-256 hashes of the downloaded and aggregated rasters. No immutable upstream release identifier is recorded, so the reproducibility target is this archived snapshot rather than the changing live service.

The service labels are Water (1), Trees (2), Flooded vegetation (4), Crops (5), Built (7), Bare (8), Snow/Ice (9), Clouds (10) and Rangeland (11). We mapped them to water (1), woody vegetation (2), wetland (4), low vegetation (5 and 11), built (7) and bare (8), excluding snow/ice and clouds. Mapping Rangeland to low vegetation is a study crosswalk decision, not an official land-use statement. A descriptive counterfactual mapping it to bare before the same 10 × 10 majority aggregation changes 2,265–2,792 100-m labels per year (Supplementary Table S6); no model was refit, so this does not establish rank sensitivity. Native 10-m labels were retained for audit, then aggregated after crosswalking by majority among usable cells in each 10 × 10 block. The resulting majority fraction served as the ArcGIS-track aggregation-quality term; it is not equivalent to Dynamic World's maximum temporal-mean probability. Both sequences are explicitly treated as public land cover. Neither provides residential, commercial or industrial land use, zoning, cadastral status or development approvals.

Annual 64-dimensional AlphaEarth embeddings were spatially averaged to the canonical grid and locally L2-normalized (Brown et al., 2025). The collection is GOOGLE/SATELLITE_EMBEDDING/V1/ANNUAL, with raster hashes recorded in the GEE input manifest; Brown et al. (2025) is cited as a preprint describing the embedding model.

We formed the night-time-light driver from monthly `NOAA/VIIRS/DNB/MONTHLY_V1/VCMSLCFG` composites (Earth Observation Group, n.d.). The implementation takes an unweighted mean of available, unmasked `avg_rad` values within each calendar year; absent months are not imputed, and the collection is required to be nonempty rather than to contain twelve months. It does not apply an additional `cf_cvg` mask or observation-count weighting. This author-generated annual feature is distinct from the annual product described by Elvidge et al. (2021), which is cited for background. The monthly product documentation recommends using cloud-free observation counts to assess coverage and notes that temporary lights and background values are not separated. Uneven coverage and transient illumination can therefore affect this driver.

Copernicus DEM GLO-30 release `2024_1` supplied surface elevation and a finite-difference slope derivative (Copernicus, 2024). This is a digital surface model (DSM) containing buildings, infrastructure and vegetation, not a bare-earth terrain model. Its release identifier is not an acquisition year; the catalogue lists a 2010–2020 observation range. We have not established tile-specific acquisition dates or quantified urban surface-object effects on slope, so it is treated as a static retrospective covariate. OpenStreetMap road geometries from the Geofabrik GCC snapshot `gcc-states-260731.osm.pbf` were rasterized into distance-to-road and distance-to-major-road surfaces (Geofabrik, 2026). The source URL, snapshot date and SHA-256 are preserved in `osm_input_manifest.json`; the city geometry is separately recorded in `boundary_manifest.json`. ESA WorldCover 2021 supplied public water and wetland/mangrove constraint proxies (Zanaga et al., 2022). All dynamic and static layers were checked for exact CRS, transform, width and height agreement.

For an external public-product diagnostic, the ESA WorldCover 2020 v1.0 and 2021 v2.0 built-up class (value 50) was converted to built fraction on each 100-m benchmark cell (Zanaga et al., 2021, 2022). Built presence was tested at fractions of 0.05, 0.10, 0.20 and 0.30. Built gain required a cell to cross from below to at or above the threshold; built loss used the reverse definition. Binary precision, recall, F1 and intersection over union were calculated for the Dynamic World transition and for the 2020-origin predictions. The original oracle-demand comparison uses Dynamic World 2021 built counts; because the built count decreases in this window, it cannot allocate any built gains and is a structural-zero, zero-power test of gain location. We therefore also supplied the WorldCover built-gain count as the action, ranked candidate cells with the 2020-origin Kernel proposal, and compared it with random allocation from the same candidate population. This count-controlled variant is the informative allocation diagnostic, but it remains product agreement rather than ground-truth validation: the two WorldCover years use different product versions, WorldCover and Dynamic World both derive from Sentinel observations, and neither represents statutory Abu Dhabi land use.

### Geospatial Kernel state, action and transition proposal

Let $S_t(i)$ denote the six-class state at valid cell $i$, $A_t$ the action for the interval $t\rightarrow t+1$, and $X_t$ the aligned driver layers. The Kernel separates a proposal from a projection:

$$
Q_t(i,c)=p_\theta\big(c\mid x_i(S_t,X_t)\big),
\qquad
S_{t+1}=\Pi_{\mathcal C,A_t}(Q_t,S_t).
$$

The feature vector $x_i$ contains 25 values: six one-hot current-class indicators; twelve neighbourhood proportions, comprising 3 × 3 and 7 × 7 windows for each of the six classes; and seven continuous variables, namely normalized row and column coordinates, clipped elevation, clipped slope, log-transformed VIIRS radiance, log distance to roads and log distance to major roads. The HistGradientBoostingClassifier implementation in scikit-learn 1.9.0, as specified in the archived environment lock, estimates the six-class probability vector (Pedregosa et al., 2011). It uses learning rate 0.08, 120 iterations, at most 31 leaf nodes, minimum leaf size 40 and L2 regularization 1.0.

Training samples combine all changed valid cells and a 20% random sample of stable valid cells in each fit transition. The sample weight is the product of a change emphasis, $1+5\mathbf{1}(S_t\ne S_{t+1})$, and a quality factor, $0.5+\min(r_t,r_{t+1})$. Here $r$ is Dynamic World maximum temporal-mean probability in the original track and the within-block majority fraction in the ArcGIS-served track. These terms have different semantics and are retained as parts of their respective product pipelines. A held-out target is never used during fitting or model selection.

### Constraint projection and state writeback

For a mutable source cell $i$ of class $s$ and target class $c$, the base allocation score is

$$
q_{i,s\rightarrow c}=\log p_\theta(c\mid x_i)-\log p_\theta(s\mid x_i)+\lambda\rho^{(7)}_{i,c},
$$

where $\rho^{(7)}_{i,c}$ is the 7 × 7 fraction of neighbouring cells currently in class $c$, and $\lambda=0.35$. The algorithm computes class deficits and excesses from the action's feasible target counts, ranks all admissible source–target candidates by $q$, and changes cells in descending order until all deficits and excesses are zero. Permanent water and the protected wetland/ecological mask are held fixed. If the counts cannot be satisfied without changing a hard-exclusion cell, the step fails closed rather than silently violating the action.

This projection is a minimum-change allocator. Let $n_c$ and $a_c$ be origin and feasible target counts. The number of changed cells is exactly $M=\frac12\sum_c|a_c-n_c|$. A class can supply cells or receive cells in one step, but cannot do both; unchanged class totals therefore suppress within-class gross gain/loss exchanges. This is a substantive restriction on land-cover dynamics, shared by GeoFM-LDN through its use of the same allocator, rather than a consequence of exact-count constraints in general. With $O$ observed changed cells, strict FoM is bounded above by $\min(M,O)/\max(M,O)$ when the denominator is nonzero. This is a loose count-only bound, not an attainable optimum: destination classes, hard masks and spatial restrictions can further reduce attainable hits. Supplementary Table S7 derives the bound from the frozen fold reports and checks predicted moves against origin and feasible target counts. We do not divide observed FoM by this bound or interpret such a ratio as independently validated skill.

The projected raster is written as the next `KernelState`. Every step records a state reference, action evidence, model version, parameter reference, projection status and diagnostic counts. The runtime checks domain identity, source-time consistency and action time advancement. This execution contract is the Geospatial Kernel's algorithmic contribution; the Abu Dhabi adapter supplies the land-cover-specific features, learner and constraint masks.

### Baselines and common evaluator

The baseline was run through a GeoSOS-derived FLUS-style ANN–CA console (study-specific build; `paper-benchmark-flus-v1.1`) using seven continuous drivers: normalized row and column coordinates, elevation, slope, VIIRS radiance, distance to roads and distance to major roads. Its ANN suitability surface was passed to a cellular-automata allocation stage with the common class totals and public hard mask. The archived run used one 2021 training year, eight ANN hidden neurons, a 3 × 3 CA neighbourhood, neighbourhood strength 1.0, acceleration factor 0.1 and 1,000 iterations. Its frozen transition matrix protected water and wetland but did not prohibit built-to-non-built transitions. The algorithmic base is traceable to the GeoSOS team's public FLUS source release (Liu et al., 2017; GeoSOS team, n.d.). The binary was rebuilt from the preceding source revision `deb0a54`; the retained `paper-benchmark-flus-v1.1` source tag at `47e65b3` adds invalid-input failure handling only. Both revisions contain the study-specific `train`/`train-update` entry points and `FLUS_RANDOM_SEED` seeding for ANN sampling and CA roulette draws, so the build is not the unmodified upstream executable. A 25-feature Kernel-matched input was then executed with absolute paths for seeds 31, 47 and 73 and is reported only as a platform-sensitive diagnostic. It shares the Kernel feature family, but not the learning target or projection semantics: the FLUS ANN estimates same-year label suitability $p(S_t\mid X_t)$, whereas the Kernel proposal is trained to estimate a next-state transition $p(S_{t+1}\mid S_t,X_t)$ before constrained projection. Matching features therefore does not match the training task. Two intermediate configurations were retained as mechanism diagnostics: 13 features (seven drivers plus current-class indicators) and 19 features (seven drivers plus neighbourhood fractions). The 25-feature run collapsed to zero change for macOS seeds 47 and 73 and for all three independent external Windows x86_64 verification runs; the remaining macOS seed-31 run is not used as a valid estimator. The external evidence is identified in Supplementary Table S3; its source rasters are not locally archived. The 19-feature mode produced changes for all three macOS seeds but underfilled the observed 4,500 and 8,464 changed cells in 2023 and 2024. Both modes are therefore diagnostic-only.

GeoFM-LDN (Geospatial Foundation-Model Latent Dynamics Network; the repository's former `paper58` path identifier) was implemented as a demand-conditioned residual latent-dynamics network on 64-channel AlphaEarth patches. Three 128-channel convolutions use dilation rates 1, 2 and 4, followed by a 1 × 1 projection to a 64-dimensional latent state. A 12-dimensional action vector (origin and target counts for six classes) is encoded by a two-layer MLP and broadcast across the patch before concatenation with the embedding. Group normalization and GELU activations are used in the residual blocks. A scikit-learn logistic-regression decoder maps the predicted latent embedding to six semantic classes. Training uses 64 × 64 patches, batch size 2, eight epochs, AdamW with learning rate $3\times10^{-4}$ and weight decay $10^{-4}$; the loss is the weighted sum of cosine embedding loss, 0.5 semantic cross-entropy, 0.1 demand-consistency loss and 0.2 hard-constraint consistency loss. The released checkpoints correspond to seeds 31, 47 and 73 and were trained in August 2026. The default reproduction loads these fixed checkpoints rather than retraining; the runner exposes retraining separately. Fixed checkpoints do not remove the decoding runtime boundary: categorical output still depends on the locked Torch and scikit-learn stack. Same-stack reproduction is the declared reference; no independent cross-stack GeoFM-LDN raster comparison is claimed, and changes between pre-lock and locked-environment outputs are not attributed to CPU architecture or to one library. During allocation, GeoFM-LDN directly calls the Geospatial Kernel `allocate_action` routine, so both methods share the same constrained projection and differ primarily in their proposal model. The comparison is therefore a proposal/pipeline comparison, not a comparison of two independent projection architectures. The name describes this benchmark implementation and does not attribute an external publication or performance claim.

For the cross-product backtest, the FLUS-style suitability fit expanded from 2017 through the origin year, the Kernel transition fit ended at the origin, and GeoFM-LDN used only pre-origin label years for its decoder, pre-selection transitions for network fitting and the transition ending at the origin for epoch selection. All GeoFM-LDN folds were retrained for eight epochs at each seed rather than loading the original fixed checkpoints. The three learned candidates were evaluated alongside persistence and an exact-count random minimum-change allocator. Kernel, GeoFM-LDN and random allocation met feasible oracle class totals exactly; the finite-iteration FLUS-style CA retained any unmet demand as normalized demand total variation rather than receiving a post-hoc raster correction.

The common evaluator computes actual class counts, normalized demand total variation, hard-mask violations, strict multi-class change FoM, binary change FoM, change F1, overall accuracy and macro-F1 for historical runs. The strict FoM counts a hit only when the predicted destination class equals the observed destination class; wrong destination changes are retained in the denominator. It also generates persistence and minimum-change zero controls, spatial-block bootstrap intervals and paired model-difference intervals for strict FoM, overall accuracy and macro-F1. For planning runs it additionally computes ecological conversion, new-built neighbourhood fraction, new-built component counts, the union of 2024 built and newly built components, all-final-built component counts, a 500-m leapfrog rate, distances to roads and prior built cells, infrastructure proxy distance and built retirement. Pareto membership is calculated within each scenario over three release objectives: major-road distance, prior-built distance and union-built component density. Ecological conversion is retained as a descriptive public-data pressure proxy because it is structurally zero for the two exact-count allocators and therefore has no discriminating power in their comparison. Vegetation gain is a scenario input and remains descriptive, not an objective.

### Scenario actions and uncertainty

The moderate-growth, green-priority-growth and high-outward-growth actions are stored in the tracked product-specific scenario manifests; the legacy `compact` path identifier is retained only for artifact compatibility. It is not an endorsement of compact-city outcomes, which can have distributional trade-offs (Burton, 2000). Dynamic World-origin actions cover 2025–2031 and ArcGIS-origin actions cover 2026–2031. Their totals are explicit extensions of the preceding annual difference and are not derived from an official population, housing or infrastructure forecast. Future exogenous rasters are held at their respective final observed-year values. The green-priority action is not a water-budget model. Each candidate is run at seeds 31, 47 and 73, and planning tables report arithmetic means and population standard deviations. No p-values are reported because the three seeds describe computational variability, not independent field samples. The green-priority label denotes a vegetation-quantity sensitivity action, not demonstrated ecological sustainability. The primary Pareto comparison is within each scenario, contrasting the three models under the same product-specific action; cross-product frontier membership is a sensitivity test, not a forecast-accuracy comparison. The current release objective set is road access, prior-built distance and union-built component density. Ecological conversion is reported as a diagnostic rather than a Pareto objective because it is structurally zero for the exact-count Kernel and GeoFM-LDN allocations. We treat this as a release objective set rather than a prespecified planning preference, and treat its variants as robustness diagnostics.

### Change polygons and reproducibility

For each model–scenario pair, annual and cumulative differences from the origin raster are extracted as changed 100-m cells and dissolved into GeoPackage layers. The Dynamic World-origin delivery manifest covers 45 ensemble rasters for 2027–2031 and nine vector packages. The ArcGIS-origin delivery contains 54 ensemble rasters for 2026–2031, nine multilayer GeoPackages and matching Shapefiles; a separate native-10-m GeoPackage records observed 2024→2025 product change. The audit scripts fail on missing source rasters, reports or vectors. Historical predictions and bootstrap reports for both product tracks retain per-file hashes and temporal-firewall declarations. The vector layers preserve raster-cell geometry and should not be interpreted as cadastral parcels.

## Results

### A common benchmark separates allocation skill from demand assumptions

The benchmark covers the Abu Dhabi city polygon represented by OpenStreetMap relation R4479763. The canonical grid is a 475 × 360 lattice in EPSG:32640 at 100-m resolution. The original Dynamic World evaluation mask contains 79,726 cells and the ArcGIS-served track contains 79,775 cells before target-specific common-coverage checks. Each cell represents 1 ha. Both annual sequences were harmonized to six land-cover classes: water, woody vegetation, low vegetation, wetland, built and bare. AlphaEarth annual embeddings, VIIRS night-time lights, Copernicus DEM derivatives and OpenStreetMap road distances supplied transition drivers. ESA WorldCover and public OpenStreetMap geometries supplied water, wetland and infrastructure exclusion proxies.

The comparison shared the canonical grid, origin states, target actions, hard masks and evaluator, but the public-data run was not information-balanced. The original FLUS-style control used seven continuous drivers in its external ANN suitability model, whereas Geospatial Kernel used 25 features including current-class indicators and neighbourhood proportions; GeoFM-LDN used AlphaEarth latent embeddings and the Kernel allocator. We therefore report the original result as an unmatched-input pipeline comparison, not evidence that one learner is intrinsically superior. The additional 25-feature FLUS run is a feature-space diagnostic only, because it still learns same-year suitability rather than next-state transitions and does not use the Kernel projection implementation. Across six platform–seed runs, five produced zero-change outputs through current-class identity leakage. The archived FLUS console is a Mach-O arm64 executable rebuilt from the public GeoSOS source base with the author-modified `train`/`train-update` entry points and `FLUS_RANDOM_SEED` seeding patch; its exact source is archived at `FLUS_console_crossplatform` commit `deb0a54`. It is not asserted to be bitwise equivalent to an unmodified upstream build. All headline and diagnostic runs used seeds 31, 47 and 73.

The execution trace makes the distinction between proposal and admission explicit. A Kernel step records the source state, action, probability-cube proposal, projected state, model identity, input evidence and next-state reference. The runtime checks that the action advances the source time and that the projected raster becomes the next state. This is the operational meaning of the Kernel in this study: not a claim that all GWM domains share the same learner, but a claim that they can share an auditable execution contract. The shared inputs and execution boundary are summarized in Fig. 1.

![Benchmark and Geospatial Kernel execution contract. Public annual land-cover, embedding, night-light, terrain and road layers are aligned to a common 100-m Abu Dhabi grid. The Kernel exposes a learned proposal, a constraint projection and a state writeback. The schematic describes a public-data benchmark and does not imply statutory planning boundaries.](figures/fig01_benchmark_contract.png){width=100%}

\FloatBarrier

### Secondary historical benchmark and planning objective definitions

The historical track uses observed target class totals to isolate spatial
allocation from demand estimation. The primary metric is strict multi-class
change FoM: a hit requires the predicted destination class to equal the
observed destination class, while wrong destination changes remain in the
denominator (Pontius et al., 2008). Overall accuracy, macro-F1, change F1 and
binary FoM are secondary diagnostics. Uncertainty is estimated with an
8 × 8-pixel spatial-block bootstrap, and model contrasts are computed from the
same resampled blocks for each frozen seed. Persistence and random
minimum-change allocation are explicit zero-model controls.

The original planning track starts from the observed 2024 state and applies three
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

The Dynamic World quality-proxy sensitivity is a label-quality and selection-effect diagnostic,
not an independent validation set or a model-skill test. Requiring both the
origin and target Dynamic World maximum temporal-mean probability to exceed 0.5 retains only
25 of 4,500 observed changes (0.56%) in 2023 and 56 of 8,464 (0.66%) in 2024.
Strict FoM is 0.000 for all three models in 2023; in 2024 the means are 0.0040
for the FLUS-style console, 0.0055 for Geospatial Kernel and 0.0188 for
GeoFM-LDN. Screening only the quality-proxy value of the year immediately preceding the
target avoids filtering on the target-year quality proxy, but still retains only 129
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
of the three seeds. The shared low 2022 values (Kernel 0.0724; random 0.0048)
indicate a difficult 2021→2022 transition for all allocators, consistent with
the elevated label-reversion rate in Fig. S2 and the contemporaneous fluctuation
in Dynamic World built counts, rather than a Kernel-specific failure. Persistence
also retained higher overall accuracy than Kernel in 2022–2024, whereas Kernel
had higher overall accuracy only in 2021. The change-specific and all-cell
metrics therefore answer different questions.

The WorldCover comparison has two distinct interpretations. Across built
fractions from 0.05 to 0.30, WorldCover contained 1,445–1,802 built-gain cells
and 1,408–1,506 built-loss cells. Dynamic World-to-WorldCover built-gain F1 was
only 0.0111–0.0192. Dynamic World built pixels decreased from 9,642 in 2020 to
8,553 in 2021, so under the 2020→2021 Dynamic World oracle-demand action the
Kernel, random and persistence allocators necessarily produced no built-gain
cells. Their F1 of 0 is therefore a structural-zero, zero-power result and
cannot evaluate gain-location skill. The informative count-controlled variant
used the WorldCover gain count as the action and ranked 2020-origin Kernel
proposals against a random allocation from the same candidate population. Kernel
F1 was 0.0157–0.0397 versus 0.0251–0.0277 for random allocation. The mean ±
sample-SD pairs (Kernel versus random) were 0.0157 ± 0.0008 versus 0.0268 ±
0.0058 at 0.05, 0.0228 ± 0.0007 versus 0.0277 ± 0.0036 at 0.10, 0.0268 ±
0.0011 versus 0.0251 ± 0.0011 at 0.20, and 0.0397 ± 0.0007 versus 0.0251 ±
0.0075 at 0.30. Thus Kernel was below random at 0.05, the 0.10–0.20
differences were not distinguishable from three-seed variation, and only the
0.30 result was clearly above random. The low-threshold deficit is consistent
with WorldCover cells that barely exceed 5% built fraction, including sparse or
road-edge structure that Dynamic World does not consistently label as built;
the Kernel proposal learned from Dynamic World therefore ranks these product-
specific gains later than random candidates. For 2021 built stock, Kernel F1 was 0.3518–0.3971, while persistence was 0.3886–0.4387. The
corresponding Dynamic World 2020 and 2021 observed-stock baselines were
0.3908–0.4334 and 0.3501–0.3924, respectively, showing that the apparent
persistence advantage mirrors greater agreement of the 2020 label with
WorldCover rather than a model advantage. Fig. 3 separates these stock and
count-controlled gain comparisons; none is authoritative validation.

![Rolling-origin robustness and external-product diagnostics. Panel a reports strict destination-change FoM for four leakage-controlled one-step targets; points show means and sample standard deviations across three computational seeds. Panel b reports Kernel-minus-baseline paired spatial-block contrasts; points are mean seed medians and whiskers span the minimum to maximum of seed-specific 95% intervals from 1,000 resamples of 8 × 8-cell blocks. Panel c compares same-year Dynamic World 2020 and 2021 built stocks, plus 2021 Kernel and persistence predictions, with the corresponding WorldCover products at four 100-m built-fraction thresholds. Panel d compares Dynamic World built gain with the count-controlled Kernel and random allocations, where WorldCover gain count is supplied as the action. The original oracle-demand gain test is structural-zero and is not plotted as model evidence. The WorldCover comparison is an external public-product diagnostic, not authoritative ground truth. Source data are provided in source_data_fig03_rolling_external_diagnostics.csv.](figures/fig03_rolling_external_diagnostics.png){width=100%}

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

### Cross-product replication changes measured model skill

The harmonized products disagree materially even before a model is fitted.
Across 2017–2024, same-year all-class agreement ranged from 0.651 to 0.745 and
built-class intersection over union from 0.320 to 0.449. In 2024, Dynamic World
mapped 155.98 km² of built land on the common grid, whereas the ArcGIS-served
Impact Observatory/Microsoft/Esri series mapped 335.57 km². The latter declined
to 327.31 km² in 2025. The added year improves the currency of the public origin
state, but neither the larger built stock nor the native 10-m pixel size
establishes greater local accuracy.

The complete 6 × 6 annual cross-product matrices are supplied with the source
data. In 2021, 2022 and 2024, 61–68% of discordant cells were Dynamic World
bare mapped as ArcGIS-served built (13,078, 18,787 and 17,987 cells,
respectively); a further 3,723–4,496 cells per year were Dynamic World bare
mapped as ArcGIS-served water. The ArcGIS-served product also mapped 4,501,
4,985 and 5,131 more water cells than Dynamic World in those three years.
Because origin-year water and wetland are hard masks, this product difference
reduces the feasible allocation domain in the ArcGIS track. It is therefore a
pipeline difference, not an isolated replacement of target labels.

The ArcGIS-served sequence is also not temporally homogeneous under this
crosswalk. Its mapped built cells rise from 21,608 in 2021 to 28,214 in 2022
(+30.6%), while bare cells fall from 34,521 to 27,821. Woody vegetation declines
from 293 cells in 2021 to 22 in 2023 and 2 in 2025; wetland similarly declines
from 792 to 24 and 17. Supplementary Table S6 reports all annual class stocks,
the crosswalk sensitivity and product-agreement data. Dynamic World, in contrast,
retains roughly 900–1,100 wetland cells and 311–917 woody cells. The Living Atlas
documentation flags a different 2017 imagery basis but provides no annual
model-version history, so we cannot attribute the 2021–2023 break to a specific
service change. It must not be read as observed city conversion. In particular,
the high 2022 ArcGIS score evaluates allocation against a target whose class
totals partly encode this discontinuity; it is not evidence that the model
recovered a verified one-year construction event. The ArcGIS 2025 planning origin
likewise contains only two woody and 17 wetland cells. Water and wetland masks
remain hard exclusions, but ecological semantics attached to the latter class are
structurally sparse in that product track.

Under the leakage-controlled matched protocol, Geospatial Kernel had the
largest mean strict FoM in all four Dynamic World targets (0.2595, 0.0724,
0.2116 and 0.1816 for 2021–2024), but in only two of the four matched
ArcGIS-served targets. FLUS-style ANN–CA had the highest mean in the
ArcGIS-served 2021 target (0.0625 versus Kernel 0.0154 and GeoFM-LDN 0.0314),
but this is not a like-for-like minimum-change comparison: FLUS changed
779–6,860 cells across seeds whereas the other three allocators changed exactly
278. GeoFM-LDN led in 2022
(0.4488 versus 0.2775 and 0.2227), and Kernel numerically led in 2023 and 2024
(0.1619 and 0.1674). The Kernel-minus-random paired spatial-block interval
excluded zero in every ArcGIS-served year and seed, including the additional
2025 target, but its ArcGIS-minus-Dynamic World mean FoM difference was -0.244,
+0.205, -0.050 and -0.014 across the four matched years. Thus the learned
allocator contains repeatable spatial signal relative to its zero model, while
its absolute score and rank remain dependent on the product pipeline. Supplementary
Table S7 reports all seed-specific paired intervals for Kernel versus FLUS-style
and GeoFM-LDN versus Kernel. In the ArcGIS 2023 target, all three GeoFM-LDN-minus-
Kernel intervals include zero despite Kernel's higher mean; in 2024, two exclude
zero in Kernel's favour and one includes zero. These are conditional intervals,
not a pooled ranking test. The additional ArcGIS 2025 target gives mean FoM of
0.0731 for FLUS-style, 0.0654 for GeoFM-LDN and 0.0579 for Kernel. The FLUS mean
is driven upward by its seed-73 result (6,693 changed cells; FoM 0.1052), while
its other two seeds (1,651 and 957 changed cells; FoM 0.0632 and 0.0510) overlap
the Kernel seed range. Kernel is therefore not the numerical leader in that fold,
but neither is a seed-pooled claim of FLUS superiority supported. Block-size
sensitivity has not been established, and repeated seeds do not constitute
independent spatial or temporal replication. The
finite-iteration FLUS-style CA retained demand total variation up to 0.00153 in
the ArcGIS-served track and 0.00415 in Dynamic World; the exact-count Kernel,
GeoFM-LDN and random allocators had zero demand error by construction.
Supplementary Table S6 reports all target years and product-agreement values.

The count-only analysis exposes an additional source of score dependence for
the exact minimum-change projections only. In
the ArcGIS 2021 fold, the minimum-change action permits 278 moves against 3,241
observed changes, bounding strict FoM at 0.0858 even before destination or
hard-mask restrictions. In 2022, 6,864 permitted moves against 8,446 observed
changes give a much higher bound of 0.8127. The corresponding Dynamic World
bounds are 0.4590 and 0.2885. All nine fold bounds and observed scores are
reported in Supplementary Table S7. The reversal in these bounds means that
cross-product FoM differences combine allocation skill with the relationship
between net and gross product change. It does not identify which product is
more accurate. Supplementary Table S7 also shows that FLUS already permits
simultaneous class inflows and outflows: its altered-cell totals span 1.1–24.7
times M across the ArcGIS folds. The bounds therefore do not explain its 2021
mean or constrain its FoM.

Frontier membership was more stable than the historical numerical ranking. Recomputing
the same three-objective Pareto rule on each product-specific 2031 scenario
bundle retained FLUS-style and Kernel candidates, and excluded GeoFM-LDN, in
all three scenarios. This does not validate either future bundle; it shows only
that frontier membership was insensitive to this particular public-product
replacement under the released proxy objectives. The retained candidates trade
off different objectives after product replacement: in every ArcGIS scenario,
FLUS has lower mean major-road distance and lower union-built component density,
whereas Kernel has lower mean distance to pre-existing built cells (Supplementary
Table S1). Identical membership among three candidates therefore does not
establish spatial agreement, stable objective profiles or planning benefits.
Product-specific origins, horizons and actions also differ; this is not a
controlled experiment holding demand and initial conditions fixed. Fig. 4 separates changes in
mapped stock, same-year product agreement, ArcGIS-served historical skill and
the matched product difference.

![Land-cover product robustness. Panel a compares annual mapped built area; the dashed line marks the apparent 2021–2022 ArcGIS class-composition break, not a verified city-change event. Only the ArcGIS-served Impact Observatory/Microsoft/Esri series extends to 2025. Panel b reports same-year all-class agreement and built-class intersection over union after six-class harmonization at 100 m. Panel c reports strict destination-change FoM for the ArcGIS-served expanding-window backtest; points are three-seed means and whiskers are population standard deviations. Panel d gives the ArcGIS-served-minus-Dynamic World mean FoM for the four matched one-step targets. All models omit the later road snapshot. Product-specific labels, origin states, oracle totals, origin water/wetland masks and quality semantics are retained, so this is a whole-product-pipeline test rather than authoritative validation. Source data are provided in source_data_fig04_product_robustness.csv.](figures/fig04_product_robustness.png){width=100%}

\FloatBarrier

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
The ArcGIS-origin bundle does not preserve the same objective ordering. In its
three scenarios, FLUS-style ANN–CA has lower mean distance to major roads
(368/366/389 m) and lower union-built component density (0.731/0.798/0.631 per
1,000 cells), whereas Kernel has lower mean distance to pre-existing built
cells (119/113/155 m; Supplementary Table S1). Thus the two retained frontier
members are stable as a set, but the dimension supporting each member changes
when the product-specific origin and actions change.
The corresponding objective profiles and diagnostic trade-offs are shown in
Fig. 5.

![Conditional planning objectives. The 2031 outcomes compare the three models under moderate-growth, green-priority-growth and high-outward-growth actions. Panels show the three release objectives: distance to major roads, distance to pre-existing built cells, and connected components in the combined 2024-built and newly built footprint. Black outlines indicate membership of the within-scenario Pareto frontier.](figures/fig05_planning_objectives.png){width=100%}

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

The base Kernel allocation score adds a 7 × 7 target-class neighbourhood fraction with weight 0.35. The existing sensitivity and mechanism artefacts are retained as diagnostic controls; they do not identify a causal effect because the proposal features and allocator both contain spatial context. The neighbourhood term is therefore interpreted as evidence about the execution mechanism, not as an independently estimated planning preference. Fig. 6A shows focused proposal controls, and Fig. 6B reports the matched runtime controls.

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

![Mechanism controls. Panel A compares the full transition proposal with selected proposal controls. Panel B gives the strict destination-change FoM difference between matched runtime controls and the full Kernel. Bars show mean plus or minus population standard deviation across the three frozen seeds. The no-state-writeback control is undefined for the 2023 one-step target and is therefore shown only for 2024. These are execution diagnostics, not causal policy experiments.](figures/fig06_mechanism_ablation.png){width=100%}

\FloatBarrier

### Spatial footprints are scenario-conditioned, not parcel predictions

The 2031 majority-vote ensemble L1 demand errors were 8, 44 and 42 pixels for
the Kernel's moderate, green-priority and high-outward scenarios, respectively;
the corresponding GeoFM-LDN errors were 1,580, 1,524 and 1,148 pixels and the
FLUS-style errors were 2,504, 2,888 and 2,568 pixels. Kernel and GeoFM-LDN seed-level projections
meet their feasible class totals, whereas the finite-iteration FLUS control can
retain demand error. Majority voting can produce a different raster and therefore
a non-zero ensemble error even for an exact-count allocator. The constraint-
preserving claim applies to individual projected members, not to count preservation
in the majority-vote delivery. Those ensembles are descriptive consensus maps.
Any use requiring exact totals must select and audit a feasible seed-level member
or reproject the consensus, with objective values recomputed on that final map.
No such reprojected ensemble is evaluated here. All 312 historical,
rolling-origin and planning prediction records passed the raster audit, and the
two frozen WorldCover evidence rasters passed the evidence audit. Fig. 7 uses the high-outward
scenario to make the spatial contrast legible; the complete nine-panel atlas is
provided as Fig. S1. These are raster-cell change footprints, not
parcel boundaries or statutory zoning maps.

![High-outward-growth spatial footprints. The observed 2024 state is compared with each model's 2031 majority-vote ensemble. Orange denotes cells newly built between 2024 and 2031; grey denotes cells already built in 2024. The map is a 100-m scenario stress-test product, not a cadastral or statutory land-use map.](figures/fig07_planning_maps_2031.png){width=100%}

\FloatBarrier

## Discussion

This study positions Geospatial Kernel as a candidate execution layer for constrained spatial reasoning and, more broadly, proposes an audit protocol for annual label-product uncertainty. The defensible contribution is that a transition proposal and a planning admission rule can be represented and inspected separately even when the observational product changes. Kernel exceeded the random minimum-change control in every Dynamic World and ArcGIS-served expanding-window fold, but product replacement changed its absolute FoM by as much as 0.244 downward and 0.205 upward and changed which learned model ranked first. The original unmatched 2023–2024 result is therefore supporting evidence, not a universal ordering. By contrast, the released three-objective planning frontiers retained FLUS-style and Kernel candidates across both product-specific scenario bundles. Historical allocation skill and conditional planning-objective membership are different robustness questions; neither is a test of statutory forecast accuracy.

The WorldCover diagnostic also does not provide blanket external validation: the original Dynamic World-count gain comparison is structurally zero-powered because the observed built count declines. Its count-controlled variant remains near opportunity-level agreement overall: Kernel is below random at 0.05, indistinguishable from random at 0.10–0.20 given three-seed variation, and above random only at 0.30. The low-threshold deficit is consistent with WorldCover's sparse or road-edge cells just above the 5% built-fraction threshold being inconsistently represented by Dynamic World. Confidence filtering, rolling-window stability, WorldCover agreement and the new complete-product replication test different failure modes. None substitutes for authoritative local validation.

The evidence remains bounded. The six classes are remote-sensing land cover, not
statutory residential, commercial or industrial land use. Dynamic World and the
ArcGIS-served series are both global products derived from Sentinel observations;
their disagreement does not identify which label is correct. Product-native
quality terms and origin-year water/wetland masks also differ, so the replication
measures complete pipeline dependence rather than a causal effect of replacing
labels alone. The ArcGIS series additionally has a pronounced internal
class-composition break between 2021 and 2023, with no published annual
model-version history. Its 2022 change prevalence and high GeoFM-LDN FoM may
therefore partly score a product reclassification rather than land-cover change;
the sparse ArcGIS wetland/woody states also weaken ecological interpretation of
the 2025-origin scenario track. The available 2020–2021 WorldCover diagnostic is neither fully
independent nor authoritative, and no local reference change sample or observed
2026–2031 label exists. The original headline analysis also uses a 31 July 2026 OSM road snapshot,
which may contain roads constructed after 2022. Sharing this information does not guarantee an unchanged model ordering,
because learners can exploit it differently; the strict rolling-origin analysis removes those road
features. This firewall controls downstream target-label use and the late road snapshot; it does not establish that retrospective global products, pretrained embeddings or the static DSM were available to a forecaster at each historical origin. As a descriptive bound,
the road-free rolling 2023 one-step FoM is 0.2116, of the same order as the
headline 2023 value of 0.1961; these values are not directly comparable because
the rolling fit uses 23 features and training through 2022, whereas the headline
fit uses 25 features and training through 2021. Public wetland and
protected-area layers are proxies, future drivers are held at the respective
2024 or 2025 origin-year values, and the
green-priority action has no water-budget constraint. The FLUS-style
control is an Apple-Silicon binary rebuilt from the public GeoSOS source base
with study-specific `train`/`train-update` and deterministic-seeding patches;
its headline comparison uses seven drivers. It is already a gross-transition
allocator: across ArcGIS folds it changes 1.1–24.7 times the exact minimum-change
budget while retaining near-zero demand error. This extra transition budget does
not itself deliver higher FoM: FLUS is below Kernel on Dynamic World 2021 despite
changing 4.4–5.2 times as many cells, and its apparent ArcGIS 2021/2025 mean
advantages occur where its seed-specific altered-cell totals are highly variable.
The next gross-transition experiment should therefore hold the proposal model,
candidate pool and constraints fixed rather than treating the existing FLUS
baseline as a direct test of Kernel's projection. The 25-feature run is a
platform-sensitive identity-leakage diagnostic: five of six platform–seed runs
collapsed to zero change, so the non-collapsed macOS seed-31 result is not used
as a comparative estimate.
These public-data stress tests therefore do
not establish causal planning effects or a validated Abu Dhabi forecast. An
authoritative deployment would replace public labels and masks with locally
approved land-use, infrastructure, ecological and development-demand records
while retaining the same execution contract.

### Implications for planning use and validation

The practical role of this protocol is to expose where a public-data scenario
depends on observational definitions and allocation restrictions before a
planner treats its map as evidence. Stable frontier membership is insufficient
for selecting a site or infrastructure corridor: a decision also requires the
spatial overlap and disagreement of new-built locations, feasible water and
infrastructure demands, and the magnitude of the objective differences. These
decision-level tests have not been completed here. The existing frontier is a
conditional comparison of three implementations, not a search over all feasible
plans or a recommendation that either retained model should determine land use.

The next validation step should use a spatially stratified reference sample of
product-agreement changes, product-disagreement changes and stable cells, assessed
from contemporaneous independent imagery or locally approved records. Reference
interpretation should be blinded to model identity, record ambiguous cases and
report sampling weights and class-specific gain/loss accuracy. In parallel, a
transition-budget allocator permitting simultaneous gain and loss should be
compared with the minimum-change projection under the same proposal, candidate
pool and masks. The FLUS baseline provides only partial evidence because its
suitability learner, finite CA iterations and candidate mechanism also differ.
Neither independent reference validation nor this controlled gross-transition
experiment has been performed. They are requirements for extending the present
conditional allocation findings to operational planning claims.

## Conclusions

Replacing Dynamic World with a newer ArcGIS-served 10-m annual product did not
simply raise or lower every score. It changed mapped built stock, transition
prevalence and the leading model by year, while its 2021–2023 class-composition
break made part of the apparent change unsuitable as evidence of city change.
Geospatial Kernel remained consistently better than random minimum-change
allocation, but it was not universally the best learned model. Its strongest
transferable property in this experiment is therefore the auditable separation
of learned proposal, constrained projection and state writeback, not a
product-independent accuracy claim. The count-only bounds constrain only the
exact minimum-change projections; the FLUS baseline already shows that allowing
more gross change alone does not determine FoM. A controlled gross-transition
comparison must separate that budget from proposal-model skill.

The refreshed series adds a 2025 public origin state, native-10-m audit rasters
and complete 2026–2031 raster and vector scenario deliveries. Model execution
remains at 100 m, and both future bundles are conditional stress tests. A valid
operational forecast still requires locally approved land-use history, planning
constraints, demand assumptions and an independent change-validation design.

## Data availability

The public-data benchmark manifests, protocols, reports and generated delivery artefacts are organized under `benchmarks/abu_dhabi_land_use_v1/` and `benchmarks/abu_dhabi_land_use_v2/` in the accompanying repository. The ArcGIS-served cross-product source release is archived at Zenodo v2.0.0 (https://doi.org/10.5281/zenodo.22689057), corresponding to GitHub tag `v2.0.0` at commit `77e2c59`; the version-independent concept DOI is https://doi.org/10.5281/zenodo.22663475. The published v2 release is defined by `reproducibility/MANIFEST.json` (immutable inputs, assets and code) and `reproducibility/PUBLICATION_OUTPUTS.json` (reports, source data, figures and delivered rasters/vectors). This manuscript's separate working-revision manifest additionally freezes the 27 per-seed 2031 ArcGIS planning rasters required to regenerate Fig. 4 and Supplementary Tables S1/S6 from frozen inputs. The Zenodo record contains GitHub's automatically generated source ZIP, which was inspected after publication and contains Git LFS pointers rather than hydrated large rasters, GeoPackages and model checkpoints. A full numerical rerun therefore requires checking out the tagged GitHub repository and retrieving its LFS objects; the DOI record alone is not a self-contained binary-data archive. The main evidence files are:

- `comparison_report_current.json` and `comparison_report_current.md` for historical metrics when a data-complete rerun is available;
- `planning_comparison_report_public_2025_2031_current.json` and its Markdown rendering for 2031 planning objectives;
- `planning_scenario_report_public_2025_2031_current.json` for per-seed rollout traces;
- `planning_public_2025_2031_delivery_manifest_current.json` for raster and vector delivery;
- `output_audit.json` for the current raster audit; `output_audit_reproducible.json` is a compatibility copy produced by the same run;
- `artifacts/rolling_backtest/report.json` and `paired_spatial_uncertainty.json` for the four leakage-controlled one-step windows;
- `supplementary_table_S5_rolling_external_diagnostics.md` for the synchronized rolling and external-product table;
- `artifacts/external_validation/worldcover/` for frozen WorldCover built-fraction inputs, hashes and the external-product diagnostic;
- the v2 source manifest under `artifacts/arcgis_sentinel2_landcover/` for service metadata, catalog records and downloaded-raster hashes;
- the v2 paired reports under `artifacts/arcgis_v2_historical_backtest/` and `artifacts/dynamic_world_matched_backtest/` for the two complete three-model expanding-window tracks;
- the v2 cross-product summary under `results_arcgis_v2/paper_refresh/`, Supplementary Tables S1/S6, and the 27 frozen per-seed 2031 ArcGIS planning states, whose locations and hashes are recorded in the working-revision publication-output manifest;
- the v2 `results_arcgis_v2/ensembles/` and `vectors/` directories for the 2026–2031 raster and change-footprint deliveries;
- the data-audit, protocol and source-input manifests for data provenance;
- The released bundle includes the aligned 2017–2024 public rasters, historical and rolling-origin prediction rasters, frozen WorldCover built-fraction rasters, 2025–2031 planning rasters, nine GeoPackages of dissolved change footprints, model checkpoints and SHA-256 manifests. Working-revision text records use canonical LF hashes and pass with `core.autocrlf=true`; exact verification of the published v2.0.0 manifests requires a separate LF checkout (`git -c core.autocrlf=false checkout v2.0.0`) because six historic text records use raw-byte hashes. The locked macOS arm64 execution environment remains the reference for model outputs. An archived arm64 Linux rerun of the six historical Kernel rasters differed from the macOS reference by 498–1,147 cells (0.62%–1.44%), with strict-FoM deltas from -0.0023 to +0.0010; these cross-stack differences are quantified rather than treated as categorical identity. A maintained GitHub Actions Ubuntu x86_64 rerun of all six rasters under the resolved lock had zero categorical differences; the repository-stored CI audit is in `artifacts/cross_platform`, and the workflow is versioned under `.github/workflows/`. Independent external Windows evidence remains separately labelled for FLUS because the corresponding rasters are not archived locally. No private database address, credential or client-only service is included. Authoritative Abu Dhabi land-use and independent reference data remain outside this study.

The current working revision and the published v2.0.0 archive are distinct
versions. The published DOI continues to identify its original tagged inputs,
outputs and manuscript. The working revision adds report-derived allocation and
crosswalk analyses, working-revision 2031 seed rasters, and revised interpretation
without retraining models or replacing historical prediction rasters. Its separate working manifests and source hashes
are described in `benchmarks/abu_dhabi_land_use_v2/reproducibility/WORKING_REVISION.md`;
passing them verifies the declared revision, not a new DOI release.

## Code availability

The analysis scripts, a vendored Geospatial Kernel runtime snapshot, benchmark protocol, model runners and figure-generation code are maintained in the accompanying repository. Principal entry points are listed separately to keep the manuscript readable:

- `run_geospatial_kernel.py` for the Kernel historical run;
- `run_rolling_backtest.py` and `run_rolling_uncertainty.py` for the expanding-window experiment and paired spatial-block intervals;
- `materialize_worldcover_validation.py` for frozen WorldCover inputs;
- `run_worldcover_external_diagnostic.py` for the agreement diagnostic;
- the vendored `geospatial_kernel/runtime.py` snapshot;
- `render_nature_figures.py` and `render_rolling_validation_figure.py` for publication artwork;
- `source_data_fig03_rolling_external_diagnostics.csv` for the quantitative source data behind Fig. 3.
- `run_arcgis_historical_backtest.py` for both leakage-controlled product tracks;
- `analyze_product_robustness.py`, `source_data_fig04_product_robustness.csv`, `supplementary_table_S1_arcgis_planning_objectives.md` and `supplementary_table_S6_product_robustness.md` for the cross-product analysis; its frozen 2031 seed states allow this analysis to rerun without a new simulation;
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
`zhouning@freedotech.com`. The versioned v2 source release is archived at
https://doi.org/10.5281/zenodo.22689057 and corresponds to GitHub tag `v2.0.0`
at commit `77e2c59`; the DOI identifies the public benchmark source release,
not the eventual journal article DOI. Hydrated Git LFS objects must be fetched
from the tagged repository for a full numerical rerun.

## Declarations

**Funding.** No external funding was received for this study.

**Competing interests.** Ning Zhou is employed by Beijing Freedo Technology Co., Ltd., which develops geospatial-world-model software. The author declares no other competing financial or personal interests.

**CRediT author statement.** Ning Zhou: Conceptualization, methodology, software, data curation, formal analysis, visualization, writing—original draft, writing—review and editing.

**Acknowledgements.** The author thanks the anonymous reviewers for independent technical verification and constructive methodological comments.

**Ethics statement.** Not applicable; the study used geospatial raster, vector and derived public-data products and did not involve human or animal participants.

**Declaration of generative AI and AI-assisted technologies in the writing process.** During preparation of this work, the author used OpenAI Codex for language editing, code review and document-formatting assistance. The author reviewed and revised all outputs and takes full responsibility for the content of the publication.

## References

Abu Dhabi Urban Planning Council. (2007). Plan Abu Dhabi 2030: urban structure framework plan. Abu Dhabi, United Arab Emirates.

Brown, C. F., Brumby, S. P., Guzder-Williams, B., Birch, T., Hyde, S. B., Mazzariello, J., Czerwinski, W., Pasquarella, V. J., Haertel, R., Ilyushchenko, S., Schwehr, K., Weisse, M., Stolle, F., Hanson, C., Guinan, O., Moore, R., & Tait, A. M. (2022). Dynamic World, near real-time global 10 m land use land cover mapping. *Scientific Data*, 9, 251. https://doi.org/10.1038/s41597-022-01307-4

Brown, C. F., Kazmierski, M. R., Pasquarella, V. J., Rucklidge, W. J., Samsikova, M., Zhang, C., Shelhamer, E., Lahera, E., Wiles, O., Ilyushchenko, S., Gorelick, N., Zhang, L. L., Alj, S., Schechter, E., Askay, S., Guinan, O., Moore, R., Boukouvalas, A., & Kohli, P. (2025). AlphaEarth Foundations: An embedding field model for accurate and efficient global mapping from sparse label data. *arXiv*. https://doi.org/10.48550/arXiv.2507.22291

Burton, E. (2000). The compact city: just or just compact? A preliminary analysis. *Urban Studies*, 37, 1969–2006. https://doi.org/10.1080/00420980050162184

Copernicus. (2024). Copernicus DEM GLO-30 (2024_1): Global 30m Digital Elevation Model [Data set; digital surface model]. Google Earth Engine Data Catalog. https://developers.google.com/earth-engine/datasets/catalog/COPERNICUS_DEM_GLO30_2024_1 (accessed 10 September 2026).

Earth Observation Group, Payne Institute for Public Policy, Colorado School of Mines. (n.d.). VIIRS Stray Light Corrected Nighttime Day/Night Band Composites Version 1 [Monthly data set; VCMSLCFG]. Google Earth Engine Data Catalog. https://developers.google.com/earth-engine/datasets/catalog/NOAA_VIIRS_DNB_MONTHLY_V1_VCMSLCFG (accessed 10 September 2026).

Elvidge, C. D., Zhizhin, M., Ghosh, T., Hsu, F.-C., & Taneja, J. (2021). Annual time series of global VIIRS nighttime lights derived from monthly averages: 2012 to 2019. *Remote Sensing*, 13, 922. https://doi.org/10.3390/rs13050922

Esri. (2026). Sentinel-2 10 m land cover time series of the world [Data set]. ArcGIS Living Atlas of the World. https://www.arcgis.com/home/item.html?id=cfcb7609de5f478eb7666240902d4d3d (accessed 11 September 2026).

Geofabrik. (2026). GCC States OpenStreetMap extract, 31 July 2026 [Data set; gcc-states-260731.osm.pbf]. https://download.geofabrik.de/asia/gcc-states-260731.osm.pbf

GeoSOS team, Sun Yat-sen University. (n.d.). FLUS source code for non-commercial academic research. http://www.geosimulation.cn/FLUS-source-code.html (accessed 6 September 2026).

Gorelick, N., Hancher, M., Dixon, M., Ilyushchenko, S., Thau, D., & Moore, R. (2017). Google Earth Engine: planetary-scale geospatial analysis for everyone. *Remote Sensing of Environment*, 202, 18–27. https://doi.org/10.1016/j.rse.2017.06.031

Impact Observatory, Microsoft, & Esri. (n.d.). Sentinel-2 10m land cover time series of the world [Data set]. ArcGIS ImageServer. https://ic.imagery1.arcgis.com/arcgis/rest/services/Sentinel2_10m_LandCover/ImageServer (archived materialization manifest dated 9 September 2026; upstream release version not recorded).

Karra, K., Kontgis, C., Statman-Weil, Z., Mazzariello, J. C., Mathis, M., & Brumby, S. P. (2021). Global land use/land cover with Sentinel 2 and deep learning. *2021 IEEE International Geoscience and Remote Sensing Symposium IGARSS*, 4704–4707. https://doi.org/10.1109/IGARSS47720.2021.9553499

Lau, K. H., & Kam, B. H. (2005). A cellular automata model for urban land-use simulation. *Environment and Planning B: Planning and Design*, 32, 247–263. https://doi.org/10.1068/b31110

Liang, X., Guan, Q., Clarke, K. C., Liu, S., Wang, B., & Yao, Y. (2021). Understanding the drivers of sustainable land expansion using a patch-generating land use simulation (PLUS) model: A case study in Wuhan, China. *Computers, Environment and Urban Systems*, 85, 101569. https://doi.org/10.1016/j.compenvurbsys.2020.101569

Liu, X., Liang, X., Li, X., Xu, X., Ou, J., Chen, Y., Li, S., Wang, S., & Pei, F. (2017). A future land use simulation model (FLUS) for simulating multiple land use scenarios by coupling human and natural effects. *Landscape and Urban Planning*, 168, 94–116. https://doi.org/10.1016/j.landurbplan.2017.09.019

OpenStreetMap contributors. (2026). Abu Dhabi city boundary, relation 4479763 [Data set; retrieved 1 August 2026; geometry documented in boundary_manifest.json]. https://www.openstreetmap.org/relation/4479763

Pedregosa, F., Varoquaux, G., Gramfort, A., Michel, V., Thirion, B., Grisel, O., Blondel, M., Prettenhofer, P., Weiss, R., Dubourg, V., Vanderplas, J., Passos, A., Cournapeau, D., Brucher, M., Perrot, M., & Duchesnay, E. (2011). Scikit-learn: Machine learning in Python. *Journal of Machine Learning Research*, 12, 2825–2830. https://jmlr.org/papers/v12/pedregosa11a.html

Pontius, R. G., Jr., Boersma, W., Castella, J.-C., Clarke, K., de Nijs, T., Dietzel, C., Duan, Z., Fotsing, E., Goldstein, N., Kok, K., Koomen, E., Lippitt, C. D., McConnell, W., Mohd Sood, A., Pijanowski, B., Pithadia, S., Sweeney, S., Trung, T. N., Veldkamp, A. T., & Verburg, P. H. (2008). Comparing the input, output, and validation maps for several models of land change. *The Annals of Regional Science*, 42, 11–37. https://doi.org/10.1007/s00168-007-0138-2

Pontius, R. G., Jr., & Millones, M. (2011). Death to Kappa: birth of quantity disagreement and allocation disagreement for accuracy assessment. *International Journal of Remote Sensing*, 32, 4407–4429. https://doi.org/10.1080/01431161.2011.552923

Silva, E. A., & Clarke, K. C. (2002). Calibration of the SLEUTH urban growth model for Lisbon and Porto, Portugal. *Computers, Environment and Urban Systems*, 26, 525–552. https://doi.org/10.1016/S0198-9715(01)00014-X

Soares-Filho, B. S., Cerqueira, G. C., & Pennachin, C. L. (2002). DINAMICA—a stochastic cellular automata model designed to simulate the landscape dynamics in an Amazonian colonization frontier. *Ecological Modelling*, 154, 217–235. https://doi.org/10.1016/S0304-3800(02)00059-5

van Vliet, J., Bregt, A. K., & Hagen-Zanker, A. (2011). Revisiting Kappa to account for change in the accuracy assessment of land-use change models. *Ecological Modelling*, 222, 1367–1375. https://doi.org/10.1016/j.ecolmodel.2011.01.017

van Vliet, J., Bregt, A. K., Brown, D. G., van Delden, H., Heckbert, S., & Verburg, P. H. (2016). A review of current calibration and validation practices in land-change modeling. *Environmental Modelling & Software*, 82, 174–182. https://doi.org/10.1016/j.envsoft.2016.04.017

Verburg, P. H., Soepboer, W., Veldkamp, A., Limpiada, R., Espaldon, V., & Mastura, S. S. A. (2002). Modeling the spatial dynamics of regional land use: the CLUE-S model. *Environmental Management*, 30, 391–405. https://doi.org/10.1007/s00267-002-2630-x

Zanaga, D., Van De Kerchove, R., De Keersmaecker, W., Souverijns, N., Brockmann, C., Quast, R., Wevers, J., Grosu, A., Paccini, A., Vergnaud, S., Cartus, O., Santoro, M., Fritz, S., Georgieva, I., Lesiv, M., Carter, S., Herold, M., Li, L., Tsendbazar, N.-E., Ramoino, F., & Arino, O. (2021). ESA WorldCover 10 m 2020 v100 [Data set]. Zenodo. https://doi.org/10.5281/zenodo.5571936

Zanaga, D., Van De Kerchove, R., Daems, D., De Keersmaecker, W., Brockmann, C., Kirches, G., Wevers, J., Cartus, O., Santoro, M., Fritz, S., Lesiv, M., Herold, M., Tsendbazar, N.-E., Xu, P., Ramoino, F., & Arino, O. (2022). ESA WorldCover 10 m 2021 v200 [Data set]. Zenodo. https://doi.org/10.5281/zenodo.7254221

## Supplementary information outline

- **Supplementary Table S1:** ArcGIS-served 2031 model–scenario objective profiles with per-seed dispersion (see `supplementary_table_S1_arcgis_planning_objectives.md`).
- **Supplementary Table S2:** Neighbourhood-weight sensitivity at 0, 0.175, 0.35 and 0.7 (see `supplementary_table_S2_neighbourhood_weight_sensitivity.md`).
- **Supplementary Table S3:** FLUS 13-, 19- and 25-feature diagnostics, platform boundary and demand-underfill evidence (see `supplementary_table_S3_flus_feature_diagnostics.md`).
- **Supplementary Table S5:** Rolling-origin and WorldCover external-product diagnostics (see `supplementary_table_S5_rolling_external_diagnostics.md`).
- **Supplementary Table S6:** Matched Dynamic World and ArcGIS-served whole-product-pipeline backtests (see `supplementary_table_S6_product_robustness.md`).
- **Supplementary Table S7:** Net-change FoM upper bounds and 54 seed-specific paired model intervals (see `supplementary_table_S7_allocation_limits.md`).
- **Fig. S1:** Full 3-scenarios × 3-model 2031 new-built footprint atlas (`figures/figS01_planning_atlas_2031.*`).
- **Fig. S2:** Dynamic World quality proxy and quality-filtered change sensitivity (`figures/figS02_input_label_quality.*`).
- **Fig. S3:** Historical maps and change-error maps for 2024 (`figures/figS03_historical_2024_maps_and_errors.*`).
- **Fig. S4:** Driver layers and experiment design in English (`figures/figS04_driver_layers_and_experiment_design.*`).

---
