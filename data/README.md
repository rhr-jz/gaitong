# 数据目录说明

## 原始数据（已入库）

**canonical 路径**（代码中请用 `src.config.HOURLY_DIR`）：

```text
data/beijing+multi+site+air+quality+data/
  PRSA2017_Data_20130301-20170228/
    PRSA_Data_20130301-20170228/
      PRSA_Data_<站点名>_20130301-20170228.csv   × 12 站
```

- 时间范围：2013-03-01 — 2017-02-28，小时分辨率  
- 站点：Aotizhongxin, Changping, Dingling, Dongsi, Guanyuan, Gucheng, Huairou, Nongzhanguan, Shunyi, Tiantan, Wanliu, Wanshouxigong  
- 来源：[UCI 501](https://archive.ics.uci.edu/dataset/501/beijing+multi+site+air+quality+data)

同目录下还有 `data.csv` / `test.csv`（课程样例）、`PRSA2017_Data_....zip`（压缩包备份）。

## 本地副本（不要提交）

`data/raw/` 与上面 CSV **内容重复**，已在根目录 `.gitignore` 忽略。分析时请只读 `HOURLY_DIR`。

## 处理后数据（本地生成）

`data/processed/` 存放清洗、聚合结果，例如：

- `processed_hourly.csv`
- `processed_daily.csv`
- `data_summary.json`

默认不入库；若助教要求一并提交，由组长确认后再从 `.gitignore` 中放开。

## 处理后数据说明

B 项负责对北京 12 个空气质量监测站点的小时级原始数据进行合并、清洗、汇总和探索性分析。

### 1. 数据预处理

运行以下命令生成处理后数据：

```bash
python scripts/preprocess_data.py
```

该脚本完成以下工作：

1. 读取 `data/beijing+multi+site+air+quality+data/` 下的 12 个站点 CSV 文件；
2. 合并所有站点的小时级数据；
3. 根据 `year`、`month`、`day`、`hour` 生成统一的 `datetime` 时间列；
4. 将污染物变量和气象变量转换为数值类型；
5. 按站点进行时间序列插值，处理缺失值；
6. 生成小时级处理数据和日均数据。

输出文件包括：

* `data/processed/processed_hourly.csv`
* `data/processed/processed_daily.csv`
* `data/processed/data_summary.json`

本次处理结果：

* 小时级数据行数：420768
* 日均数据行数：17532
* 站点数量：12

### 2. 探索性分析

运行以下命令生成 EDA 图表和统计表：

```bash
python scripts/eda.py
```

输出图像保存到：

* `reports/figures/site_pm25_mean.png`
* `reports/figures/pollutant_correlation.png`
* `reports/figures/pm25_time_trend.png`
* `reports/figures/monthly_pm25_pattern.png`
* `reports/figures/urban_suburban_pm25_boxplot.png`

输出表格保存到：

* `reports/tables/data_overview.csv`
* `reports/tables/pollutant_summary.csv`
* `reports/tables/site_pm25_summary.csv`
* `reports/tables/urban_suburban_pm25_summary.csv`

### 3. 复现命令

从原始数据开始复现 B 项结果，可以依次运行：

```bash
python scripts/preprocess_data.py
python scripts/eda.py
```

## 4. 分布分析、置信区间与假设检验

统计推断脚本为：

```text
scripts/statistical_analysis.py
```

运行命令：

```bash
python scripts/statistical_analysis.py
```

该脚本基于 `data/processed/processed_daily.csv` 进行统计分析，主要完成以下工作：

1. 生成主要污染物的分布统计表；
2. 绘制 PM2.5 原始分布直方图；
3. 绘制 `log(PM2.5 + 1)` 分布直方图；
4. 绘制 `log(PM2.5 + 1)` 的 Q-Q 图；
5. 计算各站点 PM2.5 日均值的 95% 置信区间；
6. 计算城区与郊区 PM2.5 日均值的 95% 置信区间；
7. 使用 Welch t-test 检验城区与郊区 PM2.5 均值是否存在显著差异；
8. 同时对原始 PM2.5 和 `log(PM2.5 + 1)` 进行检验，便于比较结果。

输出表格包括：

```text
reports/tables/pollutant_distribution_summary.csv
reports/tables/station_pm25_confidence_interval.csv
reports/tables/urban_suburban_pm25_confidence_interval.csv
reports/tables/urban_suburban_pm25_ttest.csv
```

输出图像包括：

```text
reports/figures/pm25_distribution_histogram.png
reports/figures/log_pm25_distribution_histogram.png
reports/figures/log_pm25_qqplot.png
```

### 4.1 分布分析说明

为了解 PM2.5 日均值的分布特征，本部分绘制了 PM2.5 原始分布直方图和 `log(PM2.5 + 1)` 分布直方图。

由于空气污染物浓度数据通常存在右偏分布，即少数高污染天会使数据分布向右拉长，因此本项目同时对 PM2.5 进行对数变换：

```text
log(PM2.5 + 1)
```

其中加 1 是为了避免 PM2.5 数值为 0 时无法取对数。

分布分析输出图像包括：

```text
reports/figures/pm25_distribution_histogram.png
reports/figures/log_pm25_distribution_histogram.png
reports/figures/log_pm25_qqplot.png
```

主要污染物的分布统计结果保存于：

```text
reports/tables/pollutant_distribution_summary.csv
```

该表包含以下统计量：

```text
样本量 n
均值 mean
中位数 median
标准差 std
最小值 min
第一四分位数 q25
第三四分位数 q75
最大值 max
偏度 skewness
峰度 kurtosis
```

### 4.2 置信区间说明

本部分对 PM2.5 日均值计算 95% 置信区间，用于估计总体均值可能所在的范围。

置信区间计算公式为：

```text
mean ± t * standard_error
```

其中：

```text
standard_error = sample_std / sqrt(n)
```

各站点 PM2.5 日均值的 95% 置信区间保存于：

```text
reports/tables/station_pm25_confidence_interval.csv
```

城区与郊区 PM2.5 日均值的 95% 置信区间保存于：

```text
reports/tables/urban_suburban_pm25_confidence_interval.csv
```

### 4.3 假设检验说明

为比较城区与郊区 PM2.5 水平是否存在显著差异，本部分使用 Welch t-test。

Welch t-test 适用于两组样本均值比较，并且不要求两组样本方差完全相等，因此适合用于比较城区站点和郊区站点的 PM2.5 日均值差异。

原假设与备择假设为：

```text
H0：城区与郊区 PM2.5 均值不存在显著差异
H1：城区与郊区 PM2.5 均值存在显著差异
```

显著性水平设定为：

```text
alpha = 0.05
```

判断规则为：

```text
若 p_value < 0.05，则拒绝原假设，认为城区与郊区 PM2.5 均值差异显著；
若 p_value >= 0.05，则不拒绝原假设，认为没有足够证据说明差异显著。
```

假设检验结果保存于：

```text
reports/tables/urban_suburban_pm25_ttest.csv
```

该文件中同时包含两种检验结果：

```text
Welch t-test on raw daily PM2.5
Welch t-test on log(PM2.5 + 1)
```

其中，`log(PM2.5 + 1)` 的检验结果可作为主要参考，因为对数变换可以一定程度上缓解 PM2.5 数据右偏的问题。

### 4.4 完整复现命令

如果从原始数据开始完整复现 B 项结果，可以依次运行：

```bash
python scripts/preprocess_data.py
python scripts/eda.py
python scripts/statistical_analysis.py
```

运行完成后，将生成以下结果目录：

```text
data/processed/
reports/tables/
reports/figures/
```



