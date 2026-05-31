import numpy as np
import polars as pl
import altair as alt
from generate_survival import make_survival_data, MEAN_SURVIVAL

# TRUE_RATE is the reciprocal of MEAN_SURVIVAL: lambda = 1/mu for an Exponential distribution.
TRUE_RATE = 1.0 / MEAN_SURVIVAL

# T_MAX_DAYS: upper limit for plotting the exponential curve, set to 3 mean lifetimes
# so the curve is visually close to zero by the right edge.
T_MAX_DAYS = 3 * MEAN_SURVIVAL


# mccole: naive-rate
def naive_rate(times, observed):
    """Estimate lambda using only uncensored observations."""
    uncensored = [t for t, o in zip(times, observed) if o]
    return 1.0 / (sum(uncensored) / len(uncensored))
# mccole: /naive-rate


# mccole: corrected-rate
def corrected_rate(times, observed):
    """MLE of lambda for exponential under censoring: d / sum(t)."""
    d = sum(observed)
    return d / sum(times)
# mccole: /corrected-rate


# mccole: empirical-curve
def empirical_survival(times, observed):
    """Empirical survival: fraction of uncensored events occurring after each time point."""
    event_times = sorted(t for t, o in zip(times, observed) if o)
    n = len(event_times)
    fractions = [(n - i) / n for i in range(n)]
    return event_times, fractions
# mccole: /empirical-curve


# mccole: plot
def plot_survival(times, observed, lam_naive, lam_corrected, filename):
    """Save a chart with the empirical survival curve and two exponential fits.

    The empirical curve shows the fraction of uncensored events that occurred
    after each event time.  The naive and corrected exponential curves are
    overlaid for comparison.
    """
    event_times, fractions = empirical_survival(times, observed)
    emp_df = pl.DataFrame({"t": event_times, "S": fractions})
    emp_line = (
        alt.Chart(emp_df)
        .mark_line(color="steelblue", strokeWidth=2, interpolate="step-after")
        .encode(
            x=alt.X("t:Q", title="Time (days)"),
            y=alt.Y("S:Q", title="Survival fraction", scale=alt.Scale(domain=[0, 1])),
        )
    )

    # Build smooth exponential curves over [0, T_MAX_DAYS].
    t_vals = np.linspace(0, T_MAX_DAYS, 300)
    exp_df = pl.DataFrame(
        {
            "t": np.concatenate([t_vals, t_vals]),
            "S": np.concatenate(
                [np.exp(-lam_naive * t_vals), np.exp(-lam_corrected * t_vals)]
            ),
            "model": ["naive"] * len(t_vals) + ["corrected"] * len(t_vals),
        }
    )
    exp_lines = (
        alt.Chart(exp_df)
        .mark_line(strokeDash=[4, 2], strokeWidth=1.5)
        .encode(
            x="t:Q",
            y="S:Q",
            color=alt.Color(
                "model:N",
                scale=alt.Scale(
                    domain=["naive", "corrected"],
                    range=["firebrick", "darkorange"],
                ),
            ),
        )
    )

    chart = alt.layer(emp_line, exp_lines).properties(
        width=500, height=250, title="Empirical survival curve with exponential fits"
    )
    chart.save(filename)
# mccole: /plot


if __name__ == "__main__":
    df = make_survival_data()
    times = df["time"].to_list()
    observed = df["observed"].to_list()
    lam_n = naive_rate(times, observed)
    lam_c = corrected_rate(times, observed)
    n_events = sum(observed)
    print(f"Events: {n_events} / {len(times)}, censored: {len(times) - n_events}")
    print(f"True rate: {TRUE_RATE:.4f}  (mean survival {MEAN_SURVIVAL:.1f} days)")
    print(f"Naive rate: {lam_n:.4f}  (mean {1/lam_n:.1f} days)")
    print(f"Corrected rate: {lam_c:.4f}  (mean {1/lam_c:.1f} days)")
    plot_survival(times, observed, lam_n, lam_c, "survival.svg")
    print("Saved survival.svg")
