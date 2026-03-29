import numpy as np
import polars as pl

# mccole: constants
SEED = 7493418  # RNG seed for reproducibility
N_PER_CLASS = 150  # samples per class

# Class 0 (benign): Gaussian cluster centred at BENIGN_MEAN.
# Class 1 (malignant): Gaussian cluster centred at MALIGNANT_MEAN.
# Both classes share the same isotropic standard deviation FEATURE_STD.
BENIGN_MEAN = [1.5, 1.5]
MALIGNANT_MEAN = [3.5, 3.5]
FEATURE_STD = 0.6  # within-class spread for each feature
# mccole: /constants


# mccole: generate
def make_tumor_data(
    n_per_class=N_PER_CLASS,
    benign_mean=None,
    malignant_mean=None,
    feature_std=FEATURE_STD,
    seed=SEED,
):
    """Return a Polars DataFrame with columns 'feature_1', 'feature_2', and 'label'.

    Class 0 (benign) is centred at benign_mean; class 1 (malignant) at malignant_mean.
    Both use isotropic Gaussian noise with standard deviation feature_std.
    Rows are shuffled so that class labels do not appear in a block.
    """
    if benign_mean is None:
        benign_mean = BENIGN_MEAN
    if malignant_mean is None:
        malignant_mean = MALIGNANT_MEAN
    rng = np.random.default_rng(seed)
    benign = rng.normal(benign_mean, feature_std, (n_per_class, 2))
    malignant = rng.normal(malignant_mean, feature_std, (n_per_class, 2))
    features = np.vstack([benign, malignant])
    labels = np.array([0] * n_per_class + [1] * n_per_class)
    idx = rng.permutation(len(labels))
    features = features[idx]
    labels = labels[idx]
    return pl.DataFrame(
        {"feature_1": features[:, 0], "feature_2": features[:, 1], "label": labels}
    )
# mccole: /generate


if __name__ == "__main__":
    df = make_tumor_data()
    print(
        f"Total samples: {len(df)}, benign: {(df['label'] == 0).sum()}, "
        f"malignant: {(df['label'] == 1).sum()}"
    )
    print(
        f"Feature 1 range: [{df['feature_1'].min():.2f}, {df['feature_1'].max():.2f}]"
    )
    print(
        f"Feature 2 range: [{df['feature_2'].min():.2f}, {df['feature_2'].max():.2f}]"
    )
