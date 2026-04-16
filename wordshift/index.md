# Word Frequency Change Over Time

## The Problem

-   A word's relative frequency in a corpus can rise or fall over decades as cultural
    and linguistic fashions change.
-   [%g diachronic_analysis "Diachronic analysis" %] asks: given a corpus of texts
    labelled by period, how can we detect and quantify these changes?
-   The approach here:
    -   Generate a synthetic corpus in which each decade's token counts include three
        target words with known injected linear trends.
    -   Normalize raw counts by total tokens per decade to obtain
        [%g normalized_frequency "normalized frequencies" %].
    -   Estimate a [%g word_shift "word-shift" %] slope for each target word using
        [%g ordinary_least_squares "ordinary least squares" %].
    -   Visualize frequency trajectories with Vega-Altair.

<div class="forma-multiple-choice" data-lang="en" markdown="1">

Why normalize raw word counts by the total tokens per decade rather than
comparing raw counts directly?

Because raw counts are always larger in recent decades due to digitization bias.
:   Wrong: raw counts may be larger in any decade depending on corpus size;
    the direction of that bias is not fixed.

Because a word can appear more often simply because more text was produced in
that decade, not because the word became more popular.
:   Correct: normalizing converts counts to relative frequencies so that an
    increase in a word's share of tokens is attributable to changed usage, not
    to a larger corpus.

Because normalized frequencies are always integers and easier to work with.
:   Wrong: normalized frequencies are proportions (values between 0 and 1), not
    integers.

Because the normalization removes all sampling noise from the data.
:   Wrong: normalization corrects for corpus size differences but cannot remove
    the statistical variation that results from sampling a finite corpus.

</div>

## Normalized Frequency

-   For word $w$ in decade $d$ with raw count $c_{w,d}$ and total token count
    $N_d = \sum_{w'} c_{w',d}$, the normalized frequency is:

$$f_{w,d} = \frac{c_{w,d}}{N_d}$$

-   All normalized frequencies in a decade sum to 1, making them comparable across
    decades regardless of how many texts were digitized or produced.

## Linear Trend

-   A linear trend assumes that the normalized frequency changes by a constant amount
    per decade: $f_{w,d} = \alpha_w + \beta_w \cdot d_{\text{idx}}$, where
    $d_{\text{idx}}$ is the decade index (0 for the earliest decade, 1 for the next,
    and so on).
-   The [%g ordinary_least_squares "OLS" %] slope estimator is:

<p>$$\hat{\beta}_w = \frac{\displaystyle\sum_d (d_{\text{idx}} - \bar{d})(f_{w,d} - \bar{f}_w)} {\displaystyle\sum_d (d_{\text{idx}} - \bar{d})^2}$$</p>

-   A positive $\hat{\beta}_w$ means the word's share of tokens rose over time;
    a negative slope means it fell.
-   The units of $\hat{\beta}_w$ are normalized-frequency change per 10-year period.

## Generating Synthetic Data

-   Decade indices run from 0 (1850) to 10 (1950)
-   "telegraph" has base frequency 0.005 and rises by 0.002 per decade
-   "candle" has base frequency 0.025 and falls by 0.002 per decade
-   "steam" is stable at 0.015 throughout (zero slope, used as a control)
-   97 background words share the remaining probability mass equally
-   Multinomial sampling with 5000 tokens per decade adds realistic noise

[%inc generate_wordshift.py mark="generate"%]

## Computing Normalized Frequencies

[%inc wordshift.py mark="normalize"%]

## Estimating Trend Slopes

[%inc wordshift.py mark="trend"%]

## Visualizing Frequency Trajectories

[%inc wordshift.py mark="plot"%]

[%figure
  slug="wordshift-trajectory"
  img="wordshift-trajectory.svg"
  alt="Line chart with three lines. The telegraph line rises from near zero to about 0.025. The candle line falls from 0.025 to near zero. The steam line remains roughly flat near 0.015."
  caption="Normalized frequency of three target words across decades 1850–1950. The rising and falling trends in telegraph and candle are clearly visible despite multinomial sampling noise."
%]

## Testing

Normalization sums to one
:   After normalization, the sum of all word frequencies within each decade must
    equal 1.0 to floating-point precision.

Non-negative frequencies
:   All normalized frequencies must be non-negative; a negative value would indicate
    a bug in the join or division step.

Flat series has zero slope
:   A sequence of identical frequencies gives OLS slope exactly 0.0.

Known-slope recovery
:   A perfectly linear sequence with slope 0.002 must return slope 0.002 to
    machine precision (no sampling noise, so no tolerance needed).

Single-point series
:   A single-point input has a zero denominator; the function must return 0.0
    rather than raising an exception.

Slope signs
:   The slope for "telegraph" must be positive, for "candle" negative, and
    for "steam" near zero (within 0.001).

Slope magnitude
:   The recovered slope for each target word must be within 0.001 of the true
    injected value.  The expected standard error of the OLS estimator for this
    corpus is below 0.0002, so 0.001 allows more than five standard errors of
    sampling variation before a test failure.

[%inc test_wordshift.py%]

<div class="forma-flashcard" data-lang="en" markdown="1">

Word frequency change key terms

Diachronic analysis
:   The study of how linguistic features (word frequencies, grammatical constructions)
    change across time periods; contrasted with synchronic analysis, which examines
    a single point in time

Normalized frequency
:   A word's count divided by the total token count for the same period; expresses
    the word's share of the corpus rather than its raw occurrence count, making
    comparisons across periods of different sizes fair

Word shift
:   A change in the relative frequency of a word over time; a positive shift
    indicates rising usage, a negative shift indicates declining usage

OLS slope
:   In this context, $\hat{\beta}_w = \sum_d (d-\bar{d})(f-\bar{f}) / \sum_d (d-\bar{d})^2$;
    the rate of change of normalized frequency per decade estimated by ordinary least squares

</div>

<section class="exercises" markdown="1">

## Exercises

### Do the math

1.  A word appears 50 times in a decade that contains 2000 total tokens.
    What is its normalized frequency?

1.  A word has normalized frequency 0.010 at decade index 0 and 0.020 at decade
    index 1 (two data points only).
    The mean decade index is 0.5 and the mean frequency is 0.015.
    What is the OLS slope?

### Confidence interval on the slope

Extend `linear_trend` to return both the slope and its standard error
$\text{SE}(\hat{\beta}) = \hat{\sigma} / \sqrt{\sum_d (d - \bar{d})^2}$,
where $\hat{\sigma}^2 = \sum_d (f_{w,d} - \hat{f}_{w,d})^2 / (n - 2)$ is the
residual variance.
Report a 95% confidence interval for each target word and check whether the
interval for "steam" contains zero.

### Detecting non-linear change

The linear model assumes a constant rate of change.
Add a word "flash" to the generator whose frequency rises steeply from 1850 to 1900
and then falls back to its starting level from 1900 to 1950 (an inverted V shape).
Compute its OLS slope and explain why the slope is near zero even though the word's
usage clearly changed.
What alternative measure would capture the inverted-V pattern?

### Rank shift

Instead of absolute frequency, use the rank of each target word within each decade
(rank 1 = most frequent).
Compute the rank-change slope and compare it to the frequency-change slope.
In which cases do they agree and in which do they diverge?

### Real corpus application

Download word-frequency data for two contrasting words from a public corpus such as
Google Ngrams.
Normalize by total token count per year, aggregate to decades, and apply `linear_trend`.
Does the recovered slope match the visual trend in the trajectory plot?

</section>
