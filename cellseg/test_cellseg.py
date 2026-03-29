import numpy as np
from generate_image import make_image, make_pure_noise, N_CELLS, IMAGE_SIZE
from cellseg import smooth, segment, cell_sizes, THRESHOLD


def test_smooth_reduces_noise():
    # Gaussian smoothing must reduce pixel-to-pixel variance.
    rng = np.random.default_rng(7)
    noise = rng.normal(0, 1, (64, 64))
    assert smooth(noise, sigma=2).var() < noise.var()


def test_smooth_preserves_shape():
    image = np.ones((IMAGE_SIZE, IMAGE_SIZE))
    assert smooth(image).shape == image.shape


def test_smooth_constant_unchanged():
    # Smoothing a uniform image must leave interior values unchanged.
    image = np.full((50, 50), 0.7)
    result = smooth(image, sigma=2)
    interior = result[4:-4, 4:-4]
    assert np.allclose(interior, 0.7, atol=1e-6)


def test_segment_finds_all_cells():
    # With default parameters the pipeline must recover all N_CELLS cells.
    image, centers = make_image()
    labeled, n_found = segment(smooth(image))
    assert n_found == N_CELLS, f"Expected {N_CELLS} cells, found {n_found}"


def test_cell_sizes_reasonable():
    # Every detected cell must have a pixel area in the physically plausible range.
    # At the operating threshold the analytic area is ≈ 148 px²; we allow 50–350 px²
    # to accommodate smoothing and noise effects without being unnecessarily tight.
    image, _ = make_image()
    labeled, _ = segment(smooth(image))
    sizes = cell_sizes(labeled)
    assert np.all(sizes >= 50), f"Cell too small: {sizes.min()} px"
    assert np.all(sizes <= 350), f"Cell too large: {sizes.max()} px"


def test_threshold_above_max_finds_nothing():
    # A threshold above the maximum smoothed value must produce zero cells.
    image, _ = make_image()
    labeled, n_found = segment(smooth(image), threshold=999.0)
    assert n_found == 0


def test_pure_noise_false_positives():
    # At a threshold of 0.05, pure noise produces false detections.
    # Smoothed noise std dev ≈ NOISE_SCALE / (2·sqrt(π)·SMOOTH_SIGMA) ≈ 0.021;
    # 0.05 ≈ 2.4σ, so roughly 0.8% of pixels exceed it, forming several blobs.
    noise = make_pure_noise()
    _, n_false = segment(smooth(noise), threshold=0.05)
    assert n_false > 0, "Expected false positives from pure noise at threshold 0.05"

    # At the operating threshold (0.50 ≈ 24σ) pure noise must not trigger any cell.
    _, n_safe = segment(smooth(noise), threshold=THRESHOLD)
    assert n_safe == 0, "Operating threshold should reject all noise blobs"
