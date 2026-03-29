import numpy as np
import pytest
from generate_tumor import make_tumor_data
from tumor import sigmoid, predict_proba, predict, train, confusion_matrix, accuracy


def test_sigmoid_midpoint():
    # sigmoid(0) = 0.5 by definition.
    assert sigmoid(0.0) == pytest.approx(0.5)


def test_sigmoid_large_positive():
    # sigmoid saturates to 1 for large positive inputs.
    assert sigmoid(100.0) == pytest.approx(1.0, abs=1e-10)


def test_sigmoid_large_negative():
    # sigmoid saturates to 0 for large negative inputs.
    assert sigmoid(-100.0) == pytest.approx(0.0, abs=1e-10)


def test_predict_proba_zero_weights():
    # With w=0 and b=0 every prediction is 0.5 regardless of X.
    X = np.array([[1.0, 2.0], [3.0, 4.0]])
    w = np.array([0.0, 0.0])
    proba = predict_proba(X, w, 0.0)
    assert np.allclose(proba, 0.5)


def test_confusion_matrix_perfect_classifier():
    # A perfect classifier has TP=FP=FN=TN matching the class counts.
    y_true = np.array([0, 0, 1, 1])
    y_pred = np.array([0, 0, 1, 1])
    cm = confusion_matrix(y_true, y_pred)
    # [[TN, FP], [FN, TP]]
    assert cm[0, 0] == 2  # TN
    assert cm[1, 1] == 2  # TP
    assert cm[0, 1] == 0  # FP
    assert cm[1, 0] == 0  # FN


def test_confusion_matrix_all_wrong():
    # When every prediction is wrong, TP=TN=0.
    y_true = np.array([0, 0, 1, 1])
    y_pred = np.array([1, 1, 0, 0])
    cm = confusion_matrix(y_true, y_pred)
    assert cm[0, 0] == 0  # TN
    assert cm[1, 1] == 0  # TP
    assert cm[0, 1] == 2  # FP
    assert cm[1, 0] == 2  # FN


def test_accuracy_perfect():
    y_true = np.array([0, 1, 0, 1])
    assert accuracy(y_true, y_true) == pytest.approx(1.0)


def test_accuracy_half():
    y_true = np.array([0, 0, 1, 1])
    y_pred = np.array([1, 1, 0, 0])
    assert accuracy(y_true, y_pred) == pytest.approx(0.0)


def test_train_well_separated_clusters():
    # With class means 2 standard deviations apart in each feature,
    # gradient descent should reach > 95% accuracy on the full dataset.
    df = make_tumor_data()
    X = df.select(["feature_1", "feature_2"]).to_numpy()
    y = df["label"].to_numpy()
    w, b = train(X, y, lr=0.1, n_iter=2000)
    y_pred = predict(X, w, b)
    # The two Gaussian clusters are separated by (3.5-1.5)/0.6 ≈ 3.3 std in each
    # feature; 95% is a conservative lower bound for well-separated classes.
    assert accuracy(y, y_pred) > 0.95
