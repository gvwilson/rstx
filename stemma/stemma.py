import numpy as np
import matplotlib.pyplot as plt
import networkx as nx
from generate_stemma import MANUSCRIPTS

# True branch lengths for the reference stemma.
# Each value is the fraction of loci that differ between a node and its parent.
#
# Stemma structure:
#   ((A:0.05, B:0.03):0.07, (C:0.06, D:0.04):0.05)
#
# Reading: A and B share an intermediate ancestor alpha that is separated from
# the archetype by 0.07.  C and D share beta, separated from the archetype by 0.05.
_BRANCH = {
    ("A", "B"): 0.05 + 0.03,  # both through alpha: 0.08
    ("A", "C"): 0.05 + 0.07 + 0.05 + 0.06,  # through archetype: 0.23
    ("A", "D"): 0.05 + 0.07 + 0.05 + 0.04,  # 0.21
    ("B", "C"): 0.03 + 0.07 + 0.05 + 0.06,  # 0.21
    ("B", "D"): 0.03 + 0.07 + 0.05 + 0.04,  # 0.19
    ("C", "D"): 0.06 + 0.04,  # both through beta: 0.10
}


# mccole: hamming
def hamming_distance(seq_a, seq_b):
    """Return the fraction of loci where seq_a and seq_b differ.

    Both sequences must be 1-D integer arrays of the same length.
    A value of 0.0 means identical manuscripts; 1.0 means they differ at
    every locus.  This is the Hamming distance normalized by sequence length.
    """
    return float(np.sum(seq_a != seq_b)) / len(seq_a)
# mccole: /hamming


# mccole: make-dist
def make_distance_matrix(noise_scale=0.0, seed=42):
    """Return (names, D) using exact tree-additive distances.

    When noise_scale=0.0 (default) the distances are exact and NJ recovers
    the true topology and branch lengths to machine precision.
    A non-zero noise_scale adds symmetric Gaussian noise to simulate the
    imperfect additivity of real manuscript data.
    """
    n = len(MANUSCRIPTS)
    D = np.zeros((n, n))
    for i, a in enumerate(MANUSCRIPTS):
        for j, b in enumerate(MANUSCRIPTS):
            if i < j:
                key = (a, b) if (a, b) in _BRANCH else (b, a)
                D[i, j] = D[j, i] = _BRANCH[key]
    if noise_scale > 0.0:
        rng = np.random.default_rng(seed)
        noise = rng.normal(0, noise_scale, (n, n))
        noise = (noise + noise.T) / 2
        np.fill_diagonal(noise, 0)
        D = np.maximum(D + noise, 0.0)
    return list(MANUSCRIPTS), D
# mccole: /make-dist


# mccole: upgma
def upgma(names, dist_matrix):
    """Run the UPGMA algorithm and return a list of (node_a, node_b, length) edges.

    `names` is a list of manuscript labels.
    `dist_matrix` is a symmetric distance matrix with zero diagonal.

    UPGMA (Unweighted Pair-Group Method with Arithmetic means) builds a rooted,
    ultrametric tree.  At each step it merges the pair with the smallest pairwise
    distance, assigns each branch half that distance, then recomputes distances to
    the new node as the average of the merged nodes' distances.

    Returns a list of (node_a, node_b, branch_length) triples.  For each internal
    node u created by merging i and j, two edges are added: (u, i, D(i,j)/2) and
    (u, j, D(i,j)/2).  The final two nodes are joined by one last edge.
    """
    names = list(names)
    D = dist_matrix.copy().astype(float)
    edges = []
    # node_counter starts after all leaf indices so generated names never
    # collide with manuscript labels such as "A", "B", etc.
    node_counter = len(names)

    while len(names) > 2:
        n = len(names)

        # Find the pair (i, j) with i < j that has the smallest distance.
        np.fill_diagonal(D, np.inf)
        idx = np.argmin(D)
        np.fill_diagonal(D, 0.0)
        i, j = divmod(int(idx), n)
        if i > j:
            i, j = j, i

        d_ij = D[i, j]
        # Each branch from the new node u to i and j has length D(i,j)/2.
        half = d_ij / 2.0
        u_name = f"node{node_counter}"
        node_counter += 1
        edges.append((u_name, names[i], half))
        edges.append((u_name, names[j], half))

        # Distance from u to every remaining taxon k is the average of the
        # distances from i and from j to k (UPGMA averaging rule).
        new_row = np.array(
            [0.5 * (D[i, k] + D[j, k]) for k in range(n)]
        )

        # Remove rows/columns for i and j; append row/column for u.
        keep = [k for k in range(n) if k != i and k != j]
        D_new = D[np.ix_(keep, keep)]
        extra = new_row[keep]
        size = len(keep) + 1
        D2 = np.zeros((size, size))
        D2[: len(keep), : len(keep)] = D_new
        D2[: len(keep), -1] = extra
        D2[-1, : len(keep)] = extra
        D = D2
        names = [names[k] for k in keep] + [u_name]

    # Two nodes remain; connect them with the remaining distance.
    edges.append((names[0], names[1], D[0, 1]))
    return edges
# mccole: /upgma


# mccole: draw
def draw_stemma(edges, manuscripts, filename):
    """Save an unrooted stemma tree diagram to `filename`.

    Manuscript nodes (leaves) are drawn in steelblue; reconstructed
    intermediate ancestor nodes are drawn in lightgrey.
    Edge labels show the branch length (fraction of differing loci)
    rounded to two decimal places.
    """
    G = nx.Graph()
    for a, b, length in edges:
        G.add_edge(a, b, weight=round(length, 4))

    pos = nx.spring_layout(G, seed=3)

    leaf_nodes = [n for n in G.nodes() if n in manuscripts]
    internal_nodes = [n for n in G.nodes() if n not in manuscripts]

    fig, ax = plt.subplots(figsize=(6, 5))
    nx.draw_networkx_nodes(
        G, pos, nodelist=leaf_nodes, node_color="steelblue", node_size=700, ax=ax
    )
    nx.draw_networkx_nodes(
        G, pos, nodelist=internal_nodes, node_color="lightgrey", node_size=500, ax=ax
    )
    nx.draw_networkx_labels(
        G,
        pos,
        ax=ax,
        font_size=10,
        font_color="white",
        labels={n: n for n in leaf_nodes},
    )
    nx.draw_networkx_labels(
        G, pos, ax=ax, font_size=8, labels={n: n for n in internal_nodes}
    )
    nx.draw_networkx_edges(G, pos, ax=ax)
    edge_labels = {(a, b): f"{d:.2f}" for a, b, d in edges}
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=7, ax=ax)

    ax.set_title("Reconstructed manuscript stemma")
    ax.axis("off")
    plt.tight_layout()
    plt.savefig(filename)
    plt.close(fig)
# mccole: /draw


if __name__ == "__main__":
    names, D = make_distance_matrix()
    print("Distance matrix:")
    header = f"{'':6}" + "".join(f"{t:8}" for t in names)
    print(header)
    for i, row in enumerate(D):
        print(f"{names[i]:6}" + "".join(f"{v:8.4f}" for v in row))
    edges = upgma(names, D)
    print("\nRecovered edges (UPGMA):")
    for a, b, length in edges:
        print(f"  {a} -- {b}: {length:.4f}")
    draw_stemma(edges, MANUSCRIPTS, "stemma-tree.svg")
    print("Saved stemma-tree.svg")
