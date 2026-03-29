import numpy as np
import polars as pl

SEED = 7493418

# Decades from 1850 to 1950 in 10-year steps (11 decades total).
DECADES = list(range(1850, 1960, 10))

# Total word tokens to generate per decade.  5000 tokens gives enough
# signal to detect three-fold frequency changes over 11 decades while
# keeping the corpus small.
TOKENS_PER_DECADE = 5000

# Background vocabulary: words with stable relative frequencies.
# 97 background words plus 3 target words = 100 total.
BACKGROUND_VOCAB_SIZE = 97

# The three target words whose true trend slopes are injected by the generator.
# Frequencies are expressed as proportions of the total token count per decade.
# slope is the change in proportion per decade (per 10-year step).
#
# telegraph: 0.005 at 1850, rising by 0.002 per decade to 0.025 at 1950.
# candle:    0.025 at 1850, falling by 0.002 per decade to 0.005 at 1950.
# steam:     0.015 throughout (zero slope, used as a no-trend control).
TARGET_WORDS = ["telegraph", "candle", "steam"]
TARGET_BASE_FREQ = [0.005, 0.025, 0.015]
TARGET_SLOPE = [0.002, -0.002, 0.000]


# mccole: generate
def make_corpus(
    decades=DECADES,
    tokens_per_decade=TOKENS_PER_DECADE,
    bg_vocab_size=BACKGROUND_VOCAB_SIZE,
    target_words=TARGET_WORDS,
    target_base_freq=TARGET_BASE_FREQ,
    target_slope=TARGET_SLOPE,
    seed=SEED,
):
    """Return a Polars DataFrame with columns decade, word, count.

    For each decade, target word frequencies follow the injected linear trend
    (base_freq + slope * decade_index).  The remaining probability mass is
    shared equally among bg_vocab_size background words and sampled with a
    multinomial draw, so each run with the same seed produces identical counts.
    """
    rng = np.random.default_rng(seed)
    records = []
    for decade_index, decade in enumerate(decades):
        # Target word frequencies for this decade.
        target_freqs = [
            base + slope * decade_index
            for base, slope in zip(target_base_freq, target_slope)
        ]
        remaining = 1.0 - sum(target_freqs)
        bg_freq = remaining / bg_vocab_size

        # Build probability vector: target words first, then background words.
        bg_words = [f"word{i:03d}" for i in range(bg_vocab_size)]
        all_words = target_words + bg_words
        all_probs = target_freqs + [bg_freq] * bg_vocab_size

        counts = rng.multinomial(tokens_per_decade, all_probs)
        for word, count in zip(all_words, counts):
            records.append({"decade": decade, "word": word, "count": int(count)})

    return pl.DataFrame(records)
# mccole: /generate


if __name__ == "__main__":
    df = make_corpus()
    n_decades = df["decade"].n_unique()
    total = df["count"].sum()
    print(f"Decades: {n_decades}, total tokens: {total}")
    target_summary = (
        df.filter(pl.col("word").is_in(TARGET_WORDS))
        .group_by(["word", "decade"])
        .agg(pl.col("count").sum())
        .sort(["word", "decade"])
    )
    print(target_summary)
