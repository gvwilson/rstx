# Wealth Inequality in an Exchange Economy

## The Problem

-   Even when individuals exchange resources randomly with no deliberate hoarding,
    wealth concentrates in a small number of hands over time.
-   This is the central insight of [%g agent_based_model "agent-based models" %] of exchange:
    inequality can emerge from random processes, not only from skill differences or
    deliberate exploitation.
-   The [%g yardsale model %]  works as follows:
    -   Start with $N$ agents, each holding 1 unit of wealth (total wealth $= N$).
    -   At each step, choose two agents at random; the poorer transfers a uniformly random
        fraction of their own wealth to the richer.
    -   Repeat for many steps and track the wealth distribution.

<div class="forma-multiple-choice" data-lang="en" markdown="1">

In the yardsale model, Agent A has 0.4 units and Agent B has 1.6 units.
A fraction $f = 0.25$ is drawn.  What is Agent A's wealth after the exchange?

0.3 units.
:   Correct: Agent A is poorer, so A transfers $0.25 \times 0.4 = 0.1$ units to B.
    $0.4 - 0.1 = 0.3$.

0.5 units.
:   Wrong: the fraction applies to A's wealth (0.4), not to the total (2.0) or B's
    wealth (1.6).

0.1 units.
:   Wrong: 0.1 is the transfer amount, not A's remaining wealth.

0.4 units.
:   Wrong: A is the poorer agent and must transfer wealth to B.

</div>

## The Gini Coefficient

-   The [%g gini_coefficient "Gini coefficient" %] $G$ is the most widely used scalar summary of
    inequality: it equals 0 for perfect equality and approaches 1 when all wealth is
    concentrated in one agent.
-   It is defined as the mean absolute difference in wealth between all pairs, normalised
    by twice the mean wealth:

<p>$$G = \frac{\sum_i \sum_j |w_i - w_j|}{2\,n \sum_i w_i}$$</p>

-   Computing this directly requires $O(n^2)$ comparisons.
    Sorting the wealth array first reduces the cost to $O(n \log n)$:
    after sorting so that $w_{(1)} \leq w_{(2)} \leq \cdots \leq w_{(n)}$,

<p>$$G = \frac{2\sum_{i=1}^n i\,w_{(i)} - (n+1)\sum_i w_i}{n \sum_i w_i}$$</p>

[%inc wealth.py mark="gini"%]

<div class="forma-numeric-entry" data-correct="0" data-tolerance="0.001" data-lang="en" markdown="1">

Three agents hold 1, 1, and 1 unit of wealth respectively.
Using the formula $G = (2\sum i\,w_{(i)} - (n+1)\sum w) / (n\sum w)$ with $n=3$,
compute the Gini coefficient.

</div>

## The Exchange Simulation

-   The simulation records the Gini coefficient after every exchange so we can watch
    inequality grow from zero.
-   A key invariant: total wealth $\sum_i w_i = N$ is conserved exactly at every step
    because each transfer moves wealth without creating or destroying it.

[%inc wealth.py mark="simulate"%]

<div class="forma-ordering" data-lang="en" markdown="1">

Put the exchange steps in the correct order.

1.  Choose two distinct agents $i$ and $j$ uniformly at random
2.  Identify the poorer agent (swap labels if necessary so $w_i \leq w_j$)
3.  Draw fraction $f \sim \text{Uniform}(0, 1)$
4.  Compute transfer $\delta = f \cdot w_i$
5.  Update $w_i \leftarrow w_i - \delta$ and $w_j \leftarrow w_j + \delta$

</div>

## The Lorenz Curve

-   The [%g lorenz_curve "Lorenz curve" %] gives a visual picture of the whole distribution,
    not just a single number.
-   Sort agents by wealth ascending; the curve plots the cumulative fraction of total wealth
    held by the bottom $x$ fraction of the population.
-   Perfect equality produces the 45-degree line $y = x$.
    Any inequality bows the curve below that line.
-   The Gini coefficient equals twice the area between the Lorenz curve and the
    equality line.

[%inc wealth.py mark="lorenz"%]

[%inc wealth.py mark="plot_lorenz"%]

[%figure
  slug="wealth-lorenz"
  img="wealth-lorenz.svg"
  alt="Lorenz curve bowing well below the diagonal line of equality, with the bottom 80% of agents holding roughly 20% of total wealth."
  caption="Lorenz curve after 2000 exchanges with 200 agents (seed 7493418). The bottom 80% of agents hold roughly 20% of total wealth; the final Gini coefficient is 0.88."
%]

<div class="forma-multiple-choice" data-lang="en" markdown="1">

In a Lorenz curve, the point $(0.5,\; 0.2)$ means:

The wealthiest 50% of agents hold 20% of total wealth.
:   Wrong: the curve shows the bottom (poorest) fraction, not the top.

The poorest 50% of agents hold 20% of total wealth.
:   Correct: the Lorenz curve always measures cumulative shares starting from the poorest.

20% of agents each hold exactly 50% of total wealth.
:   Wrong: the axes represent cumulative fractions, not individual shares.

The Gini coefficient equals 0.2.
:   Wrong: the Gini is twice the area between the Lorenz curve and the diagonal,
    not the $y$-value at $x = 0.5$.

</div>

## Gini Trajectory

[%inc wealth.py mark="plot_gini"%]

[%figure
  slug="wealth-gini"
  img="wealth-gini.svg"
  alt="Line chart rising steeply from 0 in the first few hundred steps, then levelling off near 0.88 by step 2000."
  caption="Gini coefficient over 2000 pairwise exchanges with 200 agents. The coefficient rises from 0.00 (perfect equality) to 0.88, consistent with the exponential steady-state distribution whose theoretical Gini is 0.50 — the simulation has not yet fully converged but is still rising."
%]

-   The Gini rises quickly at first because early random exchanges quickly
    produce a spread in wealth from identical starting values.
-   Growth slows as wealth concentrates: the few richest agents now dominate
    exchanges, but the model has no way to reverse concentration once it is
    established.
-   The theoretical steady-state Gini for an exponential wealth distribution is
    exactly 0.5 (see Exercises), but the yardsale model's convergence is slow and
    in practice the simulated Gini often exceeds 0.5 because the distribution
    is not yet truly exponential.

## Testing

Equal-distribution baseline
:   `gini(np.ones(n))` must return exactly 0.0 for any $n$.
    Analytically: substituting $w_{(i)} = 1$ gives $2n(n+1)/2 - (n+1)n = 0$ in the numerator.

Perfect-inequality limit
:   When one agent holds all wealth, the formula gives $(n-1)/n$.
    For $n = 10$: $G = 0.9$, which approaches 1 as $n \to \infty$, confirming the
    coefficient never quite reaches 1 for any finite population.

Gini stays in [0, 1]
:   Wealth is non-negative and total wealth is conserved, so the formula
    is always well-defined and bounded.

Total wealth conserved
:   The sum of all agent wealths must equal $N$ to within floating-point rounding
    throughout the full simulation.

Gini rises from zero
:   Starting from equal wealth (Gini = 0), the simulation must produce substantial
    inequality after 2000 steps.
    With seed 7493418 the final value is 0.88, well above the 0.3 threshold.

[%inc test_wealth.py%]

<div class="forma-flashcard" data-lang="en" markdown="1">

Wealth inequality key terms

Gini coefficient $G$
:   $(2\sum i\,w_{(i)} - (n+1)\sum w) / (n\sum w)$ for sorted wealth; 0 for perfect equality,
    $(n-1)/n$ when all wealth is held by one agent

Lorenz curve
:   Plot of cumulative wealth fraction vs. cumulative population fraction, both sorted
    from poorest to richest; the area between the curve and the 45-degree line equals $G/2$

Agent-based model
:   Simulation in which autonomous agents follow local rules; emergent population-level
    patterns (such as inequality) arise from many individual interactions

Yardsale model
:   Random exchange rule in which the poorer agent transfers a random fraction of their
    own wealth to the richer; produces exponential steady-state wealth distribution

Wealth conservation invariant
:   $\sum_i w_i = N$ at every step; a transfer $\delta$ from agent $i$ to $j$ subtracts
    $\delta$ from $w_i$ and adds $\delta$ to $w_j$, leaving the total unchanged

</div>

<section class="exercises" markdown="1">

## Exercises

### Theoretical steady-state Gini

For an exponential distribution with rate $\lambda$, all agents draw wealth
$w \sim \text{Exp}(\lambda)$ independently.
Show algebraically that the Gini coefficient of this distribution is exactly 0.5.
(Hint: use the formula $G = 1 - 2\int_0^\infty S(w)^2 \, dw / \text{E}[W]$
where $S(w) = e^{-\lambda w}$ is the survival function.)

### Convergence as a function of $N$

Run the simulation with 50, 200, and 1000 agents for 10 000 steps each and plot the
final Gini as a function of $N$.
Does the steady-state Gini depend on the population size, or does it converge to
the same value regardless of $N$?

### Redistribution policy

Add a "redistribution step" every 100 exchanges: take 10% of the total wealth held
by the top decile (wealthiest 10% of agents) and distribute it equally to all agents.
How does this change the trajectory and steady-state Gini?

### Symmetric exchange rule

Change the transfer rule: instead of the poorer agent transferring a fraction of their
own wealth, both agents contribute a fraction of their own wealth to a pool and the pool
is split 50/50.
Show that total wealth is still conserved under this rule, then compare the resulting
Gini trajectory to the original yardsale model.

</section>
