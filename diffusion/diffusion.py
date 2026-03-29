import numpy as np
import polars as pl
import altair as alt

# mccole: constants
# Spatial grid: 50 points give dx = 0.02, fine enough to resolve a Gaussian
# pulse of width 0.05 (about 2.5 grid cells per standard deviation).
GRID_POINTS = 50
LENGTH = 1.0
DX = LENGTH / (GRID_POINTS - 1)

# Diffusion coefficient in arbitrary units.
DIFFUSIVITY = 0.1

# The explicit finite-difference scheme is stable only when the stability
# ratio r = D*dt/dx^2 <= 0.5.
# Using STABILITY_RATIO = 0.4 gives a 20% safety margin.
STABILITY_RATIO = 0.4
DT = STABILITY_RATIO * DX**2 / DIFFUSIVITY

# Run for 500 steps; save a snapshot every 100 steps.
N_STEPS = 500
SNAPSHOT_INTERVAL = 100

# Initial Gaussian pulse centered in the domain.  Width 0.05 keeps the tails
# more than 4 standard deviations from each boundary throughout the full run.
PULSE_CENTER = 0.5
PULSE_WIDTH = 0.05
# mccole: /constants


# mccole: make-initial
def make_initial():
    """Return spatial grid and Gaussian initial concentration profile."""
    x = np.linspace(0, LENGTH, GRID_POINTS)
    c = np.exp(-((x - PULSE_CENTER) ** 2) / (2 * PULSE_WIDTH**2))
    return x, c
# mccole: /make-initial


# mccole: step
def step(c):
    """Return concentration after one explicit finite-difference time step.

    Prepend and append ghost cells equal to the boundary values to enforce
    zero-flux boundary conditions: no material enters or leaves the domain.
    This makes the total mass exactly conserved each step.
    """
    r = DIFFUSIVITY * DT / DX**2
    padded = np.concatenate([[c[0]], c, [c[-1]]])
    return c + r * (padded[2:] - 2 * padded[1:-1] + padded[:-2])
# mccole: /step


# mccole: simulate
def simulate():
    """Run the simulation and return concentration snapshots as a DataFrame."""
    x, c = make_initial()
    records = _make_records(x, c, 0.0)
    for i in range(1, N_STEPS + 1):
        c = step(c)
        if i % SNAPSHOT_INTERVAL == 0:
            records += _make_records(x, c, round(i * DT, 6))
    return pl.DataFrame(records)


def _make_records(x, c, time):
    return [
        {"x": float(xi), "concentration": float(ci), "time": time}
        for xi, ci in zip(x, c)
    ]
# mccole: /simulate


# mccole: plot
def plot(df):
    """Return an Altair line chart of concentration profiles over time."""
    return (
        alt.Chart(df)
        .mark_line()
        .encode(
            x=alt.X("x", title="Position"),
            y=alt.Y("concentration", title="Concentration"),
            color=alt.Color("time:O", title="Time (s)"),
        )
        .properties(width=400, height=300)
    )
# mccole: /plot


if __name__ == "__main__":
    df = simulate()
    chart = plot(df)
    chart.save("diffusion.html")
    chart.save("diffusion.svg")
    print(f"Saved diffusion.html and diffusion.svg ({len(df)} rows)")
