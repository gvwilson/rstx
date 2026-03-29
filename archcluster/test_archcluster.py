import numpy as np

from generate_archcluster import (
    make_sites,
    REGION_MIN,
    REGION_MAX,
)
from archcluster import (
    build_grid,
    find_hot_cells,
    find_clusters,
    assign_labels,
    cluster_centroids,
    GRID_SIZE,
    HOT_THRESHOLD,
)


def test_build_grid_shape():
    # Grid must have the requested number of rows and columns.
    coords = np.array([[10.0, 20.0], [50.0, 50.0], [90.0, 80.0]])
    grid = build_grid(coords, REGION_MIN, REGION_MAX, GRID_SIZE)
    assert grid.shape == (GRID_SIZE, GRID_SIZE)


def test_build_grid_sum():
    # Every site must land in exactly one cell, so the grid sum equals site count.
    df = make_sites()
    coords = df.select(["easting", "northing"]).to_numpy()
    grid = build_grid(coords, REGION_MIN, REGION_MAX, GRID_SIZE)
    assert grid.sum() == len(coords)


def test_find_hot_cells_threshold():
    # Cells with count >= threshold must be True; cells below must be False.
    grid = np.array([[0, 1, 2], [3, 4, 0], [1, 2, 5]])
    hot = find_hot_cells(grid, threshold=2)
    expected = grid >= 2
    assert np.array_equal(hot, expected)


def test_find_clusters_two_disconnected_blocks():
    # Two separated 1-cell hot regions must receive distinct non-negative IDs.
    hot = np.zeros((3, 3), dtype=bool)
    hot[0, 0] = True   # top-left block
    hot[2, 2] = True   # bottom-right block (not 8-connected to top-left)
    labels = find_clusters(hot)
    lbl_a = labels[0, 0]
    lbl_b = labels[2, 2]
    assert lbl_a >= 0
    assert lbl_b >= 0
    assert lbl_a != lbl_b
    # Cold cells stay -1.
    assert labels[0, 1] == -1
    assert labels[1, 0] == -1


def test_find_clusters_8connectivity():
    # Diagonal neighbors must be merged into one cluster.
    hot = np.zeros((3, 3), dtype=bool)
    hot[0, 0] = True
    hot[1, 1] = True   # diagonal from (0,0)
    labels = find_clusters(hot)
    assert labels[0, 0] == labels[1, 1]
    assert labels[0, 0] >= 0


def test_assign_labels_produces_two_or_more_clusters():
    # On the standard synthetic data the pipeline must find at least two clusters.
    df = make_sites()
    coords = df.select(["easting", "northing"]).to_numpy()
    grid = build_grid(coords, REGION_MIN, REGION_MAX, GRID_SIZE)
    hot = find_hot_cells(grid, HOT_THRESHOLD)
    cell_labels = find_clusters(hot)
    labels = assign_labels(coords, cell_labels, REGION_MIN, REGION_MAX, GRID_SIZE)
    n_clusters = len(set(labels[labels >= 0]))
    assert n_clusters >= 2


def test_cluster_centroids_one_per_label():
    # cluster_centroids must return exactly one entry for every unique non-negative label.
    coords = np.array([
        [10.0, 10.0],
        [11.0, 10.0],
        [50.0, 50.0],
        [51.0, 50.0],
        [90.0, 90.0],  # noise
    ])
    labels = np.array([0, 0, 1, 1, -1])
    centroids = cluster_centroids(coords, labels)
    assert set(centroids.keys()) == {0, 1}
    cx0, cy0 = centroids[0]
    assert abs(cx0 - 10.5) < 1e-9
    assert abs(cy0 - 10.0) < 1e-9
