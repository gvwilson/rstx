import numpy as np
import polars as pl
import altair as alt
from scipy.integrate import solve_ivp
from scipy.optimize import least_squares
from generate_sir import I0, N_POP, T_MAX, generate

# mccole: constants
# Initial parameter guesses for the optimizer.  Starting near biologically
# plausible values helps the solver converge; exact values do not matter
# as long as residuals decrease monotonically from the starting point.
BETA_INIT = 0.3
GAMMA_INIT = 0.1

# Both parameters must be positive; upper bounds are generous.
LOWER_BOUNDS = [1e-6, 1e-6]
UPPER_BOUNDS = [2.0, 2.0]
# mccole: /constants


# mccole: sir-rhs
def sir_rhs(t, y, beta, gamma, n):
    """Return [dS/dt, dI/dt, dR/dt] for the SIR epidemic model.

    S, I, R are the numbers of susceptible, infectious, and recovered
    individuals.  The force of infection beta * I / N uses
    frequency-dependent (proportional) transmission: each susceptible
    encounters a fixed fraction of the population per unit time.
    The total N = S + I + R is conserved: dS/dt + dI/dt + dR/dt = 0.
    """
    susc, infect, rec = y
    force = beta * susc * infect / n
    return [-force, force - gamma * infect, gamma * infect]
# mccole: /sir-rhs


# mccole: model-cases
def model_cases(beta, gamma, n=N_POP, i0=I0, t_max=T_MAX):
    """Return modelled daily new cases for parameters beta and gamma.

    Integrates the SIR ODEs at integer days and returns the daily incidence
    new_cases(t) = S(t-1) - S(t), the number of new infections per day.
    """
    t_eval = np.arange(0, t_max + 1, dtype=float)
    sol = solve_ivp(
        sir_rhs,
        [0.0, float(t_max)],
        [float(n - i0), float(i0), 0.0],
        args=(beta, gamma, n),
        t_eval=t_eval,
        rtol=1e-8,
        atol=1e-10,
    )
    return np.maximum(np.diff(sol.y[0]) * -1.0, 0.0)
# mccole: /model-cases


# mccole: fit
def fit(observed, n=N_POP, i0=I0, t_max=T_MAX):
    """Fit beta and gamma to observed daily case counts by least squares.

    Minimises the sum of squared residuals between the modelled and observed
    daily incidence.  Returns the fitted (beta, gamma) as a tuple.
    """

    def residuals(params):
        beta, gamma = params
        return model_cases(beta, gamma, n, i0, t_max) - observed

    result = least_squares(
        residuals,
        x0=[BETA_INIT, GAMMA_INIT],
        bounds=(LOWER_BOUNDS, UPPER_BOUNDS),
    )
    return float(result.x[0]), float(result.x[1])
# mccole: /fit


# mccole: plot
def plot(days, observed, beta, gamma):
    """Return an Altair chart of observed cases and the fitted SIR model curve."""
    fitted = model_cases(beta, gamma)
    df_obs = pl.DataFrame(
        {"day": days, "cases": observed.tolist(), "source": ["observed"] * len(days)}
    )
    df_fit = pl.DataFrame(
        {
            "day": list(range(1, T_MAX + 1)),
            "cases": fitted.tolist(),
            "source": ["fitted"] * T_MAX,
        }
    )
    return (
        alt.Chart(pl.concat([df_obs, df_fit]))
        .mark_line()
        .encode(
            x=alt.X("day:Q", title="Day"),
            y=alt.Y("cases:Q", title="New cases per day"),
            color=alt.Color("source:N", title=""),
            strokeDash=alt.StrokeDash("source:N"),
        )
        .properties(width=400, height=280)
    )
# mccole: /plot


if __name__ == "__main__":
    df = generate()
    days = df["day"].to_numpy()
    observed = df["cases"].to_numpy()
    beta_fit, gamma_fit = fit(observed)
    r0_fit = beta_fit / gamma_fit
    print(f"Fitted:  beta = {beta_fit:.4f}, gamma = {gamma_fit:.4f}, R0 = {r0_fit:.2f}")
    chart = plot(days, observed, beta_fit, gamma_fit)
    chart.save("sir.svg")
    print("Saved sir.svg")
