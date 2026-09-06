# Abu Dhabi 2025-2031 土地覆盖情景压力测试

以下为 2031 年三随机种子均值。Pareto 表示在声明的发布目标集合下未被同一情景中其他方案全面支配。

| 模型 | 情景 | demand TV | 集成目标偏差(px) | 绿色增益(px) | 距主干路(m) | 距原建成区(m) | 既有∪新增建成斑块/千像元 | 生态转建成率 | 蛙跳率 | Pareto |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|:---:|
| FLUS-style ANN–CA console (untraceable build) | Moderate growth (legacy compact) | 0.00068 | 2504 | 296 | 446.1 | 231.6 | 3.035 | 0.0168 | 0.083 | 是 |
| FLUS-style ANN–CA console (untraceable build) | Green-priority growth | 0.00528 | 2888 | 629 | 443.7 | 212.7 | 3.265 | 0.0177 | 0.066 | 是 |
| FLUS-style ANN–CA console (untraceable build) | High outward growth | 0.00045 | 2568 | 139 | 443.5 | 255.3 | 2.484 | 0.0131 | 0.107 | 是 |
| Geospatial Kernel | Moderate growth (legacy compact) | 0.00000 | 60 | 350 | 336.7 | 117.4 | 3.922 | 0.0000 | 0.000 | 是 |
| Geospatial Kernel | Green-priority growth | 0.00000 | 68 | 1050 | 319.8 | 111.3 | 4.256 | 0.0000 | 0.000 | 是 |
| Geospatial Kernel | High outward growth | 0.00000 | 86 | 175 | 362.5 | 141.7 | 2.969 | 0.0000 | 0.001 | 是 |
| GeoFM-LDN | Moderate growth (legacy compact) | 0.00000 | 1596 | 350 | 475.5 | 239.8 | 4.081 | 0.0000 | 0.081 | 否 |
| GeoFM-LDN | Green-priority growth | 0.00000 | 1536 | 1050 | 452.2 | 222.8 | 4.340 | 0.0000 | 0.073 | 否 |
| GeoFM-LDN | High outward growth | 0.00000 | 1174 | 175 | 507.7 | 264.4 | 3.219 | 0.0000 | 0.089 | 否 |

## 解释边界

- 三组需求是规划压力测试，不是对阿布扎比未来的预测。
- 生态和基础设施指标来自公开数据代理，不等于法定或货币化影响。
- Pareto 结果在每个情景内比较三个模型，且只在声明的目标、100 m 网格和公共约束下成立。
- 主要碎片化指标是 2024 年既有建成与新增建成的并集连通分量密度；生态转化率是描述性压力代理，不参与 Pareto 目标。
- 植被增益、500 m 蛙跳率、邻域比例、建成退出和全部建成分量密度为描述性诊断。
- 目标集敏感性结果见 JSON 的 objective_set_sensitivity，属于发布后稳健性分析。
- 集成栅格采用三种子多数投票，可能不再精确满足动作总量；表中的集成目标偏差是对此的显式审计。
- ‘Moderate growth’保留 legacy compact 路径名，但动作本身不含紧凑性优化。
- FLUS 的既有建成退出是其冻结转换规则下的模型行为，未做事后修正。
