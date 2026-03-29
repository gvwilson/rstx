import numpy as np

# mccole: constants
# Synthetic geochemical data: two mineral classes distinguished by oxide concentrations.
# Felsic rocks (e.g. granite) are silica-rich; mafic rocks (e.g. basalt) are silica-poor.
# Feature 0: SiO2 concentration (wt%)
# Feature 1: Al2O3 concentration (wt%)
SEED = 7493418  # RNG seed
FELSIC_MEAN = [70.0, 14.0]  # granite-like: high silica, moderate alumina
FELSIC_STD = [3.0, 1.5]
MAFIC_MEAN = [50.0, 9.0]  # basalt-like: lower silica, lower alumina
MAFIC_STD = [3.0, 1.5]
N_FELSIC = 80  # training + test samples per class
N_MAFIC = 80
TRAIN_FRAC = 0.75  # fraction used for training
# mccole: /constants


# mccole: make-data
def make_mineral_data(n_felsic=N_FELSIC, n_mafic=N_MAFIC, seed=SEED):
    """Return (X, y) for a two-class geochemical dataset.

    X is (n_felsic + n_mafic, 2): columns are SiO2 and Al2O3 wt%.
    y is (n_felsic + n_mafic,): 0 for felsic, 1 for mafic.
    Rows are shuffled so classes are interleaved.
    """
    rng = np.random.default_rng(seed)
    X_felsic = rng.normal(FELSIC_MEAN, FELSIC_STD, (n_felsic, 2))
    X_mafic = rng.normal(MAFIC_MEAN, MAFIC_STD, (n_mafic, 2))
    X = np.vstack([X_felsic, X_mafic])
    y = np.concatenate([np.zeros(n_felsic), np.ones(n_mafic)])
    idx = rng.permutation(len(y))
    return X[idx], y[idx]
# mccole: /make-data


# mccole: split
def train_test_split(X, y, train_frac=TRAIN_FRAC, seed=SEED):
    """Return (X_train, y_train, X_test, y_test) with stratified split."""
    rng = np.random.default_rng(seed)
    n_train = int(len(y) * train_frac)
    idx = rng.permutation(len(y))
    train_idx, test_idx = idx[:n_train], idx[n_train:]
    return X[train_idx], y[train_idx], X[test_idx], y[test_idx]
# mccole: /split


if __name__ == "__main__":
    X, y = make_mineral_data()
    print(
        f"Samples: {len(y)}  felsic: {int((y == 0).sum())}  mafic: {int((y == 1).sum())}"
    )
    print(f"SiO2  range: [{X[:, 0].min():.1f}, {X[:, 0].max():.1f}] wt%")
    print(f"Al2O3 range: [{X[:, 1].min():.1f}, {X[:, 1].max():.1f}] wt%")
