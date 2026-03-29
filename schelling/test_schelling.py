import numpy as np
import pytest
from schelling import (
    EMPTY,
    RED,
    BLUE,
    GRID_SIZE,
    SEED,
    make_grid,
    same_neighbor_fraction,
    step,
    satisfaction_rate,
    run,
)


def test_grid_shape():
    # Grid must be a square with side GRID_SIZE.
    grid = make_grid()
    assert grid.shape == (GRID_SIZE, GRID_SIZE)


def test_grid_cell_values():
    # Every cell must be EMPTY, RED, or BLUE.
    grid = make_grid()
    assert set(np.unique(grid)).issubset({EMPTY, RED, BLUE})


def test_grid_agent_counts_balanced():
    # The two agent types are built as equal halves of the agent pool,
    # so their counts differ by at most 1 (rounding when n_agents is odd).
    grid = make_grid()
    assert abs(np.sum(grid == RED) - np.sum(grid == BLUE)) <= 1


def test_neighbor_fraction_isolated_agent():
    # An agent with no occupied neighbours has same_neighbor_fraction 1.0
    # so it is treated as satisfied and never moves.
    grid = np.zeros((5, 5), dtype=int)
    grid[2, 2] = RED
    assert same_neighbor_fraction(grid, 2, 2) == pytest.approx(1.0)


def test_neighbor_fraction_all_same():
    # An agent surrounded entirely by the same type has fraction 1.0.
    grid = np.full((3, 3), RED, dtype=int)
    assert same_neighbor_fraction(grid, 1, 1) == pytest.approx(1.0)


def test_neighbor_fraction_all_different():
    # An agent surrounded entirely by the opposite type has fraction 0.0.
    grid = np.full((3, 3), BLUE, dtype=int)
    grid[1, 1] = RED
    assert same_neighbor_fraction(grid, 1, 1) == pytest.approx(0.0)


def test_stable_grid_unchanged():
    # A perfectly segregated 4x4 grid (RED left, BLUE right) has every
    # agent meeting the 0.3 threshold, so no movement should occur.
    # Border agents (column 1 or 2) have at least 5 same-type neighbours
    # out of 8, giving a fraction of 0.625 >= THRESHOLD.
    grid = np.zeros((4, 4), dtype=int)
    grid[:, :2] = RED
    grid[:, 2:] = BLUE
    rng = np.random.default_rng(SEED)
    assert np.array_equal(step(grid, rng=rng), grid)


def test_satisfaction_increases():
    # Running 20 steps from the random initial grid must raise the
    # satisfaction rate; agents self-organise into clusters.
    grid = make_grid()
    initial = satisfaction_rate(grid)
    snapshots = run(grid)
    assert satisfaction_rate(snapshots[-1]) > initial
