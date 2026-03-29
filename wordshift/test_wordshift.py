import pytest
import polars as pl
from generate_wordshift import make_corpus, TARGET_WORDS, TARGET_SLOPE
from wordshift import normalize, linear_trend, compute_trends


def test_normalize_sums_to_one():
    # After normalization, frequencies within each decade must sum to 1.0.
    df = make_corpus()
    freq_df = normalize(df)
    decade_totals = freq_df.group_by("decade").agg(
        pl.col("freq").sum().alias("total_freq")
    )
    for total in decade_totals["total_freq"].to_list():
        assert total == pytest.approx(1.0, abs=1e-9)


def test_normalize_non_negative():
    # All normalized frequencies must be non-negative.
    df = make_corpus()
    freq_df = normalize(df)
    assert freq_df["freq"].min() >= 0.0


def test_linear_trend_flat():
    # A constant frequency sequence has slope exactly 0.
    indices = list(range(11))
    freqs = [0.015] * 11
    assert linear_trend(indices, freqs) == pytest.approx(0.0)


def test_linear_trend_known_slope():
    # A perfectly linear sequence has the exact injected slope.
    # slope = 0.002, starting at 0.005, over 11 decades.
    indices = list(range(11))
    freqs = [0.005 + 0.002 * i for i in indices]
    assert linear_trend(indices, freqs) == pytest.approx(0.002, abs=1e-12)


def test_linear_trend_single_point():
    # A single-point series has an undefined denominator; the function
    # must return 0.0 without raising an exception.
    assert linear_trend([0], [0.5]) == pytest.approx(0.0)


def test_slope_signs_correct():
    # telegraph must have a positive slope, candle a negative slope,
    # and steam a slope near zero.  Tolerance of 0.001 is 5x the
    # expected standard error given 5000 tokens per decade and 11 decades.
    df = make_corpus()
    freq_df = normalize(df)
    trends = compute_trends(freq_df, TARGET_WORDS)
    assert trends["telegraph"] > 0.0
    assert trends["candle"] < 0.0
    assert trends["steam"] == pytest.approx(0.0, abs=0.001)


def test_slope_magnitude():
    # The recovered slopes should be within 0.001 of the true injected values.
    # Standard error of the OLS slope is < 0.0002 for these parameters,
    # so 0.001 allows for more than 5 standard errors of sampling variation.
    df = make_corpus()
    freq_df = normalize(df)
    trends = compute_trends(freq_df, TARGET_WORDS)
    true_slopes = dict(zip(TARGET_WORDS, TARGET_SLOPE))
    for word in TARGET_WORDS:
        assert trends[word] == pytest.approx(true_slopes[word], abs=0.001), (
            f"{word}: expected slope {true_slopes[word]}, got {trends[word]:.5f}"
        )
