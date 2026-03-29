import numpy as np
import altair as alt

from generate_agreement import make_ratings, N_CATS, SEED, N_ITEMS

# Underlying agreement probabilities used to demonstrate how kappa varies.
SCENARIOS = [0.2, 0.4, 0.6, 0.8, 0.95]


# mccole: table
def contingency_table(rater_a, rater_b, n_cats):
    """Return a (n_cats x n_cats) integer contingency table.

    table[i, j] is the number of items for which rater A assigned
    category i and rater B assigned category j.  Diagonal entries
    represent agreement; off-diagonal entries represent disagreement.
    """
    table = np.zeros((n_cats, n_cats), dtype=int)
    for a, b in zip(rater_a, rater_b):
        table[a, b] += 1
    return table
# mccole: /table


# mccole: kappa
def cohen_kappa(table):
    """Return Cohen's kappa and its standard error from a contingency table.

    Parameters
    ----------
    table : (K, K) integer array; table[i, j] = count where rater A said i
            and rater B said j

    Returns
    -------
    kappa : Cohen's kappa, correcting for chance agreement
    se    : asymptotic standard error of kappa

    Derivation
    ----------
    N   = total item count
    P_o = sum(diagonal) / N               (observed agreement proportion)
    p_i = row_i_sum / N                   (rater A's marginal for category i)
    q_j = col_j_sum / N                   (rater B's marginal for category j)
    P_e = sum_i(p_i * q_i)               (expected agreement under independence)
    kappa = (P_o - P_e) / (1 - P_e)

    The standard error uses the asymptotic formula of Cohen (1960):
    se = sqrt(P_o * (1 - P_o) / (N * (1 - P_e)^2))
    This approximates SE(P_o) = sqrt(P_o*(1-P_o)/N) and propagates it
    through the kappa formula, ignoring variability in P_e.
    """
    n = table.sum()
    p_o = table.diagonal().sum() / n
    row_sums = table.sum(axis=1) / n
    col_sums = table.sum(axis=0) / n
    p_e = float((row_sums * col_sums).sum())
    kappa = (p_o - p_e) / (1.0 - p_e)
    se = np.sqrt(p_o * (1.0 - p_o) / (n * (1.0 - p_e) ** 2))
    return float(kappa), float(se)
# mccole: /kappa


# mccole: plot
def plot_kappa_scenarios(scenarios, n_items, n_cats, seed, filename):
    """Save a bar chart of kappa values across underlying agreement scenarios."""
    records = []
    for prob in scenarios:
        df = make_ratings(n_items=n_items, n_cats=n_cats, agree_prob=prob, seed=seed)
        table = contingency_table(
            df["rater_a"].to_numpy(), df["rater_b"].to_numpy(), n_cats
        )
        kappa, se = cohen_kappa(table)
        records.append(
            {
                "agree_prob": str(prob),
                "kappa": round(kappa, 4),
                "se": round(se, 4),
            }
        )

    chart = (
        alt.Chart(alt.Data(values=records))
        .mark_bar()
        .encode(
            x=alt.X("agree_prob:O", title="Underlying agreement probability"),
            y=alt.Y("kappa:Q", title="Cohen's kappa", scale=alt.Scale(domain=[0, 1])),
            color=alt.Color(
                "kappa:Q",
                scale=alt.Scale(scheme="blues"),
                legend=None,
            ),
        )
        .properties(
            title="Cohen's kappa across agreement scenarios (N = 100, K = 3)",
            width=360,
            height=280,
        )
    )
    chart.save(filename)
# mccole: /plot


if __name__ == "__main__":
    for prob in SCENARIOS:
        df = make_ratings(n_items=N_ITEMS, n_cats=N_CATS, agree_prob=prob, seed=SEED)
        table = contingency_table(
            df["rater_a"].to_numpy(), df["rater_b"].to_numpy(), N_CATS
        )
        kappa, se = cohen_kappa(table)
        print(f"agree_prob={prob:.2f}:  kappa = {kappa:.3f}  SE = {se:.3f}")
    plot_kappa_scenarios(SCENARIOS, N_ITEMS, N_CATS, SEED, "agreement-kappa.svg")
    print("Saved agreement-kappa.svg")
