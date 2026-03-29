import numpy as np
import polars as pl
import altair as alt
from generate_mineral import make_mineral_data, train_test_split, TRAIN_FRAC

# mccole: constants
LEARNING_RATE = 0.1  # gradient-descent step size
N_ITER = 500  # number of gradient-descent iterations
# mccole: /constants


# mccole: normalize
def normalize(X, mean=None, std=None):
    """Standardize X to zero mean and unit standard deviation.

    If mean and std are supplied (from the training set), apply them to X
    without recomputing — this ensures test data is scaled identically.
    """
    if mean is None:
        mean = X.mean(axis=0)
    if std is None:
        std = X.std(axis=0)
    return (X - mean) / std, mean, std
# mccole: /normalize


# mccole: sigmoid
def sigmoid(z):
    """Map any real number to (0, 1): sigma(z) = 1 / (1 + exp(-z))."""
    return 1.0 / (1.0 + np.exp(-z))
# mccole: /sigmoid


# mccole: train
def train(X, y, lr=LEARNING_RATE, n_iter=N_ITER):
    """Fit a logistic regression model by gradient descent.

    Parameters
    ----------
    X : (n, p) array of features (should be normalized)
    y : (n,) array of labels, 0 or 1
    lr : learning rate
    n_iter : number of full-batch gradient steps

    Returns
    -------
    w : (p,) weight vector
    b : scalar bias
    losses : list of binary cross-entropy loss at each iteration
    """
    n, p = X.shape
    w = np.zeros(p)
    b = 0.0
    losses = []

    for _ in range(n_iter):
        z = X @ w + b
        p_hat = sigmoid(z)
        # Binary cross-entropy; clip to avoid log(0)
        p_hat_clipped = np.clip(p_hat, 1e-12, 1 - 1e-12)
        loss = -np.mean(y * np.log(p_hat_clipped) + (1 - y) * np.log(1 - p_hat_clipped))
        losses.append(loss)
        # Gradients
        err = p_hat - y
        dw = X.T @ err / n
        db = err.mean()
        w -= lr * dw
        b -= lr * db

    return w, b, losses
# mccole: /train


# mccole: predict
def predict(X, w, b, threshold=0.5):
    """Return binary class predictions (0 or 1) for each row of X."""
    return (sigmoid(X @ w + b) >= threshold).astype(int)


def accuracy(y_true, y_pred):
    """Return fraction of correct predictions."""
    return np.mean(y_true == y_pred)
# mccole: /predict


# mccole: boundary
def decision_boundary_line(w, b, mean, std, x_range):
    """Return (x_vals, y_vals) for the decision boundary in original feature space.

    The boundary satisfies w[0]*x_norm + w[1]*y_norm + b = 0.
    Re-expressing in un-normalized coordinates:
        w[0]*(x - mean[0])/std[0] + w[1]*(y - mean[1])/std[1] + b = 0
    Solving for y:
        y = mean[1] - std[1]/w[1] * (w[0]*(x - mean[0])/std[0] + b)
    """
    x_vals = np.linspace(*x_range, 200)
    y_vals = mean[1] - (std[1] / w[1]) * (w[0] * (x_vals - mean[0]) / std[0] + b)
    return x_vals, y_vals
# mccole: /boundary


# mccole: plot
def plot_boundary(X, y, w, b, mean, std, filename):
    """Save a scatter plot with the logistic regression decision boundary."""
    x_range = (X[:, 0].min() - 1, X[:, 0].max() + 1)
    bx, by = decision_boundary_line(w, b, mean, std, x_range)

    label_map = {0: "felsic", 1: "mafic"}
    df = pl.DataFrame(
        {
            "SiO2": X[:, 0],
            "Al2O3": X[:, 1],
            "class": [label_map[int(yi)] for yi in y],
        }
    )
    boundary_df = pl.DataFrame({"SiO2": bx, "Al2O3": by})

    scatter = (
        alt.Chart(df)
        .mark_point(size=50, opacity=0.7)
        .encode(
            x=alt.X("SiO2:Q", title="SiO₂ (wt%)"),
            y=alt.Y("Al2O3:Q", title="Al₂O₃ (wt%)"),
            color=alt.Color(
                "class:N",
                scale=alt.Scale(
                    domain=["felsic", "mafic"],
                    range=["steelblue", "firebrick"],
                ),
            ),
            shape=alt.Shape("class:N"),
        )
    )
    line = (
        alt.Chart(boundary_df)
        .mark_line(color="black", strokeWidth=1.5, strokeDash=[6, 3])
        .encode(x="SiO2:Q", y="Al2O3:Q")
    )
    chart = (scatter + line).properties(width=400, height=300)
    chart.save(filename)
# mccole: /plot


if __name__ == "__main__":
    X, y = make_mineral_data()
    X_train, y_train, X_test, y_test = train_test_split(X, y, TRAIN_FRAC)

    X_train_n, mean, std = normalize(X_train)
    X_test_n, _, _ = normalize(X_test, mean, std)

    w, b, losses = train(X_train_n, y_train)
    print(f"Final training loss: {losses[-1]:.4f}")

    y_pred = predict(X_test_n, w, b)
    acc = accuracy(y_test, y_pred)
    print(f"Test accuracy: {acc:.1%}  ({int(acc * len(y_test))}/{len(y_test)} correct)")

    plot_boundary(X_train, y_train, w, b, mean, std, "mineral.svg")
    print("Saved mineral.svg")
