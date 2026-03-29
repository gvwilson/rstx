import pytest
from generate_survival import make_survival_data
from survival import naive_rate, corrected_rate, empirical_survival


def test_naive_rate_is_reciprocal_of_uncensored_mean():
    # Only the two uncensored times (2.0 and 4.0) contribute; mean = 3.0, rate = 1/3.
    times = [2.0, 4.0, 10.0]
    observed = [1, 1, 0]
    assert naive_rate(times, observed) == pytest.approx(1.0 / 3.0)


def test_corrected_rate_is_events_over_total_time():
    # d = 2, sum(t) = 2.0 + 4.0 + 10.0 = 16.0, rate = 2/16 = 0.125.
    times = [2.0, 4.0, 10.0]
    observed = [1, 1, 0]
    assert corrected_rate(times, observed) == pytest.approx(2.0 / 16.0)


def test_naive_rate_exceeds_corrected_when_censored():
    # Censored patients survived longer than average; dropping them inflates the naive rate.
    # With any dataset that has at least one censored observation, naive > corrected.
    df = make_survival_data()
    times = df["time"].to_list()
    observed = df["observed"].to_list()
    assert naive_rate(times, observed) > corrected_rate(times, observed)


def test_empirical_survival_fractions_non_increasing_and_bounded():
    df = make_survival_data()
    times = df["time"].to_list()
    observed = df["observed"].to_list()
    _, fractions = empirical_survival(times, observed)
    # All fractions must be in [0, 1].
    assert all(0.0 <= f <= 1.0 for f in fractions)
    # Fractions must be non-increasing.
    for a, b in zip(fractions, fractions[1:]):
        assert a >= b


def test_corrected_equals_naive_when_no_censoring():
    # When every observation is an event, d/sum(t) == 1/mean(t) == naive_rate.
    times = [1.0, 2.0, 3.0, 4.0]
    observed = [1, 1, 1, 1]
    assert naive_rate(times, observed) == pytest.approx(corrected_rate(times, observed))
