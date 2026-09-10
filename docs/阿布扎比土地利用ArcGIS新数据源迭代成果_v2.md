# 阿布扎比土地利用模拟与优化：ArcGIS Sentinel‑2 10 m 数据源迭代成果（v2）

- 更新时间：2026-09-09
- 研究区域：阿布扎比市（OpenStreetMap relation R4479763）
- 建模人员：周宁（Ning Zhou）

## 1. 本轮迭代的目标

现有 v1 结果使用 Google Earth Engine 的 Dynamic World V1 年度标签（2017–2024）。本轮不覆盖、不修改 v1，而是建立独立 v2，针对客户提出的两个问题进行改进：

1. 将年度标签更新到 2025 年，降低时间滞后；
2. 保留 10 m 原生分类栅格，并在模型输入前采用明确的类别映射和面积多数聚合，避免直接粗暴重采样造成空间信息损失。

本轮使用的服务为：

`https://ic.imagery1.arcgis.com/arcgis/rest/services/Sentinel2_10m_LandCover/ImageServer`

该服务是 Impact Observatory、Microsoft 和 Esri 生产的全球 Sentinel‑2 10 m 年度土地覆盖分类产品，不是原始多光谱影像，也不是阿布扎比政府法定土地利用/规划数据库。

## 2. 数据与处理

### 2.1 年度数据

- ArcGIS 年度分类：2017–2025，共 9 年；
- 原生栅格：EPSG:32640，10 m，4750 × 3600；
- 服务导出受 4000 像元宽度限制，每年分为两个窗口后拼接；
- 每个原生栅格均写入城市中心像元掩膜，保留 SHA‑256 哈希和服务目录记录。

### 2.2 类别映射

ArcGIS 原始编码到当前六类模型体系的映射为：

| ArcGIS 值 | ArcGIS 类别 | 模型类别 |
|---:|---|---|
| 1 | Water | water |
| 2 | Trees | woody vegetation |
| 4 | Flooded Vegetation | wetland |
| 5 | Crops | low vegetation |
| 7 | Built Area | built |
| 8 | Bare Ground | bare |
| 11 | Rangeland | low vegetation |
| 9 | Snow/Ice | excluded/nodata |
| 10 | Clouds | excluded/nodata |

在 100 m 模型网格上，先把 10 m 像元映射为六类，再对每个 10×10 块执行多数类聚合；只在可用像元中计算多数比例，平票按最小类别编码确定。没有使用最近邻重采样代替类别聚合。

### 2.3 其他驱动变量

- 2025 VIIRS 年度夜间灯光：已从 Earth Engine 物化；
- 2025 AlphaEarth 年度 64 维嵌入：已从 Earth Engine 物化；
- 地形、道路可达性和生态约束：沿用已声明的静态公共代理层，并在 v2 bundle 中单独记录；
- 三模型仍使用 EPSG:32640、100 m、475×360 的统一建模契约。10 m 数据作为原生审计层和观测变化制图层，不将模型预测精度夸大为 10 m。

## 3. 三类模型与场景

在同一 2025 年 ArcGIS 状态、同一约束和同一情景需求下运行：

- GeoSOS-derived FLUS-style ANN–CA console；
- Geospatial Kernel（GWM 算法核心）；
- GeoFM-LDN（原内部路径名 paper58，本轮使用 ArcGIS 标签重新训练 decoder 和 LDN checkpoint）。

每个模型使用随机种子 31、47、73，并执行三类条件情景：

- `compact`：较低建成增长、较高紧凑性；
- `ecological_priority`：较低建成增长、较高绿地增长；
- `outward_growth`：较高建成增长、较低绿地增长。

情景起点为 2025 年，按年度滚动推演 2026–2031。用户原先重点关注的 2027–2031 可直接从该结果中截取；2026 年保留用于连续滚动。

## 4. 结果摘要

2025 年 ArcGIS 100 m 标签共有 79,775 个有效城市像元，其中：water 21,180、woody vegetation 2、low vegetation 2,694、wetland 17、built 32,731、bare 23,151。

2031 年三模型 ensemble 的建成类像元数和最后一年变化图斑数如下：

| 模型 | 场景 | 2031 建成像元 | 2031 相对 2030 变化像元 | 2025–2031 变化图斑数 |
|---|---|---:|---:|---:|
| FLUS-style | compact | 35,634 | 1,116 | 783 |
| FLUS-style | ecological priority | 34,793 | 1,089 | 765 |
| FLUS-style | outward growth | 38,660 | 1,467 | 777 |
| Geospatial Kernel | compact | 35,711 | 525 | 414 |
| Geospatial Kernel | ecological priority | 34,799 | 471 | 388 |
| Geospatial Kernel | outward growth | 38,750 | 1,028 | 604 |
| GeoFM-LDN | compact | 35,455 | 485 | 285 |
| GeoFM-LDN | ecological priority | 34,583 | 470 | 297 |
| GeoFM-LDN | outward growth | 38,480 | 1,047 | 350 |

这些数字是给定需求、约束和公共标签条件下的情景分配结果，不是阿布扎比实际政策预测。模型之间的图斑数量差异反映其空间分配与形态机制，不能仅凭图斑数量宣称某模型“精度最好”。

## 5. 观测变化与矢量成果

已生成 2024→2025 的原生 10 m 观测变化 GeoPackage：约 21,998 个变化图斑，变化面积约 36.41 km²。该图层用于检查数据产品本身的年度变化，不应与模型预测混称。

三模型各情景均生成：

- 2026–2031 年 ensemble GeoTIFF；
- 含 2026、2027、2028、2029、2030、2031 图层的 GeoPackage；
- 合并 Shapefile（每个模型×情景一个文件）；
- 每个图斑包含起始/目标年份、源类别、目标类别和面积字段。

所有预测图斑均为 100 m 栅格单元转换得到的过渡多边形，不是地籍或法定建设地块。

## 6. 完全复现路径

工程根目录：

`/Users/zhouning/abu-dhabi-geospatial-kernel-paper`

v2 目录：

`/Users/zhouning/abu-dhabi-geospatial-kernel-paper/benchmarks/abu_dhabi_land_use_v2`

关键文件：

- ArcGIS 数据和清单：`benchmarks/abu_dhabi_land_use_v2/artifacts/arcgis_sentinel2_landcover/`
- ArcGIS 输入清单：`benchmarks/abu_dhabi_land_use_v2/artifacts/arcgis_sentinel2_landcover/manifest.json`
- 约束/需求 bundle：`benchmarks/abu_dhabi_land_use_v2/artifacts/bundle/`
- GeoFM-LDN 新 checkpoint：`benchmarks/abu_dhabi_land_use_v2/artifacts/predictions/geofm_ldn_arcgis/`
- 三模型运行报告：`benchmarks/abu_dhabi_land_use_v2/planning_scenario_report_arcgis_2026_2031.json`
- 结果汇总：`benchmarks/abu_dhabi_land_use_v2/results_arcgis_v2/results_summary.md`
- GeoPackage 和 Shapefile：`benchmarks/abu_dhabi_land_use_v2/results_arcgis_v2/vectors/`
- 原生 10 m 观测变化：`benchmarks/abu_dhabi_land_use_v2/results_arcgis_v2/vectors/arcgis_observed_2024_2025_native10m.gpkg`

README 中已写入从下载、建 bundle、重训 GeoFM-LDN、批量运行到矢量导出的完整命令。

## 7. 仍然存在的限制

1. ArcGIS 产品虽然标称 10 m，但仍是全球遥感分类产品，不能证明为阿布扎比权威本地数据；
2. ArcGIS 没有 Dynamic World 同等的 `mean_top_probability` 概率质量层，v2 使用多数比例和有效源像元数作为数据质量审计量，不能与 v1 置信度数值直接等价；
3. 10 m 标签被聚合到 100 m 后，模型输出空间尺度仍为 100 m；要宣称 10 m 预测，必须重构三模型的邻域尺度、训练样本和计算契约，并有独立高精度验证；
4. 2025 预测起点是最新公开年度标签，不等同于 2025 年官方规划现状；
5. 服务许可字段为空，仅提供版权方信息。若要对外再发布原始下载栅格，应先核查 Impact Observatory、Microsoft、Esri 的适用许可；
6. 正式的客户交付仍需要阿布扎比政府/规划部门的法定土地利用、分区、地籍、审批、基础设施容量和独立验证数据。

因此，本轮成果可以严谨地表述为：**使用更新到 2025 年、保留原生 10 m 审计层的 ArcGIS 公共土地覆盖产品，完成三模型条件情景模拟与变化图斑输出；相较 v1 改善了时间新鲜度和输入产品分辨率审计，但尚未替代权威本地土地利用数据库，也未证明模型预测达到 10 m 或法定规划精度。**
