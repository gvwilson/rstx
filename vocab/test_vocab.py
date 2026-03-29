import pytest
from generate_vocab import make_corpus
from vocab import type_token_ratio, mattr, compute_richness
import polars as pl


def test_ttr_all_unique():
    # When every word is distinct the TTR is exactly 1.0.
    assert type_token_ratio(["a", "b", "c", "d"]) == pytest.approx(1.0)


def test_ttr_all_same():
    # When the same word is repeated n times the TTR is 1/n.
    assert type_token_ratio(["x"] * 10) == pytest.approx(0.1)


def test_ttr_empty():
    # Empty input returns 0.0 without raising an exception.
    assert type_token_ratio([]) == pytest.approx(0.0)


def test_mattr_short_text_equals_ttr():
    # When the text is shorter than the window, MATTR falls back to global TTR.
    words = ["a", "b", "c"]
    assert mattr(words, window=10) == pytest.approx(type_token_ratio(words))


def test_mattr_window_equals_length():
    # When text length equals the window width there is exactly one window,
    # so MATTR equals TTR exactly.
    words = ["a", "b", "c", "a"]
    assert mattr(words, window=4) == pytest.approx(type_token_ratio(words))


def test_richness_order_by_vocab_size():
    # Mean MATTR must increase with vocabulary size: Author A (200) <
    # Author B (400) < Author C (800).  The Zipfian generator guarantees
    # that a larger vocabulary produces more distinct tokens per window.
    df = make_corpus()
    richness = compute_richness(df)
    means = richness.group_by("author").agg(pl.col("mattr").mean()).sort("author")
    mattr_vals = means["mattr"].to_list()
    # Authors sort alphabetically: A, B, C -- matching ascending vocab sizes.
    assert mattr_vals[0] < mattr_vals[1] < mattr_vals[2]
