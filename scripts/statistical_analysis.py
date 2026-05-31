from pathlib import Path
import sys

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats

# 让 Python 能找到项目里的 src 文件夹
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT))

from src.config import (
    DAILY_FILE,
    POLLUTANT_COLS,
    URBAN_SITES,
    SUBURBAN_SITES,
    TABLES_DIR,
    FIGURES_DIR,
)


def load_daily_data():
    if not DAILY_FILE.exists():
        raise FileNotFoundError(
            f"没有找到日均数据：{DAILY_FILE}\n"
            "请先运行：python scripts\\preprocess_data.py"
        )

    data = pd.read_csv(DAILY_FILE)
    data["date"] = pd.to_datetime(data["date"])

    return data


def add_site_group(data):
    data = data.copy()

    def classify_station(station):
        if station in URBAN_SITES:
            return "Urban"
        if station in SUBURBAN_SITES:
            return "Suburban"
        return "Other"

    data["site_group"] = data["station"].apply(classify_station)
    return data


def mean_confidence_interval(series, confidence=0.95):
    x = pd.Series(series).dropna()
    n = len(x)

    if n < 2:
        return {
            "n": n,
            "mean": np.nan,
            "std": np.nan,
            "se": np.nan,
            "ci_lower": np.nan,
            "ci_upper": np.nan,
        }

    mean = x.mean()
    std = x.std(ddof=1)
    se = std / np.sqrt(n)
    alpha = 1 - confidence
    t_critical = stats.t.ppf(1 - alpha / 2, df=n - 1)

    return {
        "n": n,
        "mean": mean,
        "std": std,
        "se": se,
        "ci_lower": mean - t_critical * se,
        "ci_upper": mean + t_critical * se,
    }


def save_distribution_summary(data):
    rows = []

    for col in POLLUTANT_COLS:
        x = data[col].dropna()
        rows.append({
            "variable": col,
            "n": len(x),
            "mean": x.mean(),
            "median": x.median(),
            "std": x.std(ddof=1),
            "min": x.min(),
            "q25": x.quantile(0.25),
            "q75": x.quantile(0.75),
            "max": x.max(),
            "skewness": stats.skew(x),
            "kurtosis": stats.kurtosis(x),
        })

    summary = pd.DataFrame(rows)
    summary.to_csv(
        TABLES_DIR / "pollutant_distribution_summary.csv",
        index=False,
        encoding="utf-8-sig",
    )


def save_station_pm25_ci(data):
    rows = []

    for station, group in data.groupby("station"):
        ci = mean_confidence_interval(group["PM2.5"])
        ci["station"] = station
        ci["variable"] = "PM2.5"
        rows.append(ci)

    result = pd.DataFrame(rows)
    result = result[
        ["station", "variable", "n", "mean", "std", "se", "ci_lower", "ci_upper"]
    ]
    result.to_csv(
        TABLES_DIR / "station_pm25_confidence_interval.csv",
        index=False,
        encoding="utf-8-sig",
    )


def save_group_pm25_ci(data):
    data = data[data["site_group"].isin(["Urban", "Suburban"])].copy()

    rows = []

    for site_group, group in data.groupby("site_group"):
        ci = mean_confidence_interval(group["PM2.5"])
        ci["site_group"] = site_group
        ci["variable"] = "PM2.5"
        rows.append(ci)

    result = pd.DataFrame(rows)
    result = result[
        ["site_group", "variable", "n", "mean", "std", "se", "ci_lower", "ci_upper"]
    ]
    result.to_csv(
        TABLES_DIR / "urban_suburban_pm25_confidence_interval.csv",
        index=False,
        encoding="utf-8-sig",
    )


def welch_ttest_with_ci(x1, x2, label, confidence=0.95):
    x1 = pd.Series(x1).dropna()
    x2 = pd.Series(x2).dropna()

    n1 = len(x1)
    n2 = len(x2)

    mean1 = x1.mean()
    mean2 = x2.mean()
    var1 = x1.var(ddof=1)
    var2 = x2.var(ddof=1)

    diff = mean1 - mean2
    se = np.sqrt(var1 / n1 + var2 / n2)

    # Welch-Satterthwaite 自由度
    df = (var1 / n1 + var2 / n2) ** 2 / (
        (var1 / n1) ** 2 / (n1 - 1) + (var2 / n2) ** 2 / (n2 - 1)
    )

    alpha = 1 - confidence
    t_critical = stats.t.ppf(1 - alpha / 2, df=df)

    t_stat, p_value = stats.ttest_ind(x1, x2, equal_var=False)

    return {
        "test": label,
        "group_1": "Urban",
        "group_2": "Suburban",
        "n_urban": n1,
        "n_suburban": n2,
        "mean_urban": mean1,
        "mean_suburban": mean2,
        "mean_difference_urban_minus_suburban": diff,
        "t_statistic": t_stat,
        "degrees_of_freedom": df,
        "p_value": p_value,
        "ci_lower": diff - t_critical * se,
        "ci_upper": diff + t_critical * se,
        "alpha": 0.05,
        "conclusion": "significant" if p_value < 0.05 else "not significant",
    }


def save_urban_suburban_ttest(data):
    data = data[data["site_group"].isin(["Urban", "Suburban"])].copy()

    data["log_pm25"] = np.log(data["PM2.5"] + 1)

    urban = data[data["site_group"] == "Urban"]
    suburban = data[data["site_group"] == "Suburban"]

    rows = [
        welch_ttest_with_ci(
            urban["PM2.5"],
            suburban["PM2.5"],
            label="Welch t-test on raw daily PM2.5",
        ),
        welch_ttest_with_ci(
            urban["log_pm25"],
            suburban["log_pm25"],
            label="Welch t-test on log(PM2.5 + 1)",
        ),
    ]

    result = pd.DataFrame(rows)
    result.to_csv(
        TABLES_DIR / "urban_suburban_pm25_ttest.csv",
        index=False,
        encoding="utf-8-sig",
    )


def plot_pm25_distribution(data):
    plt.figure(figsize=(9, 5))
    sns.histplot(data["PM2.5"].dropna(), bins=60, kde=True)
    plt.title("Distribution of Daily PM2.5")
    plt.xlabel("Daily PM2.5")
    plt.ylabel("Frequency")
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "pm25_distribution_histogram.png", dpi=300)
    plt.close()


def plot_log_pm25_distribution(data):
    log_pm25 = np.log(data["PM2.5"].dropna() + 1)

    plt.figure(figsize=(9, 5))
    sns.histplot(log_pm25, bins=60, kde=True)
    plt.title("Distribution of log(PM2.5 + 1)")
    plt.xlabel("log(PM2.5 + 1)")
    plt.ylabel("Frequency")
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "log_pm25_distribution_histogram.png", dpi=300)
    plt.close()


def plot_log_pm25_qq(data):
    log_pm25 = np.log(data["PM2.5"].dropna() + 1)

    plt.figure(figsize=(6, 6))
    stats.probplot(log_pm25, dist="norm", plot=plt)
    plt.title("Q-Q Plot of log(PM2.5 + 1)")
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "log_pm25_qqplot.png", dpi=300)
    plt.close()


def main():
    print("开始读取日均数据...")
    data = load_daily_data()
    data = add_site_group(data)

    print("创建输出目录...")
    TABLES_DIR.mkdir(parents=True, exist_ok=True)
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)

    print("生成污染物分布统计表...")
    save_distribution_summary(data)

    print("生成各站点 PM2.5 置信区间...")
    save_station_pm25_ci(data)

    print("生成城区/郊区 PM2.5 置信区间...")
    save_group_pm25_ci(data)

    print("生成城区/郊区 Welch t 检验...")
    save_urban_suburban_ttest(data)

    print("生成 PM2.5 分布图...")
    plot_pm25_distribution(data)

    print("生成 log(PM2.5 + 1) 分布图...")
    plot_log_pm25_distribution(data)

    print("生成 log(PM2.5 + 1) Q-Q 图...")
    plot_log_pm25_qq(data)

    print("完成！")
    print(f"统计表保存到：{TABLES_DIR}")
    print(f"图像保存到：{FIGURES_DIR}")


if __name__ == "__main__":
    main()
