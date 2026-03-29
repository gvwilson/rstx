import numpy as np
from phylo import TAXA, make_distance_matrix, upgma

# Tolerance for floating-point comparisons in branch-length tests.
# UPGMA computes only averages and halvings, so round-off is well below 1e-10.
BRANCH_TOLERANCE = 1e-10


def test_matrix_symmetric():
    # The distance matrix must be symmetric with zero diagonal.
    names, D = make_distance_matrix()
    assert np.allclose(D, D.T)
    assert np.all(np.diag(D) == 0.0)


def test_upgma_edge_count():
    # A rooted binary tree on N leaves has exactly 2N-2 directed edges
    # (each internal node contributes two child edges; there are N-1 internal nodes).
    names, D = make_distance_matrix()
    edges = upgma(names, D)
    assert len(edges) == 2 * len(TAXA) - 2


def test_upgma_recovers_topology():
    # The reference tree groups (Bat, Chimp) and (Human, Gorilla).
    # UPGMA should merge Human+Gorilla first (smallest distance 0.9),
    # then Bat+Chimp (next smallest distance 1.4), then join the two clades.
    names, D = make_distance_matrix()
    edges = upgma(names, D)

    # Build parent-child adjacency from edges.
    children = {}
    for parent, child, _ in edges:
        children.setdefault(parent, []).append(child)

    # Find the internal node whose children are both leaves from the same clade.
    def siblings(taxon_a, taxon_b):
        for parent, kids in children.items():
            if taxon_a in kids and taxon_b in kids:
                return True
        return False

    assert siblings("Human", "Gorilla"), "Human and Gorilla should be sisters"
    assert siblings("Bat", "Chimp"), "Bat and Chimp should be sisters"


def test_upgma_recovers_branch_lengths():
    # With exact distances UPGMA should recover branch lengths to machine precision.
    # UPGMA merges in this order:
    #   node4 <- Human (0.45), Gorilla (0.45)   [merge height = 0.9/2 = 0.45]
    #   node5 <- Bat (0.70), Chimp (0.70)        [merge height = 1.4/2 = 0.70]
    #   node6 <- node4 (0.725), node5 (0.475)   [merge height = 2.35/2 = 1.175]
    # Branch length = merge height of parent - height of child.
    expected = {
        ("node4", "Human"): 0.45,
        ("node4", "Gorilla"): 0.45,
        ("node5", "Bat"): 0.70,
        ("node5", "Chimp"): 0.70,
        ("node6", "node4"): 0.725,
        ("node6", "node5"): 0.475,
    }
    names, D = make_distance_matrix()
    edges = upgma(names, D)
    assert len(edges) == len(expected), f"Expected {len(expected)} edges, got {len(edges)}"
    for parent, child, length in edges:
        key = (parent, child)
        assert key in expected, f"Unexpected edge {parent} -> {child}"
        assert abs(length - expected[key]) < BRANCH_TOLERANCE, (
            f"Edge {parent}->{child}: got {length:.8f}, expected {expected[key]:.8f}"
        )


def test_upgma_with_noise_recovers_topology():
    # With small Gaussian noise (scale 0.05) the correct topology should still
    # be recovered.  The Human-Gorilla distance (0.9) is well below the next
    # smallest (Bat-Chimp at 1.4), so modest noise rarely disrupts the merge order.
    names, D = make_distance_matrix(noise_scale=0.05)
    edges = upgma(names, D)
    children = {}
    for parent, child, _ in edges:
        children.setdefault(parent, []).append(child)

    def siblings(taxon_a, taxon_b):
        for parent, kids in children.items():
            if taxon_a in kids and taxon_b in kids:
                return True
        return False

    assert siblings("Human", "Gorilla"), (
        "Human and Gorilla should be sisters even under small noise"
    )
    assert siblings("Bat", "Chimp"), (
        "Bat and Chimp should be sisters even under small noise"
    )
