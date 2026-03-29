import numpy as np
import polars as pl

SEED = 7493418

# Grid dimensions for the "true" temperature field used as the reference surface.
GRID_ROWS = 40
GRID_COLS = 40

# Number of weather stations placed at random within the [0, 1] x [0, 1] domain.
N_STATIONS = 30

# Spatial frequencies for the synthetic temperature field.
# T(x, y) = sin(X_FREQ * pi * x) * cos(Y_FREQ * pi * y) produces smooth
# ridges and troughs that resemble a real regional temperature gradient while
# remaining easy to evaluate exactly at any (x, y).
X_FREQ = 3.0
Y_FREQ = 2.0


def true_field(x, y):
    """Return the synthetic temperature at coordinates (x, y) in [0, 1]^2."""
    return np.sin(X_FREQ * np.pi * x) * np.cos(Y_FREQ * np.pi * y)


# mccole: generate
def make_stations(n_stations=N_STATIONS, seed=SEED):
    """Return a Polars DataFrame of synthetic weather station observations.

    Columns:
        x     -- easting in [0, 1]
        y     -- northing in [0, 1]
        value -- observed temperature (sampled exactly from the true field)

    Stations are placed uniformly at random within the unit square.  Their
    values are taken from the smooth true field without added noise so that
    the interpolation error can be computed precisely by comparing to the
    known reference surface.
    """
    rng = np.random.default_rng(seed)
    xs = rng.uniform(0.0, 1.0, n_stations)
    ys = rng.uniform(0.0, 1.0, n_stations)
    values = true_field(xs, ys)
    return pl.DataFrame({"x": xs.tolist(), "y": ys.tolist(), "value": values.tolist()})
# mccole: /generate


def make_true_grid(rows=GRID_ROWS, cols=GRID_COLS):
    """Return the true temperature field as a (rows, cols) numpy array.

    Grid point (i, j) maps to coordinates (j / (cols-1), i / (rows-1)),
    so the grid spans [0, 1]^2 with row 0 at y=0 and column 0 at x=0.
    """
    x = np.linspace(0.0, 1.0, cols)
    y = np.linspace(0.0, 1.0, rows)
    X, Y = np.meshgrid(x, y)
    return true_field(X, Y)


if __name__ == "__main__":
    df = make_stations()
    print(f"Stations: {df.height}")
    print(f"Value range: [{df['value'].min():.4f}, {df['value'].max():.4f}]")
    field = make_true_grid()
    print(f"True field shape: {field.shape}")
    print(f"True field range: [{field.min():.4f}, {field.max():.4f}]")
