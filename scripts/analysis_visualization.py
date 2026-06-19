"""Publication-ready figures and handoff summary for statistical analyses."""

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from scipy import stats

from analysis_common import (
    MODEL_LABELS,
    WEATHER_LABELS,
    add_standardized_weather,
    fit_all_models,
    format_p_value,
    get_primary_model,
    load_analysis_data,
)
from src.config import FIGURES_DIR, MET_COLS, TABLES_DIR


def configure_plot_style():
    sns.set_theme(style="whitegrid", context="notebook")
    plt.rcParams.update(
        {
            "figure.dpi": 120,
            "savefig.dpi": 300,
            "font.family": "DejaVu Sans",
            "axes.titleweight": "bold",
            "axes.titlesize": 12,
            "axes.labelsize": 10,
            "legend.frameon": False,
            "figure.facecolor": "white",
            "axes.facecolor": "white",
        }
    )


def read_required_table(filename):
    path = TABLES_DIR / filename
    if not path.exists():
        raise FileNotFoundError(
            f"Required analysis table not found: {path}\n"
            "Run: python scripts\\run_analysis.py"
        )
    return pd.read_csv(path)


def plot_correlation_heatmap(correlations):
    plot_data = correlations[correlations["outcome"] == "log_pm25"].pivot(
        index="variable", columns="method", values="coefficient"
    )
    plot_data = plot_data.loc[MET_COLS, ["Pearson", "Spearman"]]

    fig, ax = plt.subplots(figsize=(6.8, 4.6))
    sns.heatmap(
        plot_data,
        annot=True,
        fmt=".2f",
        cmap="RdBu_r",
        center=0,
        vmin=-1,
        vmax=1,
        linewidths=0.8,
        cbar_kws={"label": "Correlation coefficient"},
        ax=ax,
    )
    ax.set_title("Meteorological Correlations with log(PM2.5 + 1)")
    ax.set_xlabel("")
    ax.set_ylabel("Meteorological variable")
    fig.tight_layout()
    fig.savefig(FIGURES_DIR / "meteorological_correlation_heatmap.png")
    plt.close(fig)


def plot_weather_relationships(data):
    sample = data.sample(n=min(6000, len(data)), random_state=42)
    fig, axes = plt.subplots(2, 3, figsize=(13, 7.5))
    axes = axes.ravel()
    labels = {
        "TEMP": "Temperature",
        "PRES": "Pressure",
        "DEWP": "Dew point",
        "RAIN": "Mean hourly rainfall",
        "WSPM": "Wind speed",
    }

    for ax, variable in zip(axes, MET_COLS):
        sns.regplot(
            data=sample,
            x=variable,
            y="log_pm25",
            scatter_kws={"alpha": 0.15, "s": 9, "color": "#4C78A8"},
            line_kws={"color": "#D1495B", "linewidth": 2},
            ci=95,
            ax=ax,
        )
        ax.set_title(labels[variable])
        ax.set_xlabel(variable)
        ax.set_ylabel("log(PM2.5 + 1)")

    axes[-1].axis("off")
    fig.suptitle(
        "Unadjusted Relationships Between Weather and Daily PM2.5",
        fontsize=14,
        fontweight="bold",
        y=1.01,
    )
    fig.tight_layout()
    fig.savefig(FIGURES_DIR / "weather_pm25_relationships.png", bbox_inches="tight")
    plt.close(fig)


def plot_weather_coefficients(coefficients):
    weather_terms = list(WEATHER_LABELS)
    subset = coefficients[coefficients["term"].isin(weather_terms)].copy()
    model_order = ["M1_weather", "M2_adjusted", "M3_year_adjusted"]
    colors_by_model = ["#4C78A8", "#F58518", "#54A24B"]
    y_base = np.arange(len(weather_terms))
    offsets = [-0.22, 0.0, 0.22]

    fig, ax = plt.subplots(figsize=(9, 5.4))
    for model, color, offset in zip(model_order, colors_by_model, offsets):
        model_data = (
            subset[subset["model"] == model]
            .set_index("term")
            .loc[weather_terms]
        )
        estimates = model_data["estimate"].to_numpy()
        lower = model_data["hc3_ci_lower"].to_numpy()
        upper = model_data["hc3_ci_upper"].to_numpy()
        ax.errorbar(
            estimates,
            y_base + offset,
            xerr=np.vstack([estimates - lower, upper - estimates]),
            fmt="o",
            color=color,
            capsize=3,
            linewidth=1.6,
            label=MODEL_LABELS[model],
        )

    ax.axvline(0, color="#333333", linewidth=1, linestyle="--")
    ax.set_yticks(y_base)
    ax.set_yticklabels([WEATHER_LABELS[x] for x in weather_terms])
    ax.invert_yaxis()
    ax.set_xlabel("Coefficient for a one-SD increase (HC3 95% CI)")
    ax.set_title("Meteorological Coefficients Across Regression Models")
    ax.legend(loc="best")
    fig.tight_layout()
    fig.savefig(FIGURES_DIR / "regression_coefficient_plot.png")
    plt.close(fig)


def plot_model_diagnostics(model):
    fitted = model["fitted"]
    residuals = model["residuals"]
    standardized = model["standardized_residuals"]
    cooks = model["cooks_distance"]
    n = len(fitted)

    fig, axes = plt.subplots(2, 2, figsize=(11, 8.5))

    residual_panel = axes[0, 0]
    hb = residual_panel.hexbin(
        fitted, residuals, gridsize=55, mincnt=1, cmap="Blues", linewidths=0
    )
    residual_panel.axhline(0, color="#D1495B", linestyle="--", linewidth=1.5)
    residual_panel.set_title("Residuals vs Fitted")
    residual_panel.set_xlabel("Fitted log(PM2.5 + 1)")
    residual_panel.set_ylabel("Residual")
    fig.colorbar(hb, ax=residual_panel, label="Count")

    qq_panel = axes[0, 1]
    theoretical, ordered = stats.probplot(standardized, dist="norm", fit=False)
    qq_panel.scatter(theoretical, ordered, s=8, alpha=0.35, color="#4C78A8")
    limits = [min(theoretical.min(), ordered.min()), max(theoretical.max(), ordered.max())]
    qq_panel.plot(limits, limits, color="#D1495B", linestyle="--")
    qq_panel.set_title("Normal Q-Q Plot")
    qq_panel.set_xlabel("Theoretical quantiles")
    qq_panel.set_ylabel("Standardized residuals")

    hist_panel = axes[1, 0]
    sns.histplot(
        standardized,
        bins=60,
        stat="density",
        color="#4C78A8",
        alpha=0.65,
        ax=hist_panel,
    )
    grid = np.linspace(-4, 4, 300)
    hist_panel.plot(grid, stats.norm.pdf(grid), color="#D1495B", linewidth=2)
    hist_panel.set_title("Standardized Residual Distribution")
    hist_panel.set_xlabel("Standardized residual")

    cook_panel = axes[1, 1]
    cook_panel.scatter(np.arange(n), cooks, s=7, alpha=0.45, color="#4C78A8")
    cook_panel.axhline(4.0 / n, color="#D1495B", linestyle="--", label="4/n")
    cook_panel.set_yscale("log")
    cook_panel.set_title("Cook's Distance")
    cook_panel.set_xlabel("Observation index")
    cook_panel.set_ylabel("Cook's distance (log scale)")
    cook_panel.legend()

    fig.suptitle(
        "Diagnostics for Weather + Season + Station Model",
        fontsize=14,
        fontweight="bold",
        y=1.01,
    )
    fig.tight_layout()
    fig.savefig(FIGURES_DIR / "regression_diagnostics.png", bbox_inches="tight")
    plt.close(fig)


def plot_monthly_pollutant_trends(monthly_series):
    monthly_series = monthly_series.copy()
    monthly_series["date"] = pd.to_datetime(monthly_series["date"])
    pollutant_order = ["PM2.5", "PM10", "SO2", "NO2", "CO", "O3"]

    fig, axes = plt.subplots(3, 2, figsize=(12, 10), sharex=True)
    for ax, pollutant in zip(axes.ravel(), pollutant_order):
        subset = monthly_series[monthly_series["pollutant"] == pollutant]
        ax.plot(
            subset["date"],
            subset["monthly_mean"],
            color="#AAB2BD",
            linewidth=1.2,
            marker="o",
            markersize=2.8,
            label="Monthly mean",
        )
        ax.plot(
            subset["date"],
            subset["rolling_12_month_mean"],
            color="#1F5A85",
            linewidth=2.4,
            label="12-month rolling mean",
        )
        ax.set_title(pollutant)
        ax.set_ylabel("Concentration")

    axes[0, 0].legend(loc="best")
    fig.suptitle(
        "Monthly Air-Pollutant Concentrations in Beijing",
        fontsize=14,
        fontweight="bold",
        y=1.01,
    )
    fig.tight_layout()
    fig.savefig(FIGURES_DIR / "monthly_pollutant_trends.png", bbox_inches="tight")
    plt.close(fig)


def plot_temporal_trend_estimates(trend_results):
    pollutant_order = ["PM2.5", "PM10", "SO2", "NO2", "CO", "O3"]
    plot_data = trend_results.set_index("pollutant").loc[pollutant_order]
    estimates = plot_data["annual_percent_change"].to_numpy()
    lower = plot_data["annual_percent_ci_lower"].to_numpy()
    upper = plot_data["annual_percent_ci_upper"].to_numpy()
    significant = plot_data["significant_after_fdr"].astype(bool).to_numpy()
    colors = np.where(significant, "#1F5A85", "#9AA4AF")
    y = np.arange(len(plot_data))

    fig, ax = plt.subplots(figsize=(8, 4.8))
    for index in range(len(plot_data)):
        ax.errorbar(
            estimates[index],
            y[index],
            xerr=[[estimates[index] - lower[index]], [upper[index] - estimates[index]]],
            fmt="o",
            color=colors[index],
            capsize=4,
            linewidth=1.8,
        )
    ax.axvline(0, color="#333333", linestyle="--", linewidth=1)
    ax.set_yticks(y)
    ax.set_yticklabels(pollutant_order)
    ax.invert_yaxis()
    ax.set_xlabel("Estimated annual change (%) with Newey-West 95% CI")
    ax.set_title("Season-Adjusted Monthly Trends, March 2013 to February 2017")
    fig.text(
        0.98,
        0.015,
        "Blue: significant after FDR correction",
        ha="right",
        va="bottom",
        fontsize=9,
        color="#4F5964",
    )
    fig.tight_layout(rect=[0, 0.05, 1, 1])
    fig.savefig(FIGURES_DIR / "season_adjusted_trend_estimates.png")
    plt.close(fig)


def write_handoff_summary(
    correlations, coefficients, comparisons, diagnostics, vif, temporal_trends
):
    log_corr = correlations[
        (correlations["outcome"] == "log_pm25")
        & (correlations["method"] == "Spearman")
    ].copy()
    strongest = log_corr.loc[log_corr["coefficient"].abs().idxmax()]
    adjusted_weather = coefficients[
        (coefficients["model"] == "M2_adjusted")
        & (coefficients["term"].isin(WEATHER_LABELS))
    ].sort_values("estimate")
    model2 = comparisons.set_index("model").loc["M2_adjusted"]
    diagnostic = diagnostics.iloc[0]
    trend_lookup = temporal_trends.set_index("pollutant")

    lines = [
        "Statistical analysis summary",
        "============================",
        f"Analysis unit: station-day; n = {int(model2['n'])}",
        "Outcome: log(PM2.5 + 1)",
        "Weather variables are standardized; coefficients represent a one-SD increase.",
        "Reference categories: Spring, Aotizhongxin, and 2013 where applicable.",
        "",
        "Correlation",
        f"Strongest absolute Spearman association: {strongest['variable']} "
        f"(rho = {strongest['coefficient']:.3f}, "
        f"p {format_p_value(strongest['p_value'])}).",
        "",
        "Primary adjusted model (weather + season + station)",
        f"Adjusted R-squared = {model2['adjusted_r_squared']:.3f}; "
        f"RMSE = {model2['rmse']:.3f}.",
    ]
    for row in adjusted_weather.itertuples(index=False):
        lines.append(
            f"- {WEATHER_LABELS[row.term]}: beta = {row.estimate:.3f}, "
            f"HC3 95% CI [{row.hc3_ci_lower:.3f}, {row.hc3_ci_upper:.3f}], "
            f"p {format_p_value(row.hc3_p_value)}."
        )
    lines.extend(
        [
            "",
            "Diagnostics",
            f"Breusch-Pagan p {format_p_value(diagnostic['breusch_pagan_p_value'])}; "
            "HC3 robust standard errors are reported for inference.",
            f"Median station-specific Durbin-Watson = "
            f"{diagnostic['median_station_durbin_watson']:.3f}.",
            f"Maximum weather VIF = {vif['vif'].max():.2f}.",
            f"Influential observations above Cook 4/n threshold = "
            f"{int(diagnostic['observations_above_cook_threshold'])}.",
            "",
            "Season-adjusted monthly trends",
        ]
    )
    for pollutant in ["PM2.5", "PM10", "SO2", "NO2", "CO", "O3"]:
        row = trend_lookup.loc[pollutant]
        lines.append(
            f"- {pollutant}: {row['annual_percent_change']:.1f}% per year, "
            f"Newey-West 95% CI [{row['annual_percent_ci_lower']:.1f}%, "
            f"{row['annual_percent_ci_upper']:.1f}%], "
            f"FDR-adjusted p {format_p_value(row['fdr_adjusted_p_value'])}."
        )
    lines.extend(
        [
            "",
            "Interpretation boundary",
            "The results describe statistical associations, not causal effects. "
            "Temporal dependence, non-random station placement, and unmeasured factors "
            "remain limitations.",
        ]
    )
    (TABLES_DIR / "c_analysis_summary.txt").write_text(
        "\n".join(lines), encoding="utf-8"
    )


def main():
    configure_plot_style()
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    data, _ = add_standardized_weather(load_analysis_data())
    models = fit_all_models(data)
    primary_model = get_primary_model(models)

    correlations = read_required_table("meteorological_correlations.csv")
    coefficients = read_required_table("regression_coefficients.csv")
    comparisons = read_required_table("regression_model_comparison.csv")
    diagnostics = read_required_table("model_diagnostics.csv")
    vif = read_required_table("weather_vif.csv")
    monthly_series = read_required_table("monthly_pollutant_series.csv")
    temporal_trends = read_required_table("temporal_trend_results.csv")

    print("Creating publication-ready analysis figures...")
    plot_correlation_heatmap(correlations)
    plot_weather_relationships(data)
    plot_weather_coefficients(coefficients)
    plot_model_diagnostics(primary_model)
    plot_monthly_pollutant_trends(monthly_series)
    plot_temporal_trend_estimates(temporal_trends)
    write_handoff_summary(
        correlations,
        coefficients,
        comparisons,
        diagnostics,
        vif,
        temporal_trends,
    )
    print(f"Figures: {FIGURES_DIR}")


if __name__ == "__main__":
    main()
