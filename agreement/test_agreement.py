import numpy as np
import pytest
from generate_agreement import make_ratings, N_ITEMS, N_CATS, AGREE_PROB
from agreement import contingency_table, cohen_kappa


def test_table_shape():
    # Contingency table must be square with side equal to N_CATS.
    df = make_ratings()
    table = contingency_table(
        df["rater_a"].to_numpy(), df["rater_b"].to_numpy(), N_CATS
    )
    assert table.shape == (N_CATS, N_CATS)


def test_table_sum_equals_n_items():
    # All entries in the contingency table must sum to the total item count.
    df = make_ratings()
    table = contingency_table(
        df["rater_a"].to_numpy(), df["rater_b"].to_numpy(), N_CATS
    )
    assert table.sum() == N_ITEMS


def test_perfect_agreement_kappa_one():
    # When both raters assign identical labels, every item lies on the diagonal
    # and kappa must equal 1.0 regardless of the marginal distribution.
    labels = np.array([0, 1, 2, 0, 1, 2, 0, 1, 2, 0])
    table = contingency_table(labels, labels, n_cats=3)
    kappa, _ = cohen_kappa(table)
    assert kappa == pytest.approx(1.0, abs=1e-9)


def test_chance_agreement_kappa_near_zero():
    # Independent uniform labels have P_o ≈ P_e = 1/K, so kappa ≈ 0.
    # With 300 items the sampling error is small; tolerance 0.15 is conservative.
    rng = np.random.default_rng(0)
    a = rng.integers(0, 3, size=300)
    b = rng.integers(0, 3, size=300)
    table = contingency_table(a, b, n_cats=3)
    kappa, _ = cohen_kappa(table)
    assert abs(kappa) < 0.15


def test_se_positive_and_finite():
    # Standard error must be a positive finite number.
    df = make_ratings()
    table = contingency_table(
        df["rater_a"].to_numpy(), df["rater_b"].to_numpy(), N_CATS
    )
    _, se = cohen_kappa(table)
    assert se > 0.0
    assert np.isfinite(se)


def test_kappa_close_to_agree_prob():
    # Under the generation model, expected kappa equals agree_prob when
    # marginals are uniform and N_CATS = 3.  Tolerance 0.15 accounts for
    # sampling variability with N_ITEMS = 100.
    df = make_ratings(agree_prob=AGREE_PROB)
    table = contingency_table(
        df["rater_a"].to_numpy(), df["rater_b"].to_numpy(), N_CATS
    )
    kappa, _ = cohen_kappa(table)
    assert abs(kappa - AGREE_PROB) < 0.15
