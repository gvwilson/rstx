import numpy as np
from scipy.signal import find_peaks
from lotka import (
    PRED_EQ,
    PERIOD_APPROX,
    PREY_EQ,
    solve,
)


def test_populations_positive():
    # The Lotka-Volterra equations conserve the positive quadrant: if x > 0
    # and y > 0 initially, both remain positive for all t > 0.  A negative
    # value would mean a population went extinct, which this model cannot
    # produce analytically; it would indicate a numerical error.
    df = solve()
    assert (df["prey"] > 0).all()
    assert (df["predator"] > 0).all()



def test_volterra_principle():
    # Volterra's averaging principle: the time mean of x(t) over any integer
    # number of complete cycles equals x* = PRED_DEATH/PRED_GROWTH, and
    # similarly for y(t).  T_MAX covers ~10 complete cycles, so the fractional-
    # cycle bias is small.  The measured errors are < 0.2%; a tolerance of
    # 1% (relative) gives a 5x safety margin.
    df = solve()
    x_mean = df["prey"].mean()
    y_mean = df["predator"].mean()
    assert abs(x_mean - PREY_EQ) / PREY_EQ < 0.01
    assert abs(y_mean - PRED_EQ) / PRED_EQ < 0.01


def test_period():
    # The small-oscillation period (linearisation around equilibrium) is
    # 2π / sqrt(PREY_BIRTH * PRED_DEATH).  For finite-amplitude oscillations
    # the true period differs by O(amplitude²).  With our initial conditions
    # the measured period is ~5.30 vs the linearised estimate of ~5.13, a
    # 3.3% difference.  A tolerance of 10% gives a 3x safety margin.
    df = solve()
    peaks, _ = find_peaks(df["prey"].to_numpy())
    t_peaks = df["t"].to_numpy()[peaks]
    assert len(t_peaks) >= 3, "too few peaks detected to estimate period"
    measured_period = np.diff(t_peaks).mean()
    assert abs(measured_period - PERIOD_APPROX) / PERIOD_APPROX < 0.10
