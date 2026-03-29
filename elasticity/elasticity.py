import numpy as np
import polars as pl
import altair as alt
from scipy.stats import t as t_dist
from generate_elasticity import make_elasticity_data, TRUE_ELASTICITY, TRUE_INTERCEPT


# mccole: ols
def log_log_ols(prices, quantities):
    """Fit log(quantity) = intercept + slope * log(price) by ordinary least squares.

    OLS formulas:
        slope     = sum[(x_i - x_mean)(y_i - y_mean)] / sum[(x_i - x_mean)^2]
        intercept = y_mean - slope * x_mean
        SE(slope) = sqrt(RSS / (n - 2)) / sqrt(sum[(x_i - x_mean)^2])

    The 95% confidence interval uses the t-distribution with n - 2 degrees of freedom.
    A large SE relative to the slope indicates a poorly constrained estimate.

    Returns (intercept, slope, se_slope, ci_low, ci_high).
    """
    x = np.log(prices)
    y = np.log(quantities)
    n = len(x)
    x_mean = np.mean(x)
    y_mean = np.mean(y)
    ss_xx = np.sum((x - x_mean) ** 2)
    ss_xy = np.sum((x - x_mean) * (y - y_mean))
    slope = ss_xy / ss_xx
    intercept = y_mean - slope * x_mean
    residuals = y - (intercept + slope * x)
    rss = np.sum(residuals**2)
    # Residual standard error: sqrt(RSS / (n - 2))
    se_slope = np.sqrt(rss / (n - 2) / ss_xx)
    t_crit = t_dist.ppf(0.975, df=n - 2)
    ci_low = slope - t_crit * se_slope
    ci_high = slope + t_crit * se_slope
    return intercept, slope, se_slope, ci_low, ci_high
# mccole: /ols


# mccole: plot
def plot_loglog(prices, quantities, intercept, slope, filename):
    """Save a log-log scatter plot with the fitted OLS line.

    Both axes are on a log scale.  The fitted curve is the power-law:
        quantity = exp(intercept) * price^slope
    shown as a straight line in log-log space.
    """
    df = pl.DataFrame({"price": prices, "quantity": quantities})
    scatter = (
        alt.Chart(df)
        .mark_point(color="steelblue", opacity=0.7, size=40)
        .encode(
            x=alt.X(
                "price:Q", scale=alt.Scale(type="log"), title="Price ($, log scale)"
            ),
            y=alt.Y(
                "quantity:Q", scale=alt.Scale(type="log"), title="Quantity (log scale)"
            ),
        )
    )

    p_range = np.linspace(prices.min(), prices.max(), 200)
    q_fit = np.exp(intercept) * p_range**slope
    fit_df = pl.DataFrame({"price": p_range, "quantity": q_fit})
    fit_line = (
        alt.Chart(fit_df)
        .mark_line(color="firebrick", strokeWidth=2)
        .encode(x="price:Q", y="quantity:Q")
    )

    chart = alt.layer(scatter, fit_line).properties(
        width=450, height=300, title="Log-log demand curve with OLS fit"
    )
    chart.save(filename)
# mccole: /plot


if __name__ == "__main__":
    df = make_elasticity_data()
    prices = df["price"].to_numpy()
    quantities = df["quantity"].to_numpy()
    intercept, slope, se, ci_low, ci_high = log_log_ols(prices, quantities)
    print(f"Estimated elasticity: {slope:.3f}  (true: {TRUE_ELASTICITY})")
    print(f"Standard error:       {se:.3f}")
    print(f"95% CI:               [{ci_low:.3f}, {ci_high:.3f}]")
    print(f"Estimated intercept:  {intercept:.3f}  (true: {TRUE_INTERCEPT})")
    plot_loglog(prices, quantities, intercept, slope, "elasticity.svg")
    print("Saved elasticity.svg")
