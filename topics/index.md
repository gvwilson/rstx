# Topic Modeling a Document Corpus

## The Problem

-   A corpus of documents often covers several recurring themes, but labeling each
    document by hand is slow and subjective.
-   Topic modeling discovers those themes automatically by finding groups of words
    that tend to appear together across documents.
-   The approach here:
    -   Generate a synthetic [%g bag_of_words "bag-of-words" %] corpus in which
        each document is produced by one of three topics, each with a distinct vocabulary.
    -   Represent each document as a [%g term_frequency "term-frequency" %] (TF) vector:
        one integer per vocabulary word recording how often that word appears.
    -   Run [%g k_means "k-means clustering" %] on those vectors to find groups of
        documents that use similar words.
    -   Compare results using raw TF counts and length-normalized TF vectors.

<div class="forma-multiple-choice" data-lang="en" markdown="1">

Why is topic modeling called an "unsupervised" method?

Because it requires labeled training documents to identify topics.
:   Wrong: topic modeling discovers structure from the text alone, with no labels
    provided; that is precisely why it is called unsupervised.

Because it infers topic structure from the documents themselves, with no
pre-specified topic labels.
:   Correct: the algorithm finds groupings based entirely on patterns of word use,
    without any human-assigned category names or example documents.

Because it only works on documents where the topics are already known.
:   Wrong: the method is designed for cases where topics are unknown; if topics
    were known, supervised classification would be used instead.

Because it ignores word order within a document.
:   Wrong: ignoring word order (the bag-of-words assumption) is a modeling choice,
    not the reason for the label "unsupervised."

</div>

## Generating Synthetic Data

-   The corpus has three topics; each topic owns six consecutive words from a twenty-word vocabulary.
-   Words from a topic's own set are sampled with weight 20; all other words receive
    weight 0.5, so about 96% of each document's tokens come from the document's true topic.
-   Document lengths vary because token counts are drawn from a Poisson distribution
    with mean 40; this mimics realistic corpora where documents differ in length.
-   Each row in the resulting DataFrame is one document with integer word-count columns.
-   `true_topic` records which topic generated each document and is used only in tests.

[%inc generate_topics.py mark="generate"%]

## Building TF Vectors

-   A [%g term_frequency "term-frequency" %] vector for document $d$ is the vector
    $\mathbf{t}_d \in \mathbb{Z}_{\geq 0}^V$ where $V$ is the vocabulary size and
    $t_{dw}$ counts how many times word $w$ appears in document $d$.
-   Extracting word-count columns from the DataFrame and converting to a NumPy matrix
    gives a two-dimensional array with shape $(\text{n\_docs},\, V)$.

[%inc topics.py mark="tf_matrix"%]

## Length Normalization

-   Raw TF vectors are proportional to document length: a document twice as long will
    have roughly twice the counts for every word, even if its topic mix is identical.
-   Dividing each document vector by its [%g term_frequency "L2 norm" %] removes this
    length effect:

<p>$$\hat{\mathbf{t}}_d = \frac{\mathbf{t}_d}{\|\mathbf{t}_d\|_2}$$</p>

-   After normalization, two documents about the same topic are close to each other
    in Euclidean space even if one is three times longer than the other.
-   This is analogous to comparing the shape of word use rather than its volume.

[%inc topics.py mark="normalize"%]

<div class="forma-multiple-choice" data-lang="en" markdown="1">

A document has TF vector $[6, 0, 2, 0]$. What is its L2 norm?

$\sqrt{6}$
:   Wrong: the L2 norm squares each entry before summing: $\sqrt{6^2 + 0^2 + 2^2 + 0^2} = \sqrt{40}$.

$\sqrt{40}$
:   Correct: $\|\mathbf{t}\|_2 = \sqrt{6^2 + 0^2 + 2^2 + 0^2} = \sqrt{36 + 4} = \sqrt{40}$.

8
:   Wrong: adding the entries directly gives 8, but the L2 norm takes the square root of
    the sum of squares, not the sum itself.

$\sqrt{8}$
:   Wrong: $\sqrt{8}$ would be the L2 norm of $[2, 2, 2, 2]$, not of $[6, 0, 2, 0]$.

</div>

## The K-Means Algorithm

-   [%g k_means "K-means" %] partitions $n$ documents into $K$ clusters by
    alternating two steps until assignments stop changing:
    1.  Assign each document to the nearest centroid (smallest Euclidean distance).
    2.  Update each centroid as the coordinate-wise mean of all documents in that cluster.
-   The centroid of a cluster is the "average document" for that cluster: its
    $w$-th coordinate is the average count (or average normalized count) of word
    $w$ across all documents assigned to the cluster.
-   The assignment distance between document $\mathbf{t}$ and centroid $\mathbf{c}$
    is the Euclidean distance:

<p>$$d(\mathbf{t},\,\mathbf{c}) = \sqrt{\sum_{w=1}^{V}(t_w - c_w)^2}$$</p>

-   The algorithm needs $K$ to be chosen before running it; topic modeling uses domain
    knowledge or model selection criteria to pick $K$.

[%inc topics.py mark="kmeans"%]

<div class="forma-numeric-entry" data-correct="5" data-tolerance="0.001" data-lang="en" markdown="1">

Consider two document vectors $\mathbf{a} = [3, 4]$ and centroid $\mathbf{c} = [0, 0]$.
What is the Euclidean distance $d(\mathbf{a}, \mathbf{c})$?

</div>

## Top Words Per Cluster

-   After k-means converges, the top words for each cluster are those with the highest
    value in the cluster's centroid vector.
-   A high centroid coordinate for word $w$ means that documents in the cluster tend
    to use word $w$ frequently, making it a good label for the cluster's theme.

[%inc topics.py mark="top_words"%]

## Raw TF vs. Normalized TF

-   With raw TF vectors, longer documents pull centroids upward uniformly across all words,
    which can make centroid coordinates reflect document length as much as topic content.
-   With normalized TF vectors, centroids reflect the typical word-use pattern (shape)
    for documents in each cluster, independent of length.
-   For this synthetic corpus both approaches recover the three topics because all documents
    have similar Poisson-distributed lengths; in a corpus with very unequal document lengths,
    normalization matters more.

## Visualizing Cluster Centroids

[%inc topics.py mark="plot"%]

[%figure
  slug="topics-heatmap"
  img="topics-heatmap.svg"
  alt="A heatmap with three cluster rows and twenty word columns. Each row shows a band of dark blue cells concentrated in one-third of the vocabulary (words w00-w05, w06-w11, or w12-w17), with near-white elsewhere. The three dark bands do not overlap."
  caption="Cluster centroid weights after k-means on normalized TF vectors. Each cluster's centroid has high weight on the six words belonging to its generating topic and near-zero weight on the rest."
%]

<div class="forma-multiple-choice" data-lang="en" markdown="1">

What does the centroid of a k-means cluster represent?

The document in the cluster that was chosen as the initial seed.
:   Wrong: the initial seed is used only for initialization; the centroid is updated
    after every assignment step and is usually no longer equal to any single document.

The coordinate-wise mean of all documents currently assigned to the cluster.
:   Correct: at each iteration the centroid is recomputed as the mean vector of its
    member documents, so it represents the "average" document in that cluster.

The document in the cluster that is farthest from all other clusters.
:   Wrong: that would be a notion from outlier detection, not from k-means; the
    centroid minimizes the sum of squared distances to its members, not maximizes them.

The document with the highest total word count in the cluster.
:   Wrong: the centroid is a mean over all cluster members, not a selection of one
    particular member based on its total count.

</div>

## Testing

-   TF matrix shape
    -   `make_tf_matrix` must return an array with one row per document and one column per
        vocabulary word; all entries must be non-negative.
-  Normalized rows have unit length
    -   After `normalize_rows`, every row must satisfy $\|\hat{\mathbf{t}}_d\|_2 = 1$.
    -   Tolerance of $10^{-10}$ is used because floating-point division introduces rounding
        errors at the level of machine epsilon ($\approx 2\times 10^{-16}$ for 64-bit floats).
    -   A zero row must remain zero (no division by zero).
-   Top-words order
    -   Given a hand-crafted centroid matrix with known highest-weight words, `top_words`
        must return them in descending order.
-   Topic recovery
    -   After running k-means with normalized TF on the synthetic corpus, every document
        in the same true-topic group must be assigned to the same cluster.
        The true-to-cluster mapping may be any permutation.

[%inc test_topics.py%]

<div class="forma-flashcard" data-lang="en" markdown="1">

Topic modeling key terms

Bag of words
:   A document representation that records only which words appear and how often,
    discarding word order; used here because topics are defined by co-occurrence
    patterns rather than syntactic structure

Term frequency (TF) vector
:   A vector with one entry per vocabulary word giving the count of that word in
    a document; raw TF is proportional to document length; normalizing by the L2
    norm removes the length effect and captures only the shape of word use

K-means clustering
:   An iterative algorithm that assigns each document to its nearest centroid, then
    updates centroids as the mean of their members; repeats until assignments stop
    changing; requires the number of clusters $K$ to be specified in advance

Centroid
:   The coordinate-wise mean of all documents assigned to a cluster; high centroid
    coordinates indicate words that are used most often in that cluster and serve
    as labels for the cluster's theme

L2 normalization
:   Dividing a vector by its Euclidean length $\|\mathbf{t}\|_2 = \sqrt{\sum_w t_w^2}$
    so that the result has unit length; makes k-means compare the shape of word use
    rather than total token volume

</div>

## From K-Means to Probabilistic Topic Models

    -   K-means assigns each document to exactly one cluster.
    -   In practice, a document can be about more than one topic: a biology paper might
        discuss both genetics and statistics.
    -   Latent Dirichlet Allocation (LDA) is a probabilistic generalization of this idea:
        rather than assigning each document to exactly one topic, it allows each document
        to be a mixture of topics, and each topic to be a distribution over words.
    -   LDA inference uses Bayesian methods (specifically collapsed Gibbs sampling, a form
        of Markov chain Monte Carlo) and requires more advanced statistics than k-means.

<section class="exercises" markdown="1">

## Exercises

### Effect of K

Run k-means on the normalized TF matrix with $K \in \{2, 3, 4, 5\}$.
For $K = 3$, the three clusters should match the three generating topics.
What happens to the cluster centroid heatmap when $K = 4$? Does the extra cluster
split one of the true topics in two, or does it find a different grouping?
Explain why increasing $K$ beyond the true number of topics does not necessarily
improve the result.

### Effect of initialization

K-means can converge to different solutions depending on which documents are
chosen as initial centroids.
Run k-means on the normalized TF matrix 10 times, each time with a different
random seed.
How often does the algorithm recover all three true topics?
What happens in the runs that fail to recover them?

### Mixed documents

Modify `make_corpus` to generate five documents that draw 50% of their tokens
from topic 0 and 50% from topic 1.
Add those documents to the corpus and re-run k-means.
Which cluster do the mixed documents end up in?
Plot the centroid weights for those documents alongside the cluster centroids
to show why the algorithm places them where it does.

### Inertia

The within-cluster sum of squared distances (inertia) measures how tightly
packed each cluster is:

<p>$$\text{inertia} = \sum_{k=0}^{K-1} \sum_{d:\,\text{label}(d)=k} \|\hat{\mathbf{t}}_d - \mathbf{c}_k\|_2^2$$</p>

Implement `inertia(matrix, labels, centroids)` and plot inertia against $K$
for $K \in \{2, 3, 4, 5, 6\}$.
The "elbow" in the plot (where inertia stops dropping sharply) is a common
heuristic for choosing $K$.
Does the elbow occur at $K = 3$ for this corpus?

</section>
