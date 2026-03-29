import pytest
import numpy as np
from generate_stemma import make_manuscripts, MANUSCRIPTS
from stemma import (
    hamming_distance,
    make_distance_matrix,
    upgma,
)


# ---------------------------------------------------------------------------
# hamming_distance
# ---------------------------------------------------------------------------


def test_hamming_identical():
    # Two identical sequences have distance 0.0.
    seq = np.array([0, 1, 0, 1, 1], dtype=np.int8)
    assert hamming_distance(seq, seq.copy()) == pytest.approx(0.0)


def test_hamming_all_different():
    # Sequences that differ at every locus have distance 1.0.
    seq_a = np.zeros(10, dtype=np.int8)
    seq_b = np.ones(10, dtype=np.int8)
    assert hamming_distance(seq_a, seq_b) == pytest.approx(1.0)


def test_hamming_half():
    # Sequences differing at exactly half the loci have distance 0.5.
    seq_a = np.zeros(8, dtype=np.int8)
    seq_b = np.array([1, 1, 1, 1, 0, 0, 0, 0], dtype=np.int8)
    assert hamming_distance(seq_a, seq_b) == pytest.approx(0.5)


# ---------------------------------------------------------------------------
# Distance matrix
# ---------------------------------------------------------------------------


def test_distance_matrix_symmetry():
    # The distance matrix must be symmetric with zero diagonal.
    names, D = make_distance_matrix()
    n = len(names)
    assert D.shape == (n, n)
    np.testing.assert_allclose(D, D.T, atol=1e-12)
    np.testing.assert_allclose(np.diag(D), 0.0, atol=1e-12)


def test_distance_matrix_within_family_smaller():
    # Within-family distances (A–B and C–D) must be smaller than cross-family
    # distances (A–C, A–D, B–C, B–D), reflecting the true copying tree.
    names, D = make_distance_matrix()
    idx = {n: i for i, n in enumerate(names)}
    d_ab = D[idx["A"], idx["B"]]
    d_cd = D[idx["C"], idx["D"]]
    cross = [D[idx[a], idx[b]] for a in "AB" for b in "CD"]
    assert d_ab < min(cross)
    assert d_cd < min(cross)


# ---------------------------------------------------------------------------
# UPGMA topology and branch lengths
# ---------------------------------------------------------------------------


def test_upgma_topology_recovery():
    # A and B must share a private internal ancestor, and C and D must share
    # a different one.  UPGMA merges the pair with the smallest distance first:
    # D(A,B) = 0.08 is the global minimum, so A and B are joined first into
    # node4; then D(C,D) = 0.10 < D(node4,C) = D(node4,D), so C and D are
    # joined into node5; finally node4 and node5 are joined.
    names, D = make_distance_matrix()
    edges = upgma(names, D)

    # Build an adjacency map.
    adj = {}
    for a, b, _ in edges:
        adj.setdefault(a, []).append(b)
        adj.setdefault(b, []).append(a)

    # Find the internal node connected to each manuscript.
    parent_a = [n for n in adj["A"] if n not in MANUSCRIPTS][0]
    parent_b = [n for n in adj["B"] if n not in MANUSCRIPTS][0]
    parent_c = [n for n in adj["C"] if n not in MANUSCRIPTS][0]
    parent_d = [n for n in adj["D"] if n not in MANUSCRIPTS][0]

    assert parent_a == parent_b, "A and B should share an internal ancestor"
    assert parent_c == parent_d, "C and D should share an internal ancestor"
    assert parent_a != parent_c, (
        "AB family and CD family should have different ancestors"
    )


def test_upgma_branch_lengths():
    # UPGMA branch lengths for the reference distance matrix.
    #
    # Step 1: merge A and B (D=0.08).  Each branch length = 0.08/2 = 0.04.
    #   D(node4, C) = (0.23 + 0.21) / 2 = 0.22
    #   D(node4, D) = (0.21 + 0.19) / 2 = 0.20
    #
    # Step 2: merge C and D (D=0.10 < 0.20 < 0.22).  Each branch length = 0.05.
    #   D(node4, node5) = (0.22 + 0.20) / 2 = 0.21
    #
    # Step 3: join node4 and node5 with the remaining distance = 0.21.
    #
    # Tolerance 1e-10 covers only accumulated floating-point rounding.
    names, D = make_distance_matrix()
    edges = upgma(names, D)

    expected = {
        frozenset(["node4", "A"]): 0.04,
        frozenset(["node4", "B"]): 0.04,
        frozenset(["node5", "C"]): 0.05,
        frozenset(["node5", "D"]): 0.05,
        frozenset(["node4", "node5"]): 0.21,
    }
    recovered = {frozenset([a, b]): length for a, b, length in edges}
    for key, true_len in expected.items():
        assert key in recovered, f"Missing edge {key}"
        assert recovered[key] == pytest.approx(true_len, abs=1e-10)


def test_upgma_all_lengths_positive():
    # Every branch length in the UPGMA tree must be strictly positive.
    names, D = make_distance_matrix()
    edges = upgma(names, D)
    for a, b, length in edges:
        assert length > 0, f"Non-positive branch length on edge {a}--{b}: {length}"


# ---------------------------------------------------------------------------
# Stochastic generator topology
# ---------------------------------------------------------------------------


def test_generator_topology():
    # Manuscripts generated stochastically must also produce a distance matrix
    # whose minimum within-family distance is smaller than the minimum
    # cross-family distance, so UPGMA can still find the correct grouping.
    mss = make_manuscripts()
    within = [
        hamming_distance(mss["A"], mss["B"]),
        hamming_distance(mss["C"], mss["D"]),
    ]
    cross = [hamming_distance(mss[a], mss[b]) for a in "AB" for b in "CD"]
    assert max(within) < min(cross), (
        "Within-family distances should be smaller than cross-family distances"
    )
