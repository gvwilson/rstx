# Signal Detection Theory Analysis

## The Problem

-   In a detection experiment, an observer responds "yes" or "no" to each stimulus
-   Some stimuli contain a signal, others do not
-   Raw accuracy conflates two separate factors
    -   The observer's ability to detect the signal
    -   Their tendency to say "yes" regardless
-   Framing the outcome as a confusion matrix keeps the two factors separate

| | Observer says "yes" | Observer says "no" |
|---|---|---|
| Signal present | Hit | Miss |
| Signal absent | False alarm | Correct rejection |

-   The [%g hit_rate "hit rate" %] (HR) is
    the proportion of signal trials on which the observer responds "yes"
    -   I.e, hits divided by total signal trials
-   The [%g false_alarm_rate "false alarm rate" %] (FAR) is
    the proportion of noise trials on which the observer incorrectly responds "yes"
    -   False alarms divided by total noise trials

<div class="forma-multiple-choice" data-lang="en" markdown="1">

An observer runs 100 signal trials and 100 noise trials.
They record 70 hits and 30 false alarms.
What are their hit rate and false alarm rate?

HR = 0.70, FAR = 0.30
:   Correct: HR = 70/100 = 0.70 and FAR = 30/100 = 0.30.

HR = 0.70, FAR = 0.70
:   Wrong: the false alarm count (30) is divided by the number of noise
    trials (100), giving 0.30, not 0.70.

HR = 70, FAR = 30
:   Wrong: hit rate and false alarm rate are proportions between 0 and 1,
    not raw counts.

HR = 0.30, FAR = 0.70
:   Wrong: hits and false alarms have been swapped; hits come from signal
    trials and false alarms come from noise trials.

</div>

## Computing Hit Rate and False Alarm Rate

[%inc sdt.py mark="rates"%]

-   `labels` is an array of 1 (signal) and 0 (noise) for each trial.
-   `decisions` is an array of 1 (responded yes) and 0 (responded no).
-   The function counts hits and false alarms
    then divides by the appropriate total number of trials

<div class="forma-ordering" data-lang="en" markdown="1">

Order the steps to compute the hit rate from experiment data.

Count the number of trials on which a signal was present.
Count the number of those signal trials on which the observer responded "yes" (hits).
Divide the hit count by the total number of signal trials.

</div>

## The ROC Curve as a Threshold Sweep

-   An observer does not simply say "yes" or "no"
    -   They have an internal numeric evidence score for each trial
        and say "yes" when that score exceeds a decision threshold
-   By varying the threshold, we trace out different (FAR, HR) pairs
    -   A very high threshold means only very strong evidence triggers a "yes"
        -   Few false alarms, but also few hits
        -   A conservative observer
    -   A very low threshold means almost any evidence triggers a "yes"
        -   Many hits, but also many false alarms
        -   A liberal observer
-   The [%g roc_curve "ROC curve" %] (Receiver Operating Characteristic) is
    the set of all (FAR, HR) pairs an observer can achieve by adjusting the threshold
-   The diagonal line FAR = HR represents chance performance
    -   I.e., the observer gains no extra hits without an equal increase in false alarms
-   A curve that bows toward the upper-left corner means that
    the observer can achieve high hit rates with low false alarm rates,
    i.e., better discrimination

[%inc sdt.py mark="roc"%]

-   `scores` contains the numeric evidence value for each trial
-   `labels` contains 1 for signal trials and 0 for noise trials
-   The function sweeps over all unique score values as candidate thresholds
    from highest (most conservative) to lowest (most liberal)
-   At each threshold,
    a trial is classified as "yes" when its score is at or above the threshold

<div class="forma-matching" data-lang="en" markdown="1">

Match each threshold choice to its likely effect on hit rate and false alarm rate.

Very high threshold
:   Low hit rate and low false alarm rate (conservative: the observer rarely responds).

Very low threshold
:   High hit rate and high false alarm rate (liberal: the observer almost always responds).

Threshold at the midpoint of all scores
:   Intermediate hit rate and false alarm rate (moderate operating point).

</div>

## Area Under the ROC Curve

-   Any single (FAR, HR) pair depends on the threshold chosen,
    which may vary between observers or experiments
-   The [%g area_under_curve "area under the ROC curve" %] (AUC)
    summarizes performance across all thresholds with a single number
-   AUC = 0.5: the ROC is the diagonal, i.e., chance performance
-   AUC = 1.0: the ROC passes through (0, 1), i.e., perfect discrimination
-   Interpretation: AUC equals the probability that a randomly chosen signal trial
    receives a higher evidence score than a randomly chosen noise trial
-   The [%g trapezoidal_rule "trapezoidal rule" %] approximates AUC from the arrays of (FAR, HR) points:

<p>$$\text{AUC} \approx \sum_i \tfrac{1}{2}(\text{HR}_i + \text{HR}_{i+1}) \cdot |\text{FAR}_i - \text{FAR}_{i+1}|$$</p>

-   Each term is the area of a trapezoid
    whose parallel sides are $\text{HR}_i$ and $\text{HR}_{i+1}$
    and whose width is the step in FAR
    -   A [%g riemann_sum "Riemann sum" %]
-   As the number of threshold steps increases, the sum converges to the true area

[%inc sdt.py mark="auc"%]

## Visualizing the ROC Curve

[%inc sdt.py mark="plot"%]

[%figure
  slug="sdt-roc"
  img="sdt-roc.svg"
  alt="A square plot with false alarm rate on the x-axis and hit rate on the y-axis, both ranging from 0 to 1. A blue curve bows toward the upper-left corner above the gray diagonal chance line."
  caption="ROC curve produced by sweeping over score thresholds (blue). The gray dashed diagonal represents chance performance (AUC = 0.5). The bowing of the curve above the diagonal indicates the observer can discriminate signal from noise."
%]

## Testing

-   Hit rate is 1.0 when all signal trials are detected
    -   If the observer responds "yes" to every signal trial, hits equal total signal trials, so HR = 1.0

-   False alarm rate is 0.0 when no noise trial triggers a response
    -   If the observer never responds "yes" on noise trials, false alarms = 0, so FAR = 0.0

-   Rates are proportional to counts
    -   With 3 hits out of 4 signal trials and 1 false alarm out of 2 noise trials, HR = 0.75 and FAR = 0.5

-   ROC starts at the origin
    -   At the threshold above every score, no trial is classified as "yes", so HR = 0 and FAR = 0

-   ROC ends at (1, 1)
    -   At the threshold below every score, every trial is classified as "yes", so HR = 1 and FAR = 1

-   ROC is monotonically increasing
    -   Lowering the threshold can only keep or increase both HR and FAR, never decrease either

-   ROC passes through (0, 1) for perfectly separable scores
    -   When every signal score exceeds every noise score,
        one threshold admits all signals and no noise, placing a point at FAR = 0, HR = 1

-   AUC of the diagonal is 0.5
    - The diagonal ROC (FAR = HR) represents chance performance,
      so its area is exactly half the unit square

-   AUC of a perfect step is 1.0
    -   A step from (0, 0) to (0, 1) to (1, 1) encloses the entire unit square

-   AUC is above 0.5 for separable scores
    -   When signal scores are on average higher than noise scores,
        the ROC bows above the diagonal and AUC > 0.5

-   AUC does not depend on the order of FAR values supplied
    -   The implementation sorts FAR internally, so reversing the input arrays gives the same result

[%inc test_sdt.py%]

<div class="forma-flashcard" data-lang="en" markdown="1">

Signal detection key terms

Hit rate
:   The proportion of signal trials on which the observer correctly responds "yes":
    HR = hits / total signal trials; also called the true positive rate.

False alarm rate
:   The proportion of noise trials on which the observer incorrectly responds "yes":
    FAR = false alarms / total noise trials; also called the false positive rate.

ROC curve
:   The Receiver Operating Characteristic curve; a plot of hit rate against false-alarm
    rate as the decision threshold varies from very conservative to very liberal;
    produced by a threshold sweep over evidence scores.

Area under the curve (AUC)
:   A summary of ROC performance computed using the trapezoidal rule; AUC = 0.5 for
    chance performance and AUC = 1.0 for perfect discrimination; equals the probability
    that a random signal trial receives a higher evidence score than a random noise trial.

</div>

## Note on the Gaussian Model

-   The equal-variance Gaussian model summarizes performance compactly
    via $d' = \Phi^{-1}(\text{HR}) - \Phi^{-1}(\text{FAR})$,
    where $\Phi^{-1}$ is the inverse of the standard normal CDF
-   This assumes both the noise distribution and the signal distribution are normal with equal variance
    -   Only their means differ
-   The threshold-sweep ROC presented in this lesson makes no distributional assumptions
    -   It works for any numeric evidence score and any underlying distribution

<section class="exercises" markdown="1">

## Exercises

### Do the math

An observer's evidence scores are identical for signal and noise trials, so their
ROC curve follows the diagonal exactly.
What is their AUC?

### Compute AUC from a small example

Given evidence scores `[0.1, 0.4, 0.35, 0.8]` and labels `[0, 0, 1, 1]`
(0 = noise, 1 = signal), trace through `roc_curve` by hand at each unique
score threshold.
Compute the AUC using the trapezoidal rule.
Check your answer against the function.

### Effect of threshold on the confusion matrix

Using the synthetic data from `generate_sdt.py`, choose three thresholds:
the 25th, 50th, and 75th percentile of all scores.
For each threshold, compute HR and FAR and mark the corresponding point on
the ROC curve.
How does moving from a conservative threshold to a liberal threshold change
the confusion matrix?

### Comparing two observers

Observer A has evidence scores that follow N(0, 1) for noise and N(1.0, 1)
for signal.
Observer B has scores that follow N(0, 1) for noise and N(2.0, 1) for signal.
Generate 200 trials for each observer (RNG seed 7493418), compute their ROC
curves and AUCs, and plot both curves on the same axes.
Which observer has the higher AUC and why?

### Trapezoidal approximation error

The trapezoidal rule is exact only when the curve is piecewise linear.
Generate a fine-grained ROC (1 000 signal and 1 000 noise trials) and a
coarse-grained ROC (20 signal and 20 noise trials) from the same underlying
score distributions.
Compare their AUC estimates.
How large is the approximation error in the coarse case?

</section>
