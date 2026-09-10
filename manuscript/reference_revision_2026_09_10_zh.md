# 参考文献与数据方法修订记录

本次修订基于 `278d00d`，核对论文引文、官方数据目录与仓库实际处理代码。修订仅澄清方法、来源和证据边界，不改变训练输入、模型参数或既有实验结果，也不代表完成独立影像判读或新增模型对照实验。

## 已落实

1. **Dynamic World**：明确年度标签由逐景标签求时间众数后再做类别映射；年度质量指标为各类别时间平均概率的最大值 `max(mean(p))`，不是 `mean(max(p))`。保留栅格中的历史波段名称，解释其不等于年度众数类别的正确概率，并同步修正样本权重和置信度分层的措辞。
2. **VIIRS**：新增 Earth Observation Group 月度产品引用；说明实际代码对可用、未掩膜月值作等权平均，不插补缺月，也未额外使用 `cf_cvg` 掩膜或权重。Elvidge et al.（2021）保留为年度产品背景，避免将本研究的年均特征误认为该文发布产品。
3. **Copernicus**：按官方目录列示的数据提供方改为 Copernicus，补充 `2024_1` 版本、目录访问日期、DSM 属性及观测时间范围。明确没有核实各瓦片的具体获取时间，也没有量化建筑和植被对坡度的影响。
4. **ArcGIS 产品**：将无法证实的出版年2026改为 n.d.；给出仓库物化清单的实际日期2026年9月9日，明确未记录上游不可变版本号，复现目标是已存档并有校验值的栅格快照。Karra et al.（2021）仅支持技术来源，不替代各年度产品的精度验证。
5. **OSM**：拆开边界对象与道路数据引用，加入具体关系链接与 Geofabrik 历史提取文件。边界清单记录的获取日期为2026年8月1日；道路快照日期为7月31日，二者不应混为一个日期。
6. **历史验证边界**：明确去除晚期道路与禁止目标标签参与训练，只控制下游特征和标签使用；不能据此声称所有回溯产品、预训练嵌入与静态DSM都在历史预测时点可获得。
7. **工作修订产物一致性**：将回溯报告、产品稳健性摘要、质量筛选说明和补充图 S2 的旧称谓同步为“maximum temporal-mean probability / quality proxy”。该修订不改变栅格、训练、预测或指标数值；仅重新生成描述性 JSON、Markdown 和图件，并更新 working 清单。

## 核查范围与尚未解决的问题

- 前轮检查的24条文献中，14篇取得 Crossref 元数据且未发现明显 DOI、题名或作者错配。AlphaEarth 的 arXiv 身份和 WorldCover 2021 v200 的 Zenodo 元数据另经官方记录核对。不能把这些检查扩大为全部文献全文核验通过。
- Pontius and Millones（2011）的出版商页面/Crossref 查询及 WorldCover 2020 v100 的部分官方访问失败；保留原条目，不凭网络失败断言不存在或填写未经核实的新信息。
- Plan Abu Dhabi 2030 的原始报告版本、稳定全文入口尚未完整核实；保留原有书目信息，不添加本次访问返回404的链接。
- GeoSOS 源码入口本次未能直接访问；正文已有实际修改版源码提交号。未将另一个软件主页冒充精确源码版本。
- 独立变化样本、允许同一类别同时新增和消失的分配器对照，以及完全匹配输入和学习任务的组件实验仍未完成。正文保留这些限制。

## 主要证据入口

- [Dynamic World 原始论文](https://www.nature.com/articles/s41597-022-01307-4)
- [VIIRS 月度产品官方目录](https://developers.google.com/earth-engine/datasets/catalog/NOAA_VIIRS_DNB_MONTHLY_V1_VCMSLCFG)
- [Copernicus DSM 官方目录](https://developers.google.com/earth-engine/datasets/catalog/COPERNICUS_DEM_GLO30_2024_1)
- [AlphaEarth 预印本记录](https://arxiv.org/abs/2507.22291)
- [WorldCover 2021 v200](https://zenodo.org/records/7254221)
- 处理代码：`benchmarks/abu_dhabi_land_use_v1/materialize_gee_inputs.py`。
- 来源清单：v1的 `gee_input_manifest.json`、`osm_input_manifest.json`、`boundary_manifest.json`，以及v2的 `artifacts/arcgis_sentinel2_landcover/manifest.json`。

已发布的 Zenodo v2.0.0 清单保持不变；本次修订的文件校验信息应写入单独的 working 清单。
