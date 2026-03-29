# Predator-Prey Dynamics

## The Problem

-   A common dynamic in predator-prey systems:
    -   When prey are abundant, predators thrive and multiply
    -   When predators are numerous, prey decline
    -   When prey are scarce, predators starve and their numbers fall
    -   Prey then recover
-   This cycle produces oscillating populations
-   The [%g lotka_volterra "Lotka-Volterra model" %]
    is the simplest mathematical description of this interaction.
    -   It is also used in chemistry (autocatalytic reactions)
        and economics (supply and demand cycles).

## The Equations

-   Let $x(t)$ be prey population and $y(t)$ be predator population.
-   The model is a pair of ordinary differential equations:

<p>$$\frac{dx}{dt} = ax - bxy \qquad \frac{dy}{dt} = cxy - dy$$</p>

-   Each term has a direct interpretation:
    -   $ax$: prey grow exponentially in the absence of predators (birth rate $a$)
    -   $bxy$: prey are removed at a rate proportional to encounters between species (predation rate $b$)
    -   $cxy$: predators gain from eating prey (efficiency $c$)
    -   $dy$: predators die at a constant per-capita rate $d$

## Parameters and Equilibrium

[%inc lotka.py mark="params"%]

-   Setting both derivatives to zero gives the equilibrium:
    $x^* = d/c$ and $y^* = a/b$.
-   At the equilibrium, populations are constant
-   But any perturbation produces oscillations
-   `PERIOD_APPROX` is derived by linearising around the equilibrium
    -   The exact period depends on the amplitude and must be measured from the solution

<div class="forma-multiple-choice" data-lang="en" markdown="1">
With `PREY_BIRTH` = 1.0, `PREDATION` = 0.1, `PRED_GROWTH` = 0.075, `PRED_DEATH` = 1.5,
what is the prey equilibrium $x^* = d/c$?

10.0
:   Wrong: 10.0 is the predator equilibrium $y^* = a/b$ = `PREY_BIRTH / PREDATION`.

13.3
:   Wrong: that is `PREY_BIRTH / PRED_GROWTH` = 1.0 / 0.075, which is not the equilibrium formula.

20.0
:   Correct: $x^* = d/c$ = `PRED_DEATH / PRED_GROWTH` = 1.5 / 0.075 = 20.0.

1.0
:   Wrong: `PREY_BIRTH` = 1.0 is a rate parameter, not the equilibrium prey population.

</div>

## Implementing the Right-Hand Side

-   `solve_ivp` requires a function that takes time $t$ and state vector $z = [x, y]$
    and returns $[dx/dt,\; dy/dt]$
-   The function must not modify $z$; instead, it should return a new list

[%inc lotka.py mark="rhs"%]

<div class="forma-ordering" data-lang="en" markdown="1">

Starting from abundant prey and few predators, put these events in the correct cyclic order.

1.  Prey population is high; predators begin to multiply
1.  Predator population peaks; prey decline rapidly
1.  Prey population is low; predators begin to starve and decline
1.  Predator population is low; prey begin to recover

</div>

<div class="forma-matching" data-lang="en" markdown="1">

Match each term in the Lotka-Volterra equations to its biological meaning.

| Term | Meaning |
| ---- | ------- |

| $ax$ | Prey grow exponentially in the absence of predators |
| $bxy$ | Prey are removed at a rate proportional to predator-prey encounters |
| $cxy$ | Predators gain population from consuming prey |
| $dy$ | Predators die at a constant per-capita rate |

</div>

## Solving the System

-   `solve_ivp` advances the state from $t = 0$ to `T_MAX` using an adaptive Runge-Kutta method
-   `t_eval` specifies the output times; it does not control the internal step size
-   `rtol` and `atol` control the solver's internal error tolerance
    -    Setting them to $10^{-8}$ and $10^{-10}$ gives solutions accurate to roughly eight significant figures.

[%inc lotka.py mark="solve"%]

## Visualizing the Results

-   Two views of the solution complement each other.

[%inc lotka.py mark="plots"%]

-   The time-series plot shows both populations over time
    -   The prey population (blue) rises first; the predator population (orange) rises shortly after
    -   Predator peaks lag prey peaks because predators need abundant food before they can multiply  
  -   Once predators are numerous, prey decline rapidly; predators then starve and their numbers fall  
  -   The prey then recover, and the cycle begins again

[%figure
  slug="lotka-timeseries"
  img="lotka_timeseries.svg"
  alt="Prey and predator populations oscillating over time, with predator peaks lagging prey peaks."
  caption="Prey (blue) and predator (orange) populations over 53 time units. Predator peaks follow prey peaks by roughly a quarter-period."
%]

-   The population trajectory plots $x$ versus $y$ at each point in time
    -   When the solution returns to approximately the same $(x, y)$ point after one cycle,
        the curve closes on itself.
    - A nearly closed loop means the system keeps repeating the same pattern indefinitely

[%figure
  slug="lotka-trajectory"
  img="lotka_trajectory.svg"
  alt="A closed loop in the prey-predator plane showing the repeating population cycle."
  caption="Population trajectory: prey ($x$-axis) versus predator ($y$-axis). The loop closes because the populations repeat the same cycle."
%]

## Testing

Populations remain positive
:   Analytically, neither population can reach zero in finite time: the positive quadrant is invariant.
    If a numerical solution produces a negative population, the solver has made a large error or the parameters are degenerate.

Volterra averaging principle
:   Volterra proved that the time mean of $x(t)$ over any complete number of cycles equals $x^* = d/c$,
    and similarly for $y(t)$.
    This is an exact analytical result, not an approximation.
    Over `T_MAX` covering ~10 complete cycles, the fractional-cycle bias is below 0.2%.
    A relative tolerance of 1% gives a 5x safety margin over that measured bias.

Period matches linearised estimate
:   Linearising the LV equations around equilibrium gives small oscillations with period $2\pi/\sqrt{ad}$.
    For finite-amplitude oscillations the true period is longer
    (the nonlinear correction is $O(\text{amplitude}^2)$).
    With our initial conditions the measured period is ~5.30
    versus the linearised estimate of ~5.13, a 3.3% deviation.
    A tolerance of 10% gives a safety factor of 3 over that measured deviation.

[%inc test_lotka.py%]

<section class="exercises" markdown="1">

## Exercises

### Starting at the equilibrium

Set `PREY_INIT = PREY_EQ` and `PRED_INIT = PRED_EQ` and run the simulation.
What does `plot_time_series` show?
What does `plot_trajectory` show?
Explain why in terms of the fixed-point analysis.

### Effect of initial conditions on period

Run the simulation with three different starting points:
$(x_0, y_0)$ = (21, 10.5), (25, 5), and (40, 2).
Plot the population trajectories on the same axes using different colors.
Measure the period of each orbit using `find_peaks`.
Is the period the same for all three orbits, or does it vary with amplitude?
Compare each measured period to `PERIOD_APPROX`.

### Harvesting prey

Add a constant harvesting term to the prey equation:
$dx/dt = ax - bxy - h$,
where $h > 0$ represents the rate at which prey are removed by fishing, hunting, or sampling.
Derive the new equilibrium $(x_h^*, y_h^*)$ algebraically.
Implement the modified `rhs` and verify your algebra by checking that the simulation
stays constant when started exactly at the new equilibrium.

### Numerical accuracy and solver tolerance

Reduce `rtol` and `atol` by a factor of 100 (to $10^{-6}$ and $10^{-8}$) and re-run the simulation.
Run the simulation for `T_MAX` time units and check whether the population trajectory still forms a
nearly closed loop.
At what tolerance does the loop visibly fail to close?
What does this tell you about the relationship between solver accuracy and the appearance of the trajectory?

</section>
