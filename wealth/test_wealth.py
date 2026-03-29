import numpy as np
import pytest
from wealth import gini, simulate_exchange, N_AGENTS


def test_gini_equal_distribution():
    # With identical wealth for every agent the Gini must be exactly 0.
    # Analytically: (2 * n(n+1)/2 - (n+1)*n) / n^2 = 0 for any n.
    assert gini(np.ones(50)) == pytest.approx(0.0, abs=1e-12)


def test_gini_perfect_inequality():
    # One agent holds all wealth; Gini = (n-1)/n.
    # With n=10: G = 9/10 = 0.9 exactly.
    n = 10
    w = np.zeros(n)
    w[-1] = float(n)
    assert gini(w) == pytest.approx((n - 1) / n, rel=1e-9)


def test_gini_bounded_during_simulation():
    # Wealth is always non-negative and total wealth is conserved, so the
    # Gini coefficient must stay in [0, 1] at every step.
    _, gini_history = simulate_exchange()
    assert np.all(gini_history >= 0.0)
    assert np.all(gini_history <= 1.0)


def test_total_wealth_conserved():
    # Every exchange transfers wealth without creation or destruction, so
    # the sum must equal n_agents (each agent starts with 1.0) to within
    # floating-point rounding.
    final_wealth, _ = simulate_exchange()
    assert np.sum(final_wealth) == pytest.approx(N_AGENTS, rel=1e-9)


def test_gini_rises_from_zero():
    # The model starts from perfect equality (Gini = 0) and should
    # produce substantial inequality after 2000 exchanges.
    # The theoretical steady-state Gini for exponential wealth distributions
    # is 0.5; after 2000 steps the simulated value reliably exceeds 0.3.
    _, gini_history = simulate_exchange()
    assert gini_history[0] == pytest.approx(0.0, abs=1e-12)
    assert gini_history[-1] > 0.3
