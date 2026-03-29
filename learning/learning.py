import numpy as np
import altair as alt
from scipy.optimize import curve_fit

from generate_learning import make_trials, TRUE_B

# Multiplier to convert a standard error into a 95% confidence interval half-width.
# 1.96 comes from the standard normal: P(-1.96 < Z < 1.96) = 0.95.  curve_fit
# returns asymptotic standard errors, so this gives an approximate 95% CI.
CI_Z = 1.96


def power_law(n, a, b):
    """Power-law learning curve: RT = a * n^(-b)."""
    return a * n ** (-b)


# mccole: fit
def fit_power_law(trials, rt):
    """Fit a power-law learning curve to per-trial reaction-time data.

    Parameters
    ----------
    trials : array-like of trial numbers (1, 2, ..., N)
    rt     : array-like of reaction times in milliseconds

    Returns
    -------
    a    : fitted amplitude (predicted RT on trial 1, in ms)
    b    : fitted learning rate exponent (larger means faster improvement)
    b_ci : (lower, upper) 95% confidence interval for b

    scipy.optimize.curve_fit minimises the sum of squared residuals and returns
    the estimated parameter covariance matrix.  The standard error of b is the
    square root of the [1, 1] diagonal entry (its variance); multiplying by
    CI_Z = 1.96 gives the half-width of the approximate 95% CI.
    """
    trials = np.asarray(trials, dtype=float)
    rt = np.asarray(rt, dtype=float)
    p0 = [rt[0], 0.2]
    popt, pcov = curve_fit(power_law, trials, rt, p0=p0, maxfev=5000)
    a, b = popt
    se_b = float(np.sqrt(pcov[1, 1]))
    b_ci = (b - CI_Z * se_b, b + CI_Z * se_b)
    return float(a), float(b), b_ci
# mccole: /fit


# mccole: plot
def plot_fit(trials, rt, a, b, b_ci, filename):
    """Save a scatter plot of raw data with the fitted power-law curve overlaid."""
    trials = np.asarray(trials, dtype=float)
    rt = np.asarray(rt, dtype=float)
    curve_n = np.arange(1, int(trials.max()) + 1, dtype=float)
    curve_rt = power_law(curve_n, a, b)

    raw = (
        alt.Chart(
            alt.Data(
                values=[{"trial": int(t), "rt": float(r)} for t, r in zip(trials, rt)]
            )
        )
        .mark_point(color="steelblue", opacity=0.6)
        .encode(
            x=alt.X("trial:Q", title="Trial number"),
            y=alt.Y("rt:Q", title="Reaction time (ms)"),
        )
    )

    fitted = (
        alt.Chart(
            alt.Data(
                values=[
                    {"trial": float(t), "rt": float(r)}
                    for t, r in zip(curve_n, curve_rt)
                ]
            )
        )
        .mark_line(color="firebrick", strokeWidth=2)
        .encode(
            x="trial:Q",
            y="rt:Q",
        )
    )

    chart = (raw + fitted).properties(
        title=(f"Power-law fit: b = {b:.3f}  (95% CI [{b_ci[0]:.3f}, {b_ci[1]:.3f}])"),
        width=480,
        height=300,
    )
    chart.save(filename)
# mccole: /plot


if __name__ == "__main__":
    df = make_trials()
    trials = df["trial"].to_numpy()
    rt = df["rt"].to_numpy()
    a, b, b_ci = fit_power_law(trials, rt)
    print(f"Fitted A: {a:.2f} ms")
    print(f"Fitted b: {b:.4f}  (true b = {TRUE_B:.4f})")
    print(f"95% CI for b: [{b_ci[0]:.4f}, {b_ci[1]:.4f}]")
    plot_fit(trials, rt, a, b, b_ci, "learning-curve.svg")
    print("Saved learning-curve.svg")
