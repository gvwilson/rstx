import numpy as np
import networkx as nx

# mccole: constants
SEED = 7493418  # RNG seed
MIN_TAXA = 3  # smallest unrooted binary tree has 3 leaves and 1 internal node
DEFAULT_BRANCH_MEAN = 0.5  # mean branch length for exponential distribution
# mccole: /constants


# Topology is built by iterative leaf insertion starting from three taxa
# connected to a single internal node.  Each additional taxon is attached
# by picking a random existing edge, inserting a new internal node in its
# middle, and connecting the new taxon to that node.  Branch lengths are
# drawn independently from Exponential(branch_mean).  An optional
# symmetric Gaussian noise with standard deviation noise_scale is added to
# the distance matrix after it is computed from the tree.
# mccole: random-tree
def make_random_tree(
    n_taxa, seed=SEED, branch_mean=DEFAULT_BRANCH_MEAN, noise_scale=0.0
):
    """Return (names, D, true_edges) for a random unrooted binary tree.

    names      — list of n_taxa strings "S00", "S01", ...
    D          — n_taxa x n_taxa symmetric distance matrix
    true_edges — list of (node_a, node_b, length) for the generating tree
    """
    if n_taxa < MIN_TAXA:
        raise ValueError(f"n_taxa must be at least {MIN_TAXA}, got {n_taxa}")

    rng = np.random.default_rng(seed)
    names = [f"S{i:02d}" for i in range(n_taxa)]

    # Start with the three-leaf star: S00, S01, S02 all connected to I0.
    internal_counter = 0
    first_internal = f"I{internal_counter}"
    internal_counter += 1
    edges = [
        [names[0], first_internal, rng.exponential(branch_mean)],
        [names[1], first_internal, rng.exponential(branch_mean)],
        [names[2], first_internal, rng.exponential(branch_mean)],
    ]

    # Insert each remaining taxon by splitting a random existing edge.
    for i in range(3, n_taxa):
        idx = int(rng.integers(len(edges)))
        u, v, _ = edges.pop(idx)

        new_internal = f"I{internal_counter}"
        internal_counter += 1
        edges.append([u, new_internal, rng.exponential(branch_mean)])
        edges.append([v, new_internal, rng.exponential(branch_mean)])
        edges.append([names[i], new_internal, rng.exponential(branch_mean)])

    # Compute all pairwise distances through the tree.
    G = nx.Graph()
    for a, b, w in edges:
        G.add_edge(a, b, weight=w)
    all_dists = dict(nx.all_pairs_dijkstra_path_length(G, weight="weight"))

    n = len(names)
    D = np.zeros((n, n))
    for i, a in enumerate(names):
        for j, b in enumerate(names):
            D[i, j] = all_dists[a][b]

    if noise_scale > 0.0:
        noise = rng.normal(0, noise_scale, (n, n))
        noise = (noise + noise.T) / 2
        np.fill_diagonal(noise, 0)
        D = np.maximum(D + noise, 0.0)

    true_edges = [(a, b, w) for a, b, w in edges]
    return names, D, true_edges
# mccole: /random-tree


# Each bipartition is a frozenset of two frozensets of taxon names,
# representing the two groups of leaves on either side of an edge.
# Internal edges (those whose removal produces two groups each containing
# at least one leaf) are included; pendant edges are excluded because they
# encode only which leaf is attached, not a non-trivial split.
def bipartitions(edges, taxa):
    """Return the set of bipartitions implied by an edge list."""
    G = nx.Graph()
    for a, b, _ in edges:
        G.add_edge(a, b)
    taxa_set = set(taxa)
    splits = set()
    for u, v in list(G.edges()):
        G.remove_edge(u, v)
        comps = list(nx.connected_components(G))
        left = frozenset(comps[0] & taxa_set)
        right = frozenset(comps[1] & taxa_set)
        if left and right and left != taxa_set and right != taxa_set:
            splits.add(frozenset([left, right]))
        G.add_edge(u, v)
    return splits


if __name__ == "__main__":
    import sys

    n = int(sys.argv[1]) if len(sys.argv) > 1 else 6
    names, D, true_edges = make_random_tree(n)
    print(f"Taxa: {names}")
    print(f"True edges ({len(true_edges)}):")
    for a, b, w in true_edges:
        print(f"  {a} -- {b}: {w:.4f}")
