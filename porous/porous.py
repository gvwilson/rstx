import numpy as np
import polars as pl
import altair as alt

# mccole: constants
GRID_SIZE = 20  # side length of the square grid (cells)
N_TRIALS = 200  # independent trials per probability value
N_PROBS = 41  # number of probability values from 0.0 to 1.0 inclusive
RNG_SEED = 7493418

# Theoretical site-percolation threshold for a 2D square lattice with
# 4-neighbor (von Neumann) connectivity.  From Stauffer & Aharony,
# Introduction to Percolation Theory (2nd ed., 1994), Appendix B.
THRESHOLD_THEORY = 0.5927
# mccole: /constants


# mccole: make-grid
def make_grid(p, rng):
    """Return a GRID_SIZE x GRID_SIZE boolean array.

    Each cell is independently True (open) with probability p.
    """
    return rng.random((GRID_SIZE, GRID_SIZE)) < p
# mccole: /make-grid


# mccole: percolates
def percolates(grid):
    """Return True if an open path connects any top-row cell to any bottom-row cell.

    Uses iterative depth-first search with 4-neighbor (von Neumann) connectivity.
    All open cells in row 0 are added to the stack as starting points.
    The search succeeds as soon as any visited cell lies in the last row.
    """
    nrows, ncols = grid.shape
    visited = np.zeros_like(grid, dtype=bool)

    stack = [(0, c) for c in range(ncols) if grid[0, c]]
    for r, c in stack:
        visited[r, c] = True

    while stack:
        r, c = stack.pop()
        if r == nrows - 1:
            return True
        for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1)):
            nr, nc = r + dr, c + dc
            if (
                0 <= nr < nrows
                and 0 <= nc < ncols
                and grid[nr, nc]
                and not visited[nr, nc]
            ):
                visited[nr, nc] = True
                stack.append((nr, nc))
    return False
# mccole: /percolates


# mccole: sweep
def sweep():
    """Return a DataFrame with the percolation fraction at each probability.

    For each p in a uniform grid from 0 to 1, runs N_TRIALS independent
    experiments and records the fraction that percolate.  All trials share
    a single RNG to ensure reproducibility from RNG_SEED.
    """
    rng = np.random.default_rng(RNG_SEED)
    probs = np.linspace(0.0, 1.0, N_PROBS)
    fractions = [
        sum(percolates(make_grid(p, rng)) for _ in range(N_TRIALS)) / N_TRIALS
        for p in probs
    ]
    return pl.DataFrame({"probability": probs, "fraction_percolating": fractions})
# mccole: /sweep


# mccole: estimate-threshold
def estimate_threshold(df):
    """Return the smallest p where the percolation fraction first reaches 0.5.

    On a finite grid the percolation transition is sharp but not a true step
    function.  The crossing of 0.5 is a conventional and reproducible
    estimator of the finite-size threshold.
    """
    above = df.filter(pl.col("fraction_percolating") >= 0.5)
    return float(above["probability"].min()) if not above.is_empty() else float("nan")
# mccole: /estimate-threshold


# mccole: plot
def plot(df):
    """Return an Altair line chart of percolation fraction vs. open probability."""
    return (
        alt.Chart(df)
        .mark_line(point=True)
        .encode(
            x=alt.X("probability:Q", title="Open-cell probability p"),
            y=alt.Y(
                "fraction_percolating:Q",
                title="Fraction of trials that percolate",
                scale=alt.Scale(domain=[0.0, 1.0]),
            ),
        )
        .properties(width=400, height=300, title="Percolation threshold sweep")
    )
# mccole: /plot


if __name__ == "__main__":
    df = sweep()
    p_c = estimate_threshold(df)
    print(f"Estimated threshold: {p_c:.3f}  (theory: {THRESHOLD_THEORY:.4f})")
    chart = plot(df)
    chart.save("porous.svg")
    print("Saved porous.svg")
