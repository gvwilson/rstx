import numpy as np
import polars as pl

# mccole: constants
SEED = 7493418  # RNG seed for reproducibility
N_POINTS = 200  # number of time points (minutes)
BASELINE_MEAN = 70.0  # baseline heart rate (bpm)
BASELINE_STD = 2.0  # normal beat-to-beat variation (bpm)
STEP_START = 90  # time index where a sustained step change begins
STEP_SIZE = 12.0  # magnitude of the step change (bpm)
# Positions of isolated spike outliers and their magnitude.
SPIKE_POSITIONS = [30, 110, 165]
SPIKE_SIZE = 18.0  # spike magnitude above local baseline (bpm)
# mccole: /constants


# mccole: generate
def make_vitals_data(
    n=N_POINTS,
    baseline_mean=BASELINE_MEAN,
    baseline_std=BASELINE_STD,
    step_start=STEP_START,
    step_size=STEP_SIZE,
    spike_positions=SPIKE_POSITIONS,
    spike_size=SPIKE_SIZE,
    seed=SEED,
):
    """Return a Polars DataFrame with columns 'time', 'heart_rate', and 'is_anomaly'.

    The baseline is Gaussian noise around baseline_mean.
    A sustained step change of step_size bpm begins at step_start.
    Isolated spikes of spike_size bpm are injected at spike_positions.
    'is_anomaly' marks both step-change positions and spike positions as 1.
    """
    rng = np.random.default_rng(seed)
    times = np.arange(n)
    values = rng.normal(baseline_mean, baseline_std, n)
    values[step_start:] += step_size
    for pos in spike_positions:
        values[pos] += spike_size
    anomaly = np.zeros(n, dtype=int)
    anomaly[step_start:] = 1
    for pos in spike_positions:
        anomaly[pos] = 1
    return pl.DataFrame({"time": times, "heart_rate": values, "is_anomaly": anomaly})
# mccole: /generate


if __name__ == "__main__":
    df = make_vitals_data()
    print(f"Points: {len(df)}, anomalies injected: {df['is_anomaly'].sum()}")
    print(f"HR range: [{df['heart_rate'].min():.1f}, {df['heart_rate'].max():.1f}] bpm")
