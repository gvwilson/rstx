import polars as pl
import pytest
from generate_authorship import make_corpus, AUTHORS
from authorship import char_ngrams, build_profile, cosine_similarity, attribute


def test_char_ngrams_basic():
    # "abc" with n=2 yields exactly the bigrams "ab" and "bc".
    counts = char_ngrams("abc", 2)
    assert counts["ab"] == 1
    assert counts["bc"] == 1
    assert len(counts) == 2


def test_char_ngrams_repeated():
    # "aaa" with n=2 yields two overlapping "aa" bigrams.
    counts = char_ngrams("aaa", 2)
    assert counts["aa"] == 2


def test_profile_sums_to_one():
    # A profile built from any non-empty text must sum to 1.
    profile = build_profile(["abcabc"], n=2)
    assert sum(profile.values()) == pytest.approx(1.0)


def test_cosine_identical_profiles():
    # Identical profiles have cosine similarity exactly 1.0.
    p = {"ab": 0.5, "cd": 0.5}
    assert cosine_similarity(p, p) == pytest.approx(1.0)


def test_cosine_disjoint_profiles():
    # Profiles with no shared n-grams have cosine similarity 0.0.
    p1 = {"ab": 1.0}
    p2 = {"cd": 1.0}
    assert cosine_similarity(p1, p2) == pytest.approx(0.0)


def test_attribution_correct_author():
    # Each test text must be attributed to its true author.
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
        assert predicted == row["author"], (
            f"Misattributed: true={row['author']}, predicted={predicted}"
        )
