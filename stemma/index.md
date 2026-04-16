# Manuscript Stemma Reconstruction

## The Problem

-   A historical text often survives in multiple manuscript copies, each introduced
    by scribes who occasionally made errors, omitted passages, or substituted words.
-   A [%g stemma "stemma" %] is the family tree of those copies: it shows which
    manuscripts descend from which others and reconstructs lost intermediate ancestors.
-   [%g stemma_reconstruction "Stemma reconstruction" %] is the computational problem
    of recovering that tree from the patterns of shared variants across surviving manuscripts.
-   The approach here:
    -   Model each manuscript as a sequence of binary [%g variant_locus "variant loci" %].
    -   Measure pairwise dissimilarity using [%g hamming_distance "Hamming distance" %].
    -   Apply the [%g upgma "UPGMA" %] algorithm to recover the tree topology and branch lengths.
    -   Visualize the reconstructed stemma.

<div class="forma-multiple-choice" data-lang="en" markdown="1">

Two manuscripts share 12 unique errors that appear in no other copy.
A third manuscript shares none of those errors.
What does this pattern most strongly suggest?

The two manuscripts are later than the third.
:   Wrong: later position in time does not follow from shared errors; a manuscript
    copied early can still share errors with a sibling copied later.

The two manuscripts descend from a common intermediate ancestor that already
contained those errors before they were each copied.
:   Correct: shared unique errors (not present in the archetype or other branches)
    are the primary evidence for a common intermediate ancestor in stemmatic analysis.

The scribe of one manuscript copied the other directly.
:   Partly correct as one possibility, but an intermediate ancestor explains
    the same pattern without requiring direct copying; more evidence is needed
    to distinguish the two cases.

The errors are scribal conventions and do not indicate copying relationships.
:   Wrong: shared unique errors in the same positions are statistically very
    unlikely to have arisen independently and are the standard evidence for
    a copying relationship.

</div>

## Variant Loci and Hamming Distance

-   A [%g variant_locus "variant locus" %] is a specific position in a manuscript
    where at least one copy reads differently from the others.
-   We represent each manuscript as a binary sequence: 0 if the reading at a locus
    matches the [%g archetype "archetype" %], 1 if it has been corrupted.
-   The [%g hamming_distance "Hamming distance" %] between two manuscripts is the
    fraction of loci where they disagree:

<p>$$D(A, B) = \frac{\text{number of loci where } A \neq B}{\text{total loci}}$$</p>

-   Manuscripts that share a common intermediate ancestor will have a smaller Hamming
    distance to each other than to manuscripts from a different family, because they
    share inherited variants in addition to their unique ones.

## Distance Matrix for the Reference Stemma

-   The reference stemma is:

<p>$$((A:0.05,\ B:0.03):0.07,\ (C:0.06,\ D:0.04):0.05)$$</p>

-   Manuscripts A and B share intermediate ancestor alpha, which is separated from
    the archetype by 0.07.  C and D share beta, separated from the archetype by 0.05.
-   Pairwise distances are sums of branch lengths along the path between each pair.

| Pair | Distance |
|------|----------|
| A, B | 0.05 + 0.03 = 0.08 |
| A, C | 0.05 + 0.07 + 0.05 + 0.06 = 0.23 |
| A, D | 0.05 + 0.07 + 0.05 + 0.04 = 0.21 |
| B, C | 0.03 + 0.07 + 0.05 + 0.06 = 0.21 |
| B, D | 0.03 + 0.07 + 0.05 + 0.04 = 0.19 |
| C, D | 0.06 + 0.04 = 0.10 |

[%inc stemma.py mark="make-dist"%]

## The UPGMA Algorithm

-   [%g upgma "UPGMA" %] (Unweighted Pair-Group Method with Arithmetic means) builds
    a rooted tree by iteratively merging the pair of nodes with the smallest pairwise
    distance.
-   At each step:
    -   Find the pair $(i, j)$ with the smallest $D(i,j)$.
    -   Create an internal node $u$.
        Each branch from $u$ has length $D(i,j)/2$:

<p>$$\ell_i = \ell_j = \frac{D(i,j)}{2}$$</p>

-   Replace $i$ and $j$ with $u$.
    Distance from $u$ to any remaining taxon $k$ is the average:

$$D(u,k) = \frac{D(i,k) + D(j,k)}{2}$$

-   Repeat until two nodes remain, then join them with an edge equal to the remaining
    distance.
-   UPGMA assumes a constant rate of scribal error across all manuscripts (analogous
    to the molecular clock in phylogenetics).
    The neighbor-joining algorithm relaxes this assumption but requires more advanced
    mathematics.

[%inc stemma.py mark="upgma"%]

## A Worked Example

Starting with $n = 4$ manuscripts and the distances from the reference stemma:

| | A | B | C | D |
|-|---|---|---|---|
| A | — | 0.08 | 0.23 | 0.21 |
| B | | — | 0.21 | 0.19 |
| C | | | — | 0.10 |
| D | | | | — |

Step 1: the minimum distance is $D(A,B) = 0.08$.
Merge A and B into node4.
Branch lengths: $\ell_A = \ell_B = 0.08/2 = 0.04$.
Update the matrix using the UPGMA averaging rule:

$$D(\text{node4}, C) = \frac{0.23 + 0.21}{2} = 0.22$$
$$D(\text{node4}, D) = \frac{0.21 + 0.19}{2} = 0.20$$

The $3 \times 3$ matrix after step 1:

| | node4 | C | D |
|-|-------|---|---|
| node4 | — | 0.22 | 0.20 |
| C | | — | 0.10 |
| D | | | — |

Step 2: the minimum distance is $D(C,D) = 0.10$.
Merge C and D into node5.
Branch lengths: $\ell_C = \ell_D = 0.10/2 = 0.05$.
Update:

$$D(\text{node4}, \text{node5}) = \frac{0.22 + 0.20}{2} = 0.21$$

Step 3: two nodes remain (node4 and node5).
Join them with the remaining edge of length $0.21$.

The recovered edges are:

| Edge | Length |
|------|--------|
| node4 -- A | 0.04 |
| node4 -- B | 0.04 |
| node5 -- C | 0.05 |
| node5 -- D | 0.05 |
| node4 -- node5 | 0.21 |

<div class="forma-multiple-choice" data-lang="en" markdown="1">

In step 2 of the worked example, which pair is merged?

node4 and C, because D(node4, C) = 0.22 is the second-smallest entry.
:   Wrong: D(C, D) = 0.10 is smaller than D(node4, C) = 0.22 and D(node4, D) = 0.20,
    so C and D are merged first.

C and D, because D(C, D) = 0.10 is the smallest remaining distance.
:   Correct: UPGMA always merges the pair with the global minimum distance
    in the current matrix.

node4 and D, because D(node4, D) = 0.20 is smaller than D(node4, C) = 0.22.
:   Wrong: D(C, D) = 0.10 is the global minimum and is smaller than
    both cross-family distances, so C and D are merged.

</div>

## Hamming Distance Function

[%inc stemma.py mark="hamming"%]

## Visualizing the Stemma

[%inc stemma.py mark="draw"%]

[%figure
  slug="stemma-tree"
  img="stemma-tree.svg"
  alt="Unrooted tree with four blue leaf nodes labelled A, B, C, D and two grey internal nodes. A and B are connected through one internal node; C and D through another; the two internal nodes are joined by a central edge."
  caption="Reconstructed stemma for the four-manuscript reference example. The two internal (grey) nodes correspond to the lost intermediate ancestors alpha (A–B family) and beta (C–D family). Branch lengths give the fraction of loci that differ along each copying step."
%]

## Generating Synthetic Manuscripts

-   The stochastic generator simulates a known copying tree by propagating random
    mutations from the archetype through each branch.
-   Each locus flips independently with probability `MUTATION_PROB = 0.05`.
-   Only the four surviving manuscripts A, B, C, D are returned; the archetype and
    intermediate ancestors are not observed.

[%inc generate_stemma.py mark="generate"%]

## Testing

-   Hamming distance edge cases
    -   Identical sequences have distance 0.0.
    -   Sequences that differ at every locus have distance 1.0.
    -   Sequences that differ at exactly half the loci have distance 0.5.

-   Distance matrix structure
    -   The matrix must be symmetric with a zero diagonal.
    -   Within-family distances (A–B and C–D) must be smaller than any cross-family
        distance, reflecting the true two-clade topology.

-   Topology recovery
    -   A and B must share a private internal ancestor (node4), and C and D must share
        a different one (node5), with no manuscript connected to both internal nodes.
    -   UPGMA merges A and B first (D=0.08, the global minimum), then C and D
        (D=0.10, the next minimum), then joins the two internal nodes.

-   Branch-length recovery
    -   With the reference distances, UPGMA assigns branch length 0.04 to each of the
        A and B edges (half of 0.08), 0.05 to each of the C and D edges (half of 0.10),
        and 0.21 to the internal edge.
    -   Tolerance $10^{-10}$ covers only accumulated floating-point rounding.

-   All lengths positive
    -   Every branch length returned by UPGMA must be strictly positive, confirming that
        no degenerate zero-length branches were produced.

-   Stochastic generator topology
    -   Manuscripts generated by the copying simulator must also satisfy the within-family
        vs. cross-family distance inequality, confirming that the mutation rate is low
        enough for the tree signal to dominate noise.

[%inc test_stemma.py%]

<div class="forma-flashcard" data-lang="en" markdown="1">

Manuscript stemma key terms

Stemma
:   The family tree of manuscript copies of a text, showing which copies derive
    from which others; internal nodes represent lost intermediate ancestors and
    leaves represent surviving manuscripts

Stemma reconstruction
:   The computational task of recovering the stemma from patterns of shared
    variants (errors or readings) across surviving manuscripts; analogous to
    phylogenetic tree reconstruction in biology

Archetype
:   The hypothetical original manuscript from which all surviving copies ultimately
    derive; it may itself be lost, in which case it is inferred as the root of the stemma

Variant locus
:   A position in a text where at least two manuscripts have different readings;
    used as the character data for computing pairwise distances

Hamming distance
:   The fraction of corresponding positions at which two sequences differ;
    for binary variant sequences, it equals the proportion of loci where one
    manuscript has the archetype reading and the other has a variant

UPGMA
:   Unweighted Pair-Group Method with Arithmetic means; a clustering algorithm
    that builds a rooted, ultrametric tree by iteratively merging the pair of
    nodes with the smallest pairwise distance and updating distances by averaging;
    assumes a constant rate of change along all branches

</div>

<section class="exercises" markdown="1">

## Exercises

### Do the math

1.  Two manuscripts each have 100 variant loci.
    Manuscript A differs from the archetype at loci 1–10 and 21–30.
    Manuscript B differs from the archetype at loci 1–10 and 41–55.
    What is the Hamming distance between A and B?

1.  After merging A and B into node4 in the first UPGMA step,
    $D(A, C) = 0.23$ and $D(B, C) = 0.21$.
    Using the UPGMA averaging rule $D(\text{node4}, C) = (D(A,C) + D(B,C)) / 2$,
    what is $D(\text{node4}, C)$?

### Hamming distance from manuscript sequences

The `generate_stemma` module produces actual sequences, not just distances.
Write `build_distance_matrix(mss)` that accepts the dict returned by
`make_manuscripts` and computes the full $4 \times 4$ Hamming distance matrix.
Run UPGMA on this matrix and compare the recovered topology to the one from
`make_distance_matrix`.
Do the stochastic distances give the same grouping?

### Effect of mutation rate

Re-run `make_manuscripts` with `mutation_prob` values of 0.01, 0.05, 0.10, and 0.20.
For each rate, compute the distance matrix and check whether UPGMA recovers the correct
two-family topology.
At what mutation rate does the signal begin to fail, and why?

### Effect of noise on UPGMA

UPGMA assumes all branch rates are equal (the constant-rate assumption).
Add Gaussian noise to the reference distance matrix using `make_distance_matrix(noise_scale=s)`
for $s \in \{0.01, 0.02, 0.05\}$.
At what noise level does UPGMA first recover the wrong topology (A or B grouped with C or D)?
How does this compare to the noiseless case?

### Adding a contaminated manuscript

A contaminated manuscript (one that was copied partly from two different sources)
does not fit a tree model.
Add a fifth manuscript E whose sequence is a 50/50 mix of A and C.
Compute the distance matrix for all five manuscripts and run UPGMA.
Does the algorithm detect the problem, and if so, how is it visible in the
recovered tree?

</section>
