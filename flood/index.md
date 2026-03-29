# Flood Frequency Analysis

## The Problem

-   Infrastructure such must be designed to withstand rare but extreme floods
-   Engineers specify design events by [%g return_period "return period" %]:
    the average number of years between events that exceed a given magnitude
-   A 100-year flood does not occur once per century on a schedule:
    it has a 1% probability of being exceeded in any given year
-   Estimating these probabilities from historical records
    by fitting a statistical distribution to the annual maximum flows

## The Log-Normal Distribution

-   Annual maximum flows are positive and right-skewed,
    so a [%g log_normal_distribution "log-normal distribution" %] is a natural starting point
-   A random variable $X$ is log-normally distributed if $Y = \ln X$ follows a normal distribution
-   The log-normal distribution is characterised by two parameters:
    -   $\mu_y$ (the mean of $\ln X$)
    -   $\sigma_y > 0$ (the standard deviation of $\ln X$)
-   If $\Phi$ is the standard normal CDF, the log-normal's cumulative distribution function is:

<p>$$F(x) = \Phi\!\left(\frac{\ln x - \mu_y}{\sigma_y}\right), \quad x > 0$$</p>

<div class="forma-multiple-choice" data-lang="en" markdown="1">

A dataset of 50 annual maximum flows has sample mean log-flow $\bar{y} = 4.80$
and sample standard deviation of log-flows $s_y = 0.40$.
Using the log-normal model, what is $\hat{\mu}_y$?

4.80
:   Correct: the method-of-moments estimate of $\mu_y$ is simply the sample mean of the log-flows.

0.40
:   Wrong: 0.40 is $s_y$, the estimate of $\sigma_y$, not of $\mu_y$.

$e^{4.80} \approx 121$
:   Wrong: exponentiating $\bar{y}$ gives the estimated median flow in m^3/s, not the log-mean parameter.

$4.80 / 0.40 = 12$
:   Wrong: dividing the log-mean by the log-standard-deviation has no statistical interpretation here.

</div>

## Generating Synthetic Data

-   We draw 50 years of annual maximum flows from a known log-normal distribution
    so that we can verify our estimator
-   Drawing $Y \sim \text{Normal}(\mu_y, \sigma_y)$ and setting $X = e^Y$
    gives $X \sim \text{LogNormal}(\mu_y, \sigma_y)$

[%inc generate_flood.py mark="constants"%]

[%inc generate_flood.py mark="generate"%]

## Fitting by the Method of Moments

-   The [%g method_of_moments "method of moments" %]
    sets the distribution's theoretical moments equal to the sample moments
    and solves for the parameters
-   For the log-normal distribution the moments of $Y = \ln X$ are exactly $\mu_y$ and $\sigma_y$,
    so the estimates are:

<p>$$\hat{\mu}_y = \bar{y} = \frac{1}{n}\sum_{i=1}^n \ln x_i \qquad \hat{\sigma}_y = s_y = \sqrt{\frac{1}{n-1}\sum_{i=1}^n (\ln x_i - \bar{y})^2}$$</p>

-   Here, the $n-1$ denominator applies [%g bessel_correction "Bessel's correction" %]
    for the sample standard deviation

[%inc flood.py mark="constants"%]

[%inc flood.py mark="fit-lognormal"%]

<div class="forma-ordering" data-lang="en" markdown="1">

Put these steps in the correct order for method-of-moments estimation of log-normal parameters.

1.  Take the natural logarithm of each annual maximum flow to get $y_i = \ln x_i$
1.  Compute $\hat{\mu}_y = \bar{y}$, the sample mean of the log-flows
1.  Compute $\hat{\sigma}_y = s_y$, the sample standard deviation of the log-flows (with $n-1$ denominator)
1.  Use $\hat{\mu}_y$ and $\hat{\sigma}_y$ to compute return levels or plot the fitted distribution

</div>

## Return Periods

-   The $T$-year return level $x_T$ is the flow magnitude exceeded with probability $1/T$ in any given year.
-   Setting $F(x_T) = 1 - 1/T$ and inverting the log-normal CDF:

<p>$$x_T = \exp\!\left(\hat{\mu}_y + z_p\, \hat{\sigma}_y\right), \quad p = 1 - \frac{1}{T}$$</p>

-   Here,
    $z_p = \Phi^{-1}(p)$ is the standard normal quantile at probability $p$,
    computed with `scipy.stats.norm.ppf`.

[%inc flood.py mark="return-level"%]

<div class="forma-numeric-entry" data-correct="308.1" data-tolerance="1.0" data-lang="en" markdown="1">

Using $\hat{\mu}_y = 4.80$ and $\hat{\sigma}_y = 0.40$, the standard normal quantile at
$p = 0.99$ is $z_{0.99} \approx 2.3263$.
Compute the 100-year return level $x_{100} = \exp(4.80 + 2.3263 \times 0.40)$.
Give your answer in m^3/s, rounded to one decimal place.

</div>

<div class="forma-multiple-choice" data-lang="en" markdown="1">

A community's flood barrier is designed for the 100-year return level.
Over the next 100 years, what is the probability that the barrier is overtopped at least once?

Exactly 1%
:   Wrong: 1% is the probability of exceedance in a single year, not over 100 years.

Approximately 63%
:   Correct: P(at least one exceedance in 100 years) = 1 - (1 - 1/100)^100 ≈ 1 - e^{-1} ≈ 63%.

Exactly 100%
:   Wrong: the return period is an average; exceedance is a random event, not guaranteed over any finite horizon.

Exactly 50%
:   Wrong: the return period T such that P(at least one exceedance in T years) = 0.5 is T ≈ 69 years, not 100.

</div>

## Normal Probability Plot

-   Plotting data on a normal probability plot ([%g q_q_plot "Q-Q plot" %])
    provides a visual check on whether the log-normal distribution fits
-   The [%g weibull_plotting_position "Weibull plotting position" %] $p_i = i/(n+1)$
    assigns a non-exceedance probability to each ranked observation without assuming a specific distribution
-   The theoretical normal quantile $z_i = \Phi^{-1}(p_i)$ linearises the log-normal CDF:
    if $\ln X$ is normally distributed, plotting $(z_i, \ln x_{(i)})$ gives a straight line

[%inc flood.py mark="plotting-positions"%]

[%inc flood.py mark="plot"%]

[%figure
  slug="flood-probability-paper"
  img="flood.svg"
  alt="Scatter plot of ln(annual maximum flow) vs. standard normal quantile, with a fitted red line. Points follow the line closely."
  caption="Normal probability plot of log-flows. Points are ranked log-observations; the red line is the fitted log-normal distribution. Departures from the line indicate that the log-normal model may not fit."
%]

## Testing

-   Parameter recovery on a large sample
    -   With $n = 10\,000$ the central-limit theorem says that
        the standard error of $\hat{\mu}_y$ is roughly $\sigma_y / \sqrt{n} \approx 0.004$,
        well under 1%
    - A relative tolerance of 5% gives a safety factor of $\sim 50$ over the expected sampling error

-   Monotone return levels
    -   The log-normal quantile $x_T = \exp(\mu_y + z_p \sigma_y)$ is strictly increasing in $T$
        because $\sigma_y > 0$ and $z_p = \Phi^{-1}(1 - 1/T)$ is strictly increasing in $T$
    -   Any violation would indicate an error in the formula or the sign conventions

-   Algebraic consistency
    -   $F(x_T) = 1 - 1/T$ is the definition of the return level
    -   it must hold to numerical precision ($< 10^{-10}$)

-   Valid plotting positions
    -   $p_i = i/(n+1) \in (0,1)$ guarantees finite normal quantiles
    -   sorted log-flows must be non-decreasing

[%inc test_flood.py%]

<section class="exercises" markdown="1">

## Exercises

### Confidence intervals by bootstrap

Estimate 95% confidence intervals for the 100-year return level using the bootstrap:
draw 1000 samples of size 50 with replacement from the original data,
fit the log-normal distribution to each, and compute the 100-year return level.
Report the 2.5th and 97.5th percentiles of the 1000 estimates.
How wide is the interval relative to the point estimate?

### Hazen plotting positions

Replace the Weibull plotting position $p_i = i/(n+1)$ with the Hazen position
$p_i = (i - 0.5) / n$, which places each observation at the midpoint of its
probability interval.
How much do the plotted points shift on the normal probability plot?
Does the fitted line change?

### Comparing distributions

The log-normal is one of several distributions used in hydrology; the Pearson
Type III (a three-parameter gamma family) is another common choice.
Use `scipy.stats.pearson3.fit` to fit the Pearson Type III distribution to
the log-flows and compare its 100-year return level with the log-normal estimate.
Which distribution fits the Q-Q plot more closely?

### Annual maxima from daily data

Generate a synthetic series of daily flows for 50 years as the exponent of a
first-order autoregressive process: $\ln Q_t = \phi \ln Q_{t-1} + \varepsilon_t$
with $\phi = 0.8$ and $\varepsilon_t \sim \text{Normal}(0, 0.2)$.
Extract the annual maximum from each year.
Fit the log-normal distribution to the maxima and plot the result on a normal
probability plot.
How does the quality of the fit compare to the case where the data were drawn
directly from a log-normal distribution?

</section>
