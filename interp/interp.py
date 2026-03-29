import numpy as np
import matplotlib.pyplot as plt

from generate_interp import make_stations, make_true_grid, GRID_ROWS, GRID_COLS

# IDW power parameter: the exponent applied to inverse distances.
# p = 2 is the standard choice in environmental science; smaller values
# produce smoother surfaces, while larger values approach nearest-neighbour
# interpolation.
IDW_POWER = 2.0

# Small offset added to every distance to prevent division by zero when a
# query point coincides exactly with a station.  1e-10 is small enough that
# the co-located station's weight is roughly 10^20 times any other station's,
# so the estimate is essentially exact at the station location.
EPSILON = 1e-10


# mccole: idw
def idw(station_xy, station_values, query_xy, power=IDW_POWER):
    """Interpolate values at query points using inverse-distance weighting.

    Parameters
    ----------
    station_xy     : (n, 2) float array of station (x, y) coordinates
    station_values : (n,) float array of observed values at each station
    query_xy       : (m, 2) float array of query point coordinates
    power          : IDW exponent; larger values give more weight to nearby
                     stations relative to distant ones

    Returns
    -------
    estimates : (m,) float array of interpolated values at each query point

    Each estimate is the weighted average sum(w_i * z_i) / sum(w_i) where
    w_i = d_i^(-power) and d_i is the Euclidean distance from the query
    point to station i.  Broadcasting computes all (m, n) distances at once.
    """
    diff = query_xy[:, np.newaxis, :] - station_xy[np.newaxis, :, :]
    dists = np.sqrt((diff**2).sum(axis=2)) + EPSILON
    weights = dists ** (-power)
    return (weights * station_values).sum(axis=1) / weights.sum(axis=1)
# mccole: /idw


# mccole: grid
def interpolate_grid(station_xy, station_values, rows, cols, power=IDW_POWER):
    """Return an IDW-interpolated field on a regular (rows x cols) grid.

    Grid point (i, j) maps to coordinates (j / (cols-1), i / (rows-1)),
    matching the coordinate system of make_true_grid in the generator.
    """
    x = np.linspace(0.0, 1.0, cols)
    y = np.linspace(0.0, 1.0, rows)
    X, Y = np.meshgrid(x, y)
    query_xy = np.column_stack([X.ravel(), Y.ravel()])
    estimates = idw(station_xy, station_values, query_xy, power)
    return estimates.reshape(rows, cols)
# mccole: /grid


# mccole: plot
def plot_comparison(true_field, idw_field, station_xy, filename):
    """Save a side-by-side comparison of the true and interpolated fields."""
    vmin = min(true_field.min(), idw_field.min())
    vmax = max(true_field.max(), idw_field.max())

    fig, axes = plt.subplots(1, 2, figsize=(10, 4), constrained_layout=True)
    for ax, field, title in zip(
        axes,
        [true_field, idw_field],
        ["True field", "IDW interpolation"],
    ):
        im = ax.imshow(
            field, origin="lower", vmin=vmin, vmax=vmax, cmap="RdBu_r", aspect="equal"
        )
        ax.set_title(title)
        ax.set_xlabel("x")
        ax.set_ylabel("y")

    axes[1].scatter(
        station_xy[:, 0] * (idw_field.shape[1] - 1),
        station_xy[:, 1] * (idw_field.shape[0] - 1),
        c="black",
        s=15,
        marker="x",
        label="Stations",
    )
    axes[1].legend(loc="upper right", fontsize=8)
    fig.colorbar(im, ax=axes, label="Temperature (normalised)", shrink=0.8)
    fig.savefig(filename)
    plt.close(fig)
# mccole: /plot


if __name__ == "__main__":
    df = make_stations()
    station_xy = df.select(["x", "y"]).to_numpy()
    station_values = df["value"].to_numpy()

    true_fld = make_true_grid(GRID_ROWS, GRID_COLS)
    idw_fld = interpolate_grid(station_xy, station_values, GRID_ROWS, GRID_COLS)

    mae = abs(true_fld - idw_fld).mean()
    print(f"Mean absolute error vs. true field: {mae:.4f}")
    plot_comparison(true_fld, idw_fld, station_xy, "interp-fields.svg")
    print("Saved interp-fields.svg")
