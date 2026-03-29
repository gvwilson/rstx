import numpy as np
import polars as pl
import altair as alt
from generate_vocab import make_corpus

# Window width for MATTR.  50 words balances local sensitivity and noise:
# shorter windows push window TTR artificially toward 1.0; longer windows
# approach the global TTR, losing the length-independence advantage.
MATTR_WINDOW = 50


# mccole: ttr
def type_token_ratio(words):
    """Return unique words / total words (type-token ratio, TTR).

    TTR falls as text length increases even when vocabulary richness is
    constant, because longer texts inevitably repeat high-frequency words.
    Use MATTR for length-fair comparisons across texts of different sizes.
    """
    words = list(words)
    if not words:
        return 0.0
    return len(set(words)) / len(words)


def mattr(words, window=MATTR_WINDOW):
    """Return the Moving-Average Type-Token Ratio.

    Computes TTR over each consecutive window of width `window`, then
    returns the mean of those window TTRs.  Because every window has the
    same length, the result is length-independent and can fairly compare
    texts of different sizes.  Falls back to global TTR when the text is
    shorter than the window.
    """
    words = list(words)
    n = len(words)
    if n <= window:
        return type_token_ratio(words)
    window_ttrs = [
        type_token_ratio(words[i : i + window]) for i in range(n - window + 1)
    ]
    return float(np.mean(window_ttrs))
# mccole: /ttr


# mccole: richness
def compute_richness(df, window=MATTR_WINDOW):
    """Return a DataFrame with TTR and MATTR for each text.

    Input df must have columns text_id, author, word.
    Output has columns text_id, author, ttr, mattr.
    """
    rows = []
    for text_id in df["text_id"].unique().sort():
        subset = df.filter(pl.col("text_id") == text_id)
        author = subset["author"][0]
        words = subset["word"].to_list()
        rows.append(
            {
                "text_id": int(text_id),
                "author": author,
                "ttr": type_token_ratio(words),
                "mattr": mattr(words, window),
            }
        )
    return pl.DataFrame(rows)
# mccole: /richness


# mccole: plot
def plot_richness(richness_df, filename):
    """Save a bar chart of MATTR per text, coloured by author."""
    df = richness_df.with_columns(
        pl.concat_str(
            [
                pl.col("author"),
                pl.lit(" \u2013 text "),
                (pl.col("text_id") + 1).cast(pl.String),
            ]
        ).alias("label")
    )
    chart = (
        alt.Chart(df)
        .mark_bar()
        .encode(
            x=alt.X("label:N", title="Text", sort=None),
            y=alt.Y("mattr:Q", title="MATTR", scale=alt.Scale(zero=False)),
            color=alt.Color("author:N", title="Author"),
        )
        .properties(
            width=320,
            height=250,
            title="Moving-Average Type-Token Ratio by Text",
        )
    )
    chart.save(filename)
# mccole: /plot


if __name__ == "__main__":
    df = make_corpus()
    richness = compute_richness(df)
    print(richness)
    plot_richness(richness, "vocab-richness.svg")
    print("Saved vocab-richness.svg")
