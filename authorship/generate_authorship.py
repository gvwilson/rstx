import numpy as np
import polars as pl


SEED = 7493418

AUTHORS = ["Author A", "Author B", "Author C"]

# 15-character alphabet split evenly among three authors.
# Author A prefers the first 5 characters, B the middle 5, C the last 5.
CHARS = "abcdefghijklmno"
N_CHARS = len(CHARS)  # 15
CHARS_PER_AUTHOR = N_CHARS // len(AUTHORS)  # 5

# Preferred characters are sampled PREFERRED_WEIGHT times more often than others.
# A 5:1 ratio produces clearly separable profiles for a corpus of this size.
PREFERRED_WEIGHT = 5.0
OTHER_WEIGHT = 1.0

WORD_LENGTH_MIN = 3
WORD_LENGTH_MAX = 6
WORDS_PER_TEXT = 150

# First TEXTS_PER_AUTHOR - 1 texts per author are training texts; the last is a test text.
TEXTS_PER_AUTHOR = 4


# mccole: generate
def make_corpus(
    authors=AUTHORS,
    chars=CHARS,
    preferred_weight=PREFERRED_WEIGHT,
    other_weight=OTHER_WEIGHT,
    chars_per_author=CHARS_PER_AUTHOR,
    word_length_min=WORD_LENGTH_MIN,
    word_length_max=WORD_LENGTH_MAX,
    words_per_text=WORDS_PER_TEXT,
    texts_per_author=TEXTS_PER_AUTHOR,
    seed=SEED,
):
    """Return a Polars DataFrame with columns author, text_id, role, text.

    role is 'train' for the first texts_per_author-1 texts per author and
    'test' for the last.  Each text is a space-separated sequence of synthetic
    words; each author's words are biased toward their preferred character set
    so that character n-gram profiles are clearly distinct between authors.
    """
    rng = np.random.default_rng(seed)
    n_chars = len(chars)
    records = []
    text_id = 0

    for a_idx, author in enumerate(authors):
        probs = np.full(n_chars, other_weight)
        start = a_idx * chars_per_author
        end = start + chars_per_author
        probs[start:end] = preferred_weight
        probs /= probs.sum()

        for t_idx in range(texts_per_author):
            words = []
            for _ in range(words_per_text):
                length = int(rng.integers(word_length_min, word_length_max + 1))
                word = "".join(
                    chars[int(rng.choice(n_chars, p=probs))] for _ in range(length)
                )
                words.append(word)
            role = "test" if t_idx == texts_per_author - 1 else "train"
            records.append(
                {
                    "author": author,
                    "text_id": text_id,
                    "role": role,
                    "text": " ".join(words),
                }
            )
            text_id += 1

    return pl.DataFrame(records)
# mccole: /generate


if __name__ == "__main__":
    df = make_corpus()
    for row in df.iter_rows(named=True):
        snippet = row["text"][:60]
        print(f"{row['author']} ({row['role']}): {snippet}...")
