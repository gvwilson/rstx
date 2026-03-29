import numpy as np
import matplotlib.pyplot as plt
import networkx as nx

SEED = 7493418

# mccole: taxa
TAXA = ["Bat", "Chimp", "Human", "Gorilla"]

# True branch lengths from the reference tree used to generate distances.
# The tree is: ((Bat:0.6, Chimp:0.8):1.2, (Human:0.4, Gorilla:0.5))
# Pairwise distances are sums of branches on the path between each pair.
_BRANCH = {
    ("Bat", "Chimp"): 0.6 + 0.8,       # 1.4
    ("Bat", "Human"): 0.6 + 1.2 + 0.4, # 2.2
    ("Bat", "Gorilla"): 0.6 + 1.2 + 0.5, # 2.3
    ("Chimp", "Human"): 0.8 + 1.2 + 0.4, # 2.4
    ("Chimp", "Gorilla"): 0.8 + 1.2 + 0.5, # 2.5
    ("Human", "Gorilla"): 0.4 + 0.5,   # 0.9
}
# mccole: /taxa


# mccole: make-dist
def make_distance_matrix(noise_scale=0.0, seed=SEED):
    """Return (names, D) where D is the symmetric pairwise distance matrix.

    When noise_scale=0.0 (default) the distances are exact tree-additive values.
    A non-zero noise_scale adds symmetric Gaussian noise so that the distances
    no longer satisfy the four-point condition exactly, simulating real data.
    """
    n = len(TAXA)
    D = np.zeros((n, n))
    for i, a in enumerate(TAXA):
        for j, b in enumerate(TAXA):
            if i < j:
                key = (a, b) if (a, b) in _BRANCH else (b, a)
                D[i, j] = D[j, i] = _BRANCH[key]
    if noise_scale > 0.0:
        rng = np.random.default_rng(seed)
        noise = rng.normal(0, noise_scale, (n, n))
        noise = (noise + noise.T) / 2  # keep symmetric
        np.fill_diagonal(noise, 0)
        D = np.maximum(D + noise, 0)  # distances must be non-negative
    return list(TAXA), D
# mccole: /make-dist


# neighbor_joining is retained for use by test_generate_tree.py.
# It is not part of the lesson; see the Exercises section for context.
def neighbor_joining(names, D):
    """Run the neighbor-joining algorithm; return (node_a, node_b, length) edges."""
    names, D, edges, nc = list(names), D.copy().astype(float), [], len(names)
    while len(names) > 2:
        n = len(names)
        rs = D.sum(axis=1)
        Q = (n - 2) * D - rs[:, None] - rs[None, :]
        np.fill_diagonal(Q, np.inf)
        i, j = divmod(int(np.argmin(Q)), n)
        if i > j:
            i, j = j, i
        d = D[i, j]
        li = 0.5 * d + (rs[i] - rs[j]) / (2 * (n - 2))
        u = f"node{nc}"
        nc += 1
        edges += [(u, names[i], li), (u, names[j], d - li)]
        nr = np.array([0.5 * (D[i, k] + D[j, k] - d) for k in range(n)])
        keep = [k for k in range(n) if k != i and k != j]
        sz = len(keep) + 1
        D2 = np.zeros((sz, sz))
        D2[:len(keep), :len(keep)] = D[np.ix_(keep, keep)]
        D2[:len(keep), -1] = D2[-1, :len(keep)] = nr[keep]
        D, names = D2, [names[k] for k in keep] + [u]
    edges.append((names[0], names[1], D[0, 1]))
    return edges


# mccole: upgma
def upgma(names, D):
    """Run the UPGMA algorithm and return a list of (parent, child, length) edges.

    `names` is a list of taxon (or internal node) labels.
    `D` is a symmetric distance matrix with zero diagonal.
    Returns a list of (parent, child, branch_length) triples for the rooted tree.
    At each step the pair with the smallest average distance is merged.
    The new node is placed at height D(i,j)/2, so the branch from the new node
    to each child is height(new) - height(child).
    """
    names = list(names)
    D = D.copy().astype(float)
    edges = []
    # Track the height (distance from root) of each node; leaves start at 0.
    heights = {name: 0.0 for name in names}
    node_counter = len(names)

    while len(names) > 1:
        n = len(names)

        # Find the pair (i, j) with the smallest distance.
        # Set the diagonal to infinity so it is never chosen.
        D_search = D.copy()
        np.fill_diagonal(D_search, np.inf)
        idx = int(np.argmin(D_search))
        i, j = divmod(idx, n)
        if i > j:
            i, j = j, i

        # The new node sits at half the merged distance (UPGMA clock assumption).
        merge_height = D[i, j] / 2.0
        u_name = f"node{node_counter}"
        node_counter += 1

        # Branch length from new node to each child is the difference in heights.
        branch_i = merge_height - heights[names[i]]
        branch_j = merge_height - heights[names[j]]
        edges.append((u_name, names[i], branch_i))
        edges.append((u_name, names[j], branch_j))
        heights[u_name] = merge_height

        # Distance from new node u to every remaining taxon k is the arithmetic mean.
        new_dists = np.array(
            [0.5 * (D[i, k] + D[j, k]) for k in range(n)]
        )

        # Rebuild the distance matrix: remove i and j, append u.
        keep = [k for k in range(n) if k != i and k != j]
        D_keep = D[np.ix_(keep, keep)]
        extra = new_dists[keep]
        size = len(keep) + 1
        D_new = np.zeros((size, size))
        D_new[: len(keep), : len(keep)] = D_keep
        D_new[: len(keep), -1] = extra
        D_new[-1, : len(keep)] = extra
        D = D_new
        names = [names[k] for k in keep] + [u_name]

    return edges
# mccole: /upgma


# mccole: draw
def draw_tree(edges, taxa, filename):
    """Save a rooted tree diagram to `filename`.

    Leaf nodes (members of `taxa`) are drawn in blue; internal nodes in grey.
    Edge labels show branch lengths rounded to two decimal places.
    """
    G = nx.DiGraph()
    for parent, child, length in edges:
        G.add_edge(parent, child, weight=round(length, 4))

    # Use a simple hierarchical layout via networkx spring layout.
    pos = nx.spring_layout(G.to_undirected(), seed=7)

    leaf_nodes = [nd for nd in G.nodes() if nd in taxa]
    internal_nodes = [nd for nd in G.nodes() if nd not in taxa]

    fig, ax = plt.subplots(figsize=(6, 5))
    nx.draw_networkx_nodes(
        G, pos, nodelist=leaf_nodes, node_color="steelblue", node_size=600, ax=ax
    )
    nx.draw_networkx_nodes(
        G, pos, nodelist=internal_nodes, node_color="lightgrey", node_size=400, ax=ax
    )
    nx.draw_networkx_labels(G, pos, ax=ax, font_size=9)
    nx.draw_networkx_edges(G, pos, ax=ax, arrows=True)
    edge_labels = {(p, c): f"{length:.2f}" for p, c, length in edges}
    nx.draw_networkx_edge_labels(
        G, pos, edge_labels=edge_labels, font_size=7, ax=ax
    )

    ax.set_title("UPGMA tree")
    ax.axis("off")
    plt.tight_layout()
    plt.savefig(filename)
    plt.close(fig)
# mccole: /draw


if __name__ == "__main__":
    names, D = make_distance_matrix()
    print("Distance matrix:")
    header = f"{'':8}" + "".join(f"{t:10}" for t in names)
    print(header)
    for i, row in enumerate(D):
        print(f"{names[i]:8}" + "".join(f"{v:10.4f}" for v in row))
    edges = upgma(names, D)
    print("\nRecovered edges:")
    for parent, child, length in edges:
        print(f"  {parent} -> {child}: {length:.4f}")
    draw_tree(edges, TAXA, "phylo.svg")
    print("Saved phylo.svg")
