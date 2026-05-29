from pathlib import Path
import sys

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# 让 Python 能找到项目里的 src 文件夹
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT))

from src.config import (
    DAILY_FILE,
    POLLUTANT_COLS,
    MET_COLS,
    URBAN_SITES,
    SUBURBAN_SITES,
)

FIGURES_DIR = PROJECT_ROOT / "reports" / "figures"
TABLES_DIR = PROJECT_ROOT / "reports" / "tables"


def load_daily_data():
    if not DAILY_FILE.exists():
        raise FileNotFoundError(
            f"没有找到处理后的日均数据：{DAILY_FILE}\n"
            "请先运行：python scripts\\preprocess_data.py"
        )

    data = pd.read_csv(DAILY_FILE)
    data["date"] = pd.to_datetime(data["date"])

    return data


def save_data_overview(data):
    overview = (
        data.groupby("station")
        .agg(
            start_date=("date", "min"),
            end_date=("date", "max"),
            days=("date", "count"),
            pm25_mean=("PM2.5", "mean"),
            pm25_median=("PM2.5", "median"),
            pm25_std=("PM2.5", "std"),
            pm25_max=("PM2.5", "max"),
            pm10_mean=("PM10", "mean"),
            no2_mean=("NO2", "mean"),
            o3_mean=("O3", "mean"),
        )
        .reset_index()
    )

    overview.to_csv(TABLES_DIR / "data_overview.csv", index=False, encoding="utf-8-sig")


def save_pollutant_summary(data):
    summary = data[list(POLLUTANT_COLS)].describe().T
    summary.to_csv(TABLES_DIR / "pollutant_summary.csv", encoding="utf-8-sig")


def plot_site_pm25_mean(data):
    site_pm25 = (
        data.groupby("station")["PM2.5"]
        .mean()
        .sort_values(ascending=False)
        .reset_index()
    )

    site_pm25.to_csv(TABLES_DIR / "site_pm25_summary.csv", index=False, encoding="utf-8-sig")

    plt.figure(figsize=(10, 6))
    sns.barplot(data=site_pm25, x="PM2.5", y="station")
    plt.title("Average PM2.5 by Station")
    plt.xlabel("Average PM2.5")
    plt.ylabel("Station")
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "site_pm25_mean.png", dpi=300)
    plt.close()


def plot_pollutant_correlation(data):
    corr = data[list(POLLUTANT_COLS)].corr()

    plt.figure(figsize=(8, 6))
    sns.heatmap(corr, annot=True, fmt=".2f", square=True)
    plt.title("Correlation Between Pollutants")
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "pollutant_correlation.png", dpi=300)
    plt.close()


def plot_pm25_time_trend(data):
    daily_mean = (
        data.groupby("date")["PM2.5"]
        .mean()
        .reset_index()
    )

    plt.figure(figsize=(12, 5))
    sns.lineplot(data=daily_mean, x="date", y="PM2.5")
    plt.title("Daily Average PM2.5 Trend")
    plt.xlabel("Date")
    plt.ylabel("Average PM2.5")
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "pm25_time_trend.png", dpi=300)
    plt.close()


def plot_monthly_pm25_pattern(data):
    data = data.copy()
    data["month"] = data["date"].dt.month

    monthly = (
        data.groupby("month")["PM2.5"]
        .mean()
        .reset_index()
    )

    plt.figure(figsize=(9, 5))
    sns.lineplot(data=monthly, x="month", y="PM2.5", marker="o")
    plt.title("Monthly Pattern of PM2.5")
    plt.xlabel("Month")
    plt.ylabel("Average PM2.5")
    plt.xticks(range(1, 13))
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "monthly_pm25_pattern.png", dpi=300)
    plt.close()


def plot_urban_suburban_pm25(data):
    data = data.copy()

    def site_group(station):
        if station in URBAN_SITES:
            return "Urban"
        if station in SUBURBAN_SITES:
            return "Suburban"
        return "Other"

    data["site_group"] = data["station"].apply(site_group)
    data = data[data["site_group"].isin(["Urban", "Suburban"])]

    group_summary = (
        data.groupby("site_group")["PM2.5"]
        .agg(["count", "mean", "median", "std", "min", "max"])
        .reset_index()
    )

    group_summary.to_csv(
        TABLES_DIR / "urban_suburban_pm25_summary.csv",
        index=False,
        encoding="utf-8-sig",
    )

    plt.figure(figsize=(8, 5))
    sns.boxplot(data=data, x="site_group", y="PM2.5")
    plt.title("PM2.5 Comparison: Urban vs Suburban Sites")
    plt.xlabel("Site Group")
    plt.ylabel("PM2.5")
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "urban_suburban_pm25_boxplot.png", dpi=300)
    plt.close()


def main():
    print("开始读取日均数据...")
    data = load_daily_data()

    print("开始创建输出目录...")
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    TABLES_DIR.mkdir(parents=True, exist_ok=True)

    print("生成数据概况表...")
    save_data_overview(data)

    print("生成污染物描述统计表...")
    save_pollutant_summary(data)

    print("生成各站点 PM2.5 均值图...")
    plot_site_pm25_mean(data)

    print("生成污染物相关性热图...")
    plot_pollutant_correlation(data)

    print("生成 PM2.5 时间趋势图...")
    plot_pm25_time_trend(data)

    print("生成 PM2.5 月份变化图...")
    plot_monthly_pm25_pattern(data)

    print("生成城区与郊区 PM2.5 对比图...")
    plot_urban_suburban_pm25(data)

    print("完成！")
    print(f"图像保存到：{FIGURES_DIR}")
    print(f"表格保存到：{TABLES_DIR}")


if __name__ == "__main__":
    main()
