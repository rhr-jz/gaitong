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
