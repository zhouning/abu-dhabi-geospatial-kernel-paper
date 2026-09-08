# 论文交付说明

本稿按 LUP 要求组织为研究论文，应用部分限定为“基于公开数据的条件规划压力测试”。公共数据复现链、图件和输出审计已经完成；但独立权威变化验证、匹配输入 FLUS 对照和期刊门户元数据仍是重投前限制，不应把结果表述为官方预测。

## 核心结论

- 严格多类别 change FoM 显示，在完全解析的锁定环境中，未匹配输入的公共数据 pipeline 下 Geospatial Kernel 的 2023 年单步均值为 0.1961，GeoFM-LDN 的 2024 年两步开环均值为 0.2708；这不是普适模型优越性结论。
- 持久性和随机可行分配零模型已加入评价代码；持久性在静态 OA 与 macro-F1 上优于主模型的事实必须在重算表中保留。
- 原始 Pareto frontier 结论已撤回。当前发布目标集为距主干路距离、距既有建成区距离，以及“2024 既有建成与新增建成”并集的连通分量密度，并在每个情景内比较三个模型；FLUS 式控制与 Kernel 在三个情景均为非支配，GeoFM-LDN 在移除结构性为零的生态转化率后均被支配。生态转化率仅作为描述性诊断，不参与 Pareto 目标。
- 当前输出审计为 `PASS`（312 条预测记录、2 个 WorldCover 证据栅格，0 项失败）；`output_audit.json` 仅作为旧 lineage 文件保留，正式证据使用 `output_audit_reproducible.json`。
- 这些未来结果是 planner-supplied scenario stress tests，不是官方预测。

## 证据边界

当前六类标签是遥感土地覆盖，不是法定 residential/commercial/industrial land use；OSM 和 ESA WorldCover 约束是公开数据代理；未来外生变量冻结在 2024；没有 2025–2031 的真实观测验证；输出图斑是 100 m 栅格变化单元溶解结果，不是地籍宗地。

## 当前已完成

1. 已用 Python/Matplotlib 重绘 Figure 1–5（箭头、图例、目标标记、比例尺和指北针已修正），并保留 SVG/PDF（文本可编辑）以及 600 dpi PNG/TIFF；渲染器遇到旧报告或缺失栅格会 fail-closed。
2. 作者、机构和通讯作者已写入稿件：Ning Zhou；Beijing Freedo Technology Co., Ltd.；通讯作者 Ning Zhou。
3. 已补充严格多类别 FoM、零模型、配对像元 bootstrap、独立形态指标和运行时快照代码。
4. 已加入目标期刊建议；公共 bundle、模型资产、机制报告和完整复现命令已纳入仓库。
5. 已更新 Data availability、Code availability、CRediT、Funding、Competing interests 和 Ethics statement；表格和图件已由当前报告重新生成。

## 投稿前仍需补充

1. Markdown 源文件已按 LUP 的 Introduction–Methods–Results–Discussion 结构重排；投稿前仍需按在线指南完成最终模板、文章类型、图文摘要、图像规格和声明字段核对。
2. 通讯作者邮箱已设置为 `zhouning@freedotech.com`；投稿时仍应按 Editorial Manager 的字段要求确认完整通讯地址。
3. 如果期刊要求尺度鲁棒性，可增加 30 m 或多分辨率敏感性实验。
4. 如果要把结果用于客户决策，应替换为权威本地土地利用、规划红线、基础设施容量和审批需求数据，并完成语义交叉表和真实历史验证。
5. 发布代码前完成公共仓库 URL、DOI、许可证和大文件存储策略的最终审核。
6. 当前完整复现命令为 `reproducibility/reproduce.py --device cpu`；它加载固定 GeoFM-LDN 检查点，并在 macOS arm64 上调用随仓库提供的 FLUS 二进制。
7. 投稿前仍需引入独立建成区产品或人工判读样本，验证 Dynamic World 2023–2024 的变化真实性；匹配输入 FLUS 已用绝对路径完成 13、19、25 特征的三种子诊断。25 特征在 macOS arm64 的 seeds 47、73 和评审提供的 Windows x86_64 三个种子均因同年类别身份泄漏退化为零变化，唯一未退化的 macOS seed 31 不再作为有效点估计或模型对比。19 特征三种子均发生需求欠填。`FLUS_RANDOM_SEED` 仅保证同平台确定性；Windows 基准和工作目录必须使用纯 ASCII 路径。FLUS 基础源码可追溯至 GeoSOS 公开版本；`paper-benchmark-flus-v1.1`（`47e65b3`）补齐无效输入失败即停处理，正常输入输出与原 v1 基准一致。
