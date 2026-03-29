import polars as pl
import altair as alt
from collections import Counter
from generate_authorship import make_corpus, AUTHORS

# Character n-gram size.  Bigrams capture adjacent-character patterns (common
# digraphs, vowel-consonant pairs) with a compact profile; the small synthetic
# texts used here have enough tokens for reliable bigram frequency estimates.
NGRAM_SIZE = 2


# mccole: ngrams
def char_ngrams(text, n):
    """Return a Counter of character n-grams in text.

    Spaces are included so that word-boundary patterns (e.g., the bigram
    formed by the last character of one word and the space before the next)
    contribute to the profile alongside within-word patterns.
    """
    return Counter(text[i : i + n] for i in range(len(text) - n + 1))
# mccole: /ngrams


# mccole: profile
def build_profile(texts, n=NGRAM_SIZE):
    """Build a normalised character n-gram frequency profile from a list of texts.

    Counts are pooled across all texts, then divided by the total count so that
    the profile is a probability distribution over observed n-grams.
    Returns a dict mapping n-gram string to relative frequency.
    """
    counts = Counter()
    for text in texts:
        counts += char_ngrams(text, n)
    total = sum(counts.values())
    return {ng: c / total for ng, c in counts.items()}
# mccole: /profile


# mccole: similarity
def cosine_similarity(profile_a, profile_b):
    """Return the cosine similarity between two n-gram frequency profiles.

    Profiles are dicts of {ngram: frequency}.  The similarity is computed as:
      dot(a, b) / (norm(a) * norm(b))
    where only n-grams present in both profiles contribute to the dot product,
    and each norm is taken over all n-grams in that profile.
    Returns a value in [0, 1]: 1 means identical profiles, 0 means no shared n-grams.
    """
    shared = set(profile_a) & set(profile_b)
    dot = sum(profile_a[ng] * profile_b[ng] for ng in shared)
    norm_a = sum(v * v for v in profile_a.values()) ** 0.5
    norm_b = sum(v * v for v in profile_b.values()) ** 0.5
    if norm_a == 0.0 or norm_b == 0.0:
        return 0.0
    return dot / (norm_a * norm_b)
# mccole: /similarity


# mccole: attribute
def attribute(unknown_profile, candidate_profiles):
    """Return candidates ranked by cosine similarity to the unknown profile.

    unknown_profile is a dict produced by build_profile for one unknown text.
    candidate_profiles is a dict mapping author name to its profile dict.
    Returns a list of (author, similarity) pairs sorted from highest to lowest.
    """
    scores = [
        (author, cosine_similarity(unknown_profile, profile))
        for author, profile in candidate_profiles.items()
    ]
    return sorted(scores, key=lambda pair: pair[1], reverse=True)
# mccole: /attribute


# mccole: plot
def plot_similarity(ranked, filename):
    """Save a horizontal bar chart of cosine similarity scores."""
    df = pl.DataFrame([{"author": author, "similarity": sim} for author, sim in ranked])
    chart = (
        alt.Chart(df)
        .mark_bar()
        .encode(
            y=alt.Y("author:N", title="Candidate author", sort=None),
            x=alt.X(
                "similarity:Q",
                title="Cosine similarity",
                scale=alt.Scale(domain=[0.0, 1.0]),
            ),
            color=alt.Color("author:N", legend=None),
        )
        .properties(
            width=320,
            height=160,
            title="Authorship attribution by character bigram similarity",
        )
    )
    chart.save(filename)
# mccole: /plot


if __name__ == "__main__":
    df = make_corpus()
    train_df = df.filter(pl.col("role") == "train")
    test_df = df.filter(pl.col("role") == "test")

    candidate_profiles = {
        author: build_profile(
            train_df.filter(pl.col("author") == author)["text"].to_list()
        )
        for author in AUTHORS
    }

    for row in test_df.iter_rows(named=True):
        unknown_profile = build_profile([row["text"]])
        ranked = attribute(unknown_profile, candidate_profiles)
        predicted = ranked[0][0]
        correct = row["author"]
        status = "correct" if predicted == correct else "WRONG"
        print(f"{correct}: predicted {predicted} ({status})")
        for author, sim in ranked:
            print(f"  {author}: {sim:.4f}")

    plot_similarity(ranked, "authorship-similarity.svg")
    print("Saved authorship-similarity.svg")
