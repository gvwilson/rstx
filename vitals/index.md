# Anomaly Detection in Patient Vital Signs

## The Problem

-   Intensive care units record physiological signals continuously: heart rate, blood pressure,
    oxygen saturation, respiratory rate.
-   Clinicians cannot watch every channel at every moment, so automated flagging of unusual
    readings reduces the chance of a dangerous change going unnoticed.
-   Two qualitatively different anomalies are common: sustained [%g step_change "step changes" %]
    (the baseline shifts to a new level) and isolated [%g spike_outlier "spikes" %]
    (a single reading is far from the local trend).
-   A simple but effective detector compares each reading to a local reference built from the
    most recent $w$ readings; a deviation beyond a chosen threshold raises a flag.

## Rolling Statistics

-   A [%g rolling_window "rolling window" %] of width $w$ centred (or trailing) at position $i$
    uses only the $w$ most recent observations to estimate the local mean and variance.
-   This makes the reference adaptive: it follows slow drifts in the baseline without permanently
    inflating the variance estimate when a sustained shift begins.
-   If $\bar{x}_i$ and $\hat{\sigma}_i$ are the rolling mean and standard deviation,
    the [%g z_score "z-score" %] of reading $x_i$ against the rolling window is:

$$z_i = \frac{x_i - \bar{x}_i}{\hat{\sigma}_i}$$

<div class="forma-numeric-entry" data-correct="2.0" data-tolerance="0.01" data-lang="en" markdown="1">

A trailing window of width 3 contains values [68, 70, 72].
The window mean is 70, and the sample standard deviation is 2.
A new reading of 74 arrives.
What is the z-score of 74 against this window?

</div>

## Detecting Anomalies

-   A reading is flagged when $|z_i| > \theta$, where $\theta$ is the detection threshold.
-   Raising $\theta$ reduces false positives (normal variation incorrectly flagged) at the cost
    of more false negatives (real anomalies missed); lowering it does the reverse.
-   When the rolling standard deviation is zero (all values in the window are identical), no
    flag is raised: there is no variation to compare against.

<div class="forma-multiple-choice" data-lang="en" markdown="1">

A z-score threshold of $\theta = 3$ is replaced with $\theta = 2$.
What is the most likely effect on the detector?

Fewer true anomalies are detected because the bar is now harder to reach.
:   Wrong: a lower threshold makes it easier for a reading to exceed the threshold, not harder.

More readings are flagged, including some that are normal variation rather than genuine anomalies.
:   Correct: the detector becomes more sensitive — it catches more anomalies but also produces more false positives.

Only step changes are detected; spikes are unaffected.
:   Wrong: the z-score test is symmetric; it flags any deviation regardless of whether it is sustained or isolated.

The rolling standard deviation doubles, compensating for the lower threshold.
:   Wrong: the standard deviation is computed from the data; changing the threshold does not alter it.

</div>

## Generating Synthetic Vital Signs

-   The baseline is Gaussian noise around 70 bpm (a typical resting heart rate).
-   A sustained step change of 12 bpm begins at minute 90, simulating a fever or
    haemodynamic deterioration.
-   Three isolated spikes of 18 bpm above the local baseline are injected at known positions.

[%inc generate_vitals.py mark="constants"%]

[%inc generate_vitals.py mark="generate"%]

## Rolling Mean and Standard Deviation

[%inc vitals.py mark="rolling"%]

-   The trailing window (ending at the current position) is the natural choice for real-time
    monitoring: a reading can only be compared against previous observations.
-   The first $w - 1$ positions use a shorter window as data accumulates; this warm-up period
    means the detector is less reliable at the very start of the recording.

## Flagging Anomalies

[%inc vitals.py mark="detect"%]

<div class="forma-matching" data-lang="en" markdown="1">

Match each anomaly type to the property that makes it detectable.

| Anomaly | Detectable because |
| ------- | ------------------ |
| Isolated spike | A single reading's z-score exceeds the threshold even though nearby readings are normal |
| Sustained step change | After the window catches up to the new level the z-score may drop, but readings near the transition have large z-scores |
| Slow drift | The rolling mean follows the drift, so z-scores stay small — this detector may miss it |

</div>

## Visualizing the Results

[%inc vitals.py mark="plot"%]

[%figure
  slug="vitals-anomalies"
  img="vitals.svg"
  alt="Time series of heart rate with rolling mean overlay and red triangle markers at four flagged anomaly positions."
  caption="Two hundred minutes of synthetic heart rate (blue line) with 20-minute rolling mean (orange). Red triangles mark the four readings flagged at threshold 3: all three injected spikes and the first point where the step change raises the z-score above 3."
%]

## Testing

Rolling statistics length
:   The output arrays must have the same length as the input regardless of the window size;
    an off-by-one in the index calculation is the most common bug.

Rolling statistics known values
:   For `[1, 2, 3, 4, 5]` with window 3, position 2 covers `[1, 2, 3]`: mean 2.0, sample
    std 1.0.  Exact integer arithmetic means no tolerance is needed.

Single-element window returns std 0
:   At position 0 only one value is in the window; the sample std is undefined ($n - 1 = 0$).
    The implementation returns 0.0 rather than raising an error or returning NaN.

Constant signal produces no anomalies
:   When every value is identical both the rolling mean and the deviation are zero, so
    $|z_i| = 0 < \theta$ everywhere.  This confirms the zero-std guard works correctly.

Isolated spike is detected
:   A single reading of 100 bpm in a constant 70 bpm sequence produces a z-score of
    approximately 2.8 against window 10 at threshold 2.0 — the spike must be flagged.
    The tolerance in the comment derivation is $\sigma \approx 9.5$ giving $z \approx 2.84$,
    which is a 42% safety factor above the threshold.

High-threshold flags nothing on normal data
:   With $\theta = 10$ (ten rolling standard deviations) and 200 normally distributed
    readings (std = 2 bpm), no value should be flagged.  The maximum expected z-score for
    200 independent Gaussian samples is around 3.5, well below 10.

Step change is eventually detected
:   A 15 bpm step change on a 0 bpm noise background produces a z-score above 3 as soon as
    the window straddles the transition.  This test uses noiseless data to guarantee detection.

[%inc test_vitals.py%]

<div class="forma-flashcard" data-lang="en" markdown="1">

Anomaly detection key terms

Rolling window
:   A fixed-width sliding buffer of the $w$ most recent observations used to estimate local statistics; as new data arrives the oldest observation drops out of the buffer

Z-score
:   The number of standard deviations by which an observation deviates from the local mean; values beyond a chosen threshold are flagged as anomalies

Detection threshold $\theta$
:   The z-score cutoff for raising a flag; a higher threshold reduces false positives but may miss smaller anomalies (lower sensitivity)

Step change
:   A sustained shift in the baseline level; a rolling detector flags readings near the transition but adapts once the window has fully moved past it

Spike
:   An isolated outlier reading that returns to baseline immediately; the rolling window is not contaminated for long so subsequent readings quickly return to normal z-scores

</div>

<section class="exercises" markdown="1">

## Exercises

### Bidirectional window

The trailing window can react only after the anomaly has entered the window.
Replace the trailing window with a centred window that looks $w/2$ steps back and $w/2$
steps forward.  Show that this detects a spike at the exact position it occurs rather than
$w/2$ steps after.  What is the cost of using a centred window in a real-time application?

### Threshold sweep

Generate 100 replicate datasets with the same parameters but different random seeds.
For each dataset count the true positive rate (fraction of injected anomalies flagged)
and false positive rate (fraction of normal readings flagged) at thresholds $1, 2, 3, 4$.
Plot the resulting ROC curve and find the threshold that maximises the F1 score.

### Exponentially weighted mean

Replace the uniform rolling window with an exponentially weighted moving average (EWMA):

<p>$$\bar{x}_i = \alpha x_i + (1 - \alpha) \bar{x}_{i-1}$$</p>

with smoothing factor $\alpha \in (0, 1)$.  Derive the corresponding EWMA variance
estimator and re-implement `rolling_stats` using it.  Compare the detection lag between
the uniform and EWMA detectors on the step-change data.

### Multivariate anomaly score

A patient has two simultaneous signals: heart rate and respiratory rate.
Anomalies in both signals at the same time are more clinically significant than anomalies
in just one.  Combine the two individual z-scores into a single multivariate score
(e.g. the Euclidean norm of the two z-score vectors) and show that it improves detection
of anomalies that affect both signals simultaneously while maintaining the per-signal
false-positive rate.

</section>
