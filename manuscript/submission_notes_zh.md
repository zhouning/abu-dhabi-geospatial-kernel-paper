# 论文交付说明

本稿采用 Nature 风格的英文研究论文结构，论文类型为算法研究论文，并将应用部分限定为“基于公开数据的条件规划压力测试”。

## 核心结论

- Geospatial Kernel 在 2023 年单步历史分配中取得最高 change FoM（0.2004）。
- GeoFM-LDN 在 2024 年两步开环历史目标中取得最高 change FoM（0.2778）。因此稿件没有声称 Geospatial Kernel 在所有预测任务中最好。
- 在 2025–2031 的三类规划情景中，Geospatial Kernel 满足目标类别数量、没有违反公开数据代理约束，并在当前目标集合下进入 Pareto frontier。
- 这些未来结果是 planner-supplied scenario stress tests，不是官方预测。

## 证据边界

当前六类标签是遥感土地覆盖，不是法定 residential/commercial/industrial land use；OSM 和 ESA WorldCover 约束是公开数据代理；未来外生变量冻结在 2024；没有 2025–2031 的真实观测验证；输出图斑是 100 m 栅格变化单元溶解结果，不是地籍宗地。

## 当前已完成

1. 已用 Python/Matplotlib 重绘五组英文主图，提供 SVG/PDF（文本可编辑）以及 600 dpi PNG/TIFF。
2. 作者、机构和通讯作者已写入稿件：Ning Zhou；Beijing Freedo Technology Co., Ltd.；通讯作者 Ning Zhou。
3. 已补做 proposal、runtime、planning morphology 和 hard-constraint mechanism controls，并在正文中明确这些是公开数据压力测试而非因果政策实验。
4. 已加入目标期刊建议，当前主投建议为 *Landscape and Urban Planning*，Nature 体系目标为 *npj Urban Sustainability*。
5. 已按 LUP 投稿检查清单补充 Highlights、Keywords、Data availability、Code availability、CRediT、Funding、Competing interests 和 Ethics statement；Table 2 已拆分为 2a/2b 并完成版心复核。

## 投稿前仍需补充

1. 查看 `landscape_urban_planning_compliance.md`，并在投稿前再次核对 LUP 在线指南中的文章类型、图文摘要、图像规格和声明字段。
2. 如有可公开使用的机构邮箱，补入通讯信息；当前稿件没有虚构邮箱。
3. 如果期刊要求尺度鲁棒性，可增加 30 m 或多分辨率敏感性实验。
4. 如果要把结果用于客户决策，应替换为权威本地土地利用、规划红线、基础设施容量和审批需求数据，并完成语义交叉表和真实历史验证。
5. 发布代码前完成公共仓库 URL、DOI、许可证和大文件存储策略的最终审核。
