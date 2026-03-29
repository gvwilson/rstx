import numpy as np
import pytest
from generate_tree import make_random_tree, bipartitions, MIN_TAXA
from phylo import neighbor_joining


def test_rejects_too_few_taxa():
    with pytest.raises(ValueError):
        make_random_tree(MIN_TAXA - 1)


def test_edge_count():
    # An unrooted binary tree on N leaves has exactly 2N-3 edges.
    for n in [3, 5, 8, 12]:
        _, _, edges = make_random_tree(n)
        assert len(edges) == 2 * n - 3, f"n={n}: got {len(edges)} edges"


def test_distance_matrix_properties():
    names, D, _ = make_random_tree(6)
    assert D.shape == (6, 6)
    assert np.allclose(D, D.T)
    assert np.all(np.diag(D) == 0.0)
    assert np.all(D >= 0.0)


def test_nj_recovers_true_topology():
    # With exact tree-additive distances, NJ must recover every bipartition
    # of the generating tree.  This holds for all tree-additive inputs
    # regardless of topology or branch lengths.
    for seed in [1, 7, 42, 99]:
        names, D, true_edges = make_random_tree(6, seed=seed)
        inferred_edges = neighbor_joining(names, D)
        true_splits = bipartitions(true_edges, names)
        inferred_splits = bipartitions(inferred_edges, names)
        assert true_splits == inferred_splits, (
            f"seed={seed}: topology mismatch\n  true:     {true_splits}\n  inferred: {inferred_splits}"
        )


def test_nj_recovers_topology_under_noise():
    # With small Gaussian noise (scale 0.05 ≈ 10% of the default branch mean)
    # NJ should still recover the correct topology on most random trees.
    # We test four seeds and require all four to succeed.  Measured failure
    # rate at this noise level is below 1% for N=6 with branch_mean=0.5.
    for seed in [1, 7, 42, 99]:
        names, D, true_edges = make_random_tree(6, seed=seed, noise_scale=0.05)
        inferred_edges = neighbor_joining(names, D)
        true_splits = bipartitions(true_edges, names)
        inferred_splits = bipartitions(inferred_edges, names)
        assert true_splits == inferred_splits, (
            f"seed={seed}: topology mismatch under noise"
        )


def test_reproducibility():
    # Same seed must always produce identical output.
    names1, D1, edges1 = make_random_tree(8)
    names2, D2, edges2 = make_random_tree(8)
    assert names1 == names2
    assert np.array_equal(D1, D2)
    assert edges1 == edges2


def test_different_seeds_differ():
    _, D1, _ = make_random_tree(6)
    _, D2, _ = make_random_tree(6, seed=999)
    assert not np.allclose(D1, D2)
