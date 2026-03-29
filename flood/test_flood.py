import numpy as np
from scipy.stats import norm
from generate_flood import TRUE_MU_LOG, TRUE_SIGMA_LOG, generate
from flood import (
    fit_lognormal,
    plotting_positions,
    return_level,
)

# Large sample size used for parameter recovery tests.  With N = 10 000 the
# standard error of the sample mean of log-flows is roughly sigma_y / sqrt(N)
# ~ 0.4 / 100 = 0.004, so a 5% relative tolerance gives a safety factor of ~50.
N_LARGE = 10_000


def test_fit_lognormal_large_sample():
    # Draw a large log-normal sample and verify that the method-of-moments
    # estimates are close to the true parameters.
    rng = np.random.default_rng(7493418)
    log_flows = rng.normal(loc=TRUE_MU_LOG, scale=TRUE_SIGMA_LOG, size=N_LARGE)
    flows = np.exp(log_flows)
    mu_y_hat, sigma_y_hat = fit_lognormal(flows)
    assert abs(mu_y_hat - TRUE_MU_LOG) / TRUE_MU_LOG < 0.05
    assert abs(sigma_y_hat - TRUE_SIGMA_LOG) / TRUE_SIGMA_LOG < 0.05


def test_return_levels_increase_with_period():
    # A T-year flood is rarer and more extreme than a shorter-period flood,
    # so return levels must be strictly increasing in T.  The log-normal quantile
    # x_T = exp(mu_y + z_p * sigma_y) is strictly increasing in T because
    # sigma_y > 0 and norm.ppf(1 - 1/T) is strictly increasing in T.
    flows = generate()["annual_max_flow"].to_numpy()
    mu_y, sigma_y = fit_lognormal(flows)
    levels = [return_level(mu_y, sigma_y, T) for T in [2, 10, 50, 100, 500]]
    assert all(levels[i] < levels[i + 1] for i in range(len(levels) - 1))


def test_return_level_probability():
    # By construction, x_T satisfies F(x_T) = 1 - 1/T under the log-normal CDF.
    # This is an algebraic identity; the residual should be below 1e-10.
    mu_y, sigma_y = 4.8, 0.4
    T = 100
    x_T = return_level(mu_y, sigma_y, T)
    # Log-normal CDF: F(x) = norm.cdf((ln(x) - mu_y) / sigma_y)
    p_fitted = norm.cdf((np.log(x_T) - mu_y) / sigma_y)
    assert abs(p_fitted - (1.0 - 1.0 / T)) < 1e-10


def test_plotting_positions_valid():
    # Weibull positions i/(n+1) lie in (0, 1), so the normal quantiles are
    # always finite.  Sorted log-flows must be non-decreasing.
    flows = generate()["annual_max_flow"].to_numpy()
    z, log_q = plotting_positions(flows)
    assert np.isfinite(z).all(), "normal quantiles contain infinite values"
    assert (np.diff(log_q) >= 0).all(), "log-flows are not sorted ascending"
