# 论文交付说明

本稿正在按 LUP 要求重构为研究论文，应用部分限定为“基于公开数据的条件规划压力测试”。本轮修改已修正评价器和主张边界，但尚未达到可直接重投状态；当前科学状态仍为阻塞，不应在投稿系统中标记为 Article type Ready。

## 核心结论

- 原始二值 change FoM 结果显示 Geospatial Kernel 在 2023 年单步历史分配中最高，GeoFM-LDN 在 2024 年两步开环历史目标中最高；这些数值必须用严格多类别 FoM 重算。
- 持久性和随机可行分配零模型已加入评价代码；持久性在静态 OA 与 macro-F1 上优于主模型的事实必须在重算表中保留。
- 原始 Pareto frontier 结论已撤回。新目标集只保留独立的道路距离、既有建成区距离、斑块密度和蛙跳率，需恢复栅格后重算。
- 当前输出审计为 `INCOMPLETE_INPUTS`（8 项失败：缺失输入和旧报告），因此不能把已有 PDF、图 2–5 或 JSON 视为最终证据。
- 这些未来结果是 planner-supplied scenario stress tests，不是官方预测。

## 证据边界

当前六类标签是遥感土地覆盖，不是法定 residential/commercial/industrial land use；OSM 和 ESA WorldCover 约束是公开数据代理；未来外生变量冻结在 2024；没有 2025–2031 的真实观测验证；输出图斑是 100 m 栅格变化单元溶解结果，不是地籍宗地。

## 当前已完成

1. 已用 Python/Matplotlib 重绘 Figure 1（箭头和公式标注已修正），并保留其 SVG/PDF（文本可编辑）以及 600 dpi PNG/TIFF；Figure 2–5 的渲染器已 fail-closed，遇到旧报告或缺失栅格会拒绝生成“看似最终”的图，仍需在数据恢复后重新生成。
2. 作者、机构和通讯作者已写入稿件：Ning Zhou；Beijing Freedo Technology Co., Ltd.；通讯作者 Ning Zhou。
3. 已补充严格多类别 FoM、零模型、配对像元 bootstrap、独立形态指标和运行时快照代码。
4. 已加入目标期刊建议；但在独立变化验证和完整复现材料到位前，不建议直接重投 LUP。
5. 已更新 Data availability、Code availability、CRediT、Funding、Competing interests 和 Ethics statement；表格和图件仍需用新结果重新生成。

## 投稿前仍需补充

1. Markdown 源文件已按 LUP 的 Introduction–Methods–Results–Discussion 结构重排；投稿前仍需按在线指南完成最终模板、文章类型、图文摘要、图像规格和声明字段核对。
2. 如有可公开使用的机构邮箱，补入通讯信息；当前稿件没有虚构邮箱。
3. 如果期刊要求尺度鲁棒性，可增加 30 m 或多分辨率敏感性实验。
4. 如果要把结果用于客户决策，应替换为权威本地土地利用、规划红线、基础设施容量和审批需求数据，并完成语义交叉表和真实历史验证。
5. 发布代码前完成公共仓库 URL、DOI、许可证和大文件存储策略的最终审核。
6. 恢复公开栅格、GeoFM-LDN 检查点和 FLUS 运行环境，重算严格 FoM、bootstrap、形态指标和全部图表。
7. 引入独立建成区产品或人工判读样本，验证 Dynamic World 2023–2024 的变化真实性。
