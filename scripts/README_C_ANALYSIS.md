# C 项分析脚本说明

本目录中的 C 项脚本负责项目计划书规定的五项工作：

1. PM2.5 与气象变量的相关分析；
2. 多元线性回归建模；
3. 回归模型诊断；
4. 六种污染物的月度时间趋势分析；
5. 报告图表美化与结果摘要生成。

C 项只读取 B 项生成的日均数据，不修改原始数据、B 项脚本或 B 项输出。

## 1. 分析目标

核心研究问题为：

> 在控制季节和监测站点差异后，温度、气压、露点、降水和风速与北京日均 PM2.5 浓度存在怎样的统计关联？

时间趋势扩展问题为：

> 在控制日历月份的季节效应后，2013 年 3 月至 2017 年 2 月期间六种主要污染物的月均浓度是否存在显著长期变化？

主分析单位为“站点-日”，因变量使用：

```text
log(PM2.5 + 1)
```

对数变换用于缓解日均 PM2.5 的右偏和重尾问题。所有结论描述的是统计关联，而不是因果效应。

## 2. 输入数据

C 项读取：

```text
data/processed/processed_daily.csv
```

该文件由 B 项脚本生成：

```powershell
python scripts/preprocess_data.py
```

必需字段如下：

| 字段 | 含义 |
|---|---|
| `station` | 监测站点 |
| `date` | 日期 |
| `PM2.5` | 日均 PM2.5 浓度 |
| `TEMP` | 日均温度 |
| `PRES` | 日均气压 |
| `DEWP` | 日均露点温度 |
| `RAIN` | 小时降水量的日平均值 |
| `WSPM` | 日均风速 |

时间趋势分析还读取 `PM10`、`SO2`、`NO2`、`CO` 和 `O3`。该模块先在每天内平均各站点，再将城市日均值聚合为月均值，避免记录较多的日期或站点获得额外权重。

C 项在内存中派生 `year`、`season`、`log_pm25` 和标准化气象变量，不写回 `processed_daily.csv`。

## 3. 脚本结构

### `analysis_common.py`

公共工具模块，供其他 C 项脚本导入，不需要单独运行。

主要功能：

- 读取并校验 `processed_daily.csv`；
- 从日期生成季节和年份；
- 计算 `log(PM2.5 + 1)`；
- 对气象变量进行 z-score 标准化；
- 构造季节、站点和年份虚拟变量；
- 使用 NumPy 实现普通最小二乘回归；
- 计算经典标准误和 HC3 异方差稳健标准误。

### `correlation_analysis.py`

负责相关分析。

对原始 PM2.5 和 `log(PM2.5 + 1)` 分别计算：

- Pearson 线性相关系数；
- Spearman 秩相关系数；
- 双侧 p 值；
- 有效样本量。

输出：

```text
reports/tables/meteorological_correlations.csv
```

### `regression_analysis.py`

负责多元线性回归建模和模型比较。

气象变量均经过标准化，因此相应系数表示气象变量增加一个标准差时，`log(PM2.5 + 1)` 的条件平均变化。

预先设定三个模型：

| 模型 | 解释变量 | 用途 |
|---|---|---|
| `M1_weather` | 五项气象变量 | 观察未经站点和季节调整的关联 |
| `M2_adjusted` | 气象变量 + 季节 + 站点 | 主模型 |
| `M3_year_adjusted` | 主模型 + 年份 | 年份敏感性分析 |

虚拟变量的参照组为：

- 季节：Spring；
- 站点：Aotizhongxin；
- 年份：2013。

回归系数表同时提供：

- 系数估计；
- 经典标准误、t 统计量、p 值和 95% 置信区间；
- HC3 稳健标准误、t 统计量、p 值和 95% 置信区间。

模型比较指标包括：

- \(R^2\) 和调整 \(R^2\)；
- RMSE 和残差标准差；
- AIC、BIC；
- 设计矩阵条件数。

输出：

```text
reports/tables/weather_scaling.csv
reports/tables/regression_coefficients.csv
reports/tables/regression_model_comparison.csv
```

### `model_diagnostics.py`

负责主模型 `M2_adjusted` 的诊断。

诊断内容：

| 方法 | 检查内容 |
|---|---|
| VIF | 气象变量之间的多重共线性 |
| Breusch-Pagan 检验 | 残差异方差 |
| Jarque-Bera 检验 | 残差正态性 |
| 站点内 Durbin-Watson | 残差时间自相关 |
| Cook 距离 | 高影响观测 |
| 标准化残差与杠杆值 | 异常点和高杠杆点 |

输出：

```text
reports/tables/model_diagnostics.csv
reports/tables/weather_vif.csv
reports/tables/station_durbin_watson.csv
reports/tables/influential_observations.csv
```

### `temporal_trend_analysis.py`

负责六种污染物的连续月度时间趋势分析。模型采用对数月均浓度作为因变量：

```text
log(月均浓度 + 1) = 截距 + 线性时间趋势 + 月份固定效应 + 误差
```

月份虚拟变量用于控制稳定的季节差异，时间系数经 `exp(beta)-1` 转换为平均年度百分比变化。推断采用滞后 3 个月的 Newey-West 标准误，以缓解异方差和短期时间相关；六种污染物的 p 值进一步使用 Benjamini-Hochberg FDR 校正。

输出：

```text
reports/tables/monthly_pollutant_series.csv
reports/tables/temporal_trend_results.csv
```

第一张表保存连续 48 个月的城市月均值和 12 个月滚动均值；第二张表保存年度变化率、Newey-West 95% 置信区间、原始 p 值、FDR 校正 p 值、调整 R² 和 Durbin-Watson 统计量。

### `analysis_visualization.py`

负责读取 C 项统计表、拟合主模型并生成最终图表和交接摘要。

输出图表：

```text
reports/figures/meteorological_correlation_heatmap.png
reports/figures/weather_pm25_relationships.png
reports/figures/regression_coefficient_plot.png
reports/figures/regression_diagnostics.png
reports/figures/monthly_pollutant_trends.png
reports/figures/season_adjusted_trend_estimates.png
```

图表分别展示：

1. 五项气象变量与对数 PM2.5 的 Pearson/Spearman 相关系数；
2. 各气象变量与对数 PM2.5 的未经调整关系；
3. 三个模型的标准化气象回归系数及 HC3 95% 置信区间；
4. 残差-拟合值图、QQ 图、残差分布和 Cook 距离；
5. 六种污染物的连续月均变化和 12 个月滚动均值；
6. 控制月份效应后的年度变化率及 Newey-West 95% 置信区间。

供报告成员快速引用的文字摘要保存为：

```text
reports/tables/c_analysis_summary.txt
```

### `run_analysis.py`

C 项一键入口，依次执行：

```text
相关分析 -> 回归分析 -> 模型诊断 -> 月度时间趋势 -> 图表和摘要
```

## 4. 运行方法

### 安装依赖

在项目根目录执行：

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 从原始数据完整复现

先运行 B 项预处理，再运行 C 项入口：

```powershell
.\.venv\Scripts\python.exe scripts\preprocess_data.py
.\.venv\Scripts\python.exe scripts\run_analysis.py
```

### 单独运行某一部分

```powershell
.\.venv\Scripts\python.exe scripts\correlation_analysis.py
.\.venv\Scripts\python.exe scripts\regression_analysis.py
.\.venv\Scripts\python.exe scripts\model_diagnostics.py
.\.venv\Scripts\python.exe scripts\temporal_trend_analysis.py
.\.venv\Scripts\python.exe scripts\analysis_visualization.py
```

可视化脚本依赖前三个脚本生成的统计表，因此独立运行时应放在最后。

## 5. 当前主要结果

基于 17,532 条站点-日观测：

- 风速与 `log(PM2.5 + 1)` 的 Spearman 相关系数约为 -0.446，是五项气象变量中绝对关联最强的变量；
- 主模型 `M2_adjusted` 的调整 \(R^2\) 约为 0.481，RMSE 约为 0.631；
- 温度和露点变量存在较强共线性，最高 VIF 约为 9.57；
- Breusch-Pagan 检验提示异方差，因此系数推断优先使用 HC3 稳健标准误；
- 站点内 Durbin-Watson 中位数约为 1.03，说明残差存在正时间相关。
- 月度趋势模块利用全部 48 个月的数据，通过月份固定效应区分季节波动和长期变化，并使用 Newey-West 标准误及 FDR 校正控制推断风险。
- SO2 的季节调整后浓度平均每年下降约 25.8%，Newey-West 95% CI 为 [-29.1%, -22.4%]，FDR 校正后 p 值约为 1.61e-14；
- NO2 平均每年下降约 5.7%，95% CI 为 [-9.7%, -1.7%]，FDR 校正后 p 值约为 0.022；
- CO 平均每年下降约 5.6%，95% CI 为 [-10.1%, -0.9%]，FDR 校正后 p 值约为 0.042；
- PM2.5 和 PM10 分别呈约 5.2%/年和 4.7%/年的下降方向，但 FDR 校正后均未达到 0.05 显著性水平；O3 的时间趋势同样不显著。

精确数值应以生成的 CSV 表和 `c_analysis_summary.txt` 为准，不应从本 README 手工复制后长期维护。

## 6. 结果解释边界

1. 回归结果表示控制其他变量后的条件关联，不能表述为气象因素“导致”PM2.5 改变。
2. 温度和露点共线性较强，单个系数对模型设定较敏感，应结合 VIF 和模型间系数变化解释。
3. HC3 标准误可缓解异方差问题，但不能消除时间自相关；普通回归 p 值仍可能偏小。
4. 监测站点不是随机抽样，结论不应无条件推广到所有地点。
5. `RAIN` 在 B 项日均数据中是小时降水量的日平均值，不是日累计降水量。
6. 2017 年数据仅覆盖 1-2 月，因此年份模型仅作为敏感性分析。
7. 月度趋势模型可以利用不完整年份，但线性趋势描述的是研究期内的平均变化，不能自动解释为政策因果效应；12 个月滚动均值仅用于展示，不参与显著性检验。

## 7. 文件所有权与协作约定

- 本文档用于追踪 C 项负责的脚本：`analysis_common.py`、`correlation_analysis.py`、`regression_analysis.py`、`model_diagnostics.py`、`temporal_trend_analysis.py`、`analysis_visualization.py` 和 `run_analysis.py`。
- C 项脚本不得覆盖或修改 A/B 项脚本、原始数据和处理后数据。
- 生成的表格和图片位于已被 `.gitignore` 忽略的目录；是否提交这些生成物由组长统一决定。
- 最终报告应优先引用 HC3 置信区间，并同时报告模型假设与局限。
