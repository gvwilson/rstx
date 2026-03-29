import numpy as np
import polars as pl
import altair as alt


SEED = 7493418
N_AGENTS = 200  # number of agents in the exchange economy
N_STEPS = 2000  # number of pairwise exchanges to simulate


# mccole: gini
def gini(wealth):
    """Gini coefficient of a wealth distribution.

    Uses the sorted-array formula:
        G = (2 * sum(i * w_(i)) - (n+1) * sum(w)) / (n * sum(w))
    where indices i are 1-based and w_(i) is the i-th smallest wealth.
    Returns 0 for perfect equality and (n-1)/n when one agent holds everything.
    """
    n = len(wealth)
    sorted_w = np.sort(wealth)
    indices = np.arange(1, n + 1)
    total = np.sum(sorted_w)
    return (2.0 * np.dot(indices, sorted_w) - (n + 1) * total) / (n * total)
# mccole: /gini


# mccole: simulate
def simulate_exchange(n_agents=N_AGENTS, n_steps=N_STEPS, seed=SEED):
    """Run the random-exchange wealth model.

    Agents start with equal wealth of 1.0 each.  At every step two distinct
    agents are chosen uniformly at random; the poorer transfers a uniformly
    random fraction of their own wealth to the richer.  Total wealth is
    conserved exactly at n_agents throughout.

    Returns (final_wealth, gini_history) where gini_history[t] is the Gini
    coefficient after t exchanges (gini_history[0] is the initial value 0.0).
    """
    rng = np.random.default_rng(seed)
    wealth = np.ones(n_agents, dtype=float)
    gini_history = np.empty(n_steps + 1)
    gini_history[0] = gini(wealth)
    for step in range(n_steps):
        i, j = rng.choice(n_agents, size=2, replace=False)
        if wealth[i] > wealth[j]:
            i, j = j, i  # i is now the poorer agent
        fraction = rng.uniform(0.0, 1.0)
        transfer = fraction * wealth[i]
        wealth[i] -= transfer
        wealth[j] += transfer
        gini_history[step + 1] = gini(wealth)
    return wealth, gini_history
# mccole: /simulate


# mccole: lorenz
def lorenz_curve(wealth):
    """Return (population_fractions, wealth_fractions) arrays for the Lorenz curve.

    Both arrays start at (0, 0) and end at (1, 1).  The area between the
    curve and the 45-degree equality line equals G/2, where G is the Gini
    coefficient.
    """
    n = len(wealth)
    sorted_w = np.sort(wealth)
    cum_w = np.cumsum(sorted_w)
    pop_fracs = np.arange(0, n + 1) / n
    wealth_fracs = np.concatenate([[0.0], cum_w / cum_w[-1]])
    return pop_fracs, wealth_fracs
# mccole: /lorenz


# mccole: plot_gini
def plot_gini_trajectory(gini_history, filename):
    """Save a line chart of the Gini coefficient at each exchange step."""
    df = pl.DataFrame(
        {
            "step": np.arange(len(gini_history)),
            "gini": gini_history,
        }
    )
    chart = (
        alt.Chart(df)
        .mark_line(color="steelblue", strokeWidth=2)
        .encode(
            x=alt.X("step:Q", title="Exchange step"),
            y=alt.Y(
                "gini:Q", scale=alt.Scale(domain=[0.0, 1.0]), title="Gini coefficient"
            ),
        )
        .properties(width=450, height=300, title="Gini coefficient over time")
    )
    chart.save(filename)
# mccole: /plot_gini


# mccole: plot_lorenz
def plot_lorenz_curve(wealth, filename):
    """Save a Lorenz curve with the line of equality overlaid."""
    pop_fracs, wealth_fracs = lorenz_curve(wealth)
    df_lorenz = pl.DataFrame({"population": pop_fracs, "wealth": wealth_fracs})
    df_equal = pl.DataFrame({"population": [0.0, 1.0], "wealth": [0.0, 1.0]})
    lorenz_line = (
        alt.Chart(df_lorenz)
        .mark_line(color="steelblue", strokeWidth=2)
        .encode(
            x=alt.X("population:Q", title="Cumulative share of population"),
            y=alt.Y("wealth:Q", title="Cumulative share of wealth"),
        )
    )
    equal_line = (
        alt.Chart(df_equal)
        .mark_line(color="gray", strokeDash=[4, 4], strokeWidth=1)
        .encode(x="population:Q", y="wealth:Q")
    )
    chart = alt.layer(equal_line, lorenz_line).properties(
        width=350, height=350, title="Lorenz curve after 2000 exchanges"
    )
    chart.save(filename)
# mccole: /plot_lorenz


if __name__ == "__main__":
    final_wealth, gini_history = simulate_exchange()
    print(f"Initial Gini:            {gini_history[0]:.4f}")
    print(f"Final Gini:              {gini_history[-1]:.4f}")
    print(
        f"Total wealth conserved:  {np.sum(final_wealth):.6f}  (expected {N_AGENTS}.0)"
    )
    plot_gini_trajectory(gini_history, "wealth-gini.svg")
    print("Saved wealth-gini.svg")
    plot_lorenz_curve(final_wealth, "wealth-lorenz.svg")
    print("Saved wealth-lorenz.svg")
