import numpy as np
import pytest
from generate_rv import make_rv_data, make_pure_noise_rv, PERIOD, AMPLITUDE
from radvel import model_rv, fit_sinusoid


def test_model_known_values():
    # At t=0 with phase=0, the model reduces to v_sys; at t=P/4 to amplitude + v_sys.
    assert model_rv(np.array([0.0]), 50.0, 10.0, 0.0, 5.0)[0] == pytest.approx(5.0)
    assert model_rv(np.array([2.5]), 50.0, 10.0, 0.0, 0.0)[0] == pytest.approx(50.0)


def test_model_periodicity():
    # Adding one full period to t must return the same value.
    t = np.array([3.7])
    v1 = model_rv(t, 50.0, 10.0, 0.3, 0.0)
    v2 = model_rv(t + 10.0, 50.0, 10.0, 0.3, 0.0)
    assert np.allclose(v1, v2)


def test_fit_noise_free_period():
    # With no noise, the fitted period must match the true period to machine precision.
    t, rv = make_rv_data(noise_scale=0.0)
    popt, _ = fit_sinusoid(t, rv)
    assert abs(popt[1] - PERIOD) < 1e-6


def test_fit_noise_free_amplitude():
    # With no noise, the fitted amplitude must match the true amplitude to machine precision.
    t, rv = make_rv_data(noise_scale=0.0)
    popt, _ = fit_sinusoid(t, rv)
    assert abs(popt[0] - AMPLITUDE) < 1e-6


def test_fit_recovers_period_with_noise():
    # With realistic noise (NOISE_SCALE / AMPLITUDE = 0.20) the fitted period must
    # fall within 5% of the true value.
    # The Cramér-Rao bound for period uncertainty with 50 points and SNR=5 is
    # roughly 0.2 days; 5% of PERIOD = 0.5 days is a 2.5× safety factor.
    t, rv = make_rv_data()
    popt, _ = fit_sinusoid(t, rv)
    assert abs(popt[1] - PERIOD) / PERIOD < 0.05


def test_fit_recovers_amplitude_with_noise():
    # The fitted amplitude must fall within 15% of the true value.
    # Measured fractional error is ~4%; 15% gives a safety factor of ~3.5.
    t, rv = make_rv_data()
    popt, _ = fit_sinusoid(t, rv)
    assert abs(popt[0] - AMPLITUDE) / AMPLITUDE < 0.15


def test_pure_noise_large_uncertainty():
    # Fitting a sinusoid to pure noise must yield a fractional amplitude uncertainty
    # greater than 0.5 — the fitted amplitude is not statistically significant.
    t, rv = make_pure_noise_rv()
    popt, perr = fit_sinusoid(t, rv)
    amplitude, amp_err = popt[0], perr[0]
    assert amp_err / amplitude > 0.5, (
        f"Expected fractional uncertainty > 0.5 for noise-only data; "
        f"got {amp_err / amplitude:.2f}"
    )
