import numpy as np
import polars as pl
import altair as alt
from generate_tumor import make_tumor_data


# mccole: sigmoid
def sigmoid(z):
    """Map any real number to (0, 1) via the logistic function 1 / (1 + exp(-z))."""
    return 1.0 / (1.0 + np.exp(-z))
# mccole: /sigmoid


# mccole: model
def predict_proba(X, w, b):
    """Return predicted class-1 probability for each row of X.

    Each probability is sigmoid(X @ w + b), the logistic regression output.
    """
    return sigmoid(X @ w + b)


def predict(X, w, b):
    """Return predicted class labels (0 or 1) by thresholding probabilities at 0.5."""
    return (predict_proba(X, w, b) >= 0.5).astype(int)
# mccole: /model


# mccole: train
def train(X, y, lr=0.1, n_iter=2000):
    """Fit logistic regression by gradient descent on binary cross-entropy loss.

    Binary cross-entropy:  L = -(1/n) sum [ y_i log(p_i) + (1-y_i) log(1-p_i) ]

    Gradients:
        dL/dw = (1/n) X^T (p - y)
        dL/db = (1/n) sum(p - y)

    Returns (w, b): weight vector and scalar bias.
    """
    n, p = X.shape
    w = np.zeros(p)
    b = 0.0
    for _ in range(n_iter):
        proba = predict_proba(X, w, b)
        residual = proba - y
        w -= lr * (X.T @ residual) / n
        b -= lr * np.mean(residual)
    return w, b
# mccole: /train


# mccole: evaluate
def confusion_matrix(y_true, y_pred):
    """Return a 2x2 confusion matrix [[TN, FP], [FN, TP]].

    Rows index actual class (0 = benign, 1 = malignant).
    Columns index predicted class (0 = benign, 1 = malignant).
    """
    tn = int(np.sum((y_pred == 0) & (y_true == 0)))
    fp = int(np.sum((y_pred == 1) & (y_true == 0)))
    fn = int(np.sum((y_pred == 0) & (y_true == 1)))
    tp = int(np.sum((y_pred == 1) & (y_true == 1)))
    return np.array([[tn, fp], [fn, tp]])


def accuracy(y_true, y_pred):
    """Return the fraction of correctly classified samples."""
    return float(np.mean(y_true == y_pred))
# mccole: /evaluate


# mccole: plot
def plot_boundary(X, y, w, b, filename):
    """Save a scatter plot of the two classes with the logistic regression decision boundary.

    The boundary is the line w[0]*x1 + w[1]*x2 + b = 0, i.e.
        x2 = -(w[0]*x1 + b) / w[1]
    plotted over the range of feature 1 values in the data.
    """
    scatter_df = pl.DataFrame(
        {"feature_1": X[:, 0], "feature_2": X[:, 1], "label": y.astype(str)}
    )
    scatter = (
        alt.Chart(scatter_df)
        .mark_point(opacity=0.7, size=30)
        .encode(
            x=alt.X("feature_1:Q", title="Feature 1 (cell size)"),
            y=alt.Y("feature_2:Q", title="Feature 2 (cell shape)"),
            color=alt.Color(
                "label:N",
                scale=alt.Scale(domain=["0", "1"], range=["steelblue", "firebrick"]),
                legend=alt.Legend(title="Class (0=benign, 1=malignant)"),
            ),
        )
    )

    x1_range = np.linspace(X[:, 0].min(), X[:, 0].max(), 200)
    x2_boundary = -(w[0] * x1_range + b) / w[1]
    boundary_df = pl.DataFrame({"feature_1": x1_range, "feature_2": x2_boundary})
    boundary_line = (
        alt.Chart(boundary_df)
        .mark_line(color="black", strokeWidth=1.5, strokeDash=[5, 3])
        .encode(x="feature_1:Q", y="feature_2:Q")
    )

    chart = alt.layer(scatter, boundary_line).properties(
        width=400, height=350, title="Logistic regression decision boundary"
    )
    chart.save(filename)
# mccole: /plot


if __name__ == "__main__":
    df = make_tumor_data()
    X = df.select(["feature_1", "feature_2"]).to_numpy()
    y = df["label"].to_numpy()

    # 80/20 train-test split (deterministic index split after shuffling in generate).
    n_train = int(0.8 * len(y))
    X_train, X_test = X[:n_train], X[n_train:]
    y_train, y_test = y[:n_train], y[n_train:]

    w, b = train(X_train, y_train)
    y_pred = predict(X_test, w, b)
    cm = confusion_matrix(y_test, y_pred)
    acc = accuracy(y_test, y_pred)
    print(f"Test accuracy: {acc:.3f}")
    print(f"Confusion matrix [[TN, FP], [FN, TP]]:\n{cm}")
    plot_boundary(X, y, w, b, "tumor.svg")
    print("Saved tumor.svg")
