import numpy as np

# mccole: constants
SEED = 7493418  # RNG seed
IMAGE_SIZE = 128  # pixels per side; kept small for fast tests
N_CELLS = 8  # number of cells to place
CELL_SIGMA = 6  # Gaussian half-width of each cell (pixels)
CELL_BRIGHTNESS = 1.0  # peak intensity (image values are in [0, 1])
NOISE_SCALE = 0.15  # std dev of additive Gaussian noise

# Minimum centre-to-centre separation that keeps midpoint intensity below the
# operating threshold of 0.5.  For two Gaussians of amplitude A and sigma σ
# separated by distance d, the midpoint value is 2A·exp(−d²/(8σ²)).
# Setting this below 0.5 gives d > 2σ·sqrt(2·ln(4A)) = 2·6·sqrt(2·ln(4)) ≈ 19.8.
# We use 24 pixels for a comfortable margin.
MIN_SEPARATION = 24
# mccole: /constants


def _place_cells(n_cells, image_size, min_sep, rng, max_attempts=10_000):
    """Return a list of (cx, cy) centres with pairwise distance ≥ min_sep."""
    margin = CELL_SIGMA * 2 + 2  # keep cells away from image edges
    centers = []
    attempts = 0
    while len(centers) < n_cells and attempts < max_attempts:
        cx = int(rng.integers(margin, image_size - margin))
        cy = int(rng.integers(margin, image_size - margin))
        if all(np.hypot(cx - ox, cy - oy) >= min_sep for ox, oy in centers):
            centers.append((cx, cy))
        attempts += 1
    if len(centers) < n_cells:
        raise RuntimeError(
            f"Could only place {len(centers)} of {n_cells} cells "
            f"after {max_attempts} attempts; try a larger image or smaller n_cells."
        )
    return centers


# mccole: make-image
def make_image(
    n_cells=N_CELLS,
    sigma=CELL_SIGMA,
    brightness=CELL_BRIGHTNESS,
    noise_scale=NOISE_SCALE,
    image_size=IMAGE_SIZE,
    seed=SEED,
):
    """Return (image, centers) for a synthetic fluorescence image.

    Each cell is a 2-D Gaussian with peak `brightness` and width `sigma`.
    Independent Gaussian noise with std dev `noise_scale` is added to every
    pixel.  Pixel values are clipped to [0, 1].  `centers` is a list of
    (x, y) pixel coordinates of the true cell centres.
    """
    rng = np.random.default_rng(seed)
    centers = _place_cells(n_cells, image_size, MIN_SEPARATION, rng)

    ys, xs = np.mgrid[0:image_size, 0:image_size]
    image = np.zeros((image_size, image_size))
    for cx, cy in centers:
        image += brightness * np.exp(
            -0.5 * ((xs - cx) ** 2 + (ys - cy) ** 2) / sigma**2
        )
    image += rng.normal(0.0, noise_scale, image.shape)
    image = np.clip(image, 0.0, None)  # negative counts are unphysical
    return image, centers
# mccole: /make-image


# mccole: make-noise
def make_pure_noise(noise_scale=NOISE_SCALE, image_size=IMAGE_SIZE, seed=SEED):
    """Return an image containing only Gaussian noise, no cell signal.

    Used to demonstrate the false-positive behaviour of the segmentation
    pipeline when the threshold is set below the noise floor.
    """
    rng = np.random.default_rng(seed)
    return np.maximum(rng.normal(0.0, noise_scale, (image_size, image_size)), 0.0)
# mccole: /make-noise


if __name__ == "__main__":
    img, centers = make_image()
    print(f"Image shape: {img.shape}, dtype: {img.dtype}")
    print(f"Pixel range: [{img.min():.3f}, {img.max():.3f}]")
    print(f"Cell centres: {centers}")
