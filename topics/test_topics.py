import numpy as np
from generate_topics import make_corpus, N_TOPICS
from topics import make_tf_matrix, normalize_rows, kmeans, top_words


def test_tf_matrix_shape():
    # The TF matrix must have one row per document and one column per word.
    df = make_corpus()
    tf, word_cols = make_tf_matrix(df)
    n_docs = len(df)
    assert tf.shape == (n_docs, len(word_cols))


def test_tf_matrix_non_negative():
    # All TF entries must be non-negative integers represented as floats.
    df = make_corpus()
    tf, _ = make_tf_matrix(df)
    assert np.all(tf >= 0)


def test_normalize_rows_unit_length():
    # After normalization, every non-zero row must have L2 norm equal to 1.
    # Tolerance of 1e-10 accounts for floating-point rounding in the division.
    df = make_corpus()
    tf, _ = make_tf_matrix(df)
    tf_norm = normalize_rows(tf)
    norms = np.linalg.norm(tf_norm, axis=1)
    np.testing.assert_allclose(norms, np.ones(len(norms)), atol=1e-10)


def test_normalize_rows_zero_vector():
    # A row of all zeros must remain all zeros after normalization (no division by zero).
    matrix = np.array([[0.0, 0.0, 0.0], [1.0, 2.0, 0.0]])
    result = normalize_rows(matrix)
    np.testing.assert_array_equal(result[0], [0.0, 0.0, 0.0])


def test_top_words_order():
    # Given a hand-crafted centroid matrix, top_words must return the
    # highest-weight words first.
    centroids = np.array([[100.0, 90.0, 1.0, 0.0], [0.0, 1.0, 80.0, 70.0]])
    word_cols = ["w0", "w1", "w2", "w3"]
    result = top_words(centroids, word_cols, n_words=2)
    assert result[0] == ["w0", "w1"]
    assert result[1] == ["w2", "w3"]


def test_kmeans_label_count():
    # k-means must return exactly one label per document.
    df = make_corpus()
    tf, _ = make_tf_matrix(df)
    labels, centroids = kmeans(tf, N_TOPICS)
    assert labels.shape == (len(df),)
    assert centroids.shape[0] == N_TOPICS


def test_kmeans_label_range():
    # Every label must be a valid cluster index in [0, K).
    df = make_corpus()
    tf, _ = make_tf_matrix(df)
    labels, _ = kmeans(tf, N_TOPICS)
    assert np.all(labels >= 0)
    assert np.all(labels < N_TOPICS)


def test_kmeans_recovers_topics_normalized():
    # After k-means on normalized TF vectors, documents from the same
    # generating topic must all be assigned to the same cluster.
    # The mapping from true topics to cluster indices may be any permutation.
    df = make_corpus()
    tf, _ = make_tf_matrix(df)
    tf_norm = normalize_rows(tf)
    labels, _ = kmeans(tf_norm, N_TOPICS)
    true_topics = df["true_topic"].to_list()
    for k in range(N_TOPICS):
        group_labels = [
            labels[i] for i, t in enumerate(true_topics) if t == k
        ]
        assert len(set(group_labels)) == 1, (
            f"True-topic group {k} split across clusters: {group_labels}"
        )
