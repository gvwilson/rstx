import numpy as np
from generate_spectrum import make_spectrum, make_pure_noise, PEAKS, DEFAULT_NOISE
from massspec import smooth, detect_peaks, SMOOTH_WINDOW, THRESHOLD


def test_smooth_constant():
    # Smoothing a constant signal must return the same constant everywhere.
    intensity = np.full(50, 3.7)
    result = smooth(intensity, window=5)
    # Edges are zero-padded by convolve mode='same'; only test the interior.
    interior = result[SMOOTH_WINDOW // 2 : -(SMOOTH_WINDOW // 2)]
    assert np.allclose(interior, 3.7)


def test_smooth_reduces_variance():
    # Smoothing must reduce point-to-point variance.
    rng = np.random.default_rng(0)
    noise = rng.normal(0, 1, 200)
    assert smooth(noise, window=7).var() < noise.var()


def test_smooth_preserves_length():
    intensity = np.ones(123)
    assert len(smooth(intensity, window=5)) == 123


def test_detect_known_peaks():
    # The detector must find all four compound peaks within 5 Da of their true centers.
    # Tolerance of 5 Da is well above the grid spacing (1 Da) and well below
    # the separation between any two peaks (> 100 Da).
    mz, raw = make_spectrum()
    detected = detect_peaks(mz, smooth(raw))
    true_centers = np.array([p[0] for p in PEAKS])
    assert len(detected) == len(true_centers), (
        f"Expected {len(true_centers)} peaks, got {len(detected)}"
    )
    for center, found in zip(true_centers, detected):
        assert abs(found - center) <= 5.0, (
            f"Peak at {center} Da detected at {found:.1f} Da (> 5 Da error)"
        )


def test_no_peaks_below_threshold():
    # A threshold above all intensities must return no peaks.
    mz, raw = make_spectrum()
    detected = detect_peaks(mz, smooth(raw), threshold=999.0)
    assert len(detected) == 0


def test_min_distance_suppresses_duplicates():
    # Use a 101-point grid (1 Da per index) so index distance equals Da distance.
    # Peaks at 50 and 60 Da are 10 indices apart and have distinct local maxima.
    # min_distance=12 merges them to the taller one; min_distance=5 keeps both.
    mz = np.linspace(0, 100, 101)
    intensity = np.exp(-0.5 * ((mz - 50) / 2.0) ** 2) + 0.9 * np.exp(
        -0.5 * ((mz - 60) / 2.0) ** 2
    )
    one = detect_peaks(mz, intensity, threshold=0.1, min_distance=12)
    two = detect_peaks(mz, intensity, threshold=0.1, min_distance=5)
    assert len(one) == 1
    assert len(two) == 2


def test_pure_noise_produces_false_positives():
    # Running the detector on pure noise with a threshold close to the noise
    # floor must produce false positives, demonstrating that threshold choice
    # matters.  The smoothed-noise std dev is DEFAULT_NOISE / sqrt(SMOOTH_WINDOW)
    # ≈ 0.022.  A threshold of 0.04 (~1.8 sigma) should yield several false peaks.
    mz, raw = make_pure_noise(noise_scale=DEFAULT_NOISE)
    smoothed = smooth(raw)
    low_threshold = 0.04
    false_peaks = detect_peaks(mz, smoothed, threshold=low_threshold)
    assert len(false_peaks) > 0, (
        "Expected false positives from pure noise at a low threshold"
    )
    # And at the normal threshold, noise alone must not trigger any peaks.
    assert len(detect_peaks(mz, smoothed, threshold=THRESHOLD)) == 0, (
        "Normal threshold should reject all noise peaks"
    )
