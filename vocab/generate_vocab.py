import numpy as np
import polars as pl


SEED = 7493418

# Three synthetic authors with increasingly large vocabularies.
# The 1:2:4 ratio makes differences in richness scores clearly visible.
AUTHORS = ["Author A", "Author B", "Author C"]
VOCAB_SIZES = [200, 400, 800]

# Two texts per author to check within-author consistency.
TEXTS_PER_AUTHOR = 2

# 500 words per text: long enough for MATTR windows of 50 to average over
# at least 10 non-overlapping windows, short enough to keep the corpus small.
TEXT_LENGTH = 500

# Zipf exponent for word-frequency distribution.  Exponent 1.0 matches
# Zipf's empirical law for natural languages: the k-th most common word
# appears with frequency proportional to 1/k.
ZIPF_EXP = 1.0


# mccole: generate
def make_corpus(
    authors=AUTHORS,
    vocab_sizes=VOCAB_SIZES,
    texts_per_author=TEXTS_PER_AUTHOR,
    text_length=TEXT_LENGTH,
    zipf_exp=ZIPF_EXP,
    seed=SEED,
):
    """Return a Polars DataFrame with columns text_id, author, word.

    Each author has a distinct vocabulary size; words are sampled from
    a Zipfian frequency distribution (frequency proportional to 1/rank^zipf_exp).
    A larger vocabulary size produces more distinct words per token and thus
    a higher type-token ratio.
    """
    rng = np.random.default_rng(seed)
    records = []
    text_id = 0
    for author, vocab_size in zip(authors, vocab_sizes):
        ranks = np.arange(1, vocab_size + 1, dtype=float)
        probs = ranks ** (-zipf_exp)
        probs /= probs.sum()
        word_forms = [f"w{i:04d}" for i in range(vocab_size)]
        for _ in range(texts_per_author):
            sampled = rng.choice(word_forms, size=text_length, p=probs)
            for w in sampled:
                records.append({"text_id": text_id, "author": author, "word": w})
            text_id += 1
    return pl.DataFrame(records)
# mccole: /generate


if __name__ == "__main__":
    df = make_corpus()
    n_texts = df["text_id"].n_unique()
    print(f"Texts: {n_texts}, total tokens: {len(df)}")
    for author in AUTHORS:
        subset = df.filter(pl.col("author") == author)
        n_unique = subset["word"].n_unique()
        print(f"  {author}: {n_unique} unique words in {len(subset)} tokens")
