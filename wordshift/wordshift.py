import numpy as np
import polars as pl
import altair as alt
from generate_wordshift import make_corpus, TARGET_WORDS


# mccole: normalize
def normalize(df):
    """Return df with a 'freq' column: each word's share of tokens that decade.

    freq = count / sum(count) for the same decade.
    The result is a probability distribution over words for each decade,
    so values sum to 1.0 within each decade.
    """
    totals = df.group_by("decade").agg(pl.col("count").sum().alias("total"))
    return df.join(totals, on="decade").with_columns(
        (pl.col("count") / pl.col("total")).alias("freq")
    )
# mccole: /normalize


# mccole: trend
def linear_trend(decade_indices, freqs):
    """Return the OLS slope: change in normalized frequency per decade.

    Uses the closed-form ordinary least-squares formula:

        slope = sum((x - x_mean) * (y - y_mean)) / sum((x - x_mean)^2)

    where x is the decade index (0, 1, ..., n-1) and y is the normalized
    frequency.  The result is in units of frequency change per 10-year period.
    """
    x = np.asarray(decade_indices, dtype=float)
    y = np.asarray(freqs, dtype=float)
    x_c = x - x.mean()
    denom = np.dot(x_c, x_c)
    if denom == 0.0:
        return 0.0
    return float(np.dot(x_c, y) / denom)


def compute_trends(freq_df, words):
    """Return a dict mapping each word to its OLS slope (per decade).

    freq_df must have columns decade, word, freq, sorted by decade.
    Decade index 0 corresponds to the earliest decade in the data.
    """
    min_decade = freq_df["decade"].min()
    trends = {}
    for word in words:
        subset = freq_df.filter(pl.col("word") == word).sort("decade")
        decade_indices = [(d - min_decade) // 10 for d in subset["decade"].to_list()]
        freqs = subset["freq"].to_list()
        trends[word] = linear_trend(decade_indices, freqs)
    return trends
# mccole: /trend


# mccole: plot
def plot_trajectories(freq_df, words, filename):
    """Save an Altair line chart of normalized frequency over time for each word.

    Each word appears as a separate line; the x-axis is the decade and the
    y-axis is the normalized frequency (proportion of all tokens that decade).
    """
    chart_df = freq_df.filter(pl.col("word").is_in(words)).sort(["word", "decade"])
    chart = (
        alt.Chart(chart_df)
        .mark_line(point=True)
        .encode(
            x=alt.X("decade:O", title="Decade"),
            y=alt.Y("freq:Q", title="Normalized frequency"),
            color=alt.Color("word:N", title="Word"),
        )
        .properties(
            width=400,
            height=260,
            title="Word frequency trajectories by decade",
        )
    )
    chart.save(filename)
# mccole: /plot


if __name__ == "__main__":
    df = make_corpus()
    freq_df = normalize(df)
    trends = compute_trends(freq_df, TARGET_WORDS)
    print("OLS slopes (per decade):")
    for word, slope in trends.items():
        print(f"  {word}: {slope:+.5f}")
    plot_trajectories(freq_df, TARGET_WORDS, "wordshift-trajectory.svg")
    print("Saved wordshift-trajectory.svg")
