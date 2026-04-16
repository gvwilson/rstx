# Estimating Price Elasticity of Demand

## The Problem

-   The [%g price_elasticity "price elasticity of demand" %] measures
    how sensitive consumer demand is to price changes
    -   If the price rises by 1%, how many fewer units are sold?
-   Formally:

<p>$$\varepsilon = \frac{\partial \ln Q}{\partial \ln P} = \frac{P}{Q} \frac{dQ}{dP}$$</p>

-   $\varepsilon < -1$: demand is elastic — a 1% price increase causes more than a 1% drop in quantity
-   $-1 < \varepsilon < 0$: demand is inelastic — quantity is relatively insensitive to price
-   $\varepsilon = -1$: unit elastic — price and quantity move in equal and opposite proportions

<div class="forma-multiple-choice" data-lang="en" markdown="1">

A product has estimated price elasticity $\varepsilon = -2.0$.
If the price increases by 10%, what happens to quantity demanded?

Quantity decreases by 2%.
:   Wrong: elasticity multiplies the percentage change in price, not adds to it.

Quantity decreases by 20%.
:   Correct: $\Delta Q / Q \approx \varepsilon \times \Delta P / P = -2.0 \times 10\% = -20\%$.

Quantity increases by 20% because supply adjusts.
:   Wrong: price elasticity of demand describes consumer response, not supplier response.

Quantity is unchanged because consumers need the product regardless of price.
:   Wrong: that would describe a perfectly inelastic good ($\varepsilon = 0$), not one with $\varepsilon = -2$.

</div>

## The Log-Log Model

-   A power-law demand curve $Q = A P^\varepsilon$ becomes linear after taking logarithms:

<p>$$\ln Q = \ln A + \varepsilon \ln P$$</p>

-   This means $\varepsilon$ is the [%g ordinary_least_squares "ordinary least squares" %] slope
    in [%g log_log_regression "log-log space" %]:
    fitting $y = a + bx$ where $y = \ln Q$ and $x = \ln P$ directly estimates the elasticity as the slope $b$
-   The intercept $a = \ln A$ gives the log of the demand intercept, but is rarely reported by itself.

## Ordinary Least Squares in Log-Log Space

-   Transforming prices and quantities to logs reduces the nonlinear power-law model
    to a straight line, so standard OLS applies:

<p>$$\hat{\varepsilon} = \frac{\sum_i (\ln P_i - \overline{\ln P})(\ln Q_i - \overline{\ln Q})}{\sum_i (\ln P_i - \overline{\ln P})^2}$$</p>

-   The standard error of $\hat{\varepsilon}$ is:

<p>$$\text{SE}(\hat{\varepsilon}) = \sqrt{\frac{\text{RSS}/(n-2)}{\sum_i (\ln P_i - \overline{\ln P})^2}}$$</p>

-   $\text{RSS} = \sum_i (\ln Q_i - \hat{a} - \hat{\varepsilon} \ln P_i)^2$ is
    the residual sum of squares
-   A 95% confidence interval is $\hat{\varepsilon} \pm t_{0.975,\,n-2} \cdot \text{SE}(\hat{\varepsilon})$

[%inc elasticity.py mark="ols"%]

<div class="forma-ordering" data-lang="en" markdown="1">

Put these log-log OLS steps in the correct order.

1.  Compute $x_i = \ln P_i$ and $y_i = \ln Q_i$ for each observation
2.  Compute $\bar{x}$ and $\bar{y}$, then $SS_{xx}$ and $SS_{xy}$
3.  Estimate slope $\hat{\varepsilon} = SS_{xy} / SS_{xx}$ and intercept $\hat{a} = \bar{y} - \hat{\varepsilon}\bar{x}$
4.  Compute residuals $e_i = y_i - (\hat{a} + \hat{\varepsilon} x_i)$ and RSS $= \sum e_i^2$
5.  Report $\hat{\varepsilon}$ with 95% CI using $t_{0.975,\,n-2} \cdot \text{SE}(\hat{\varepsilon})$

</div>

## Generating Synthetic Data

-   Prices are drawn uniformly from $[1, 20]$ dollars
    -   Log-quantities are generated from the power-law model plus Gaussian noise in log space
-   Noise in log space is equivalent to multiplicative noise in original space
    -   Each observed quantity is $Q_i = A P_i^\varepsilon \cdot e^{\epsilon_i}$,
        where $\epsilon_i \sim N(0, \sigma^2)$

[%inc generate_elasticity.py mark="constants"%]

[%inc generate_elasticity.py mark="generate"%]

## Fitting and Reporting the Elasticity

[%inc elasticity.py mark="plot"%]

[%figure
  slug="elasticity-loglog"
  img="elasticity.svg"
  alt="Log-log scatter plot of price vs quantity with a straight fitted line showing a negative slope."
  caption="Eighty synthetic price-quantity observations on log-log axes. The fitted OLS line has slope $\hat{\varepsilon} = -1.474 \pm 0.022$ (95% CI: $[-1.518,\,-1.430]$), covering the true value $\varepsilon = -1.5$."
%]

-   The confidence interval $[-1.518, -1.430]$ is narrow because
    the noise ($\sigma = 0.15$ in log space) is small relative to the price variation
-   A wide confidence interval (or one that includes zero) indicates
    insufficient price variation in the data to estimate elasticity reliably

## Testing

Noise-free recovery
:   With no noise,
    OLS returns the exact true slope and intercept to within $10^{-6}$ (relative).
    Any deviation is a bug in the OLS formula rather than a sampling artefact.

Noisy slope within 10% of true value
:   With $\sigma = 0.15$ and $n = 80$,
    the theoretical SE of the slope is approximately 0.02.
    Ten percent of $|\varepsilon| = 1.5$ equals 0.15,
    giving a safety factor of roughly 7.5 over the expected sampling error,
    so the test should pass for any reasonable random seed.

Negative elasticity
:   Any estimated slope for downward-sloping demand must be negative.
    A positive slope would indicate data generation or formula errors
    because prices and quantities are negatively correlated by construction.

95% CI contains true value
:   With the fixed seed 7493418,
    the CI $[-1.518, -1.430]$ reliably contains the true value $-1.5$.
    This test would fail only with data where the noise draw happens to be extreme,
    which the fixed seed rules out.

[%inc test_elasticity.py%]

<div class="forma-flashcard" data-lang="en" markdown="1">

Price elasticity key terms

Price elasticity of demand $\varepsilon$
:   $\partial \ln Q / \partial \ln P$; the percentage change in quantity demanded for a 1% change in price; negative for normal goods

Elastic demand ($|\varepsilon| > 1$)
:   Quantity is highly responsive to price; a 1% price rise causes more than a 1% drop in sales

Inelastic demand ($|\varepsilon| < 1$)
:   Quantity is insensitive to price; consumers buy approximately the same amount regardless of small price changes

Log-log regression
:   A linear regression of $\ln Q$ on $\ln P$; the OLS slope directly estimates the elasticity exponent of the underlying power-law demand curve

Residual standard error
:   $\sqrt{\text{RSS}/(n-2)}$; estimates the noise in log-quantity; together with price variation it determines the precision of the elasticity estimate

</div>

<section class="exercises" markdown="1">

## Exercises

### Do the math

Using $\ln Q = a + \varepsilon \ln P$ with $a = 5$ and $\varepsilon = -1.5$,
compute $\ln Q$ when $P = e$ (Euler's number, so $\ln P = 1$).
What is the corresponding elasticity (the slope of the log-log line)?

### Residual diagnostics

Plot the OLS residuals $e_i = \ln Q_i - \hat{a} - \hat{\varepsilon} \ln P_i$ against $\ln P_i$.
If the log-log model is correct, the residuals should show no trend and no heteroscedasticity
(variance should be roughly constant across prices).
Modify `make_elasticity_data` to introduce heteroscedasticity (noise that increases with price)
and show how the residual plot reveals it.

### Weighted least squares

If measurement variance is known to be proportional to price ($\text{Var}(\epsilon_i) = \sigma^2 P_i$),
ordinary OLS is inefficient.  Implement weighted OLS by minimising
$\sum_i w_i (y_i - \hat{a} - \hat{\varepsilon} x_i)^2$ with weights $w_i = 1/P_i$.
Compare the standard errors of the WLS and OLS estimates on heteroscedastic data.

### Two-stage price endogeneity correction

In observational data, price is not set randomly — firms charge more when demand is high,
creating a spurious correlation.  Instrumental variables estimation uses an instrument $Z$
correlated with price but uncorrelated with the demand shock.
Simulate endogenous prices by adding a common demand shock to both price and log-quantity,
then show that OLS overestimates $|\varepsilon|$ while two-stage least squares (using a cost
instrument) recovers the true elasticity.

### Bootstrap confidence intervals

The OLS confidence interval assumes normally distributed residuals.
Implement a bootstrap estimate: resample the 80 observations with replacement, fit the
log-log model to each resample, and take the 2.5th and 97.5th percentiles of the 1000
bootstrapped slopes as the CI.
Compare the bootstrap CI with the analytic CI; do they agree closely for the synthetic data?

</section>
