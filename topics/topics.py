import numpy as np
import polars as pl
import altair as alt
from generate_topics import make_corpus, N_TOPICS

# Number of clusters to find; must match the number of generating topics
# so that topic recovery is meaningful.
K = N_TOPICS

# Maximum k-means iterations before declaring convergence.
# 100 is sufficient for this small synthetic corpus.
MAX_ITER = 100

# RNG seed for reproducible centroid initialization.
SEED = 7493418


# mccole: tf_matrix
def make_tf_matrix(df):
    """Return a (n_docs, vocab_size) NumPy array of raw term-frequency counts.

    The first two columns of df are doc_id and true_topic; remaining columns
    are word counts.  Returns the matrix and the list of word column names.
    """
    word_cols = [c for c in df.columns if c not in ("doc_id", "true_topic")]
    tf = df.select(word_cols).to_numpy().astype(float)
    return tf, word_cols
# mccole: /tf_matrix


# mccole: normalize
def normalize_rows(matrix):
    """Return a copy of matrix with each row divided by its L2 norm.

    Documents with zero norm (all-zero rows) are left as zeros.
    Normalizing makes k-means compare the shape of word use rather than
    total volume: a short document and a long document about the same
    topic end up close together after normalization.
    """
    norms = np.linalg.norm(matrix, axis=1, keepdims=True)
    # Avoid division by zero for any all-zero document.
    safe_norms = np.where(norms == 0, 1.0, norms)
    return matrix / safe_norms
# mccole: /normalize


# mccole: kmeans
def kmeans(matrix, k, seed=SEED, max_iter=MAX_ITER):
    """Run k-means clustering and return (labels, centroids).

    Algorithm:
      1. Choose k distinct rows of matrix at random as initial centroids.
      2. Assign each row to the nearest centroid (Euclidean distance).
      3. Update each centroid as the mean of its assigned rows.
      4. Repeat steps 2-3 until assignments stop changing or max_iter is reached.

    Returns:
      labels     1-D integer array of cluster indices, one per document.
      centroids  (k, vocab_size) array of final centroid vectors.
    """
    rng = np.random.default_rng(seed)
    n_docs = matrix.shape[0]
    # Step 1: choose k random documents as initial centroids.
    init_indices = rng.choice(n_docs, size=k, replace=False)
    centroids = matrix[init_indices].copy()

    labels = np.zeros(n_docs, dtype=int)
    for _ in range(max_iter):
        # Step 2: assign each document to the nearest centroid.
        # Compute squared Euclidean distances via broadcasting.
        diffs = matrix[:, np.newaxis, :] - centroids[np.newaxis, :, :]
        sq_distances = (diffs ** 2).sum(axis=2)
        new_labels = np.argmin(sq_distances, axis=1)

        # Step 3: update centroids.
        new_centroids = np.zeros_like(centroids)
        for c in range(k):
            members = matrix[new_labels == c]
            if len(members) > 0:
                new_centroids[c] = members.mean(axis=0)
            else:
                # Empty cluster: reinitialize to a random document.
                new_centroids[c] = matrix[rng.integers(n_docs)]

        # Stop when assignments no longer change.
        if np.array_equal(new_labels, labels):
            break
        labels = new_labels
        centroids = new_centroids

    return labels, centroids
# mccole: /kmeans


# mccole: top_words
def top_words(centroids, word_cols, n_words=5):
    """Return a list of k lists, each with the top n_words for that cluster.

    The top words for a cluster are those with the highest value in the
    centroid vector: high centroid coordinates mean those words appear most
    often (on average) among documents in that cluster.
    """
    result = []
    for c in range(centroids.shape[0]):
        indices = np.argsort(centroids[c])[::-1][:n_words]
        result.append([word_cols[i] for i in indices])
    return result
# mccole: /top_words


# mccole: plot
def plot_clusters(labels, true_topics, centroids, word_cols, filename):
    """Save a heatmap of centroid word weights, one row per cluster."""
    n_clusters, vocab_size = centroids.shape
    rows = []
    for c in range(n_clusters):
        for j, w in enumerate(word_cols):
            rows.append(
                {
                    "cluster": f"cluster {c}",
                    "word": w,
                    "weight": float(centroids[c, j]),
                }
            )
    df = pl.DataFrame(rows)
    chart = (
        alt.Chart(df)
        .mark_rect()
        .encode(
            x=alt.X("word:N", title="Word", sort=word_cols),
            y=alt.Y("cluster:N", title="Cluster"),
            color=alt.Color(
                "weight:Q",
                title="Centroid weight",
                scale=alt.Scale(scheme="blues"),
            ),
        )
        .properties(
            width=400,
            height=120,
            title="Cluster centroids (word weights)",
        )
    )
    chart.save(filename)
# mccole: /plot


if __name__ == "__main__":
    df = make_corpus()
    tf, word_cols = make_tf_matrix(df)
    true_topics = df["true_topic"].to_list()

    print("=== Raw TF ===")
    labels_raw, centroids_raw = kmeans(tf, K)
    words_raw = top_words(centroids_raw, word_cols)
    for c, ws in enumerate(words_raw):
        print(f"  Cluster {c}: {', '.join(ws)}")

    print("=== Normalized TF ===")
    tf_norm = normalize_rows(tf)
    labels_norm, centroids_norm = kmeans(tf_norm, K)
    words_norm = top_words(centroids_norm, word_cols)
    for c, ws in enumerate(words_norm):
        print(f"  Cluster {c}: {', '.join(ws)}")

    plot_clusters(labels_norm, true_topics, centroids_norm, word_cols, "topics-heatmap.svg")
    print("Saved topics-heatmap.svg")
