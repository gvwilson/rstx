import numpy as np
import polars as pl
from scipy.integrate import solve_ivp

SEED = 7493418

# mccole: constants
# True SIR parameters used to generate synthetic outbreak data.
# BETA_TRUE: number of contacts per day that lead to transmission.
# GAMMA_TRUE: 1/GAMMA_TRUE is the mean infectious period (10 days here).
# R0_TRUE = BETA_TRUE / GAMMA_TRUE = 3.0: each case generates 3 secondary
# cases early in the outbreak, so an epidemic occurs (R0 > 1).
BETA_TRUE = 0.30  # transmission rate (day^-1)
GAMMA_TRUE = 0.10  # recovery rate (day^-1)
N_POP = 10_000  # total population (constant; no births or deaths)
I0 = 10  # initial number of infectious individuals

T_MAX = 160  # simulation length (days)
# mccole: /constants


# mccole: generate
def generate(beta=BETA_TRUE, gamma=GAMMA_TRUE, n=N_POP, i0=I0, t_max=T_MAX, seed=SEED):
    """Return daily new-case counts from an SIR model with Poisson observation noise.

    Integrates the SIR ODEs from day 0 to day t_max and approximates the
    daily incidence as the decrease in S between consecutive integer days:
    new_cases(t) = S(t-1) - S(t).  Poisson noise is added to mimic
    stochastic reporting; the Poisson mean is clipped to zero to avoid
    negative arguments (can occur near the epidemic peak due to ODE
    interpolation).
    """
    rng = np.random.default_rng(seed)
    t_eval = np.arange(0, t_max + 1, dtype=float)
    sol = solve_ivp(
        _sir_rhs,
        [0.0, float(t_max)],
        [float(n - i0), float(i0), 0.0],
        args=(beta, gamma, n),
        t_eval=t_eval,
        rtol=1e-8,
        atol=1e-10,
    )
    # Daily incidence: drop in S from one day to the next.
    new_cases_true = np.maximum(np.diff(sol.y[0]) * -1.0, 0.0)
    new_cases_obs = rng.poisson(new_cases_true).astype(float)
    return pl.DataFrame({"day": np.arange(1, t_max + 1), "cases": new_cases_obs})


def _sir_rhs(t, y, beta, gamma, n):
    susc, infect, rec = y
    force = beta * susc * infect / n
    return [-force, force - gamma * infect, gamma * infect]
# mccole: /generate


if __name__ == "__main__":
    df = generate()
    df.write_csv("sir_data.csv")
    print(f"Saved sir_data.csv ({len(df)} rows, total cases: {df['cases'].sum():.0f})")
