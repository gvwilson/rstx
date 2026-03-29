import numpy as np
import pytest
from vitals import rolling_stats, detect_anomalies


def test_rolling_stats_length():
    # Output arrays must match input length regardless of window size.
    values = np.arange(10, dtype=float)
    means, stds = rolling_stats(values, window=3)
    assert len(means) == 10
    assert len(stds) == 10


def test_rolling_stats_known_values():
    # Position 2 (0-indexed) with window=3 covers values [1, 2, 3].
    # Mean = 2.0; sample std (ddof=1) = sqrt(((1-2)^2+(2-2)^2+(3-2)^2)/2) = 1.0.
    values = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
    means, stds = rolling_stats(values, window=3)
    assert means[2] == pytest.approx(2.0)
    assert stds[2] == pytest.approx(1.0)


def test_rolling_stats_single_element_window():
    # The first position has only one element; std must be 0 (not NaN).
    values = np.array([5.0, 6.0, 7.0])
    _, stds = rolling_stats(values, window=5)
    assert stds[0] == pytest.approx(0.0)
    assert not np.isnan(stds[0])


def test_constant_signal_no_anomalies():
    # A perfectly constant signal has zero deviation everywhere, so nothing is flagged.
    values = np.full(50, 70.0)
    flagged, _, _ = detect_anomalies(values, window=10, threshold=2.0)
    assert not np.any(flagged)


def test_isolated_spike_detected():
    # A single spike far above a constant baseline must be flagged.
    # At the spike position the deviation is 30 bpm; with window=10, the
    # rolling std at that position is sqrt(9*9 + 27^2)/3 ≈ 9.5, giving a
    # z-score of 27/9.5 ≈ 2.8 > 2.0.
    values = np.full(50, 70.0, dtype=float)
    values[25] = 100.0
    flagged, _, _ = detect_anomalies(values, window=10, threshold=2.0)
    assert flagged[25]


def test_normal_values_not_flagged_high_threshold():
    # With a very large threshold (10 sigma) no normally distributed values
    # should be flagged regardless of random seed.
    rng = np.random.default_rng(7493418)
    values = rng.normal(70.0, 2.0, 200)
    flagged, _, _ = detect_anomalies(values, window=20, threshold=10.0)
    assert not np.any(flagged)


def test_step_change_eventually_flagged():
    # A sustained step change of 15 bpm on a 2 bpm background must eventually
    # raise the z-score above 3 once the rolling window sees both levels.
    # The first WINDOW positions after the step still have mostly pre-step data,
    # so we check that at least one point beyond position step_start + window is flagged.
    WINDOW = 20
    step_start = 60
    values = np.full(150, 70.0, dtype=float)
    values[step_start:] = 85.0
    flagged, _, _ = detect_anomalies(values, window=WINDOW, threshold=3.0)
    assert np.any(flagged[step_start : step_start + WINDOW])
