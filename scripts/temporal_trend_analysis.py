"""Estimate season-adjusted monthly trends for the six air pollutants."""

import numpy as np
import pandas as pd
from scipy import stats

from src.config import DAILY_FILE, POLLUTANT_COLS, TABLES_DIR


HAC_MAX_LAG = 3


def load_monthly_city_series():
    """Aggregate station-day observations into equally weighted city-month means."""
    if not DAILY_FILE.exists():
        raise FileNotFoundError(
            f"Processed daily data not found: {DAILY_FILE}\n"
            "Run: python scripts\\preprocess_data.py"
        )

    data = pd.read_csv(DAILY_FILE, parse_dates=["date"])
    required = {"date", "station", *POLLUTANT_COLS}
    missing = sorted(required.difference(data.columns))
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    # Average stations within each day first so every calendar day receives equal weight.
    city_daily = data.groupby("date", as_index=False)[POLLUTANT_COLS].mean()
    monthly = (
        city_daily.set_index("date")[POLLUTANT_COLS]
        .resample("MS")
        .mean()
        .dropna(how="all")
        .reset_index()
    )
    monthly["year"] = monthly["date"].dt.year
    monthly["month"] = monthly["date"].dt.month
    monthly["time_years"] = (
        (monthly["date"] - monthly["date"].min()).dt.days / 365.25
    )
    return monthly


def build_month_fixed_effect_design(monthly):
    """Create a linear time trend plus calendar-month fixed effects."""
    month_dummies = pd.get_dummies(
        monthly["month"].astype(str), prefix="month", drop_first=True, dtype=float
    )
    predictors = pd.concat(
        [monthly[["time_years"]].astype(float), month_dummies], axis=1
    )
    x = np.column_stack(
        [np.ones(len(predictors), dtype=float), predictors.to_numpy(dtype=float)]
    )
    names = ["Intercept", *predictors.columns.tolist()]
    return x, names


def newey_west_covariance(x, residuals, max_lag):
    """Compute a Bartlett-kernel Newey-West covariance matrix."""
    n, p = x.shape
    if n <= p:
        raise ValueError(f"Insufficient observations for HAC inference: {n} <= {p}")

    bread = np.linalg.pinv(x.T @ x)
    score = x * residuals[:, None]
    meat = score.T @ score
    for lag in range(1, min(max_lag, n - 1) + 1):
        weight = 1.0 - lag / (max_lag + 1.0)
        lagged = score[lag:].T @ score[:-lag]
        meat += weight * (lagged + lagged.T)

    covariance = bread @ meat @ bread
    return covariance * n / (n - p)


def fit_monthly_trend(monthly, pollutant):
    """Fit log concentration on time and month effects with HAC inference."""
    subset = monthly.dropna(subset=[pollutant]).reset_index(drop=True)
    x, names = build_month_fixed_effect_design(subset)
    y = np.log1p(subset[pollutant].to_numpy(dtype=float))

    xtx_inverse = np.linalg.pinv(x.T @ x)
    beta = xtx_inverse @ x.T @ y
    fitted = x @ beta
    residuals = y - fitted
    n, p = x.shape
    df_resid = n - p

    hac_covariance = newey_west_covariance(x, residuals, HAC_MAX_LAG)
    hac_se = np.sqrt(np.clip(np.diag(hac_covariance), 0.0, None))
    trend_index = names.index("time_years")
    trend_beta = float(beta[trend_index])
    trend_se = float(hac_se[trend_index])
    t_statistic = trend_beta / trend_se
    p_value = float(2 * stats.t.sf(abs(t_statistic), df=df_resid))
    critical = float(stats.t.ppf(0.975, df=df_resid))
    beta_lower = trend_beta - critical * trend_se
    beta_upper = trend_beta + critical * trend_se

    sse = float(residuals @ residuals)
    sst = float(((y - y.mean()) ** 2).sum())
    r_squared = 1.0 - sse / sst
    adjusted_r_squared = 1.0 - (1.0 - r_squared) * (n - 1) / df_resid
    durbin_watson = float(np.diff(residuals) @ np.diff(residuals) / sse)

    return {
        "pollutant": pollutant,
        "n_months": n,
        "start_month": subset["date"].min().strftime("%Y-%m"),
        "end_month": subset["date"].max().strftime("%Y-%m"),
        "coefficient_per_year": trend_beta,
        "hac_max_lag": HAC_MAX_LAG,
        "hac_std_error": trend_se,
        "t_statistic": t_statistic,
        "p_value": p_value,
        "annual_percent_change": 100.0 * np.expm1(trend_beta),
        "annual_percent_ci_lower": 100.0 * np.expm1(beta_lower),
        "annual_percent_ci_upper": 100.0 * np.expm1(beta_upper),
        "r_squared": r_squared,
        "adjusted_r_squared": adjusted_r_squared,
        "durbin_watson": durbin_watson,
    }


def benjamini_hochberg(p_values):
    """Return Benjamini-Hochberg adjusted p-values in original order."""
    p_values = np.asarray(p_values, dtype=float)
    order = np.argsort(p_values)
    ranked = p_values[order]
    adjusted_ranked = ranked * len(ranked) / np.arange(1, len(ranked) + 1)
    adjusted_ranked = np.minimum.accumulate(adjusted_ranked[::-1])[::-1]
    adjusted = np.empty_like(adjusted_ranked)
    adjusted[order] = np.clip(adjusted_ranked, 0.0, 1.0)
    return adjusted


def build_long_monthly_series(monthly):
    """Create a plotting table with monthly values and 12-month rolling means."""
    rows = []
    for pollutant in POLLUTANT_COLS:
        values = monthly[pollutant]
        rolling = values.rolling(window=12, min_periods=12).mean()
        for date, value, rolling_value in zip(monthly["date"], values, rolling):
            rows.append(
                {
                    "date": date.strftime("%Y-%m-%d"),
                    "pollutant": pollutant,
                    "monthly_mean": value,
                    "rolling_12_month_mean": rolling_value,
                }
            )
    return pd.DataFrame(rows)


def main():
    TABLES_DIR.mkdir(parents=True, exist_ok=True)
    monthly = load_monthly_city_series()
    results = pd.DataFrame(
        [fit_monthly_trend(monthly, pollutant) for pollutant in POLLUTANT_COLS]
    )
    results["fdr_adjusted_p_value"] = benjamini_hochberg(results["p_value"])
    results["significant_after_fdr"] = results["fdr_adjusted_p_value"] < 0.05

    series = build_long_monthly_series(monthly)
    series.to_csv(TABLES_DIR / "monthly_pollutant_series.csv", index=False)
    results.to_csv(TABLES_DIR / "temporal_trend_results.csv", index=False)

    print("Monthly temporal trend analysis completed.")
    print(results[
        [
            "pollutant",
            "annual_percent_change",
            "annual_percent_ci_lower",
            "annual_percent_ci_upper",
            "p_value",
            "fdr_adjusted_p_value",
        ]
    ].to_string(index=False))


if __name__ == "__main__":
    main()
