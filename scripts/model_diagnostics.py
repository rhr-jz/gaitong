"""Regression diagnostics for the primary adjusted model."""

import numpy as np
import pandas as pd
from scipy import stats

from analysis_common import (
    add_standardized_weather,
    fit_all_models,
    get_primary_model,
    load_analysis_data,
)
from src.config import MET_COLS, TABLES_DIR


def breusch_pagan_test(model):
    x = model["x"]
    squared_residuals = model["residuals"] ** 2
    auxiliary_beta = np.linalg.pinv(x.T @ x) @ x.T @ squared_residuals
    auxiliary_fitted = x @ auxiliary_beta
    centered = squared_residuals - squared_residuals.mean()
    sst = float(centered @ centered)
    sse = float(((squared_residuals - auxiliary_fitted) ** 2).sum())
    auxiliary_r2 = max(0.0, min(1.0, 1.0 - sse / sst)) if sst > 0 else 0.0
    lm_statistic = len(x) * auxiliary_r2
    df = x.shape[1] - 1
    return lm_statistic, df, stats.chi2.sf(lm_statistic, df)


def calculate_vif(data):
    columns = [f"{col}_z" for col in MET_COLS]
    values = data[columns].to_numpy(dtype=float)
    rows = []
    for index, column in enumerate(columns):
        y = values[:, index]
        others = np.delete(values, index, axis=1)
        x = np.column_stack([np.ones(len(values)), others])
        beta = np.linalg.pinv(x.T @ x) @ x.T @ y
        residuals = y - x @ beta
        sse = float(residuals @ residuals)
        sst = float(((y - y.mean()) ** 2).sum())
        r_squared = 1.0 - sse / sst
        vif = 1.0 / max(1.0 - r_squared, np.finfo(float).eps)
        rows.append({"variable": column, "r_squared": r_squared, "vif": vif})
    return pd.DataFrame(rows)


def station_durbin_watson(data, residuals):
    rows = []
    for station, positions in data.groupby("station", observed=True).indices.items():
        ordered_positions = np.sort(np.asarray(positions))
        station_residuals = residuals[ordered_positions]
        denominator = float((station_residuals**2).sum())
        dw = (
            float((np.diff(station_residuals) ** 2).sum()) / denominator
            if denominator > 0
            else np.nan
        )
        rows.append(
            {"station": str(station), "n": len(station_residuals), "durbin_watson": dw}
        )
    return pd.DataFrame(rows)


def build_diagnostics(data, model):
    residuals = model["residuals"]
    bp_stat, bp_df, bp_p = breusch_pagan_test(model)
    jb = stats.jarque_bera(residuals)
    dw_by_station = station_durbin_watson(data, residuals)
    cooks = model["cooks_distance"]
    cook_threshold = 4.0 / len(data)

    diagnostics = pd.DataFrame(
        [
            {
                "model": model["name"],
                "breusch_pagan_lm": bp_stat,
                "breusch_pagan_df": bp_df,
                "breusch_pagan_p_value": bp_p,
                "jarque_bera_statistic": jb.statistic,
                "jarque_bera_p_value": jb.pvalue,
                "residual_skewness": stats.skew(residuals),
                "residual_excess_kurtosis": stats.kurtosis(residuals),
                "median_station_durbin_watson": dw_by_station[
                    "durbin_watson"
                ].median(),
                "min_station_durbin_watson": dw_by_station[
                    "durbin_watson"
                ].min(),
                "max_station_durbin_watson": dw_by_station[
                    "durbin_watson"
                ].max(),
                "cook_threshold_4_over_n": cook_threshold,
                "max_cooks_distance": cooks.max(),
                "observations_above_cook_threshold": int(
                    (cooks > cook_threshold).sum()
                ),
            }
        ]
    )

    influential = data[["station", "date", "PM2.5", *MET_COLS]].copy()
    influential["fitted_log_pm25"] = model["fitted"]
    influential["residual"] = residuals
    influential["standardized_residual"] = model["standardized_residuals"]
    influential["leverage"] = model["leverage"]
    influential["cooks_distance"] = cooks
    influential = influential.nlargest(20, "cooks_distance")
    return diagnostics, dw_by_station, influential


def main():
    TABLES_DIR.mkdir(parents=True, exist_ok=True)
    print("Loading data and fitting the primary adjusted model...")
    data, _ = add_standardized_weather(load_analysis_data())
    primary_model = get_primary_model(fit_all_models(data))

    print("Calculating model diagnostics...")
    diagnostics, dw_by_station, influential = build_diagnostics(
        data, primary_model
    )
    vif = calculate_vif(data)
    diagnostics.to_csv(
        TABLES_DIR / "model_diagnostics.csv", index=False, encoding="utf-8-sig"
    )
    dw_by_station.to_csv(
        TABLES_DIR / "station_durbin_watson.csv",
        index=False,
        encoding="utf-8-sig",
    )
    influential.to_csv(
        TABLES_DIR / "influential_observations.csv",
        index=False,
        encoding="utf-8-sig",
    )
    vif.to_csv(TABLES_DIR / "weather_vif.csv", index=False, encoding="utf-8-sig")
    print(f"Diagnostic tables: {TABLES_DIR}")


if __name__ == "__main__":
    main()
