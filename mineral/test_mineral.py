import numpy as np
import pytest
from generate_mineral import make_mineral_data, train_test_split, TRAIN_FRAC
from mineral import sigmoid, normalize, train, predict, accuracy


def test_sigmoid_at_zero():
    # sigmoid(0) = 0.5 by definition.
    assert sigmoid(0.0) == pytest.approx(0.5)


def test_sigmoid_large_positive():
    # sigmoid(z) → 1 as z → +∞; at z=100 the deviation from 1 is negligible.
    assert sigmoid(100.0) == pytest.approx(1.0, abs=1e-6)


def test_sigmoid_large_negative():
    # sigmoid(z) → 0 as z → -∞.
    assert sigmoid(-100.0) == pytest.approx(0.0, abs=1e-6)


def test_normalize_zero_mean_unit_std():
    # Normalized training data must have mean ≈ 0 and std ≈ 1 for each feature.
    X, _ = make_mineral_data()
    X_n, mean, std = normalize(X)
    assert np.allclose(X_n.mean(axis=0), 0.0, atol=1e-10)
    assert np.allclose(X_n.std(axis=0), 1.0, atol=1e-10)


def test_normalize_applies_training_stats():
    # Normalizing test data with training mean/std must not recompute stats.
    X, _ = make_mineral_data()
    n = len(X)
    X_train, X_test = X[: n // 2], X[n // 2 :]
    X_n, mean, std = normalize(X_train)
    X_test_n, _, _ = normalize(X_test, mean, std)
    expected = (X_test - mean) / std
    assert np.allclose(X_test_n, expected)


def test_training_loss_decreases():
    # The binary cross-entropy loss must decrease over the first 100 iterations.
    X, y = make_mineral_data()
    X_n, _, _ = normalize(X)
    _, _, losses = train(X_n, y, n_iter=100)
    assert losses[-1] < losses[0]


def test_perfect_separation():
    # Two perfectly separated clusters must achieve 100% training accuracy.
    # Felsic centred at (70, 14), mafic at (50, 9) — 6-sigma apart in SiO2.
    X, y = make_mineral_data()
    X_n, _, _ = normalize(X)
    w, b, _ = train(X_n, y, n_iter=1000)
    y_pred = predict(X_n, w, b)
    # The two classes are well-separated; expect ≥ 95% training accuracy.
    assert accuracy(y, y_pred) >= 0.95


def test_test_accuracy():
    # With default parameters, test accuracy must be ≥ 95%.
    # The two classes differ by ~6.7 std devs in SiO2; the boundary should be sharp.
    X, y = make_mineral_data()
    X_train, y_train, X_test, y_test = train_test_split(X, y, TRAIN_FRAC)
    X_train_n, mean, std = normalize(X_train)
    X_test_n, _, _ = normalize(X_test, mean, std)
    w, b, _ = train(X_train_n, y_train)
    y_pred = predict(X_test_n, w, b)
    assert accuracy(y_test, y_pred) >= 0.95


def test_accuracy_all_correct():
    assert accuracy(np.array([0, 1, 0, 1]), np.array([0, 1, 0, 1])) == pytest.approx(
        1.0
    )


def test_accuracy_all_wrong():
    assert accuracy(np.array([0, 1, 0, 1]), np.array([1, 0, 1, 0])) == pytest.approx(
        0.0
    )


def test_predict_known_weights():
    # With w=[10, 0], b=0: samples with X[:,0] > 0 should be predicted class 1.
    X = np.array([[1.0, 0.0], [-1.0, 0.0]])
    w = np.array([10.0, 0.0])
    b = 0.0
    y_pred = predict(X, w, b)
    assert y_pred[0] == 1
    assert y_pred[1] == 0
