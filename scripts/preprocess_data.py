from pathlib import Path
import sys
import json

import pandas as pd

# 让 Python 能找到项目里的 src 文件夹
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT))

from src.config import (
    HOURLY_DIR,
    PROCESSED_DIR,
    HOURLY_FILE,
    DAILY_FILE,
    SUMMARY_FILE,
    POLLUTANT_COLS,
    MET_COLS,
    MIN_VALID_HOURS_PER_DAY,
)


def load_hourly_data():
    files = sorted(HOURLY_DIR.glob("PRSA_Data_*.csv"))

    if not files:
        raise FileNotFoundError(f"没有找到 CSV 文件，请检查目录：{HOURLY_DIR}")

    frames = []

    for file in files:
        df = pd.read_csv(file)
        df.columns = df.columns.str.strip()

        # 如果文件里没有 station 列，就从文件名里提取
        if "station" not in df.columns:
            station_name = file.stem.replace("PRSA_Data_", "").replace("_20130301-20170228", "")
            df["station"] = station_name

        frames.append(df)

    data = pd.concat(frames, ignore_index=True)

    data["datetime"] = pd.to_datetime(
        data[["year", "month", "day", "hour"]]
    )

    data = data.sort_values(["station", "datetime"]).reset_index(drop=True)

    return data


def clean_hourly_data(data):
    value_cols = list(POLLUTANT_COLS) + list(MET_COLS)

    missing_before = data[value_cols].isna().sum().to_dict()

    for col in value_cols:
        data[col] = pd.to_numeric(data[col], errors="coerce")

    # 按站点进行时间序列插值
    data[value_cols] = (
        data.groupby("station")[value_cols]
        .transform(lambda x: x.interpolate(limit_direction="both"))
    )

    missing_after = data[value_cols].isna().sum().to_dict()

    return data, missing_before, missing_after


def build_daily_data(hourly):
    value_cols = list(POLLUTANT_COLS) + list(MET_COLS)

    hourly = hourly.copy()
    hourly["date"] = hourly["datetime"].dt.date

    valid_hours = (
        hourly.groupby(["station", "date"])["PM2.5"]
        .count()
        .rename("valid_hours")
        .reset_index()
    )

    daily = (
        hourly.groupby(["station", "date"])[value_cols]
        .mean()
        .reset_index()
    )

    daily = daily.merge(valid_hours, on=["station", "date"], how="left")

    daily = daily[daily["valid_hours"] >= MIN_VALID_HOURS_PER_DAY]

    return daily


def build_summary(hourly, daily, missing_before, missing_after):
    summary = {
        "hourly_rows": int(len(hourly)),
        "daily_rows": int(len(daily)),
        "station_count": int(hourly["station"].nunique()),
        "stations": sorted(hourly["station"].dropna().unique().tolist()),
        "start_time": str(hourly["datetime"].min()),
        "end_time": str(hourly["datetime"].max()),
        "pollutant_columns": list(POLLUTANT_COLS),
        "meteorological_columns": list(MET_COLS),
        "missing_before_cleaning": missing_before,
        "missing_after_cleaning": missing_after,
    }

    return summary


def main():
    print("开始读取原始数据...")
    hourly = load_hourly_data()

    print("开始清洗小时数据...")
    hourly, missing_before, missing_after = clean_hourly_data(hourly)

    print("开始生成日均数据...")
    daily = build_daily_data(hourly)

    print("开始保存文件...")
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    hourly.to_csv(HOURLY_FILE, index=False, encoding="utf-8-sig")
    daily.to_csv(DAILY_FILE, index=False, encoding="utf-8-sig")

    summary = build_summary(hourly, daily, missing_before, missing_after)

    with open(SUMMARY_FILE, "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)

    print("完成！")
    print(f"小时数据保存到：{HOURLY_FILE}")
    print(f"日均数据保存到：{DAILY_FILE}")
    print(f"数据摘要保存到：{SUMMARY_FILE}")
    print(f"小时数据行数：{len(hourly)}")
    print(f"日均数据行数：{len(daily)}")
    print(f"站点数量：{hourly['station'].nunique()}")


if __name__ == "__main__":
    main()
