import numpy as np
import polars as pl

SEED = 7493418

# Number of practice trials in the experiment.
N_TRIALS = 80

# True power-law parameters: RT(n) = A * n^(-b) + noise
# A is the predicted reaction time on trial 1 in milliseconds.
TRUE_A = 500.0

# b is the learning rate exponent.  b = 0.3 is within the empirical range
# for motor tasks (0.2-0.4) reported by Newell and Rosenbloom (1981).
TRUE_B = 0.3

# Standard deviation of Gaussian noise added to each trial's reaction time.
# 20 ms is a plausible within-session variability for a simple motor task
# (Fitts and Posner, 1967 report typical SDs of 10-50 ms).
NOISE_SD = 20.0


# mccole: generate
def make_trials(
    n_trials=N_TRIALS,
    a=TRUE_A,
    b=TRUE_B,
    noise_sd=NOISE_SD,
    seed=SEED,
):
    """Return a Polars DataFrame of per-trial reaction times.

    Columns:
        trial -- integer trial number starting at 1
        rt    -- reaction time in milliseconds

    Reaction times follow the power-law model RT = a * trial^(-b) with
    Gaussian noise of standard deviation noise_sd.  Any simulated RT below
    1 ms is clamped to 1 ms to ensure all values are positive.
    """
    rng = np.random.default_rng(seed)
    trials = np.arange(1, n_trials + 1, dtype=float)
    rt = a * trials ** (-b) + rng.normal(0.0, noise_sd, n_trials)
    rt = np.maximum(rt, 1.0)
    return pl.DataFrame({"trial": list(range(1, n_trials + 1)), "rt": rt.tolist()})
# mccole: /generate


if __name__ == "__main__":
    df = make_trials()
    print(f"Trials: {df.height}")
    print(f"RT range: [{df['rt'].min():.1f}, {df['rt'].max():.1f}] ms")
    print(df.head(5))
