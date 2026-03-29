import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors

SEED = 7493418

# Grid dimensions: 50x50 = 2500 cells gives visible clustering
# without making each step too slow.
GRID_SIZE = 50

# 20% empty cells ensure enough vacancies for agents to move.
EMPTY_FRACTION = 0.2

# Satisfaction threshold: an agent is happy when at least 30% of its
# occupied neighbours share its type.  Schelling (1971) showed that even
# this mild preference produces strong large-scale segregation.
THRESHOLD = 0.3

# Number of simulation steps; 20 is sufficient for visible clustering.
N_STEPS = 20

EMPTY = 0
RED = 1
BLUE = 2

# Steps at which grid snapshots are captured for the lesson figure.
SNAPSHOT_STEPS = [0, 5, 10, 20]


# mccole: grid
def make_grid(size=GRID_SIZE, empty_fraction=EMPTY_FRACTION, seed=SEED):
    """Return a random grid of RED and BLUE agents with some EMPTY cells.

    Each cell contains 0 (EMPTY), 1 (RED), or 2 (BLUE).  The two agent
    types are equal in number; the remaining cells are empty.
    """
    rng = np.random.default_rng(seed)
    n_cells = size * size
    n_empty = int(n_cells * empty_fraction)
    n_agents = n_cells - n_empty
    n_red = n_agents // 2
    n_blue = n_agents - n_red
    flat = np.array([EMPTY] * n_empty + [RED] * n_red + [BLUE] * n_blue)
    rng.shuffle(flat)
    return flat.reshape(size, size)
# mccole: /grid


# mccole: neighbors
def same_neighbor_fraction(grid, row, col):
    """Return the fraction of occupied neighbours of the same type.

    Uses the Moore neighbourhood (up to 8 surrounding cells).
    Returns 1.0 when no neighbours are occupied so isolated agents
    are always considered satisfied.
    """
    size = grid.shape[0]
    agent_type = grid[row, col]
    n_same = 0
    n_occupied = 0
    for dr in (-1, 0, 1):
        for dc in (-1, 0, 1):
            if dr == 0 and dc == 0:
                continue
            r, c = row + dr, col + dc
            if 0 <= r < size and 0 <= c < size and grid[r, c] != EMPTY:
                n_occupied += 1
                if grid[r, c] == agent_type:
                    n_same += 1
    if n_occupied == 0:
        return 1.0
    return n_same / n_occupied
# mccole: /neighbors


# mccole: step
def step(grid, threshold=THRESHOLD, rng=None):
    """Return a new grid after moving all dissatisfied agents.

    Each dissatisfied agent is paired with a randomly chosen empty cell
    and moved there.  Agents that cannot be matched (too few vacancies)
    stay in place.
    """
    if rng is None:
        rng = np.random.default_rng(SEED)
    size = grid.shape[0]
    dissatisfied = [
        (r, c)
        for r in range(size)
        for c in range(size)
        if grid[r, c] != EMPTY and same_neighbor_fraction(grid, r, c) < threshold
    ]
    empties = [(r, c) for r in range(size) for c in range(size) if grid[r, c] == EMPTY]
    rng.shuffle(dissatisfied)
    rng.shuffle(empties)
    new_grid = grid.copy()
    for i, (r, c) in enumerate(dissatisfied):
        if i < len(empties):
            er, ec = empties[i]
            new_grid[er, ec] = grid[r, c]
            new_grid[r, c] = EMPTY
    return new_grid
# mccole: /step


# mccole: segregation
def satisfaction_rate(grid, threshold=THRESHOLD):
    """Return the fraction of agents that are satisfied.

    A higher satisfaction rate indicates that agents have clustered with
    like neighbours; it approaches 1.0 as stable clusters form.
    """
    size = grid.shape[0]
    n_agents = 0
    n_satisfied = 0
    for r in range(size):
        for c in range(size):
            if grid[r, c] != EMPTY:
                n_agents += 1
                if same_neighbor_fraction(grid, r, c) >= threshold:
                    n_satisfied += 1
    if n_agents == 0:
        return 1.0
    return n_satisfied / n_agents
# mccole: /segregation


# mccole: run
def run(grid, n_steps=N_STEPS, threshold=THRESHOLD, seed=SEED):
    """Run the simulation and return a list of grid snapshots.

    Element 0 is the initial grid; element i is the grid after i steps.
    """
    rng = np.random.default_rng(seed)
    snapshots = [grid.copy()]
    for _ in range(n_steps):
        grid = step(grid, threshold, rng)
        snapshots.append(grid.copy())
    return snapshots
# mccole: /run


# mccole: plot
def plot_snapshots(snapshots, steps_to_show, filename):
    """Save a figure showing the grid state at the given step indices.

    White cells are empty, red cells are type RED, blue cells are type BLUE.
    """
    n = len(steps_to_show)
    cmap = mcolors.ListedColormap(["white", "tomato", "steelblue"])
    fig, axes = plt.subplots(1, n, figsize=(3 * n, 3))
    for ax, idx in zip(axes, steps_to_show):
        ax.imshow(snapshots[idx], cmap=cmap, vmin=0, vmax=2, interpolation="nearest")
        ax.set_title(f"Step {idx}")
        ax.axis("off")
    fig.tight_layout()
    fig.savefig(filename, dpi=150)
    plt.close(fig)
# mccole: /plot


if __name__ == "__main__":
    grid = make_grid()
    snapshots = run(grid)
    print(f"Initial satisfaction rate:  {satisfaction_rate(snapshots[0]):.3f}")
    print(f"Final satisfaction rate:    {satisfaction_rate(snapshots[-1]):.3f}")
    plot_snapshots(snapshots, SNAPSHOT_STEPS, "schelling-grid.svg")
    print("Saved schelling-grid.svg")
