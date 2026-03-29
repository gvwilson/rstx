import numpy as np
from scipy.integrate import solve_ivp
from generate_sir import BETA_TRUE, GAMMA_TRUE, I0, N_POP, T_MAX
from sir import fit, model_cases, sir_rhs


def test_population_conserved():
    # dS/dt + dI/dt + dR/dt = 0 is an algebraic identity for the SIR equations,
    # so S + I + R = N for all t.  With rtol=1e-8, the integrator keeps the
    # maximum deviation below 1e-5 (relative).  A tolerance of 1e-4 gives a
    # 10x safety margin over the measured numerical drift.
    t_eval = np.linspace(0.0, float(T_MAX), 1000)
    sol = solve_ivp(
        sir_rhs,
        [0.0, float(T_MAX)],
        [float(N_POP - I0), float(I0), 0.0],
        args=(BETA_TRUE, GAMMA_TRUE, N_POP),
        t_eval=t_eval,
        rtol=1e-8,
        atol=1e-10,
    )
    total = sol.y[0] + sol.y[1] + sol.y[2]
    assert np.max(np.abs(total - N_POP)) / N_POP < 1e-4


def test_no_transmission():
    # When beta = 0 no new infections occur: S stays constant and I decays
    # exponentially.  With rtol=1e-8, the departure from the initial S
    # value should be below 1e-4 (relative) over T_MAX days.
    t_eval = np.array([0.0, float(T_MAX)])
    sol = solve_ivp(
        sir_rhs,
        [0.0, float(T_MAX)],
        [float(N_POP - I0), float(I0), 0.0],
        args=(0.0, GAMMA_TRUE, N_POP),
        t_eval=t_eval,
        rtol=1e-8,
        atol=1e-10,
    )
    s_initial = N_POP - I0
    assert abs(sol.y[0, -1] - s_initial) / N_POP < 1e-4


def test_single_epidemic_peak():
    # For R0 = BETA_TRUE / GAMMA_TRUE = 3 > 1, the epidemic curve has exactly
    # one maximum.  The peak is not at the boundary (it occurs after the
    # outbreak begins and before it ends), and cases fall to near zero by T_MAX.
    cases = model_cases(BETA_TRUE, GAMMA_TRUE)
    peak_idx = int(np.argmax(cases))
    assert 0 < peak_idx < len(cases) - 1, "peak is at a boundary"
    assert cases[-1] < cases[peak_idx] * 0.01, "epidemic has not ended by T_MAX"


def test_fit_recovers_parameters():
    # Fitting to noiseless model output should recover beta and gamma to within
    # 1%.  Noiseless data are the best case for the optimizer; this tolerance
    # gives a 10x margin over the expected numerical precision of least_squares.
    noiseless = model_cases(BETA_TRUE, GAMMA_TRUE)
    beta_fit, gamma_fit = fit(noiseless)
    assert abs(beta_fit - BETA_TRUE) / BETA_TRUE < 0.01
    assert abs(gamma_fit - GAMMA_TRUE) / GAMMA_TRUE < 0.01
