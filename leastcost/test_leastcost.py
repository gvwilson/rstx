import numpy as np
import pytest
from generate_leastcost import make_terrain, GRID_ROWS, GRID_COLS, START, END
from leastcost import least_cost_path, STEP_LEN


def test_terrain_shape():
    # Terrain must match the requested dimensions.
    elev = make_terrain(10, 15)
    assert elev.shape == (10, 15)


def test_terrain_bounds():
    # After normalisation, minimum is 0 and maximum is 1.
    elev = make_terrain(GRID_ROWS, GRID_COLS)
    assert elev.min() == pytest.approx(0.0)
    assert elev.max() == pytest.approx(1.0)


def test_terrain_reproducible():
    # Same seed must always produce identical terrain.
    elev1 = make_terrain(GRID_ROWS, GRID_COLS)
    elev2 = make_terrain(GRID_ROWS, GRID_COLS)
    assert np.array_equal(elev1, elev2)


def test_path_endpoints():
    # Path must start at START and finish at END.
    elev = make_terrain(GRID_ROWS, GRID_COLS)
    path = least_cost_path(elev, START, END)
    assert path[0] == START
    assert path[-1] == END


def test_path_connected():
    # Every consecutive pair of cells must be 8-connected neighbors.
    elev = make_terrain(GRID_ROWS, GRID_COLS)
    path = least_cost_path(elev, START, END)
    for (r1, c1), (r2, c2) in zip(path, path[1:]):
        assert (r2 - r1, c2 - c1) in STEP_LEN


def test_flat_terrain_diagonal():
    # On a uniform-elevation 5x5 grid, the cheapest path from (0,0) to (4,4)
    # is the main diagonal (4 diagonal steps, cost 4*sqrt(2) < 8 orthogonal steps).
    elev = np.ones((5, 5))
    path = least_cost_path(elev, (0, 0), (4, 4))
    assert path[0] == (0, 0)
    assert path[-1] == (4, 4)
    # Diagonal path visits exactly 5 cells.
    assert len(path) == 5


def test_valley_preferred():
    # Three-row grid: rows 0 and 2 are high (elev=1), row 1 is a valley (elev=0).
    # The path from (0,0) to (2,2) must pass through the valley to minimise cost.
    elev = np.array(
        [
            [1.0, 1.0, 1.0],
            [0.0, 0.0, 0.0],
            [1.0, 1.0, 1.0],
        ]
    )
    path = least_cost_path(elev, (0, 0), (2, 2))
    visited_rows = {r for r, c in path}
    assert 1 in visited_rows


def test_low_cost_path_cheaper_than_ridge():
    # On a 3x5 grid with a valley corridor in the middle row (elev=0) and
    # high terrain everywhere else (elev=1), the least-cost path from
    # (0,0) to (2,4) must cost strictly less than a direct ridge traverse.
    # Ridge traverse (stay in rows 0 and 2) costs at least 4 orthogonal steps
    # at (1+1)/2 = 1.0 each, for a total >= 4.0.  Valley path dips into row 1
    # where most edges cost (1+0)/2 or (0+0)/2, giving a much lower total.
    elev = np.array(
        [
            [1.0, 1.0, 1.0, 1.0, 1.0],
            [0.0, 0.0, 0.0, 0.0, 0.0],
            [1.0, 1.0, 1.0, 1.0, 1.0],
        ]
    )
    path = least_cost_path(elev, (0, 0), (2, 4))

    def total_cost(path):
        return sum(
            (elev[path[i]] + elev[path[i + 1]])
            / 2.0
            * STEP_LEN[(path[i + 1][0] - path[i][0], path[i + 1][1] - path[i][1])]
            for i in range(len(path) - 1)
        )

    # All-ridge orthogonal path (0,0)->(0,1)->(0,2)->(0,3)->(0,4)->(1,4)->(2,4)
    # costs (1+1)/2 * 4 orthogonal + (1+0)/2 + (0+1)/2 = 4 + 0.5 + 0.5 = 5.0
    ridge_cost = 5.0
    assert total_cost(path) < ridge_cost
