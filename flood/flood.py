import numpy as np
import polars as pl
import altair as alt
from scipy.stats import norm
from generate_flood import generate

# mccole: constants
# Return periods of interest (years).  A T-year flood has probability
# 1/T of being exceeded in any given year.
RETURN_PERIODS = [2, 5, 10, 25, 50, 100, 200]
# mccole: /constants


# mccole: fit-lognormal
def fit_lognormal(flows):
    """Estimate log-normal parameters by the method of moments.

    For a log-normal distribution, ln(X) ~ Normal(mu_y, sigma_y).
    The method-of-moments estimates are simply the sample mean and
    sample standard deviation of the log-transformed flows.
    """
    log_flows = np.log(flows)
    mu_y = float(np.mean(log_flows))
    sigma_y = float(np.std(log_flows, ddof=1))
    return mu_y, sigma_y
# mccole: /fit-lognormal


# mccole: return-level
def return_level(mu_y, sigma_y, T):
    """Return the flood magnitude exceeded on average once every T years.

    The T-year return level is the quantile at non-exceedance probability
    p = 1 - 1/T.  For the log-normal distribution:
      x_T = exp(mu_y + z_p * sigma_y)
    where z_p = norm.ppf(p) is the standard normal quantile at probability p.
    """
    p = 1.0 - 1.0 / T
    z_p = norm.ppf(p)
    return np.exp(mu_y + z_p * sigma_y)
# mccole: /return-level


# mccole: plotting-positions
def plotting_positions(flows):
    """Return (normal_quantiles, sorted_log_flows) for a normal probability plot.

    Ranks observations from smallest to largest and assigns Weibull
    plotting positions p_i = i / (n + 1).  The theoretical normal quantile
    z_i = norm.ppf(p_i) linearises the log-normal CDF: if ln(X) is normally
    distributed, plotting (z_i, ln(x_(i))) gives a straight line.
    """
    n = len(flows)
    sorted_log_flows = np.log(np.sort(flows))
    ranks = np.arange(1, n + 1)
    p = ranks / (n + 1.0)
    z = norm.ppf(p)
    return z, sorted_log_flows
# mccole: /plotting-positions


# mccole: plot
def plot(flows, mu_y, sigma_y):
    """Return an Altair normal probability plot (Q-Q plot) for log-flows.

    Points are the empirical log-flows plotted against their theoretical
    normal quantiles.  The line is the fitted log-normal distribution.
    If the data are log-normally distributed, the points should scatter
    around a straight line.
    """
    z_obs, log_obs = plotting_positions(flows)
    z_fit = np.linspace(z_obs.min() - 0.5, z_obs.max() + 0.5, 200)
    log_fit = mu_y + sigma_y * z_fit  # log-normal quantile: ln x = mu_y + sigma_y * z

    df_pts = pl.DataFrame({"z": z_obs, "log_flow": log_obs})
    df_line = pl.DataFrame({"z": z_fit, "log_flow": log_fit})

    points = (
        alt.Chart(df_pts)
        .mark_point()
        .encode(
            x=alt.X("z:Q", title="Standard normal quantile z"),
            y=alt.Y("log_flow:Q", title="ln(annual maximum flow)"),
        )
    )
    line = (
        alt.Chart(df_line)
        .mark_line(color="firebrick")
        .encode(
            x=alt.X("z:Q"),
            y=alt.Y("log_flow:Q"),
        )
    )
    return (points + line).properties(
        width=400, height=300, title="Normal probability plot of log-flows"
    )
# mccole: /plot


if __name__ == "__main__":
    df = generate()
    flows = df["annual_max_flow"].to_numpy()
    mu_y, sigma_y = fit_lognormal(flows)
    print(f"Fitted:  mu_y = {mu_y:.3f},  sigma_y = {sigma_y:.3f}")
    for T in RETURN_PERIODS:
        x = return_level(mu_y, sigma_y, T)
        print(f"  {T:4d}-year return level: {x:.1f} m^3/s")
    chart = plot(flows, mu_y, sigma_y)
    chart.save("flood.svg")
    print("Saved flood.svg")
