"""Multiple linear regression analysis of daily PM2.5."""

import pandas as pd

from analysis_common import add_standardized_weather, fit_all_models, load_analysis_data
from src.config import TABLES_DIR


def main():
    TABLES_DIR.mkdir(parents=True, exist_ok=True)
    print("Loading and standardizing weather variables...")
    data, scaling = add_standardized_weather(load_analysis_data())
    scaling.to_csv(
        TABLES_DIR / "weather_scaling.csv", index=False, encoding="utf-8-sig"
    )

    print("Fitting the three pre-specified regression models...")
    models = fit_all_models(data)
    coefficients = pd.concat(
        [model["coefficients"] for model in models], ignore_index=True
    )
    comparisons = pd.DataFrame([model["comparison"] for model in models])
    coefficients.to_csv(
        TABLES_DIR / "regression_coefficients.csv",
        index=False,
        encoding="utf-8-sig",
    )
    comparisons.to_csv(
        TABLES_DIR / "regression_model_comparison.csv",
        index=False,
        encoding="utf-8-sig",
    )
    print(f"Regression tables: {TABLES_DIR}")


if __name__ == "__main__":
    main()
