import numpy as np

SEED = 7493418  # RNG seed

# mccole: constants
MZ_MIN = 100.0  # lower end of m/z range (daltons)
MZ_MAX = 600.0  # upper end of m/z range (daltons)
N_POINTS = 500  # number of evenly-spaced m/z values

# Each peak is (center_mz, height, sigma): three compounds at known masses.
# Heights are relative to the tallest peak (1.0).
PEAKS = [
    (150.0, 1.00, 2.0),  # compound A
    (280.0, 0.65, 1.5),  # compound B
    (390.0, 0.85, 2.5),  # compound C
    (510.0, 0.45, 2.0),  # compound D
]

DEFAULT_NOISE = 0.05  # Gaussian noise std dev relative to tallest peak
# mccole: /constants


# mccole: make-spectrum
def make_spectrum(
    peaks=PEAKS,
    noise_scale=DEFAULT_NOISE,
    n_points=N_POINTS,
    mz_min=MZ_MIN,
    mz_max=MZ_MAX,
    seed=SEED,
):
    """Return (mz, intensity) for a synthetic mass spectrum.

    The signal is a sum of Gaussian peaks, each defined by a
    (center_mz, height, sigma) triple.  Independent Gaussian noise
    with standard deviation `noise_scale` is added at every point.
    Negative intensities are clipped to zero.
    """
    rng = np.random.default_rng(seed)
    mz = np.linspace(mz_min, mz_max, n_points)
    intensity = np.zeros(n_points)
    for center, height, sigma in peaks:
        intensity += height * np.exp(-0.5 * ((mz - center) / sigma) ** 2)
    intensity += rng.normal(0.0, noise_scale, n_points)
    intensity = np.maximum(intensity, 0.0)
    return mz, intensity
# mccole: /make-spectrum


# mccole: make-noise
def make_pure_noise(
    noise_scale=DEFAULT_NOISE,
    n_points=N_POINTS,
    mz_min=MZ_MIN,
    mz_max=MZ_MAX,
    seed=SEED,
):
    """Return (mz, intensity) containing only Gaussian noise, no signal peaks.

    This is used to demonstrate the false-positive behaviour of the
    peak detector when the threshold is set too low.
    """
    rng = np.random.default_rng(seed)
    mz = np.linspace(mz_min, mz_max, n_points)
    intensity = np.maximum(rng.normal(0.0, noise_scale, n_points), 0.0)
    return mz, intensity
# mccole: /make-noise


if __name__ == "__main__":
    mz, intensity = make_spectrum()
    print(f"m/z range: {mz[0]:.1f} – {mz[-1]:.1f}")
    print(f"Max intensity: {intensity.max():.4f} at m/z {mz[intensity.argmax()]:.1f}")
