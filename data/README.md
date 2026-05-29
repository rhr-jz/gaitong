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

