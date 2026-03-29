import numpy as np
from diffusion import (
    DIFFUSIVITY,
    DT,
    DX,
    N_STEPS,
    PULSE_CENTER,
    PULSE_WIDTH,
    SNAPSHOT_INTERVAL,
    make_initial,
    step,
)


def test_stability_ratio():
    # The explicit scheme is stable only when r = D*dt/dx^2 <= 0.5.
    # This test catches accidental changes to DIFFUSIVITY, DT, or DX
    # that would break the simulation.
    r = DIFFUSIVITY * DT / DX**2
    assert r <= 0.5, f"stability ratio {r:.4f} exceeds 0.5"


def test_mass_conservation():
    # With zero-flux boundaries, the total amount of substance is conserved.
    # The ghost-cell implementation makes the correction term sum to zero in
    # exact arithmetic.  Floating-point rounding accumulates at roughly
    # N_STEPS * machine_epsilon, so a relative tolerance of 1e-10 is safe.
    _, c = make_initial()
    initial_mass = c.sum() * DX
    for _ in range(N_STEPS):
        c = step(c)
    final_mass = c.sum() * DX
    assert abs(final_mass - initial_mass) / initial_mass < 1e-10


def test_symmetry():
    # The Gaussian initial condition is symmetric about x = 0.5 and the
    # boundary conditions are identical at both ends, so the profile must
    # remain symmetric at every step.  Tolerance is 1e-12 (floating-point
    # symmetry of the arithmetic operations).
    _, c = make_initial()
    for _ in range(N_STEPS):
        c = step(c)
        assert np.max(np.abs(c - c[::-1])) < 1e-12


def test_peak_decreases():
    # As the pulse spreads out, its peak concentration must fall monotonically.
    _, c = make_initial()
    peaks = [c.max()]
    for i in range(1, N_STEPS + 1):
        c = step(c)
        if i % SNAPSHOT_INTERVAL == 0:
            peaks.append(c.max())
    assert all(peaks[i] > peaks[i + 1] for i in range(len(peaks) - 1))


def test_matches_analytical():
    # On an infinite domain a Gaussian pulse with standard deviation sigma_0
    # spreads so that sigma^2(t) = sigma_0^2 + 2*D*t (Crank 1975).  After
    # 20 steps the pulse tails are more than 4 sigma from each wall, so
    # boundary effects are negligible.
    # The scheme has truncation error O(DT + DX^2) ~ 2e-3 with our parameters.
    # The measured maximum error at n=20 is ~3e-3 (the prefactor exceeds 1).
    # A tolerance of 5e-3 gives a safety factor of ~1.7 over the measured error.
    n_check = 20
    x, c = make_initial()
    for _ in range(n_check):
        c = step(c)
    t = n_check * DT
    sigma2 = PULSE_WIDTH**2 + 2 * DIFFUSIVITY * t
    analytical = (PULSE_WIDTH / np.sqrt(sigma2)) * np.exp(
        -((x - PULSE_CENTER) ** 2) / (2 * sigma2)
    )
    assert np.max(np.abs(c - analytical)) < 5e-3
