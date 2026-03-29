# Phylogenetic Tree Reconstruction

## The Problem

-   Species that share a common ancestor tend to have similar DNA or protein sequences.
-   A [%g phylogenetic_tree "phylogenetic tree" %] shows how a set of species, genes, or individuals
    are related by common descent
-   The leaves of the tree are the observed [%g "taxa" taxa %],
    while internal nodes represent hypothetical ancestors
-   Given only pairwise sequence distances,
    we want to infer the tree topology (who is related to whom)
    and branch lengths (how different they are)

<div class="forma-multiple-choice" data-lang="en" markdown="1">

A rooted binary tree on 4 leaves has how many internal nodes (not counting the leaves themselves)?

2
:   Wrong: a rooted binary tree on N leaves has N-1 internal nodes, so 4-1=3.

3
:   Correct: a rooted binary tree on N leaves has N-1 internal nodes; here 4-1=3.

4
:   Wrong: 4 is the number of leaves; the number of internal nodes is N-1=3.

5
:   Wrong: this would require N=6 leaves.

</div>

## Distance Matrices

-   A [%g distance_matrix "distance matrix" %] $D$ stores the evolutionary distance between every pair of taxa
-   Distances are estimated from aligned sequences:
    the fraction of positions that differ, corrected for multiple substitutions

[%inc phylo.py mark="taxa"%]

The six pairwise distances for our four-taxon example:

| Pair | Distance |
|------|----------|
| Bat, Chimp | 1.4 |
| Human, Gorilla | 0.9 |
| Bat, Human | 2.2 |
| Bat, Gorilla | 2.3 |
| Chimp, Human | 2.4 |
| Chimp, Gorilla | 2.5 |

[%inc phylo.py mark="make-dist"%]

## The UPGMA Algorithm

-   [%g upgma "UPGMA" %] (Unweighted Pair Group Method with Arithmetic Mean)
    reconstructs a rooted tree from a distance matrix using only arithmetic means
-   At each step, merge the pair of taxa with the smallest pairwise distance
-   Place the new internal node at height $D(i,j)/2$
    (i.e., half the merged distance)
    which is the estimated time of the common ancestor
-   Branch length from the new node to each merged taxon is the difference in heights
-   Update the distance from the new node $u$ to any remaining taxon $k$ as the arithmetic mean:

<p>$$D(u, k) = \frac{D(i, k) + D(j, k)}{2}$$</p>

-   Replace $i$ and $j$ with $u$ in the matrix and repeat until only one node remains.

<div class="forma-ordering" data-lang="en" markdown="1">

Put these steps for one iteration of UPGMA in the correct order.

1.  Find the pair (i, j) with the smallest distance in the current matrix
1.  Create a new internal node u at height D(i, j) / 2
1.  Record branch lengths: branch to i = height(u) - height(i), branch to j = height(u) - height(j)
1.  Compute distances from u to all remaining taxa as arithmetic means
1.  Remove i and j from the matrix, add u, and repeat

</div>

## A Worked Example

-   Starting with $n = 4$ taxa and the distances above,
    Human and Gorilla have the smallest distance (0.9),
    so they are merged first into node4 at height $0.9/2 = 0.45$
-   Branch lengths:
    $\ell_\text{Human} = 0.45 - 0 = 0.45$ and $\ell_\text{Gorilla} = 0.45 - 0 = 0.45$ (both start at height 0)
-   After replacing Human and Gorilla with node4,
    the next smallest distance is Bat-Chimp (1.4),
    which becomes node5 at height $1.4/2 = 0.70$.
    Branch lengths to Bat and Chimp are each $0.70 - 0 = 0.70$.
-   The final merge joins node4 and node5.
    The average distance between node4 and node5,
    computed as the arithmetic mean of all pairwise distances between the two groups,
    works out to $2.35$.
    The final node (node6) sits at height $2.35/2 = 1.175$.
    Branch lengths are $1.175 - 0.45 = 0.725$ to node4 and $1.175 - 0.70 = 0.475$ to node5.

<div class="forma-numeric-entry" data-correct="0.45" data-tolerance="0.005" data-lang="en" markdown="1">

In the first UPGMA iteration Human and Gorilla are merged.
$D(\text{Human}, \text{Gorilla}) = 0.9$.
The new internal node is placed at height $D/2$.
What is the branch length from the new node to Human?
Give your answer to two decimal places.

</div>

<div class="forma-multiple-choice" data-lang="en" markdown="1">

Why does UPGMA assume a molecular clock?

Because it always picks the pair with the smallest distance, regardless of how far each taxon is from others.
:   Wrong: that is the merge criterion, not the clock assumption.

Because it places each internal node at half the merged distance, assuming all lineages evolve at the same rate.
:   Correct: placing the node at $D(i,j)/2$ assumes that $i$ and $j$ are equidistant from their common ancestor, which requires equal rates of evolution in both lineages.

Because it uses arithmetic means to update distances.
:   Wrong: the arithmetic mean update is a computational convenience, not the molecular clock assumption.

Because it produces a rooted tree rather than an unrooted tree.
:   Wrong: whether a tree is rooted or unrooted is independent of the clock assumption.

</div>

## Displaying the Tree

[%inc phylo.py mark="draw"%]

[%figure
  slug="phylo-tree"
  img="phylo.svg"
  alt="Rooted UPGMA tree for Bat, Chimp, Human, Gorilla with branch lengths labelled."
  caption="UPGMA tree for four taxa. Blue nodes are observed taxa; grey nodes are reconstructed ancestors. Branch lengths reflect the arithmetic-mean distances used at each merge step."
%]

## Testing

-   Matrix symmetry
    -   Distances must satisfy $D(i,j) = D(j,i)$ and $D(i,i) = 0$
    -   An asymmetric matrix would indicate a bug in the construction code

-   Edge count
    -   A rooted binary tree on $N$ leaves has exactly $2N - 2$ directed edges
       (each of the $N - 1$ internal nodes contributes two child edges)
    -   Any other count means the loop terminated early or ran too many iterations

-   Topology recovery
    -   Two pairs of taxa (Bat, Chimp) and (Human, Gorilla) should each share a private internal node
    -   If either pair is split across different internal nodes, the algorithm recovered the wrong topology

-   Branch length recovery
    -   With exact tree-additive distances the algorithm recovers every branch length to machine precision
    -   No tolerance is needed: floating-point round-off in the arithmetic means is below $10^{-10}$

-   Topology under noise
    -   Real distance data are not perfectly additive
    -   With small Gaussian noise (scale 0.05) the correct topology should still be recovered
    -   This test documents the robustness of UPGMA to modest measurement error

[%inc test_phylo.py%]

## Generating Random Trees

-   A single hand-crafted example is useful for tracing through the algorithm,
    but it cannot reveal how UPGMA behaves on different topologies or at larger scales
-   `generate_tree.py` provides `make_random_tree`
    which builds a random unrooted binary tree
    and returns its exact distance matrix alongside the true edge list

### Building a random topology

-   Start with three leaves connected to a single internal node
-   For each additional taxon
    -   Pick a random existing edge
    -   Insert a new internal node in the middle of it
    -   Attach the new taxon to that node
-   Branch lengths are drawn independently from an exponential distribution with a specified mean

[%inc generate_tree.py mark="random-tree"%]

### Computing distances and checking topology

-   Once the tree is built,
    pairwise distances are computed as shortest-path lengths through the networkx graph weighted by branch length
-   To compare topologies,
    each tree is converted to its set of [%g bipartition "bipartitions" %]
    -   For every edge, the two groups of leaves on either side
-   Two trees have the same topology if and only if their bipartition sets are identical

[%inc test_generate_tree.py%]

<section class="exercises" markdown="1">

## Exercises

### Neighbor-joining comparison

Neighbor-joining (Saitou and Nei, 1987) uses a Q-matrix correction that removes long-branch
attraction bias and does not assume a molecular clock.
Implement `neighbor_joining(names, D)` returning edges as `(node_a, node_b, length)` triples.
Verify that UPGMA and neighbor-joining agree on the topology for the exact distance matrix,
then add noise (scale 0.05) and show a case where they disagree.

### Bootstrapping

Phylogenetic bootstrap estimates how well-supported each split is.
Draw 100 perturbed distance matrices using `make_distance_matrix(noise_scale=0.1, seed=i)`
for $i = 0, \ldots, 99$ and run UPGMA on each.
Report what fraction of replicates recover the correct (Bat, Chimp) clade.

### Four-point condition

A distance matrix is tree-additive if and only if it satisfies the four-point condition:
for every four taxa $i, j, k, l$, the largest two of the three sums
$D(i,j)+D(k,l)$, $D(i,k)+D(j,l)$, $D(i,l)+D(j,k)$ are equal.
Write `is_additive(names, D)` that checks this condition for all $\binom{N}{4}$ quadruples
and returns `True` or `False`.
Verify that the exact matrix passes and a noisy matrix fails.

### Larger synthetic trees

Extend `make_distance_matrix` to accept an arbitrary Newick-format string such as
`"((A:0.1,B:0.2):0.3,(C:0.4,D:0.5):0.6)"` and compute the full distance matrix from it.
Use this to generate a 10-taxon example and confirm that UPGMA recovers the correct topology.

</section>
