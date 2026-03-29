import numpy as np
from scipy.integrate import solve_ivp
import polars as pl
import altair as alt

# mccole: params
# Rate parameters (arbitrary units).
# PREY_BIRTH: per-capita prey growth rate in the absence of predators.
# PREDATION:  rate at which one predator removes prey (per predator per prey).
# PRED_GROWTH: rate at which predators gain from eating prey (per predator per prey).
# PRED_DEATH: per-capita predator death rate in the absence of prey.
PREY_BIRTH = 1.0
PREDATION = 0.1
PRED_GROWTH = 0.075
PRED_DEATH = 1.5

# Equilibrium populations: the fixed point of the ODE system.
# Setting dx/dt = 0 and dy/dt = 0 gives x* = PRED_DEATH/PRED_GROWTH
# and y* = PREY_BIRTH/PREDATION.
PREY_EQ = PRED_DEATH / PRED_GROWTH  # 20.0
PRED_EQ = PREY_BIRTH / PREDATION  # 10.0

# Initial conditions: start above the prey equilibrium and below the
# predator equilibrium to produce a visible oscillation.
PREY_INIT = 25.0
PRED_INIT = 5.0

# Simulate for ~10 complete cycles.  The small-oscillation period
# (linearised around equilibrium) is 2π / sqrt(PREY_BIRTH * PRED_DEATH).
# The true nonlinear period is ~5.30 for these initial conditions,
# so T_MAX = 53.0 covers roughly 10 full cycles.
PERIOD_APPROX = 2 * np.pi / np.sqrt(PREY_BIRTH * PRED_DEATH)
T_MAX = 53.0

# Dense output resolution: one point per 0.05 time units.
N_EVAL = int(T_MAX / 0.05) + 1
# mccole: /params


# mccole: rhs
def rhs(t, z):
    """Return [dx/dt, dy/dt] for the Lotka-Volterra equations.

    z[0] = x (prey population)
    z[1] = y (predator population)
    """
    x, y = z
    dxdt = PREY_BIRTH * x - PREDATION * x * y
    dydt = PRED_GROWTH * x * y - PRED_DEATH * y
    return [dxdt, dydt]
# mccole: /rhs


# mccole: solve
def solve():
    """Integrate the Lotka-Volterra equations and return results as a DataFrame."""
    t_eval = np.linspace(0, T_MAX, N_EVAL)
    sol = solve_ivp(
        rhs,
        [0, T_MAX],
        [PREY_INIT, PRED_INIT],
        t_eval=t_eval,
        method="RK45",
        rtol=1e-8,
        atol=1e-10,
    )
    return pl.DataFrame({"t": sol.t, "prey": sol.y[0], "predator": sol.y[1]})
# mccole: /solve


# mccole: plots
def plot_time_series(df):
    """Return an Altair chart of prey and predator populations over time."""
    long = df.unpivot(
        index="t",
        on=["prey", "predator"],
        variable_name="species",
        value_name="population",
    )
    return (
        alt.Chart(long)
        .mark_line()
        .encode(
            x=alt.X("t", title="Time"),
            y=alt.Y("population", title="Population"),
            color=alt.Color("species:N", title="Species"),
        )
        .properties(width=400, height=250, title="Population over time")
    )


def plot_trajectory(df):
    """Return an Altair chart of the predator-prey population trajectory."""
    return (
        alt.Chart(df)
        .mark_line()
        .encode(
            x=alt.X("prey", title="Prey"),
            y=alt.Y("predator", title="Predator"),
        )
        .properties(width=300, height=300, title="Population trajectory")
    )
# mccole: /plots


if __name__ == "__main__":
    df = solve()
    ts_chart = plot_time_series(df)
    traj_chart = plot_trajectory(df)
    ts_chart.save("lotka_timeseries.svg")
    traj_chart.save("lotka_trajectory.svg")
    print(f"Saved lotka_timeseries.svg and lotka_trajectory.svg ({len(df)} rows)")
