import numpy as np
import polars as pl
import altair as alt
from scipy.optimize import curve_fit
from generate_rv import (
    make_rv_data,
    make_pure_noise_rv,
    PERIOD,
    AMPLITUDE,
    PHASE,
    T_MAX,
)


# mccole: model
def model_rv(t, amplitude, period, phase, v_sys):
    """Sinusoidal radial-velocity model for a single planet.

    v(t) = amplitude * sin(2π t / period + phase) + v_sys
    """
    return amplitude * np.sin(2 * np.pi * t / period + phase) + v_sys
# mccole: /model


# mccole: fit
def fit_sinusoid(t, rv):
    """Fit model_rv to the data and return (params, errors).

    params = [amplitude, period, phase, v_sys]
    errors = one-standard-deviation uncertainties from the covariance matrix

    Initial guesses:
      amplitude ← std(rv) * sqrt(2)   (std of a sinusoid = K / sqrt(2))
      period    ← time span / 3       (assumes ≈3 cycles are visible)
      phase     ← 0
      v_sys     ← mean(rv)

    Bounds keep amplitude positive and period within [0.5 day, full baseline].
    """
    amp_guess = np.std(rv) * np.sqrt(2)
    period_guess = (t[-1] - t[0]) / 3.0
    p0 = [amp_guess, period_guess, 0.0, np.mean(rv)]
    bounds = (
        [0.0, 0.5, -np.pi, -np.inf],
        [np.inf, t[-1] - t[0], np.pi, np.inf],
    )
    popt, pcov = curve_fit(model_rv, t, rv, p0=p0, bounds=bounds, max_nfev=10_000)
    perr = np.sqrt(np.diag(pcov))
    return popt, perr
# mccole: /fit


# mccole: plot
def plot_fit(t, rv, popt, filename, t_true=None, rv_true=None):
    """Save an Altair figure with data, fitted curve, and (optionally) the true signal.

    Blue points: observations.
    Red line: best-fit sinusoid.
    Grey dashed line: true underlying signal (when t_true and rv_true are supplied).
    """
    t_dense = np.linspace(t[0], t[-1], 400)
    rv_fit = model_rv(t_dense, *popt)

    data_df = pl.DataFrame({"t": t, "rv": rv})
    fit_df = pl.DataFrame({"t": t_dense, "rv": rv_fit})

    scatter = (
        alt.Chart(data_df)
        .mark_point(color="steelblue", opacity=0.8, size=40)
        .encode(
            x=alt.X("t:Q", title="Time (days)"),
            y=alt.Y("rv:Q", title="Radial velocity (m/s)"),
        )
    )
    fit_line = (
        alt.Chart(fit_df)
        .mark_line(color="firebrick", strokeWidth=2)
        .encode(x="t:Q", y="rv:Q")
    )
    layers = [scatter, fit_line]

    if t_true is not None and rv_true is not None:
        true_df = pl.DataFrame({"t": t_true, "rv": rv_true})
        true_line = (
            alt.Chart(true_df)
            .mark_line(color="grey", strokeWidth=1.5, strokeDash=[6, 3])
            .encode(x="t:Q", y="rv:Q")
        )
        layers.append(true_line)

    chart = alt.layer(*layers).properties(width=500, height=250)
    chart.save(filename)
# mccole: /plot


if __name__ == "__main__":
    t, rv = make_rv_data()
    popt, perr = fit_sinusoid(t, rv)
    amp, period, phase, v_sys = popt
    amp_err, period_err, _, _ = perr
    print(f"Fitted amplitude: {amp:.2f} ± {amp_err:.2f} m/s  (true: {AMPLITUDE})")
    print(f"Fitted period:    {period:.3f} ± {period_err:.3f} days  (true: {PERIOD})")

    t_dense = np.linspace(0, T_MAX, 400)
    rv_true = model_rv(t_dense, AMPLITUDE, PERIOD, PHASE, 0.0)
    plot_fit(t, rv, popt, "radvel.svg", t_dense, rv_true)
    print("Saved radvel.svg")

    # Pure-noise demonstration.
    t_n, rv_n = make_pure_noise_rv()
    popt_n, perr_n = fit_sinusoid(t_n, rv_n)
    amp_n, amp_err_n = popt_n[0], perr_n[0]
    print(
        f"\nNoise-only fit: amplitude {amp_n:.2f} ± {amp_err_n:.2f} m/s  "
        f"(fractional uncertainty {amp_err_n / amp_n:.2f})"
    )
    plot_fit(t_n, rv_n, popt_n, "radvel_noise.svg")
    print("Saved radvel_noise.svg")
