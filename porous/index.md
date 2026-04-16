# Percolation in a Porous Medium

## The Problem

-   Porous materials such as sandstone, soil, and filter membranes have a random network of connected pores.
-   A fluid injected at one face can flow to the other face only if there is a continuous path of connected open pores.
-   The critical question is: at what fraction of open pores does flow first become possible?
-   This is the [%g percolation_threshold "percolation threshold" %], a sharp transition that appears in hydrology, materials science, and network theory.

## The Grid Model

-   We approximate the material as a square grid: each cell is independently open (passable) with probability $p$ or blocked (solid) with probability $1-p$.
-   This is [%g site_percolation "site percolation" %] on a 2D square lattice with 4-neighbor (von Neumann) connectivity.
-   "Percolation" means a connected path of open cells exists from any cell in the top row to any cell in the bottom row.

[%inc porous.py mark="constants"%]

[%inc porous.py mark="make-grid"%]

<div class="forma-multiple-choice" data-lang="en" markdown="1">

The expression `rng.random((GRID_SIZE, GRID_SIZE)) < p` produces a boolean grid.
What fraction of its cells are True on average?

$1 - p$
:   Wrong: cells with a uniform random value less than p are True with probability p, not 1-p.

$p$
:   Correct: each cell is drawn from Uniform(0, 1) and is less than p with probability p.

$p^2$
:   Wrong: the cells are independent; their joint probability involves products only when all must be True simultaneously.

$\sqrt{p}$
:   Wrong: the comparison `< p` gives probability p directly, with no square root.

</div>

## Depth-First Search

-   We test percolation by searching for a path from the top row to the bottom row.
-   [%g depth_first_search "Depth-first search" %] (DFS) explores as far as possible along each branch before backtracking.
-   All open cells in row 0 are added to a stack as starting points; the search succeeds as soon as any visited cell reaches the last row.

[%inc porous.py mark="percolates"%]

-   `visited` prevents cells from being added to the stack twice, keeping the search $O(N^2)$ in the grid size.
-   Marking cells as visited before the main loop (not after popping) ensures no cell is pushed onto the stack more than once.

<div class="forma-ordering" data-lang="en" markdown="1">

Put these steps in the correct order for the iterative DFS percolation test.

1.  Collect all open cells in row 0 and push them onto the stack; mark them as visited
1.  Pop a cell (r, c) from the stack
1.  If r equals the last row index, return True (percolation found)
1.  For each unvisited open 4-neighbor, mark it visited and push it onto the stack
1.  If the stack is empty and the last row was never reached, return False

</div>

<div class="forma-multiple-choice" data-lang="en" markdown="1">

Why must cells be marked as visited before they are popped from the stack, rather than after?

Marking after popping is a valid alternative that produces the same result.
:   Wrong: marking after popping allows the same cell to be pushed multiple times, making the algorithm O(N^4) instead of O(N^2).

Marking before popping prevents a cell from being pushed onto the stack more than once.
:   Correct: once a cell is marked visited, no future neighbor scan will add it again, bounding the stack size by the number of cells.

The visited array must be filled in top-to-bottom order to work correctly.
:   Wrong: the visited array is indexed by (row, column), not traversal order; order of marking does not matter.

Marking after popping would cause the algorithm to miss cells in the last row.
:   Wrong: the check `r == nrows - 1` happens after popping; the order of marking does not affect which cells are checked.

</div>

## Sweeping the Probability

-   We run `N_TRIALS` independent trials at each probability value and record the fraction that percolate.
-   At low $p$, almost no trial percolates; at high $p$, almost every trial does.
-   The transition from 0 to 1 sharpens as the grid size increases.

[%inc porous.py mark="sweep"%]

[%inc porous.py mark="estimate-threshold"%]

## Visualizing the Results

[%inc porous.py mark="plot"%]

[%figure slug="porous-sweep"
         img="porous.svg"
         alt="S-shaped curve: fraction percolating vs. open probability. The curve rises steeply near p = 0.59."
         caption="Percolation fraction vs. open-cell probability p on a 20 x 20 grid, 200 trials per point. The transition is centred near the theoretical threshold p_c = 0.5927."%]

## Testing

### Boundary cases

-   At $p = 0$ all cells are closed; the stack starts empty and the search returns `False` immediately.
-   At $p = 1$ all cells are open; a straight vertical path always exists.
-   A single-row grid percolates if and only if any cell in that row is open (row 0 and row $N-1$ are the same).

### Fraction in $[0, 1]$

-   Each trial produces a boolean; the fraction is a count divided by `N_TRIALS`, always in $[0, 1]$.

### Threshold near theory

-   On an infinite lattice the threshold is $p_c \approx 0.5927$ (Stauffer & Aharony 1994).
-   On a $20 \times 20$ grid with 200 trials the finite-size correction and Monte Carlo variance together are within 0.07 of this value.
-   A tolerance of 0.07 is tight enough to catch a wrong algorithm but loose enough to accommodate finite-size effects.

[%inc test_porous.py%]

<section class="exercises" markdown="1">

## Exercises

### Do the math

The theoretical percolation threshold for 2D site percolation on a square lattice with
4-neighbor connectivity is commonly cited as 0.5927.
To three decimal places, what is `THRESHOLD_THEORY` as defined in `porous.py`?

### Larger grids

Increase `GRID_SIZE` to 50 and rerun `sweep` (you may need to reduce `N_TRIALS` to 50 to keep the run time reasonable).
Does the threshold estimate get closer to 0.5927?
Does the transition curve become steeper?

### 8-neighbor connectivity

Change the neighbor offsets in `percolates` from the 4-neighbor pattern to 8-neighbor (Moore neighborhood):
add the four diagonal directions $(\pm 1, \pm 1)$.
The theoretical threshold for 8-neighbor site percolation is approximately 0.407.
Update `THRESHOLD_THEORY` and verify that `test_threshold_near_theory` still passes.

### Bond percolation

In bond percolation, edges between adjacent cells are open with probability $p$ (rather than cells themselves).
Implement a `make_bond_grid` function that creates a random boolean array for horizontal bonds and another for vertical bonds.
Modify `percolates` to use bond arrays instead of a cell array.
The theoretical threshold for 2D bond percolation on a square lattice is exactly $p_c = 0.5$.
Estimate it numerically and compare.

### Cluster size distribution

Instead of returning only a boolean, modify `percolates` to return the sizes of all connected open clusters
found during the DFS.
At $p = p_c$, the largest cluster grows as a power law of the grid size $N$.
Run sweeps at several grid sizes and plot the largest cluster size vs. $N$ near the threshold.

</section>
