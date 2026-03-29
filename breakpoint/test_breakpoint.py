import numpy as np
import pytest
from generate_breakpoint import make_breakpoint_data, BREAK_STEP, N_STEPS
from breakpoint import residuals_mean, residuals_trend, cusum, detect_break


def test_cusum_all_zero_residuals():
    # The CUSUM of a zero-residual sequence is identically zero.
    assert np.all(cusum(np.zeros(50)) == 0.0)


def test_cusum_matches_cumsum():
    # By definition CUSUM must equal numpy's cumsum on the same array.
    residuals = np.array([1.0, -2.0, 3.0, -0.5, 0.5])
    np.testing.assert_array_equal(cusum(residuals), np.cumsum(residuals))


def test_mean_residuals_sum_to_zero():
    # OLS residuals from a mean-only fit sum to zero because the least-squares
    # intercept equals the sample mean, centering the residuals exactly.
    df = make_breakpoint_data()
    values = df["value"].to_numpy()
    assert np.sum(residuals_mean(values)) == pytest.approx(0.0, abs=1e-10)


def test_trend_residuals_sum_to_zero():
    # OLS with an intercept always centers the residuals, so they also sum to
    # zero for the linear-trend fit.
    df = make_breakpoint_data()
    values = df["value"].to_numpy()
    assert np.sum(residuals_trend(values)) == pytest.approx(0.0, abs=1e-10)


def test_detect_break_clean_signal():
    # With no noise the CUSUM of mean-only residuals reaches its maximum
    # absolute value at index BREAK_STEP - 1 (the last step before the break),
    # because the cumulative deficit reaches its deepest point exactly there.
    values = np.concatenate(
        [
            np.zeros(BREAK_STEP),
            3.0 * np.ones(N_STEPS - BREAK_STEP),
        ]
    )
    detected = detect_break(cusum(residuals_mean(values)))
    assert detected == BREAK_STEP - 1


def test_detect_break_noisy_within_ten_steps():
    # With seed 7493418 and a signal-to-noise ratio of 3 (mean shift 3.0,
    # noise std 1.0), the detected break must be within 10 steps of the
    # true break.  detect_break returns the last index before the break,
    # so the estimated break location is detected + 1.
    df = make_breakpoint_data()
    values = df["value"].to_numpy()
    detected = detect_break(cusum(residuals_mean(values)))
    assert abs((detected + 1) - BREAK_STEP) <= 10
