"""Run every statistical analysis stage in its required order."""

from correlation_analysis import main as run_correlation
from model_diagnostics import main as run_diagnostics
from regression_analysis import main as run_regression
from temporal_trend_analysis import main as run_temporal_trends
from analysis_visualization import main as run_visualization


def main():
    print("[1/5] Correlation analysis")
    run_correlation()
    print("[2/5] Regression analysis")
    run_regression()
    print("[3/5] Model diagnostics")
    run_diagnostics()
    print("[4/5] Monthly temporal trend analysis")
    run_temporal_trends()
    print("[5/5] Visualization and handoff summary")
    run_visualization()
    print("All statistical analysis stages completed.")


if __name__ == "__main__":
    main()
