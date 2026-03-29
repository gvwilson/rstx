import numpy as np

# mccole: constants
SEED = 7493418  # RNG seed
PERIOD = 10.0  # orbital period (days)
AMPLITUDE = 50.0  # radial-velocity semi-amplitude (m/s)
PHASE = 0.3  # initial orbital phase (radians)
V_SYSTEMIC = 0.0  # centre-of-mass (systemic) velocity (m/s)
NOISE_SCALE = 10.0  # per-observation measurement noise (m/s); 20% of AMPLITUDE
N_POINTS = 50  # number of observations
T_MAX = 30.0  # time baseline (days); spans 3 complete periods
# mccole: /constants


# mccole: make-rv
def make_rv_data(
    period=PERIOD,
    amplitude=AMPLITUDE,
    phase=PHASE,
    v_sys=V_SYSTEMIC,
    noise_scale=NOISE_SCALE,
    n_points=N_POINTS,
    t_max=T_MAX,
    seed=SEED,
):
    """Return (t, rv) for a star hosting one planet.

    Observation times are drawn uniformly at random over [0, t_max] to
    simulate realistic (unevenly spaced) survey data.  Radial velocity is:

        v(t) = amplitude * sin(2π t / period + phase) + v_sys + ε

    where ε ~ N(0, noise_scale²).
    """
    rng = np.random.default_rng(seed)
    t = np.sort(rng.uniform(0.0, t_max, n_points))
    signal = amplitude * np.sin(2 * np.pi * t / period + phase) + v_sys
    rv = signal + rng.normal(0.0, noise_scale, n_points)
    return t, rv
# mccole: /make-rv


# mccole: make-noise-rv
def make_pure_noise_rv(
    noise_scale=NOISE_SCALE, n_points=N_POINTS, t_max=T_MAX, seed=SEED
):
    """Return (t, rv) containing only measurement noise, no planetary signal."""
    rng = np.random.default_rng(seed)
    t = np.sort(rng.uniform(0.0, t_max, n_points))
    rv = rng.normal(0.0, noise_scale, n_points)
    return t, rv
# mccole: /make-noise-rv


if __name__ == "__main__":
    t, rv = make_rv_data()
    print(f"Points: {len(t)}, time span: {t[-1]:.2f} days")
    print(f"RV range: [{rv.min():.1f}, {rv.max():.1f}] m/s")
