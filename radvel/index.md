# Exoplanet Detection via Radial Velocity

## The Problem

-   A planet orbiting a star pulls the star gravitationally,
    causing it to wobble around the system's centre of mass
-   This wobble produces a periodic Doppler shift in the star's spectral lines
    that can be measured as a [%g radial_velocity "radial-velocity" %] (RV) variation
-   Fitting a sinusoidal model to the RV time series recovers the planet's orbital period
    and a lower bound on its mass
-   The RV method discovered the first confirmed exoplanet around a Sun-like star (51 Pegasi b, in 1995)
    and remains one of the most productive detection techniques

## The Radial Velocity Signal

-   The velocity of the star along the line of sight varies as:

<p>$$v(t) = K \sin\!\left(\frac{2\pi t}{P} + \phi\right) + v_\text{sys}$$</p>

-   $K$ is the [%g semi_amplitude "semi-amplitude" %] (m/s),
    $P$ the orbital period (days), $\phi$ the phase,
    and $v_\text{sys}$ the systemic (centre-of-mass) velocity
-   For a circular orbit the semi-amplitude is related to the planet mass by:

<p>$$K = \left(\frac{2\pi G}{P}\right)^{1/3} \frac{M_p \sin i}{(M_\star + M_p)^{2/3}}$$</p>

-   Because only $M_p \sin i$ appears in the formula,
    the RV method gives a minimum planet mass; the true mass requires an independent inclination measurement.

## Generating Synthetic Observations

-   Observation times are drawn uniformly at random across the time baseline
    to simulate a realistic (unevenly spaced) survey schedule

[%inc generate_rv.py mark="constants"%]
[%inc generate_rv.py mark="make-rv"%]

## Fitting the Model

-   `scipy.optimize.curve_fit` minimises the sum of squared residuals between the data and `model_rv`,
    returning the best-fit parameters and their [%g covariance_matrix "covariance matrix" %]
-   The one-sigma uncertainties are the square roots of the diagonal entries of the covariance matrix
-   Initial guesses are derived from the data without assuming knowledge of the true parameters
    -   The amplitude guess uses the fact that the standard deviation of a sinusoid equals $K / \sqrt{2}$
    -   The period guess assumes roughly three cycles are visible in the baseline

[%inc radvel.py mark="model"%]
[%inc radvel.py mark="fit"%]

<div class="forma-matching" data-lang="en" markdown="1">

Match each initial-guess formula to the property of a sinusoid it exploits.

| Formula | Sinusoid |
| ------- | -------- |
| `amp_guess` = std(rv) $\times \sqrt{2}$ | The time-average of a zero-mean sinusoid is zero |
| `period_guess` = $(t_\text{max} - t_\text{min}) / 3$ | The std dev of a sinusoid with amplitude K is $K / \sqrt{2}$ |
| `v_sys_guess` = mean(rv) | About three complete cycles are visible in the time baseline |

</div>

[%figure
  slug="radvel-signal"
  img="radvel.svg"
  alt="Radial velocity data (blue points), best-fit sinusoid (red line), and true underlying signal (grey dashed line)."
  caption="Fifty synthetic observations (noise 10 m/s) with the best-fit sinusoid overlaid. Fitted: K = 51.3 ± 1.7 m/s, P = 10.12 ± 0.05 days. True values: K = 50 m/s, P = 10 days."
%]

## When the Fit Is Meaningless: Pure Noise

-   If there is no planet, the RV measurements contain only noise
-   Fitting a sinusoid to pure noise always returns some amplitude and period:
    the fit cannot report "no signal found"
-   The covariance matrix reveals whether the result is meaningful
    -   If the uncertainty on the fitted amplitude is comparable to or larger than the amplitude itself,
        the detection is not statistically significant

[%inc generate_rv.py mark="make-noise-rv"%]

<div class="forma-multiple-choice" data-lang="en" markdown="1">

The pure-noise fit returns K = 2.4 m/s with uncertainty $\sigma_K = 2.2$ m/s,
so $\sigma_K / K = 0.92$. What does this mean?

The planet has a very small semi-amplitude and is marginally detectable
:   Wrong: $\sigma_K / K = 0.92$ means the uncertainty is nearly as large as the value itself — the signal is consistent with zero, not merely small.

The fit converged to a local minimum far from the true parameters
:   Wrong: convergence quality is a separate issue; $\sigma_K / K$ measures statistical significance of the result, not convergence.

The fitted amplitude is indistinguishable from zero — no planet is detected
:   Correct: a fractional uncertainty above 0.5 means the fitted amplitude is less than $2\sigma$ from zero, so the detection is not statistically significant.

The noise level is 92% of the signal, so the planet is weakly detected
:   Wrong: $\sigma_K / K$ compares the uncertainty to the fitted value, not the noise to the true signal amplitude.

</div>

[%figure
  slug="radvel-noise"
  img="radvel_noise.svg"
  alt="Pure-noise radial velocity data with a meaningless best-fit sinusoid overlaid."
  caption="Fitting a sinusoid to pure noise (no planet signal). Fitted: K = 2.4 ± 2.2 m/s, fractional uncertainty 0.92. A fractional uncertainty above 0.5 indicates a non-detection."
%]

-   The fractional amplitude uncertainty $\sigma_K / K$ is a quick significance diagnostic:
    -   $\sigma_K / K < 0.1$: strong detection
    -   $\sigma_K / K > 0.5$: non-detection

## Testing

Model values
:   At $t = 0$ and $\phi = 0$ the model reduces to $v_\text{sys}$.
    At $t = P/4$ it reaches $K + v_\text{sys}$.
    Checking known exact values guards against sign errors in the sine argument.

Periodicity
:   Adding one full period to $t$ must return the same velocity.
    This is a pure algebraic property of the model and requires no tolerance.

Noise-free recovery
:   With no measurement noise, the fit must recover both amplitude and period to machine precision.
    Any failure points to a bug in the fitting setup
    (wrong parameter order, wrong initial guess structure, or flipped bounds)
    rather than a noise effect.

Noisy recovery of period
:   With noise-to-amplitude ratio 0.20 and 50 points,
    the [%g cramer_rao_bound "Cramér-Rao bound" %] on the period uncertainty is roughly 0.2 days.
    The 5% tolerance (0.5 days) gives a safety factor of 2.5X compared to the measured error of ~0.12 days.

Noisy recovery of amplitude
:   The measured fractional amplitude error with `seed=42` is ~2.5%.
    The 15% tolerance gives a safety factor of ~6X,
    which is wide enough to accommodate other random seeds.

Pure-noise uncertainty
:   A fractional amplitude uncertainty above 0.5 means
    the fitted amplitude is not distinguishable from zero at the 2-sigma level.
    This must always hold for pure noise data.
    A failure would indicate the fit was accidentally converging to a spurious periodic signal in the noise.

[%inc test_radvel.py%]

<div class="forma-flashcard" data-lang="en" markdown="1">

Radial velocity key terms

Semi-amplitude K
:   The maximum radial velocity of the star due to gravitational pull from the planet (m/s)
Systemic velocity $v_\text{sys}$
:   The centre-of-mass velocity of the star-planet system along the line of sight; a constant offset in the RV signal
Minimum planet mass $M_p \sin i$
:   The RV method cannot determine orbital inclination i, so it gives only a lower bound on the true planet mass
Fractional amplitude uncertainty $\sigma_K / K$
:   Values above 0.5 indicate a non-detection: the fitted amplitude is consistent with zero at the 2-sigma level
[%g lomb_scargle Lomb-Scargle periodogram %]
:   A method for finding periodic signals in unevenly sampled time series without requiring an initial period guess

</div>

<section class="exercises" markdown="1">

## Exercises

### Do the math

Using $v(t) = K \sin(2\pi t / P + \varphi) + v_\text{sys}$ with $K = 50$ m/s, $P = 10$ days,
$\varphi = 0$, $v_\text{sys} = 0$, what is $v(2.5)$? Give your answer in m/s.

### Lomb-Scargle periodogram

`scipy.optimize.curve_fit` requires a period initial guess; a poor guess may converge to a
wrong local minimum.  The Lomb-Scargle periodogram finds periodic signals
in unevenly sampled data without an initial guess.
Use `scipy.signal.lombscargle` to compute the power spectrum of the synthetic RV data,
identify the peak frequency, and use it as the initial period estimate for `curve_fit`.
Show that this two-step approach still recovers the correct period when the single-step
approach fails (try a very different initial guess to trigger failure).

### Eccentric orbit

A circular orbit produces a pure sinusoid, but most real exoplanets have eccentric orbits.
Replace the model with:

$$v(t) = K [\cos(\omega + \nu(t)) + e \cos\omega] + v_\text{sys}$$

where $e$ is the eccentricity, $\omega$ the argument of periapsis, and $\nu(t)$ the true
anomaly (obtained by solving Kepler's equation numerically).
Generate data with $e = 0.3$ and show that fitting a pure sinusoid to it yields a
systematically biased period estimate.

### Multiple planets

Extend `make_rv_data` to superpose signals from two planets with different periods.
Show that `fit_sinusoid` (single-planet model) fails to recover either period correctly,
then fit a two-planet model and demonstrate clean recovery.

### Detection threshold

Generate 200 data sets for each of ten noise levels from 2 to 50 m/s.
For each data set, run `fit_sinusoid` and classify the result as a detection when
$\sigma_K / K < 0.1$.  Plot the detection fraction as a function of noise level and
identify the noise floor at which detection drops below 50%.

</section>
