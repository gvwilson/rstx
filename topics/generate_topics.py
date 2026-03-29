import numpy as np
import polars as pl


SEED = 7493418

N_TOPICS = 3
# 15 documents per topic gives 45 documents total, well within the 30-50 target.
DOCS_PER_TOPIC = 15
# 20-word vocabulary divided evenly: each topic owns 6 words, with 2 shared background words.
VOCAB_SIZE = 20
# Each topic owns this many consecutive words in the vocabulary.
WORDS_PER_TOPIC = 6
# Mean number of tokens per document drawn from a Poisson distribution so that
# documents have realistic length variation.
MEAN_TOKENS_PER_DOC = 40
# Weight given to a topic's own words relative to background words.
# High ratio (20 vs 0.5) keeps topic signal clear for k-means recovery.
TOPIC_WEIGHT = 20.0
BACKGROUND_WEIGHT = 0.5


# mccole: generate
def make_corpus(
    n_topics=N_TOPICS,
    docs_per_topic=DOCS_PER_TOPIC,
    vocab_size=VOCAB_SIZE,
    words_per_topic=WORDS_PER_TOPIC,
    mean_tokens=MEAN_TOKENS_PER_DOC,
    topic_weight=TOPIC_WEIGHT,
    background_weight=BACKGROUND_WEIGHT,
    seed=SEED,
):
    """Return a Polars DataFrame with columns doc_id, true_topic, and one column per word.

    Each row is a document; word columns contain integer token counts (raw TF vectors).
    true_topic records which topic generated each document and is used only in tests.
    """
    rng = np.random.default_rng(seed)
    word_forms = [f"w{i:02d}" for i in range(vocab_size)]

    records = []
    doc_id = 0
    for k in range(n_topics):
        probs = np.full(vocab_size, background_weight)
        start = k * words_per_topic
        end = start + words_per_topic
        probs[start:end] = topic_weight
        probs /= probs.sum()

        for _ in range(docs_per_topic):
            # Use Poisson-distributed length so documents vary naturally.
            n_tokens = int(rng.poisson(mean_tokens))
            # Ensure at least one token so TF vectors are non-zero.
            n_tokens = max(n_tokens, 1)
            sampled = rng.choice(vocab_size, size=n_tokens, p=probs)
            counts = np.bincount(sampled, minlength=vocab_size)
            row = {"doc_id": doc_id, "true_topic": k}
            for w, c in zip(word_forms, counts):
                row[w] = int(c)
            records.append(row)
            doc_id += 1

    return pl.DataFrame(records)
# mccole: /generate


if __name__ == "__main__":
    df = make_corpus()
    n_docs = len(df)
    word_cols = [c for c in df.columns if c.startswith("w")]
    total_tokens = df.select(word_cols).sum_horizontal().sum()
    print(f"Documents: {n_docs}, vocabulary size: {len(word_cols)}, total tokens: {total_tokens}")
    for k in range(N_TOPICS):
        subset = df.filter(pl.col("true_topic") == k)
        topic_sum = subset.select(word_cols).sum()
        top = sorted(
            zip(word_cols, topic_sum.row(0)),
            key=lambda x: x[1],
            reverse=True,
        )[:5]
        print(f"  Topic {k} top words: {[w for w, _ in top]}")
