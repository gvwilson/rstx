import numpy as np
from porous import (
    RNG_SEED,
    THRESHOLD_THEORY,
    estimate_threshold,
    make_grid,
    percolates,
    sweep,
)


def test_empty_grid_never_percolates():
    # When p = 0 every cell is closed (False), so the stack is empty from
    # the start and the DFS returns False immediately.
    rng = np.random.default_rng(RNG_SEED)
    grid = make_grid(0.0, rng)
    assert not percolates(grid)


def test_full_grid_always_percolates():
    # When p = 1 every cell is open (True).  A straight vertical path
    # through column 0 connects row 0 to row GRID_SIZE - 1.
    rng = np.random.default_rng(RNG_SEED)
    grid = make_grid(1.0, rng)
    assert percolates(grid)


def test_single_row_grid():
    # A one-row grid percolates if and only if at least one cell in that row
    # is open, because the top row and the bottom row are the same row.
    open_row = np.array([[True, False, True]])
    assert percolates(open_row)
    closed_row = np.array([[False, False, False]])
    assert not percolates(closed_row)


def test_fractions_in_unit_interval():
    # Each trial either percolates or not, so the fraction must lie in [0, 1].
    df = sweep()
    assert (df["fraction_percolating"] >= 0.0).all()
    assert (df["fraction_percolating"] <= 1.0).all()


def test_threshold_near_theory():
    # On a 20 x 20 grid with 200 trials the finite-size threshold should be
    # within 0.07 of the infinite-lattice value 0.5927.  Finite-size effects
    # and Monte Carlo variance both contribute; a tolerance of 0.07 gives a
    # comfortable margin without being so wide that a wrong algorithm passes.
    df = sweep()
    p_c = estimate_threshold(df)
    assert abs(p_c - THRESHOLD_THEORY) < 0.07, (
        f"estimated threshold {p_c:.3f} is too far from theory {THRESHOLD_THEORY:.4f}"
    )
