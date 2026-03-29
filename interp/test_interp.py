import numpy as np
import pytest
from generate_interp import (
    make_stations,
    N_STATIONS,
    GRID_ROWS,
    GRID_COLS,
)
from interp import idw, interpolate_grid


def test_station_count():
    # Generator must produce exactly N_STATIONS rows.
    df = make_stations()
    assert df.height == N_STATIONS


def test_exact_recovery_at_station():
    # IDW evaluated at a station's coordinates must return approximately
    # that station's value.  EPSILON shifts the distance slightly above
    # zero, giving the co-located station a weight of (EPSILON)^{-2} ≈ 10^{20}
    # relative to any other station; the estimate is therefore exact to
    # within about 1e-4 for 30 stations spanning a field of amplitude 1.
    df = make_stations()
    station_xy = df.select(["x", "y"]).to_numpy()
    station_values = df["value"].to_numpy()
    query = station_xy[[0], :]
    result = idw(station_xy, station_values, query)
    assert result[0] == pytest.approx(station_values[0], abs=1e-4)


def test_grid_shape():
    # interpolate_grid must return an array of the requested shape.
    df = make_stations()
    station_xy = df.select(["x", "y"]).to_numpy()
    station_values = df["value"].to_numpy()
    grid = interpolate_grid(station_xy, station_values, 10, 15)
    assert grid.shape == (10, 15)


def test_interpolated_values_in_range():
    # IDW is a convex combination: all estimates must lie within the observed
    # range of station values.
    df = make_stations()
    station_xy = df.select(["x", "y"]).to_numpy()
    station_values = df["value"].to_numpy()
    grid = interpolate_grid(station_xy, station_values, GRID_ROWS, GRID_COLS)
    assert grid.min() >= station_values.min() - 1e-9
    assert grid.max() <= station_values.max() + 1e-9


def test_weights_decrease_with_distance():
    # A query point closer to station A than station B must produce an estimate
    # closer to A's value than to B's, because A's inverse-distance weight is
    # larger.
    stations = np.array([[0.0, 0.0], [1.0, 0.0]])
    values = np.array([1.0, 0.0])
    query = np.array([[0.2, 0.0]])  # 0.2 from A, 0.8 from B
    result = idw(stations, values, query)
    assert result[0] > 0.5


def test_cross_validation_mae():
    # Leave-one-out cross-validation: remove each station in turn, interpolate
    # its value from the remaining 29, and average the absolute errors.
    # Tolerance 0.3 is justified by the field amplitude of 1.0 and the
    # density of 30 stations on a smooth sinusoidal field: LOO error should
    # be well below 30% of the amplitude.
    df = make_stations()
    station_xy = df.select(["x", "y"]).to_numpy()
    station_values = df["value"].to_numpy()
    errors = []
    for i in range(len(station_values)):
        mask = np.ones(len(station_values), dtype=bool)
        mask[i] = False
        pred = idw(station_xy[mask], station_values[mask], station_xy[[i]])
        errors.append(abs(pred[0] - station_values[i]))
    assert np.mean(errors) < 0.3
