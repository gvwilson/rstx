import numpy as np
import polars as pl

SEED = 7493418

# Number of observations rated by both raters.
N_ITEMS = 100

# Number of rating categories (e.g., thematic codes in qualitative research).
N_CATS = 3

# Default underlying agreement probability for the main scenario.
# When marginals are uniform and N_CATS = 3, the expected Cohen's kappa
# equals AGREE_PROB.  See the lesson for the derivation.
AGREE_PROB = 0.7


# mccole: generate
def make_ratings(n_items=N_ITEMS, n_cats=N_CATS, agree_prob=AGREE_PROB, seed=SEED):
    """Return a Polars DataFrame of paired rater label vectors.

    Columns:
        rater_a -- integer category label from rater A (0 to n_cats - 1)
        rater_b -- integer category label from rater B (0 to n_cats - 1)

    For each item, with probability agree_prob both raters draw the same
    category uniformly from 0..n_cats-1.  With probability 1 - agree_prob
    each rater independently draws a category uniformly.  Under this model
    the expected Cohen's kappa equals agree_prob when marginals are uniform
    (see lesson for the derivation).
    """
    rng = np.random.default_rng(seed)
    a_labels = np.empty(n_items, dtype=int)
    b_labels = np.empty(n_items, dtype=int)
    for i in range(n_items):
        if rng.random() < agree_prob:
            label = int(rng.integers(0, n_cats))
            a_labels[i] = label
            b_labels[i] = label
        else:
            a_labels[i] = int(rng.integers(0, n_cats))
            b_labels[i] = int(rng.integers(0, n_cats))
    return pl.DataFrame({"rater_a": a_labels.tolist(), "rater_b": b_labels.tolist()})
# mccole: /generate


if __name__ == "__main__":
    for prob in [0.3, 0.5, 0.7, 0.9]:
        df = make_ratings(agree_prob=prob, seed=SEED)
        n_agree = df.filter(pl.col("rater_a") == pl.col("rater_b")).height
        print(f"agree_prob={prob:.1f}: {n_agree}/{df.height} matching pairs")
