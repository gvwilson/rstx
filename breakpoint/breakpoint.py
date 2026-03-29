import numpy as np
import polars as pl
import altair as alt
from generate_breakpoint import make_breakpoint_data, BREAK_STEP


# [mccole] mean_residuals
def residuals_mean(values):
    """Residuals from a mean-only fit.

    Subtracts the sample mean from each observation.  Residuals sum to zero
    by construction.  Use this model when the series is expected to be
    stationary around a constant mean before and after the break.
    """
    return values - np.mean(values)
# [/mccole] mean_residuals


# [mccole] trend_residuals
def residuals_trend(values):
    """Residuals from a linear-trend fit.

    Fits y_t = a + b*t using np.polyfit, then returns e_t = y_t - (a + b*t).
    Removes any linear drift so the CUSUM responds only to departures from
    the fitted trend, such as a sudden mean shift.
    Use this model when the series is expected to have a linear trend in
    addition to a possible break.
    """
    t = np.arange(len(values), dtype=float)
    coeffs = np.polyfit(t, values, 1)
    return values - np.polyval(coeffs, t)
# [/mccole] trend_residuals


# mccole: cusum
def cusum(residuals):
    """Cumulative sum (CUSUM) of residuals.

    C_t = sum_{s=0}^{t} e_s  (0-indexed).

    A structural break shifts the expected sign of residuals, so C_t drifts
    away from zero before the break and then reverses afterwards.  The index
    of maximum |C_t| estimates the location of the break.
    """
    return np.cumsum(residuals)


def detect_break(cusum_values):
    """Return the index where |CUSUM| is largest.

    This index is the last step before the detected break: the series
    properties are estimated to shift at index detect_break(...) + 1.
    """
    return int(np.argmax(np.abs(cusum_values)))
# mccole: /cusum


# mccole: plot
def plot_series_with_break(values, detected_break, filename):
    """Save a time-series plot with a vertical rule at the detected break."""
    n = len(values)
    df = pl.DataFrame({"step": np.arange(n, dtype=float), "value": values})
    series = (
        alt.Chart(df)
        .mark_line(color="steelblue", strokeWidth=1.5)
        .encode(
            x=alt.X("step:Q", title="Step"),
            y=alt.Y("value:Q", title="Value"),
        )
    )
    break_df = pl.DataFrame({"step": [float(detected_break + 1)]})
    break_rule = (
        alt.Chart(break_df)
        .mark_rule(color="firebrick", strokeWidth=2, strokeDash=[6, 3])
        .encode(x="step:Q")
    )
    chart = alt.layer(series, break_rule).properties(
        width=450,
        height=250,
        title=f"Time series with detected break at step {detected_break + 1}",
    )
    chart.save(filename)


def plot_cusum_comparison(cusum_mean, cusum_trend, true_break, filename):
    """Save CUSUM trajectories for both OLS models on the same axes."""
    n = len(cusum_mean)
    steps = np.arange(n, dtype=float)
    df = pl.DataFrame(
        {
            "step": np.concatenate([steps, steps]),
            "cusum": np.concatenate([cusum_mean, cusum_trend]),
            "model": ["mean-only"] * n + ["linear trend"] * n,
        }
    )
    lines = (
        alt.Chart(df)
        .mark_line(strokeWidth=2)
        .encode(
            x=alt.X("step:Q", title="Step"),
            y=alt.Y("cusum:Q", title="CUSUM"),
            color=alt.Color("model:N", legend=alt.Legend(title="OLS model")),
        )
    )
    break_df = pl.DataFrame({"step": [float(true_break)]})
    break_rule = (
        alt.Chart(break_df)
        .mark_rule(color="gray", strokeDash=[4, 4], strokeWidth=1.5)
        .encode(x="step:Q")
    )
    chart = alt.layer(lines, break_rule).properties(
        width=450,
        height=300,
        title="CUSUM comparison: mean-only vs. linear-trend residuals",
    )
    chart.save(filename)
# mccole: /plot


if __name__ == "__main__":
    df = make_breakpoint_data()
    values = df["value"].to_numpy()

    res_mean = residuals_mean(values)
    res_trend = residuals_trend(values)
    cs_mean = cusum(res_mean)
    cs_trend = cusum(res_trend)
    break_mean = detect_break(cs_mean)
    break_trend = detect_break(cs_trend)

    print(f"True break at step:             {BREAK_STEP}")
    print(f"Detected (mean-only CUSUM):     {break_mean + 1}")
    print(f"Detected (linear-trend CUSUM):  {break_trend + 1}")

    plot_series_with_break(values, break_mean, "breakpoint-series.svg")
    print("Saved breakpoint-series.svg")
    plot_cusum_comparison(cs_mean, cs_trend, BREAK_STEP, "breakpoint-cusum.svg")
    print("Saved breakpoint-cusum.svg")
