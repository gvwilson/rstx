import numpy as np
import polars as pl


SEED = 7493418
N_STEPS = 200  # total length of the time series
BREAK_STEP = 100  # true break: indices 0..99 have MEAN_BEFORE, 100..199 have MEAN_AFTER
MEAN_BEFORE = 0.0  # series mean before the break
MEAN_AFTER = 3.0  # series mean after the break (shift of 3 standard deviations)
# Noise level chosen so the signal-to-noise ratio at the break is exactly 3,
# giving high detection power with N_STEPS=200 while leaving visible scatter.
NOISE_STD = 1.0


# mccole: generate
def make_breakpoint_data(
    n_steps=N_STEPS,
    break_step=BREAK_STEP,
    mean_before=MEAN_BEFORE,
    mean_after=MEAN_AFTER,
    noise_std=NOISE_STD,
    seed=SEED,
):
    """Return a Polars DataFrame with columns 'step' and 'value'.

    The series has a single structural break at break_step:
      - value[t] ~ N(mean_before, noise_std^2)  for t < break_step
      - value[t] ~ N(mean_after,  noise_std^2)  for t >= break_step

    The break is abrupt: there is no gradual transition.
    """
    rng = np.random.default_rng(seed)
    steps = np.arange(n_steps)
    means = np.where(steps < break_step, mean_before, mean_after)
    values = means + rng.normal(0.0, noise_std, n_steps)
    return pl.DataFrame({"step": steps, "value": values})
# mccole: /generate


if __name__ == "__main__":
    df = make_breakpoint_data()
    before = df.filter(pl.col("step") < BREAK_STEP)["value"]
    after = df.filter(pl.col("step") >= BREAK_STEP)["value"]
    print(f"Steps:          {len(df)}")
    print(f"True break at:  step {BREAK_STEP}")
    print(f"Mean (before):  {before.mean():.3f}  (true: {MEAN_BEFORE})")
    print(f"Mean (after):   {after.mean():.3f}  (true: {MEAN_AFTER})")
