import numpy as np
import polars as pl
import altair as alt
from generate_vitals import make_vitals_data, STEP_START, SPIKE_POSITIONS


# mccole: rolling
def rolling_stats(values, window):
    """Compute trailing rolling mean and standard deviation.

    For position i the window covers indices [max(0, i - window + 1), i].
    The first window - 1 positions use a shorter window as data accumulates.
    Standard deviation uses ddof=1 (sample std); positions with only one
    value in the window return std = 0.
    """
    n = len(values)
    means = np.empty(n)
    stds = np.empty(n)
    for i in range(n):
        start = max(0, i - window + 1)
        segment = values[start : i + 1]
        means[i] = np.mean(segment)
        stds[i] = np.std(segment, ddof=1) if len(segment) > 1 else 0.0
    return means, stds
# mccole: /rolling


# mccole: detect
def detect_anomalies(values, window, threshold):
    """Flag time points where the value deviates from the rolling mean by more than
    threshold standard deviations.

    Returns (flagged, means, stds) where flagged is a boolean array.
    A position is flagged when |value - rolling_mean| > threshold * rolling_std.
    Positions with rolling_std = 0 are never flagged (no variation to compare against).
    """
    means, stds = rolling_stats(values, window)
    deviations = np.abs(values - means)
    flagged = deviations > threshold * stds
    return flagged, means, stds
# mccole: /detect


# mccole: plot
def plot_vitals(times, values, means, flagged, filename):
    """Save an Altair figure with the time series, rolling mean, and flagged anomalies."""
    df = pl.DataFrame({"time": times, "heart_rate": values, "rolling_mean": means})
    flag_df = pl.DataFrame({"time": times[flagged], "heart_rate": values[flagged]})

    raw_line = (
        alt.Chart(df)
        .mark_line(color="steelblue", strokeWidth=1, opacity=0.7)
        .encode(
            x=alt.X("time:Q", title="Time (minutes)"),
            y=alt.Y("heart_rate:Q", title="Heart rate (bpm)"),
        )
    )
    mean_line = (
        alt.Chart(df)
        .mark_line(color="darkorange", strokeWidth=2)
        .encode(x="time:Q", y="rolling_mean:Q")
    )
    anomaly_pts = (
        alt.Chart(flag_df)
        .mark_point(color="firebrick", size=60, shape="triangle-up")
        .encode(x="time:Q", y="heart_rate:Q")
    )

    chart = alt.layer(raw_line, mean_line, anomaly_pts).properties(
        width=550, height=250, title="Anomaly detection in patient vital signs"
    )
    chart.save(filename)
# mccole: /plot


# Rolling window width and z-score threshold for anomaly detection.
WINDOW = 20  # number of minutes in the trailing window
THRESHOLD = 3.0  # flag readings more than 3 rolling standard deviations from the mean


if __name__ == "__main__":
    df = make_vitals_data()
    times = df["time"].to_numpy()
    values = df["heart_rate"].to_numpy()
    flagged, means, stds = detect_anomalies(values, WINDOW, THRESHOLD)
    n_flagged = int(flagged.sum())
    print(f"Flagged {n_flagged} anomalies out of {len(values)} readings")
    step_flagged = flagged[STEP_START]
    spike_flagged = [flagged[p] for p in SPIKE_POSITIONS]
    print(f"Step change at {STEP_START} flagged: {step_flagged}")
    print(f"Spikes at {SPIKE_POSITIONS} flagged: {spike_flagged}")
    plot_vitals(times, values, means, flagged, "vitals.svg")
    print("Saved vitals.svg")
