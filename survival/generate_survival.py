import numpy as np
import polars as pl

# mccole: constants
SEED = 7493418  # RNG seed for reproducibility
N_PATIENTS = 100  # number of patients in the study
MEAN_SURVIVAL = (
    20.0  # mean event time drawn from Exponential(scale=MEAN_SURVIVAL) in days
)
# Censoring time drawn from Uniform(CENSOR_MIN, CENSOR_MAX): patients followed up for a random
# duration, with the study ending if the event has not yet occurred.
CENSOR_MIN = 10.0  # minimum follow-up time (days)
CENSOR_MAX = 35.0  # maximum follow-up time (days)
# mccole: /constants


# mccole: generate
def make_survival_data(
    n=N_PATIENTS,
    mean_survival=MEAN_SURVIVAL,
    censor_min=CENSOR_MIN,
    censor_max=CENSOR_MAX,
    seed=SEED,
):
    """Return a Polars DataFrame with columns 'time' and 'observed'.

    Each patient has a true event time drawn from Exponential(scale=mean_survival).
    An independent censoring time is drawn from Uniform(censor_min, censor_max).
    The observed time is whichever comes first.
    'observed' is 1 if the event occurred before censoring, 0 otherwise.
    """
    rng = np.random.default_rng(seed)
    true_event_times = rng.exponential(scale=mean_survival, size=n)
    censoring_times = rng.uniform(low=censor_min, high=censor_max, size=n)
    observed = (true_event_times <= censoring_times).astype(int)
    times = np.minimum(true_event_times, censoring_times)
    return pl.DataFrame({"time": times, "observed": observed})
# mccole: /generate


if __name__ == "__main__":
    df = make_survival_data()
    n_events = df["observed"].sum()
    print(f"Patients: {len(df)}, events: {n_events}, censored: {len(df) - n_events}")
    print(f"Time range: [{df['time'].min():.2f}, {df['time'].max():.2f}] days")
