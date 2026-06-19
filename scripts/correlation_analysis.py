"""Pearson and Spearman correlations between PM2.5 and weather."""

import pandas as pd
from scipy import stats

from analysis_common import load_analysis_data
from src.config import MET_COLS, TABLES_DIR


def calculate_correlations(data):
    rows = []
    for outcome in ["PM2.5", "log_pm25"]:
        for variable in MET_COLS:
            x = data[variable].to_numpy(dtype=float)
            y = data[outcome].to_numpy(dtype=float)
            pearson = stats.pearsonr(x, y)
            spearman = stats.spearmanr(x, y)
            rows.extend(
                [
                    {
                        "outcome": outcome,
                        "variable": variable,
                        "method": "Pearson",
                        "coefficient": pearson.statistic,
                        "p_value": pearson.pvalue,
                        "n": len(data),
                    },
                    {
                        "outcome": outcome,
                        "variable": variable,
                        "method": "Spearman",
                        "coefficient": spearman.statistic,
                        "p_value": spearman.pvalue,
                        "n": len(data),
                    },
                ]
            )
    return pd.DataFrame(rows)


def main():
    TABLES_DIR.mkdir(parents=True, exist_ok=True)
    print("Loading processed daily data...")
    data = load_analysis_data()
    print("Calculating Pearson and Spearman correlations...")
    correlations = calculate_correlations(data)
    output = TABLES_DIR / "meteorological_correlations.csv"
    correlations.to_csv(output, index=False, encoding="utf-8-sig")
    print(f"Correlation table: {output}")


if __name__ == "__main__":
    main()
