import numpy as np

SEED = 7493418

GRID_ROWS = 40
GRID_COLS = 60

# Trade route endpoints: top-left corner to bottom-right corner.
START = (0, 0)
END = (GRID_ROWS - 1, GRID_COLS - 1)


# mccole: terrain
def make_terrain(rows, cols, seed=SEED):
    """Return a (rows, cols) elevation array with values in [0, 1].

    The terrain is a superposition of sinusoidal waves at four octaves.
    Each octave has half the amplitude of the previous and twice the spatial
    frequency, producing a fractal-like surface.  Random per-octave phases
    are seeded for reproducibility.  The result is normalised so that the
    minimum elevation is 0 and the maximum is 1; valleys appear dark and
    ridges appear bright.
    """
    rng = np.random.default_rng(seed)
    x = np.linspace(0.0, 2.0 * np.pi, cols)
    y = np.linspace(0.0, 2.0 * np.pi, rows)
    X, Y = np.meshgrid(x, y)
    elev = np.zeros((rows, cols))
    for k in range(1, 5):
        amp = 1.0 / k
        px = rng.uniform(0.0, 2.0 * np.pi)
        py = rng.uniform(0.0, 2.0 * np.pi)
        elev += amp * np.sin(k * X + px) * np.cos(k * Y + py)
    lo, hi = elev.min(), elev.max()
    return (elev - lo) / (hi - lo)
# mccole: /terrain


if __name__ == "__main__":
    elev = make_terrain(GRID_ROWS, GRID_COLS)
    print(f"Terrain shape: {elev.shape}")
    print(f"Elevation range: [{elev.min():.4f}, {elev.max():.4f}]")
    print(f"Mean elevation: {elev.mean():.4f}")
