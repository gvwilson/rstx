import numpy as np
import pytest
from generate_elasticity import make_elasticity_data, TRUE_ELASTICITY, TRUE_INTERCEPT
from elasticity import log_log_ols


def test_noise_free_slope_recovery():
    # With no noise, OLS must recover the true slope to near machine precision.
    # We use a generous relative tolerance of 1e-6 to allow for floating-point
    # arithmetic, which is far tighter than the noise-corrupted case (< 10%).
    prices = np.linspace(1.0, 20.0, 60)
    log_quantities = TRUE_INTERCEPT + TRUE_ELASTICITY * np.log(prices)
    quantities = np.exp(log_quantities)
    _, slope, _, _, _ = log_log_ols(prices, quantities)
    assert slope == pytest.approx(TRUE_ELASTICITY, rel=1e-6)


def test_noise_free_intercept_recovery():
    prices = np.linspace(1.0, 20.0, 60)
    log_quantities = TRUE_INTERCEPT + TRUE_ELASTICITY * np.log(prices)
    quantities = np.exp(log_quantities)
    intercept, _, _, _, _ = log_log_ols(prices, quantities)
    assert intercept == pytest.approx(TRUE_INTERCEPT, rel=1e-6)


def test_noisy_slope_within_ten_percent():
    # With Gaussian log-quantity noise (std=0.15) and 80 observations,
    # the OLS slope must land within 10% of the true value.
    # The theoretical SE of the slope is roughly noise_std / sqrt(SS_xx),
    # where SS_xx grows with n; 10% of |TRUE_ELASTICITY| = 0.15 gives
    # a safety factor of ~3 over the expected SE ≈ 0.04.
    df = make_elasticity_data()
    prices = df["price"].to_numpy()
    quantities = df["quantity"].to_numpy()
    _, slope, _, _, _ = log_log_ols(prices, quantities)
    assert abs(slope - TRUE_ELASTICITY) / abs(TRUE_ELASTICITY) < 0.10


def test_elasticity_is_negative():
    # Normal demand: higher price → lower quantity → negative slope in log-log space.
    df = make_elasticity_data()
    prices = df["price"].to_numpy()
    quantities = df["quantity"].to_numpy()
    _, slope, _, _, _ = log_log_ols(prices, quantities)
    assert slope < 0.0


def test_confidence_interval_contains_true_value():
    # The 95% CI should contain the true elasticity.
    # With a well-specified model and n=80 points this should virtually always hold;
    # it fails only in extreme noise draws that do not occur with seed 7493418.
    df = make_elasticity_data()
    prices = df["price"].to_numpy()
    quantities = df["quantity"].to_numpy()
    _, _, _, ci_low, ci_high = log_log_ols(prices, quantities)
    assert ci_low < TRUE_ELASTICITY < ci_high
