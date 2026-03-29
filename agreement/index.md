# Inter-Rater Agreement

## The Problem

-   In qualitative research, clinical coding, or data annotation,
    two or more human raters independently assign categories to the same observations
-   The fraction of observations on which raters agree is straightforward to compute,
    but it is inflated by the agreement that would occur by chance
    even if raters were assigning labels randomly.
-   [%g cohens_kappa "Cohen's kappa" %] corrects for chance agreement
    and produces a standardized measure of
    how much the observed agreement exceeds the expectation under independence
-   Our approach:
    -   Generate synthetic rating pairs with a known underlying agreement probability
        using a controlled random model
    -   Construct the [%g contingency_table_raters "contingency table" %] of rater label pairs
        and compute kappa with its standard error
    - Compare kappa across several scenarios with different agreement levels

<div class="forma-multiple-choice" data-lang="en" markdown="1">

Two raters each independently assign one of three equally likely categories to
100 items. Even if they have no shared understanding of the categories, what
fraction of items do they agree on by chance?

0%, because random assignment never produces agreement.
:   Wrong: by chance, whenever both raters happen to pick the same category
    for the same item they agree; with three equally likely categories that
    happens 1/3 of the time.

About 33%, because with three equally likely categories the probability of
two independent draws matching is 1/3.
:   Correct: P(agree by chance) = sum over k of P(A = k) * P(B = k) = 3 * (1/3)^2 = 1/3.

About 50%, because raters tend to pick the most common category.
:   Wrong: with equally likely categories no single category dominates; the
    expected agreement is 1/K where K is the number of categories.

100%, because raters always agree eventually with enough practice.
:   Wrong: practice is not relevant here; the calculation is a probability
    under the assumption of independent uniform random choices.

</div>

## The Contingency Table

-   For $K$ categories,
    the contingency table is a $K \times K$ integer matrix
    where entry $C_{ij}$ is the number of items for which rater A assigned category $i$
    and rater B assigned category $j$
-   The diagonal entries $C_{ii}$ represent agreements,
    while off-diagonal entries represent disagreements
-   The table summarises all information needed to compute kappa

[%inc agreement.py mark="table"%]

## Cohen's Kappa

-   Let $N$ be the total number of items and:
    -   $P_o = \sum_i C_{ii} / N$: observed agreement proportion
    -   $p_i = \sum_j C_{ij} / N$: rater A's marginal probability for category $i$
    -   $q_j = \sum_i C_{ij} / N$: rater B's marginal probability for category $j$
    -   $P_e = \sum_i p_i q_i$: expected agreement under independence
-   Cohen's kappa is:

<p>$$\kappa = \frac{P_o - P_e}{1 - P_e}$$</p>

-   $\kappa = 0$ when observed agreement equals the chance expectation
-   $\kappa = 1$ when raters agree perfectly ($P_o = 1$)
-   $\kappa < 0$ is possible when observed agreement falls below chance,
    though this rarely occurs in practice

<div class="forma-numeric-entry" data-correct="0.5" data-tolerance="0.005" data-lang="en" markdown="1">

A 3x3 contingency table has 20 items on each diagonal cell and 5 items on each
off-diagonal cell (N = 90). Given P_o = 2/3 and P_e = 1/3, what is kappa?

</div>

[%inc agreement.py mark="kappa"%]

## The Expected Agreement P_e

-   $P_e = \sum_i p_i q_i$ is the probability that two independently drawn labels
    (one from rater A's marginal, one from rater B's)
    happen to match
-   Under the generation model used here,
    with probability `agree_prob` both raters draw the same uniform label,
    and otherwise they draw independently
-   With $K$ categories this gives:

<p>$$P_o = \text{agree\_prob} + \frac{1 - \text{agree\_prob}}{K}$$</p>

-   When marginals are uniform ($p_i = q_i = 1/K$):
    $P_e = K \cdot (1/K)^2 = 1/K$
-   Substituting into the kappa formula and simplifying gives
    $\kappa = \text{agree\_prob}$.
-   So the synthetic generator produces data where
    the expected kappa directly equals the underlying agreement probability,
    making it easy to verify the implementation

## Generating Synthetic Rating Data

[%inc generate_agreement.py mark="generate"%]

## Standard Error of Kappa

-   The asymptotic standard error is:

<p>$$\text{SE}(\kappa) = \sqrt{\frac{P_o(1 - P_o)}{N(1 - P_e)^2}}$$</p>

-   This approximates $\text{SE}(P_o) = \sqrt{P_o(1-P_o)/N}$
    (each item is an independent Bernoulli trial for agreement)
    and propagates it through the kappa formula by dividing by $(1 - P_e)$
-   A 95% confidence interval for $\kappa$ is $\kappa \pm 1.96 \cdot \text{SE}(\kappa)$

## Comparing Scenarios

[%inc agreement.py mark="plot"%]

[%figure
  slug="agreement-kappa"
  img="agreement-kappa.svg"
  alt="A bar chart with five bars. The x-axis shows underlying agreement probabilities of 0.2, 0.4, 0.6, 0.8, and 0.95. The y-axis shows Cohen's kappa from 0 to 1. The bars increase from left to right, reaching close to 1 for the highest agreement probability. Bar color darkens with increasing kappa."
  caption="Cohen's kappa for five synthetic rating scenarios (N = 100 items, K = 3 categories). Kappa closely tracks the underlying agreement probability, confirming the theoretical result that expected kappa equals agree_prob under the uniform marginal model."
%]

## Testing

Table shape
:   `contingency_table` with `n_cats=3` must return a $(3, 3)$ array.

Table sum equals item count
:   All entries in the contingency table must sum to `N_ITEMS`.

Perfect agreement gives kappa = 1
:   When both raters assign identical labels,
    every item is on the diagonal and kappa must equal 1.0 regardless of the marginal distribution.

Chance agreement gives kappa near zero
:   Independent uniform labels have $P_o \approx P_e = 1/K$,
    so kappa should be near zero.
    The tolerance 0.15 accounts for sampling variability.

Standard error positive and finite
:   The standard error must be a positive finite number for any valid table.

Kappa close to agree_prob
:   With `N_ITEMS = 100` and uniform marginals,
    the observed kappa must be within 0.15 of `AGREE_PROB`.
    This is conservative given the sampling variability of approximately $\text{SE} \approx 0.05$
    at this sample size

[%inc test_agreement.py%]

<div class="forma-flashcard" data-lang="en" markdown="1">

Inter-rater agreement key terms

Inter-rater agreement
:   The degree to which two or more raters independently assign the same
    category to the same observations; raw percent agreement is easy to compute
    but is inflated by chance; Cohen's kappa corrects for this inflation

Contingency table (raters)
:   A K x K matrix whose entry C[i, j] counts the number of observations for
    which rater A assigned category i and rater B assigned category j; diagonal
    entries are agreements, off-diagonal entries are disagreements

Cohen's kappa
:   A chance-corrected measure of inter-rater agreement:
    kappa = (P_o - P_e) / (1 - P_e), where P_o is the observed agreement
    proportion and P_e is the agreement expected under independence; kappa = 0
    at chance, kappa = 1 at perfect agreement, kappa < 0 below chance

Expected agreement P_e
:   The probability that two raters would agree purely by chance, computed as
    the sum over categories of the product of rater A's marginal probability
    and rater B's marginal probability for that category

</div>

<section class="exercises" markdown="1">

## Exercises

### Weighted kappa

In ordinal coding (e.g., severity on a 1-5 scale) disagreements near the
diagonal should be penalised less than disagreements far from it.
Implement weighted kappa using linear weights:
$w_{ij} = 1 - |i - j| / (K - 1)$.
Apply it to a 5-category synthetic dataset and compare it to the unweighted kappa.
When does the difference between weighted and unweighted kappa matter most?

### Confidence intervals across scenarios

For each of the five `SCENARIOS` in `agreement.py`, compute the 95% confidence
interval for kappa using the standard error formula.
Add error bars to the bar chart.
Do the confidence intervals for adjacent scenarios overlap?

### Three or more raters

Extend the generator to produce ratings from three raters.
Compute all three pairwise kappa values and the mean pairwise kappa.
How do pairwise kappas relate to each other when one rater is systematically
more conservative than the others?

### Category prevalence

The expected-agreement correction assumes the marginal distributions are
determined by chance.
Generate a dataset where rater A's marginals are highly skewed (e.g., 70%
in category 0) and compute kappa.
How does a skewed marginal affect kappa relative to percent agreement?

</section>
