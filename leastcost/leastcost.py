import heapq
import numpy as np
import matplotlib.pyplot as plt

from generate_leastcost import make_terrain, GRID_ROWS, GRID_COLS, START, END

# Diagonal moves cover sqrt(2) cell-widths; orthogonal moves cover 1.
# The ratio is exact so that shortest-path distances are geometrically correct.
SQRT2 = 2.0**0.5

# Eight-connected neighbor offsets and their Euclidean step lengths.
OFFSETS = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]

STEP_LEN = {
    (-1, -1): SQRT2,
    (-1, 0): 1.0,
    (-1, 1): SQRT2,
    (0, -1): 1.0,
    (0, 1): 1.0,
    (1, -1): SQRT2,
    (1, 0): 1.0,
    (1, 1): SQRT2,
}


# mccole: dijkstra
def least_cost_path(elev, start, end):
    """Return the least-cost path through an elevation grid.

    Returns a list of (row, col) pairs from start to end (inclusive).
    The cost of traversing the edge from cell A to adjacent cell B is:

        edge_cost = (elev[A] + elev[B]) / 2 * step_length

    Averaging the endpoint elevations penalises ridges and rewards valleys.
    Dijkstra's algorithm finds the path that minimises the total accumulated
    cost from start to end.
    """
    rows, cols = elev.shape
    dist = np.full((rows, cols), np.inf)
    prev = {}
    dist[start] = 0.0
    heap = [(0.0, start)]

    while heap:
        d, (r, c) = heapq.heappop(heap)
        if (r, c) == end:
            break
        if d > dist[r, c]:
            continue
        for dr, dc in OFFSETS:
            nr, nc = r + dr, c + dc
            if not (0 <= nr < rows and 0 <= nc < cols):
                continue
            step = STEP_LEN[(dr, dc)]
            edge = (elev[r, c] + elev[nr, nc]) / 2.0 * step
            new_d = dist[r, c] + edge
            if new_d < dist[nr, nc]:
                dist[nr, nc] = new_d
                prev[(nr, nc)] = (r, c)
                heapq.heappush(heap, (new_d, (nr, nc)))

    path = []
    node = end
    while node != start:
        path.append(node)
        node = prev[node]
    path.append(start)
    path.reverse()
    return path
# mccole: /dijkstra


# mccole: plot
def plot_path(elev, path, filename):
    """Save a terrain map with the least-cost path overlaid as an SVG."""
    fig, ax = plt.subplots(figsize=(8, 5))
    im = ax.imshow(elev, cmap="terrain", origin="upper")
    fig.colorbar(im, ax=ax, label="Normalized elevation")

    rows_p = [r for r, c in path]
    cols_p = [c for r, c in path]
    ax.plot(cols_p, rows_p, color="red", linewidth=1.5, label="Least-cost path")
    ax.plot(cols_p[0], rows_p[0], "wo", markersize=8, label="Start")
    ax.plot(cols_p[-1], rows_p[-1], "w^", markersize=8, label="End")
    ax.legend(loc="upper left", fontsize=8)
    ax.set_title("Least-cost trade route through synthetic terrain")
    ax.set_xlabel("Column")
    ax.set_ylabel("Row")
    fig.tight_layout()
    fig.savefig(filename)
    plt.close(fig)
# mccole: /plot


if __name__ == "__main__":
    elev = make_terrain(GRID_ROWS, GRID_COLS)
    path = least_cost_path(elev, START, END)
    print(f"Path length: {len(path)} cells")
    total_cost = sum(
        (elev[path[i]] + elev[path[i + 1]])
        / 2.0
        * STEP_LEN[(path[i + 1][0] - path[i][0], path[i + 1][1] - path[i][1])]
        for i in range(len(path) - 1)
    )
    print(f"Total cost: {total_cost:.4f}")
    plot_path(elev, path, "leastcost-path.svg")
    print("Saved leastcost-path.svg")
