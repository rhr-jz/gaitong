"""Shared data preparation and OLS helpers for statistical analyses."""

from pathlib import Path
import sys

import numpy as np
import pandas as pd
from scipy import stats


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT))

from src.config import DAILY_FILE, MET_COLS


SEASON_ORDER = ["Spring", "Summer", "Autumn", "Winter"]
SEASON_BY_MONTH = {
    1: "Winter",
    2: "Winter",
    3: "Spring",
    4: "Spring",
    5: "Spring",
    6: "Summer",
    7: "Summer",
    8: "Summer",
    9: "Autumn",
    10: "Autumn",
    11: "Autumn",
    12: "Winter",
}
MODEL_SPECIFICATIONS = [
    ("M1_weather", False, False),
    ("M2_adjusted", True, False),
    ("M3_year_adjusted", True, True),
]
MODEL_LABELS = {
    "M1_weather": "Weather only",
    "M2_adjusted": "Weather + season + station",
    "M3_year_adjusted": "Weather + season + station + year",
}
WEATHER_LABELS = {
    "TEMP_z": "Temperature",
    "PRES_z": "Pressure",
    "DEWP_z": "Dew point",
    "RAIN_z": "Rainfall",
    "WSPM_z": "Wind speed",
}


def load_analysis_data():
    """Load daily data and derive analysis variables in memory."""
    if not DAILY_FILE.exists():
        raise FileNotFoundError(
            f"Processed daily data not found: {DAILY_FILE}\n"
            "Run: python scripts\\preprocess_data.py"
        )

    data = pd.read_csv(DAILY_FILE)
    required = {"station", "date", "PM2.5", *MET_COLS}
    missing = sorted(required.difference(data.columns))
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    data["date"] = pd.to_datetime(data["date"], errors="raise")
    data["year"] = data["date"].dt.year
    data["season"] = data["date"].dt.month.map(SEASON_BY_MONTH)
    data["season"] = pd.Categorical(
        data["season"], categories=SEASON_ORDER, ordered=True
    )
    data["station"] = pd.Categorical(
        data["station"], categories=sorted(data["station"].unique())
    )

    analysis_cols = ["station", "date", "year", "season", "PM2.5", *MET_COLS]
    data = data[analysis_cols].dropna().copy()
    data = data[data["PM2.5"] >= 0].copy()
    data["log_pm25"] = np.log1p(data["PM2.5"])
    return data.sort_values(["station", "date"]).reset_index(drop=True)


def add_standardized_weather(data):
    """Add z-scored weather variables and return their scaling parameters."""
    data = data.copy()
    rows = []
    for col in MET_COLS:
        mean = float(data[col].mean())
        std = float(data[col].std(ddof=0))
        if not np.isfinite(std) or std <= 0:
            raise ValueError(f"Cannot standardize {col}: standard deviation is {std}")
        data[f"{col}_z"] = (data[col] - mean) / std
        rows.append({"variable": col, "mean": mean, "std_ddof0": std})
    return data, pd.DataFrame(rows)


def build_design_matrix(data, add_fixed_effects=False, add_year=False):
    """Build an OLS matrix with explicit reference categories."""
    weather_cols = [f"{col}_z" for col in MET_COLS]
    pieces = [data[weather_cols].astype(float)]

    if add_fixed_effects:
        pieces.extend(
            [
                pd.get_dummies(
                    data["season"], prefix="season", drop_first=True, dtype=float
                ),
                pd.get_dummies(
                    data["station"], prefix="station", drop_first=True, dtype=float
                ),
            ]
        )

    if add_year:
        pieces.append(
            pd.get_dummies(
                data["year"].astype(str), prefix="year", drop_first=True, dtype=float
            )
        )

    predictors = pd.concat(pieces, axis=1)
    x = np.column_stack(
        [np.ones(len(predictors), dtype=float), predictors.to_numpy(dtype=float)]
    )
    return x, ["Intercept", *predictors.columns.tolist()]


def fit_ols(x, y, names, model_name):
    """Fit OLS and calculate classical and HC3 inference."""
    n, p = x.shape
    rank = int(np.linalg.matrix_rank(x))
    if rank < p:
        raise ValueError(f"{model_name} design matrix is rank deficient: {rank} < {p}")

    xtx_inverse = np.linalg.pinv(x.T @ x)
    beta = xtx_inverse @ x.T @ y
    fitted = x @ beta
    residuals = y - fitted
    sse = float(residuals @ residuals)
    df_resid = n - p
    mse = sse / df_resid

    leverage = np.einsum("ij,jk,ik->i", x, xtx_inverse, x)
    leverage = np.clip(leverage, 0.0, 1.0 - 1e-10)

    classical_se = np.sqrt(
        np.clip(np.diag(mse * xtx_inverse), 0.0, None)
    )
    hc3_scale = (residuals / (1.0 - leverage)) ** 2
    hc3_meat = x.T @ (x * hc3_scale[:, None])
    hc3_cov = xtx_inverse @ hc3_meat @ xtx_inverse
    hc3_se = np.sqrt(np.clip(np.diag(hc3_cov), 0.0, None))

    t_stat = np.divide(
        beta,
        classical_se,
        out=np.full_like(beta, np.nan),
        where=classical_se > 0,
    )
    hc3_t = np.divide(
        beta, hc3_se, out=np.full_like(beta, np.nan), where=hc3_se > 0
    )
    p_value = 2 * stats.t.sf(np.abs(t_stat), df=df_resid)
    hc3_p_value = 2 * stats.t.sf(np.abs(hc3_t), df=df_resid)
    t_critical = stats.t.ppf(0.975, df=df_resid)

    coefficients = pd.DataFrame(
        {
            "model": model_name,
            "term": names,
            "estimate": beta,
            "std_error": classical_se,
            "t_statistic": t_stat,
            "p_value": p_value,
            "ci_lower": beta - t_critical * classical_se,
            "ci_upper": beta + t_critical * classical_se,
            "hc3_std_error": hc3_se,
            "hc3_t_statistic": hc3_t,
            "hc3_p_value": hc3_p_value,
            "hc3_ci_lower": beta - t_critical * hc3_se,
            "hc3_ci_upper": beta + t_critical * hc3_se,
        }
    )

    sst = float(((y - y.mean()) ** 2).sum())
    r_squared = 1.0 - sse / sst
    adjusted_r_squared = 1.0 - (1.0 - r_squared) * (n - 1) / df_resid
    log_likelihood_term = np.log(max(sse / n, np.finfo(float).tiny))
    comparison = {
        "model": model_name,
        "n": n,
        "parameters": p,
        "r_squared": r_squared,
        "adjusted_r_squared": adjusted_r_squared,
        "rmse": np.sqrt(sse / n),
        "residual_std_error": np.sqrt(mse),
        "aic": n * log_likelihood_term + 2 * p,
        "bic": n * log_likelihood_term + np.log(n) * p,
        "condition_number": np.linalg.cond(x),
    }

    cooks_distance = (
        residuals**2 / (p * mse) * leverage / (1.0 - leverage) ** 2
    )
    standardized_residuals = residuals / np.sqrt(mse * (1.0 - leverage))

    return {
        "name": model_name,
        "x": x,
        "names": names,
        "coefficients": coefficients,
        "comparison": comparison,
        "fitted": fitted,
        "residuals": residuals,
        "standardized_residuals": standardized_residuals,
        "leverage": leverage,
        "cooks_distance": cooks_distance,
        "mse": mse,
    }


def fit_all_models(data):
    """Fit the three pre-specified regression models."""
    y = data["log_pm25"].to_numpy(dtype=float)
    models = []
    for model_name, add_fixed_effects, add_year in MODEL_SPECIFICATIONS:
        x, names = build_design_matrix(
            data, add_fixed_effects=add_fixed_effects, add_year=add_year
        )
        models.append(fit_ols(x, y, names, model_name))
    return models


def get_primary_model(models):
    return next(model for model in models if model["name"] == "M2_adjusted")


def format_p_value(value):
    if value == 0 or value < 1e-300:
        return "< 1e-300"
    if value < 0.001:
        return f"= {value:.2e}"
    return f"= {value:.3f}"
