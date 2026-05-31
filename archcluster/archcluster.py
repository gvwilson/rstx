import numpy as np
import polars as pl
import altair as alt

from generate_archcluster import make_sites, REGION_MIN, REGION_MAX

# Number of grid cells per axis (20x20 grid).  At 100 coordinate units across,
# each cell is 5 units wide, which is comparable to the cluster spread (sigma=5),
# so a real cluster fills several adjacent cells.
GRID_SIZE = 20

# Minimum sites per cell to be considered a concentration.  Cells with fewer
# sites are treated as background.  2 requires at least two independent finds
# in the same cell, reducing the chance that a single displaced point triggers
# a false cluster.
HOT_THRESHOLD = 2


# mccole:grid
def build_grid(coords, region_min, region_max, grid_size):
    """Count sites per grid cell.

    Each coordinate is mapped to a cell index by floor division:
        cell = int((value - region_min) / cell_width)
    clipped to [0, grid_size - 1] so that sites exactly on the upper boundary
    fall in the last cell rather than out of bounds.

    Returns a 2D integer array of shape (grid_size, grid_size) where entry
    [row, col] counts sites whose northing maps to row and easting to col.
    """
    cell_width = (region_max - region_min) / grid_size
    grid = np.zeros((grid_size, grid_size), dtype=int)
    for easting, northing in coords:
        col = int((easting - region_min) / cell_width)
        row = int((northing - region_min) / cell_width)
        col = min(col, grid_size - 1)
        row = min(row, grid_size - 1)
        grid[row, col] += 1
    return grid
# mccole: /grid


# mccole:hot-cells
def find_hot_cells(grid, threshold):
    """Boolean mask: True where count >= threshold."""
    return grid >= threshold
# mccole: /hot-cells


# mccole:dfs
def find_clusters(hot):
    """DFS connected components with 8-connectivity.

    Visits every True cell in the boolean mask exactly once, assigning
    consecutive integer labels starting at 0.  Cells where hot is False
    receive label -1.

    8-connectivity means each cell has up to 8 neighbors (4 cardinal + 4
    diagonal), so clusters that touch only at corners are still merged.

    Returns an integer label array of the same shape as hot.
    """
    nrows, ncols = hot.shape
    labels = np.full((nrows, ncols), -1, dtype=int)
    cluster_id = 0

    for start_r in range(nrows):
        for start_c in range(ncols):
            if not hot[start_r, start_c] or labels[start_r, start_c] != -1:
                continue
            # Start a new cluster from this unlabelled hot cell.
            stack = [(start_r, start_c)]
            labels[start_r, start_c] = cluster_id
            while stack:
                r, c = stack.pop()
                for dr in (-1, 0, 1):
                    for dc in (-1, 0, 1):
                        if dr == 0 and dc == 0:
                            continue
                        nr, nc = r + dr, c + dc
                        if 0 <= nr < nrows and 0 <= nc < ncols:
                            if hot[nr, nc] and labels[nr, nc] == -1:
                                labels[nr, nc] = cluster_id
                                stack.append((nr, nc))
            cluster_id += 1

    return labels
# mccole: /dfs


# mccole:assign
def assign_labels(coords, cell_labels, region_min, region_max, grid_size):
    """Map each site coordinate to its cluster label.

    Applies the same floor-division formula used in build_grid to find which
    cell each site belongs to, then returns the label for that cell.  Sites
    whose cell is not hot receive label -1 (noise).

    Returns a 1D integer array of length len(coords).
    """
    cell_width = (region_max - region_min) / grid_size
    site_labels = np.empty(len(coords), dtype=int)
    for i, (easting, northing) in enumerate(coords):
        col = int((easting - region_min) / cell_width)
        row = int((northing - region_min) / cell_width)
        col = min(col, grid_size - 1)
        row = min(row, grid_size - 1)
        site_labels[i] = cell_labels[row, col]
    return site_labels
# mccole: /assign


# mccole:centroids
def cluster_centroids(coords, labels):
    """Mean x/y per cluster, excluding noise (label -1).

    Returns a dict mapping each non-negative cluster label to a (easting,
    northing) tuple.
    """
    centroids = {}
    unique_labels = set(labels[labels >= 0])
    for lbl in unique_labels:
        mask = labels == lbl
        centroids[lbl] = (coords[mask, 0].mean(), coords[mask, 1].mean())
    return centroids
# mccole: /centroids


# mccole:plot
def plot_clusters(df, filename):
    """Save a scatter map coloured by cluster label."""
    chart = (
        alt.Chart(df)
        .mark_point(size=60, filled=True)
        .encode(
            x=alt.X("easting:Q", title="Easting", scale=alt.Scale(domain=[0, 100])),
            y=alt.Y("northing:Q", title="Northing", scale=alt.Scale(domain=[0, 100])),
            color=alt.Color(
                "cluster_label:N",
                title="Cluster",
                scale=alt.Scale(scheme="category10"),
            ),
            shape=alt.Shape(
                "is_noise:N",
                scale=alt.Scale(domain=["false", "true"], range=["circle", "cross"]),
                legend=alt.Legend(title="Noise"),
            ),
        )
        .properties(
            width=360,
            height=360,
            title="Grid-cell density clustering of archaeological sites",
        )
    )
    chart.save(filename)
# mccole: /plot


if __name__ == "__main__":
    df = make_sites()
    coords = df.select(["easting", "northing"]).to_numpy()

    grid = build_grid(coords, REGION_MIN, REGION_MAX, GRID_SIZE)
    hot = find_hot_cells(grid, HOT_THRESHOLD)
    cell_labels = find_clusters(hot)
    labels = assign_labels(coords, cell_labels, REGION_MIN, REGION_MAX, GRID_SIZE)

    n_clusters = len(set(labels[labels >= 0]))
    n_noise = (labels == -1).sum()
    print(f"Clusters found: {n_clusters}")
    print(f"Noise points:   {n_noise}")

    centroids = cluster_centroids(coords, labels)
    for lbl, (cx, cy) in sorted(centroids.items()):
        print(f"  Cluster {lbl}: centroid ({cx:.1f}, {cy:.1f})")

    df = df.with_columns(
        [
            pl.Series(
                "cluster_label", [str(lbl) if lbl >= 0 else "noise" for lbl in labels]
            ),
            pl.Series("is_noise", [lbl < 0 for lbl in labels]),
        ]
    )
    plot_clusters(df, "archcluster-sites.svg")
    print("Saved archcluster-sites.svg")
