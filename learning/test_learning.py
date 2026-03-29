import numpy as np
from generate_learning import make_trials, N_TRIALS, TRUE_B
from learning import fit_power_law, power_law


def test_trial_count():
    # Generator must produce exactly N_TRIALS rows.
    df = make_trials()
    assert df.height == N_TRIALS


def test_all_rt_positive():
    # All reaction times must be positive; values below 1 ms are clamped.
    df = make_trials()
    assert (df["rt"] > 0).all()


def test_trial_numbers():
    # Trial numbers must run from 1 to N_TRIALS without gaps.
    df = make_trials()
    assert df["trial"].to_list() == list(range(1, N_TRIALS + 1))


def test_fitted_exponent_close_to_true():
    # With 80 trials and noise SD = 20 ms the fitted exponent should recover
    # TRUE_B to within 0.10.  The signal range is about 210 ms (500 to 290 ms
    # over 80 trials) while the noise SD is 20 ms, giving moderate SNR; with
    # 80 data points curve_fit converges well within 0.10 of the true value.
    df = make_trials()
    _, b, _ = fit_power_law(df["trial"].to_numpy(), df["rt"].to_numpy())
    assert abs(b - TRUE_B) < 0.10


def test_ci_brackets_true_exponent():
    # The 95% confidence interval returned by fit_power_law must contain TRUE_B.
    df = make_trials()
    _, _, b_ci = fit_power_law(df["trial"].to_numpy(), df["rt"].to_numpy())
    assert b_ci[0] <= TRUE_B <= b_ci[1]


def test_predicted_rt_decreasing():
    # The fitted curve must be strictly decreasing: performance always improves
    # with more practice when b > 0 and a > 0.
    df = make_trials()
    a, b, _ = fit_power_law(df["trial"].to_numpy(), df["rt"].to_numpy())
    predicted = power_law(np.arange(1, 21, dtype=float), a, b)
    assert all(predicted[i] > predicted[i + 1] for i in range(len(predicted) - 1))
