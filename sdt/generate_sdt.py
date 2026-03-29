"""Generate synthetic evidence scores and labels for the SDT lesson.

Each trial is either a signal trial (label=1) or a noise trial (label=0).
Evidence scores for noise trials are drawn from N(0, 1) and for signal
trials from N(1.5, 1), so an ideal observer would achieve AUC > 0.5.
The separation of 1.5 standard deviations gives a clear ROC bow without
making the task trivially easy.

RNG seed 7493418 is used for all random number generation in this project.
"""
import numpy as np

# Fixed seed used for all synthetic data generators in this project.
RNG_SEED = 7493418

# Number of signal and noise trials.
N_SIGNAL = 100
N_NOISE = 100

# Mean evidence for signal trials; noise trials use mean 0.
# This separation produces an AUC well above 0.5 but below 1.0,
# giving a clearly bowed ROC curve suitable for illustration.
SIGNAL_MEAN = 1.5


def generate_data():
    """Return (scores, labels) arrays for N_SIGNAL + N_NOISE trials."""
    rng = np.random.default_rng(RNG_SEED)
    noise_scores = rng.standard_normal(N_NOISE)
    signal_scores = rng.standard_normal(N_SIGNAL) + SIGNAL_MEAN
    scores = np.concatenate([noise_scores, signal_scores])
    labels = np.concatenate([np.zeros(N_NOISE, dtype=int), np.ones(N_SIGNAL, dtype=int)])
    return scores, labels


def load_data():
    """Alias for generate_data; returns (scores, labels)."""
    return generate_data()


if __name__ == "__main__":
    scores, labels = generate_data()
    for score, label in zip(scores, labels):
        print(f"{score:.6f},{label}")
