import numpy as np
import pytest
from sdt import confusion_rates, roc_curve, auc


# ---------------------------------------------------------------------------
# confusion_rates
# ---------------------------------------------------------------------------

def test_hit_rate_all_hits():
    # Every signal trial is detected: hit rate must be 1.0.
    labels = [1, 1, 1, 0, 0]
    decisions = [1, 1, 1, 0, 0]
    hr, far = confusion_rates(labels, decisions)
    assert hr == pytest.approx(1.0)


def test_false_alarm_rate_zero():
    # No noise trial triggers a false alarm: FAR must be 0.0.
    labels = [1, 0, 0, 0]
    decisions = [1, 0, 0, 0]
    _, far = confusion_rates(labels, decisions)
    assert far == pytest.approx(0.0)


def test_hit_and_false_alarm_rates_proportional():
    # 3 out of 4 signal trials are hits; 1 out of 2 noise trials is a false alarm.
    labels = [1, 1, 1, 1, 0, 0]
    decisions = [1, 1, 1, 0, 1, 0]
    hr, far = confusion_rates(labels, decisions)
    assert hr == pytest.approx(0.75)
    assert far == pytest.approx(0.5)


# ---------------------------------------------------------------------------
# roc_curve
# ---------------------------------------------------------------------------

def test_roc_starts_at_origin():
    # The first point (highest threshold) should classify nothing as signal,
    # so both FAR and HR are 0.
    scores = [0.1, 0.5, 0.9, 0.2, 0.8]
    labels = [1,   1,   1,   0,   0  ]
    far, hr = roc_curve(scores, labels)
    assert far[0] == pytest.approx(0.0)
    assert hr[0] == pytest.approx(0.0)


def test_roc_ends_at_one():
    # The last point (lowest threshold) classifies everything as signal,
    # so both FAR and HR are 1.
    scores = [0.1, 0.5, 0.9, 0.2, 0.8]
    labels = [1,   1,   1,   0,   0  ]
    far, hr = roc_curve(scores, labels)
    assert far[-1] == pytest.approx(1.0)
    assert hr[-1] == pytest.approx(1.0)


def test_roc_monotonically_increasing():
    # Both FAR and HR must be non-decreasing across threshold steps.
    rng = np.random.default_rng(7493418)
    scores = np.concatenate([rng.standard_normal(50), rng.standard_normal(50) + 1.5])
    labels = np.concatenate([np.zeros(50, dtype=int), np.ones(50, dtype=int)])
    far, hr = roc_curve(scores, labels)
    assert all(far[i] <= far[i + 1] for i in range(len(far) - 1))
    assert all(hr[i] <= hr[i + 1] for i in range(len(hr) - 1))


def test_roc_perfect_scores():
    # When every signal score exceeds every noise score the ROC passes
    # through (0, 1): at the threshold that admits all signals but no noise,
    # FAR = 0 and HR = 1.
    scores = [2.0, 3.0, 4.0, 0.5, 1.0]
    labels = [1,   1,   1,   0,   0  ]
    far, hr = roc_curve(scores, labels)
    # The point (FAR=0, HR=1) must appear somewhere in the curve.
    assert any(f == pytest.approx(0.0) and h == pytest.approx(1.0) for f, h in zip(far, hr))


# ---------------------------------------------------------------------------
# auc
# ---------------------------------------------------------------------------

def test_auc_chance_diagonal():
    # The diagonal ROC (FAR = HR everywhere) has AUC = 0.5.
    far = np.linspace(0, 1, 101)
    hr = np.linspace(0, 1, 101)
    assert auc(far, hr) == pytest.approx(0.5, abs=1e-6)


def test_auc_perfect():
    # A step from (0, 0) to (0, 1) to (1, 1) encloses the full unit square: AUC = 1.0.
    far = np.array([0.0, 0.0, 1.0])
    hr = np.array([0.0, 1.0, 1.0])
    assert auc(far, hr) == pytest.approx(1.0, abs=1e-6)


def test_auc_above_chance_for_separable_scores():
    # When signal scores are generally higher than noise scores, AUC > 0.5.
    rng = np.random.default_rng(7493418)
    noise = rng.standard_normal(200)
    signal = rng.standard_normal(200) + 1.5
    scores = np.concatenate([noise, signal])
    labels = np.concatenate([np.zeros(200, dtype=int), np.ones(200, dtype=int)])
    far, hr = roc_curve(scores, labels)
    area = auc(far, hr)
    assert area > 0.5


def test_auc_symmetric():
    # auc should not depend on whether FAR is supplied in ascending or
    # descending order, because the implementation sorts internally.
    far = np.array([0.0, 0.25, 0.5, 0.75, 1.0])
    hr = np.array([0.0, 0.6,  0.8, 0.9,  1.0])
    assert auc(far, hr) == pytest.approx(auc(far[::-1], hr[::-1]), abs=1e-10)
