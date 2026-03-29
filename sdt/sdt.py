import numpy as np
import altair as alt

# Number of threshold steps used to trace the ROC curve.
# 200 points gives a smooth curve with no visible steps.
N_ROC_POINTS = 200


# mccole: rates
def confusion_rates(labels, decisions):
    """Return (hit_rate, false_alarm_rate) from binary label and decision arrays.

    labels    -- 1-D array of 1 (signal) or 0 (noise) for each trial
    decisions -- 1-D array of 1 (responded yes) or 0 (responded no)

    hit_rate        = hits / total signal trials
    false_alarm_rate = false alarms / total noise trials
    """
    labels = np.asarray(labels)
    decisions = np.asarray(decisions)
    signal_trials = labels == 1
    noise_trials = labels == 0
    hits = np.sum((decisions == 1) & signal_trials)
    false_alarms = np.sum((decisions == 1) & noise_trials)
    hit_rate = hits / np.sum(signal_trials)
    false_alarm_rate = false_alarms / np.sum(noise_trials)
    return float(hit_rate), float(false_alarm_rate)
# mccole: /rates


# mccole: roc
def roc_curve(scores, labels):
    """Return (far, hr) arrays tracing the ROC curve from evidence scores.

    scores -- 1-D array of numeric evidence values, one per trial
    labels -- 1-D array of 1 (signal) or 0 (noise) for each trial

    The threshold sweeps over all unique score values plus a value just
    above the maximum so that the curve starts near (0, 0).  At each
    threshold, a trial is classified as "yes" when its score is >= threshold.
    The curve runs from near (0, 0) at the highest threshold to (1, 1) at
    the lowest, tracing all (FAR, HR) pairs the observer can achieve.
    """
    scores = np.asarray(scores, dtype=float)
    labels = np.asarray(labels)
    # Thresholds: from just above max down to min, covering the full range.
    thresholds = np.sort(np.unique(scores))[::-1]
    # Prepend a threshold above every score so the curve starts at (0, 0).
    top = np.array([thresholds[0] + 1.0])
    thresholds = np.concatenate([top, thresholds])

    n_signal = np.sum(labels == 1)
    n_noise = np.sum(labels == 0)

    far = np.empty(len(thresholds))
    hr = np.empty(len(thresholds))
    for i, t in enumerate(thresholds):
        decisions = (scores >= t).astype(int)
        hits = np.sum((decisions == 1) & (labels == 1))
        fa = np.sum((decisions == 1) & (labels == 0))
        hr[i] = hits / n_signal
        far[i] = fa / n_noise

    return far, hr
# mccole: /roc


# mccole: auc
def auc(far, hr):
    """Return the area under the ROC curve using the trapezoidal rule.

    The trapezoidal rule approximates the area as a sum of trapezoids:

        AUC = sum_i  0.5 * (HR_i + HR_{i+1}) * |FAR_i - FAR_{i+1}|

    This is a Riemann sum that converges to the true AUC as the number
    of threshold steps increases.  AUC = 0.5 for chance performance
    (the diagonal) and AUC = 1.0 for perfect discrimination.
    """
    far = np.asarray(far, dtype=float)
    hr = np.asarray(hr, dtype=float)
    # Sort by FAR so the trapezoidal sum goes left to right.
    order = np.argsort(far)
    sorted_far = far[order]
    sorted_hr = hr[order]
    widths = np.abs(np.diff(sorted_far))
    heights = 0.5 * (sorted_hr[:-1] + sorted_hr[1:])
    return float(np.sum(widths * heights))
# mccole: /auc


# mccole: plot
def plot_roc(roc_far, roc_hr, filename):
    """Save an ROC curve plot as an SVG file."""
    curve_data = [{"far": float(f), "hr": float(h)} for f, h in zip(roc_far, roc_hr)]
    diag_data = [{"far": 0.0, "hr": 0.0}, {"far": 1.0, "hr": 1.0}]

    base = alt.Chart().encode(
        x=alt.X("far:Q", title="False alarm rate", scale=alt.Scale(domain=[0, 1])),
        y=alt.Y("hr:Q", title="Hit rate", scale=alt.Scale(domain=[0, 1])),
    )
    curve = base.mark_line(color="steelblue", strokeWidth=2).properties(
        data=alt.Data(values=curve_data)
    )
    diagonal = base.mark_line(strokeDash=[4, 4], color="gray").properties(
        data=alt.Data(values=diag_data)
    )

    chart = (curve + diagonal).properties(
        title="ROC curve (threshold sweep)",
        width=360,
        height=360,
    )
    chart.save(filename)
# mccole: /plot


if __name__ == "__main__":
    import generate_sdt

    scores, labels = generate_sdt.load_data()
    far, hr = roc_curve(scores, labels)
    area = auc(far, hr)
    print(f"AUC: {area:.4f}")
    plot_roc(far, hr, "sdt-roc.svg")
    print("Saved sdt-roc.svg")
