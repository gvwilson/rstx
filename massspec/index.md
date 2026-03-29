# Peak Detection in Mass Spectra

## The Problem

-   A mass spectrometer measures how many ions in a sample have each mass-to-charge ratio (m/z)
-   The output is a spectrum, i.e., a curve of intensity versus m/z, with a peak wherever a compound is present
-   In practice the spectrum is noisy, so the peaks must be found algorithmically rather than by eye
-   Peak detection is a preprocessing step in proteomics, metabolomics, and analytical chemistry

## Representing a Spectrum

-   A synthetic spectrum is a sum of Gaussian peaks at known m/z values plus Gaussian noise:

<p>$$I(m) = \sum_k h_k \exp\!\left(-\frac{(m - \mu_k)^2}{2\sigma_k^2}\right) + \varepsilon, \qquad \varepsilon \sim \mathcal{N}(0,\,\sigma_\text{noise}^2)$$</p>

-   $\mu_k$, $h_k$, and $\sigma_k$ are the center, height, and width of peak $k$
-   Intensities are clipped to zero because a negative ion count has no physical meaning

[%inc generate_spectrum.py mark="constants"%]
[%inc generate_spectrum.py mark="make-spectrum"%]

## Smoothing

-   Noise causes random local maxima that look like peaks but carry no chemical information
-   A [%g moving_average "moving-average" %] filter
    replaces each point with the mean of its $w$ nearest neighbours,
    reducing point-to-point variance by a factor of $w$:

<p>$$\hat{I}_i = \frac{1}{w} \sum_{j=i-\lfloor w/2 \rfloor}^{i+\lfloor w/2 \rfloor} I_j$$</p>

-   Smoothing attenuates noise without shifting peak positions
    as long as $w$ is small relative to the peak width

[%inc massspec.py mark="smooth"%]

<div class="forma-multiple-choice" data-lang="en" markdown="1">

The noise standard deviation before smoothing is $\sigma_\text{noise} = 0.05$.
After applying a moving-average filter with window w = 5,
what is the approximate standard deviation of the smoothed noise?

0.05 (unchanged)
:   Wrong: averaging reduces variance — a filter that left noise unchanged would be useless.

$0.05 / \sqrt{5} \approx 0.022$
:   Correct: averaging w independent values reduces variance by $1/w$, so standard deviation by $1/\sqrt{w}$.

0.05 / 5 = 0.010
:   Wrong: the variance (not the standard deviation) is divided by w; the std dev is divided by $\sqrt{w}$.

$0.05 \times \sqrt{5} \approx 0.112$
:   Wrong: smoothing reduces noise, not increases it.

</div>

## Peak Detection

-   After smoothing,
    a peak candidate is any point that is a strict local maximum and whose smoothed intensity exceeds a threshold
-   A single broad peak can produce several adjacent local maxima after smoothing
-   [%g non_maximum_suppression "Non-maximum suppression" %] keeps only
    the tallest candidate within a window of `min_distance` index positions

[%inc massspec.py mark="detect"%]

<div class="forma-ordering" data-lang="en" markdown="1">

Put these peak-detection steps in the correct order.

1.  Generate a spectrum: sum Gaussian peaks and add noise
1.  Apply a moving-average filter to smooth the spectrum
1.  Find all points that are strict local maxima above the threshold
1.  Apply non-maximum suppression within `min_distance` positions
1.  Return the m/z values of the surviving candidates

</div>

<div class="forma-matching" data-lang="en" markdown="1">

Match each parameter to the problem it is designed to address.

| Parameter | Solves |
| --------- | ------ |
| `SMOOTH_WINDOW` | Prevents one broad peak from being reported as multiple peaks |
| `THRESHOLD` | Attenuates point-to-point noise before the peak search |
| `MIN_DISTANCE` | Rejects local maxima that are only noise fluctuations |

</div>

[%figure
  slug="massspec-signal"
  img="massspec.svg"
  alt="Mass spectrum showing raw intensity in grey, smoothed in blue, and detected peaks as red vertical lines."
  caption="Synthetic spectrum with four compounds. Grey: raw signal. Blue: smoothed signal (window = 5). Red rules: detected peak positions. All four compounds are recovered within 1 Da of their true m/z values."
%]

## What the Detector Finds in Pure Noise

-   The same detector,
    with the same threshold,
    applied to a spectrum that contains no signal at all produces false peaks

[%inc generate_spectrum.py mark="make-noise"%]

[%figure
  slug="massspec-noise"
  img="massspec_noise.svg"
  alt="Pure-noise spectrum with 9 false peaks marked by red vertical lines."
  caption="Pure Gaussian noise (no signal) smoothed and searched with a threshold of 0.04. Nine false peaks are reported. The same noise searched at the normal threshold of 0.10 produces zero false peaks."
%]

-   With noise standard deviation $\sigma_\text{noise} = 0.05$ and window $w = 5$,
    the smoothed noise has standard deviation $0.05 / \sqrt{5} \approx 0.022$
-   A threshold of 0.04 is roughly $1.8\sigma$
    -   Roughly 7% of smoothed values exceed it,
        so several local maxima among them are expected
-   The operating threshold of 0.10 is $4.5\sigma$
    -   Fewer than one point in 100,000 exceeds it by chance,
        making false positives negligible for a 500-point spectrum

[%inc massspec.py mark="constants"%]

<div class="forma-multiple-choice" data-lang="en" markdown="1">

The noise figure shows 9 false peaks at threshold 0.04 and 0 false peaks at threshold 0.10.
What is the most important conclusion?

The detector is broken — a correct detector should never find peaks in pure noise
:   Wrong: any threshold-based detector produces false positives when the threshold is below the noise floor — this is expected behaviour, not a bug.

A threshold of 0.10 is always the right choice for any spectrum
:   Wrong: the right threshold depends on the noise level and peak heights; 0.10 is calibrated specifically to this synthetic dataset.

The threshold must be set well above the smoothed noise floor to suppress false positives
:   Correct: at 0.04 $\approx 1.8\sigma$ roughly 7% of smoothed noise exceeds the threshold; at 0.10 $\approx 4.5\sigma$ fewer than 1 in 100 000 values do.

Increasing the smoothing window eliminates false positives at any threshold
:   Wrong: more smoothing reduces noise amplitude but cannot reduce it to zero; false positives persist if the threshold is too low.

</div>

## Testing

Smoothing a constant
:   A constant signal has no noise to reduce; smoothing must leave it unchanged
    (except at the boundaries, which are zero-padded by `np.convolve`).

Variance reduction
:   The defining purpose of the filter is to reduce variance.
    If smoothing increases variance the implementation is wrong.

Length preservation
:   `np.convolve` with `mode='same'` always returns an array of the same length as the input.
    This is worth checking explicitly because changing the mode would silently break downstream code.

Known peak positions
:   The detector must find all four compounds within a tolerance that reflects the grid spacing
    (1 Da per index) and is well below the minimum peak separation (> 100 Da).
    A tolerance of 5 Da is used:
    it is 5X the grid spacing and 20X smaller than the nearest adjacent peaks,
    giving a clear pass/fail criterion without being unnecessarily tight.

Threshold at infinity
:   Raising the threshold until it exceeds all values must produce an empty result.
    This guards against off-by-one errors in the threshold comparison.

Non-maximum suppression
:   The test constructs two well-separated Gaussians (10 Da apart, sigma = 2 Da)
    that produce two distinct local maxima in the intensity array.
    With `min_distance = 12`, only the taller is kept;
    with `min_distance = 5`, both survive.

Pure noise
:   Running the detector on pure noise at a low threshold must return at least one false peak,
    confirming the expected false-positive behaviour.
    Running at the operating threshold must return none,
    confirming it is set high enough.

[%inc test_massspec.py%]

<section class="exercises" markdown="1">

## Exercises

### Savitzky-Golay filter

Replace the moving-average smoother with a Savitzky-Golay filter, which fits a low-degree
polynomial to each window rather than taking a plain mean.  The advantage is that the filter
preserves peak heights more accurately.
Use `scipy.signal.savgol_filter` and compare the peak positions and heights it reports
to those from the moving-average filter on the same synthetic spectrum.

### Baseline correction

Real spectra often have a slowly varying baseline (background signal) that shifts all
intensities upward.  Simulate this by adding a low-frequency sinusoid
$B(m) = 0.3 \sin(2\pi m / 800)$ to the synthetic spectrum before adding noise.
Implement `subtract_baseline(mz, intensity, window)` that uses a moving minimum over a
large window to estimate and remove the baseline, then show that peak detection on the
corrected spectrum recovers the same four compounds.

### Peak area

The area under a Gaussian peak is $h \sigma \sqrt{2\pi}$ and is proportional to compound
abundance.  After detecting each peak, fit a Gaussian to the smoothed signal in a small
window around it using `scipy.optimize.curve_fit` and report the fitted height, center,
and area.  Compare the fitted values to the ground truth in `PEAKS`.

### Receiver operating characteristic

Use `make_pure_noise` to generate 200 noise-only spectra and `make_spectrum` to generate
200 signal spectra.  For each, record whether the detector finds at least one peak.
Sweep the threshold from 0.01 to 0.30 and plot the ROC curve (true positive rate vs.
false positive rate).  Report the threshold that maximises the F1 score.

</section>
