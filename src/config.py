"""Project paths and shared constants."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT / "data" / "raw"
PROCESSED_DIR = ROOT / "data" / "processed"
FIGURES_DIR = ROOT / "reports" / "figures"
TABLES_DIR = ROOT / "reports" / "tables"

HOURLY_FILE = PROCESSED_DIR / "processed_hourly.csv"
DAILY_FILE = PROCESSED_DIR / "processed_daily.csv"
SUMMARY_FILE = PROCESSED_DIR / "data_summary.json"

MIN_VALID_HOURS_PER_DAY = 18
RANDOM_SEED = 42
BOOTSTRAP_N = 2000

# Pre-defined site groups (urban core vs suburban/rural background)
URBAN_SITES = [
    "Dongsi",
    "Tiantan",
    "Guanyuan",
    "Wanshouxigong",
    "Aotizhongxin",
    "Nongzhanguan",
]
SUBURBAN_SITES = [
    "Changping",
    "Dingling",
    "Shunyi",
    "Huairou",
    "Wanliu",
    "Gucheng",
]

POLLUTANT_COLS = ["PM2.5", "PM10", "SO2", "NO2", "CO", "O3"]
MET_COLS = ["TEMP", "PRES", "DEWP", "RAIN", "WSPM"]
HEAVY_POLLUTION_THRESHOLD = 75.0

SITE_LABELS_ZH = {
    "Aotizhongxin": "奥体中心",
    "Changping": "昌平",
    "Dingling": "定陵",
    "Dongsi": "东四",
    "Guanyuan": "官园",
    "Gucheng": "古城",
    "Huairou": "怀柔",
    "Nongzhanguan": "农展馆",
    "Shunyi": "顺义",
    "Tiantan": "天坛",
    "Wanliu": "万柳",
    "Wanshouxigong": "万寿西宫",
}
