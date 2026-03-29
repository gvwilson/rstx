# 1D Diffusion Simulation

## The Problem

-   Diffusion describes how a dissolved substance spreads through a stationary medium over time
-   The key physical idea is that the substance moves from regions of high concentration
    toward regions of low concentration
-   The rate of change at any point is proportional to
    how much its concentration differs from the average of its immediate neighbours

## Setting Up the Grid

-   Discretize the domain $[0, 1]$ into evenly spaced grid points separated by $\Delta x$
-   Represent concentration as a 1D NumPy array, one value per grid point
-   Choose the number of points and the pulse width so the initial Gaussian is well-resolved

[%inc diffusion.py mark="constants"%]

-   `DT` is derived from the stability condition explained below
-   The initial concentration is a Gaussian pulse centered in the domain:

[%inc diffusion.py mark="make-initial"%]

## Deriving the Update Rule

-   Label grid points $i = 0, 1, \ldots, N-1$ and time steps $n = 0, 1, 2, \ldots$
-   Write $c_i^n$ for the concentration at point $i$ after $n$ steps
-   The statement "the rate of change is proportional to the deviation from the neighbourhood average" becomes:

<p>$$\frac{c_i^{n+1} - c_i^n}{\Delta t} = \frac{D}{\Delta x^2}\left(c_{i+1}^n - 2c_i^n + c_{i-1}^n\right)$$</p>

-   The left side is the forward difference in time
    -   The change in one step divided by the step size
-   The right side uses the centred second difference in space
    -   $(c_{i+1}^n - 2c_i^n + c_{i-1}^n)/\Delta x^2$ measures
    how much $c_i^n$ deviates from the average of its two neighbours
-   Both approximations follow from truncating a Taylor series after the leading term
    -   The error in each approximation shrinks as $\Delta t$ and $\Delta x$ shrink
-   Rearranging gives the explicit update rule:

<p>$$c_i^{n+1} = c_i^n + r\left(c_{i+1}^n - 2c_i^n + c_{i-1}^n\right)$$</p>

-   $r = D\,\Delta t / \Delta x^2$ is called the stability ratio.

## Stability

-   The explicit scheme only produces physically correct results when $r \le 0.5$
-   If $r > 0.5$ the numerical solution grows without bound, producing meaningless results
-   This bound can be derived mathematically,
    but we treat it empirically:
    set `STABILITY_RATIO = 0.6` and run the simulation for 20 steps
    to see what happens to the concentration values
-   We choose `DT` so that $r$ = `STABILITY_RATIO` = 0.4,
    giving a 20% safety margin below the limit.

<div class="forma-multiple-choice" data-lang="en" markdown="1">

`DT` is computed as `STABILITY_RATIO * DX**2 / DIFFUSIVITY`, so `r = STABILITY_RATIO` at every run.
Which change would make `r` exceed 0.5 and make the simulation produce meaningless results?

Setting STABILITY_RATIO = 0.6
:   Correct: r equals STABILITY_RATIO by construction, so r = 0.6 &gt; 0.5 and the scheme will blow up.

Doubling `GRID_POINTS`
:   Wrong: a finer grid halves `DX`, but `DT` is recalculated from `DX**2`, so r = `STABILITY_RATIO` is unchanged.

Multiplying DIFFUSIVITY by 10
:   Wrong: DT is divided by DIFFUSIVITY, so increasing DIFFUSIVITY shrinks DT and keeps r = STABILITY_RATIO.

Running 10 000 steps instead of 500
:   Wrong: the number of steps does not affect r — it only determines how long the simulation runs.

</div>

## Boundary Conditions

-   At the two ends of the grid ($i = 0$ and $i = N-1$),
    the centred difference formula requires values at $i = -1$ and $i = N$,
    which do not exist
-   We use [%g zero_flux_boundary "zero-flux boundary conditions" %]:
    no material enters or leaves the domain
-   We implement this with [%g ghost_cell "ghost cells" %]
    -   Before each update,
        we prepend a copy of `c[0]` and append a copy of `c[-1]`,
        which makes the gradient at each boundary zero

[%inc diffusion.py mark="step"%]

-   The ghost-cell approach makes the sum of the correction term exactly zero,
    so total mass is conserved at each step

<div class="forma-ordering" data-lang="en" markdown="1">

Put these operations in the correct order for one explicit time step with no-flux boundary conditions.

1.  Prepend c[0] and append c[-1] to form a padded array
1.  Compute the centred second difference from the padded array
1.  Multiply the second difference by the stability ratio r
1.  Add the result to the current concentration array c

</div>

<div class="forma-multiple-choice" data-lang="en" markdown="1">

The ghost-cell implementation conserves total mass exactly. Which boundary condition produces this behaviour?

Dirichlet (absorbing): c = 0 at both ends
:   Wrong: absorbing boundaries remove mass from the domain; total mass decreases over time.

Neumann (no-flux): zero gradient at both ends
:   Correct: zero-flux boundaries prevent material from entering or leaving, so mass is conserved at every step.

Periodic: c[0] = c[-1] at every step
:   Wrong: periodic boundaries also conserve mass, but they are implemented differently — the concentration wraps around, not reflects.

No boundary condition is needed — mass is conserved automatically
:   Wrong: without an explicit boundary condition the update formula has no information about what happens at the grid edges.

</div>

## Running the Simulation

-   Advance the concentration array one step at a time, saving a snapshot every `SNAPSHOT_INTERVAL` steps
-   Store snapshots in a Polars dataframe with columns `x`, `concentration`, and `time`

[%inc diffusion.py mark="simulate"%]

## Visualizing the Results

-   Plot each snapshot as a separate line, color-coded by time, to show how the pulse spreads

[%inc diffusion.py mark="plot"%]

[%figure
  slug="diffusion-profiles"
  img="diffusion.svg"
  alt="Five concentration profiles at t=0 through t=0.83, showing a Gaussian pulse flattening and broadening over time."
  caption="Concentration profiles at five equally-spaced snapshots. The pulse spreads and flattens; the area under each curve (total mass) is constant."
%]

## Testing

-   Stability check
    -   If `DIFFUSIVITY`, `DT`, or `DX` are changed carelessly, the simulation may become unstable.
    -   This test catches that immediately:

```python
r = DIFFUSIVITY * DT / DX**2
assert r <= 0.5
```

-   Mass conservation
    -   Zero-flux boundaries mean no substance leaves the domain, so total mass must be constant.
    -   The ghost-cell implementation conserves mass exactly in floating-point arithmetic.
    -   We allow a relative tolerance of $10^{-10}$ to account for accumulated rounding over `N_STEPS` steps.

-   Symmetry
    -   The initial Gaussian is symmetric about $x = 0.5$, and both boundaries are identical.
    -   The profile must therefore remain symmetric at every step.
    -   Asymmetry would indicate a bug in the boundary-condition code.

-   Monotone peak decrease
    -   As the pulse spreads, its peak value must fall at every snapshot.
    -   This test checks physical plausibility without requiring knowledge of the exact solution.

-   Comparison to analytical solution
    -   On an infinite domain, a Gaussian pulse with standard deviation $\sigma_0$ evolves so that
        $\sigma^2(t) = \sigma_0^2 + 2Dt$
    -   After 20 steps the pulse tails are more than $4\sigma$ from each wall,
        so the boundary has negligible effect.
    -   We compare the numerical solution to this analytical formula.

## Choosing the tolerance

-   The explicit scheme has global [%g truncation_error "truncation error" %] $O(\Delta t + \Delta x^2)$.
    This notation means the error scales with $\Delta t$ and $\Delta x^2$ as those quantities shrink,
    but it says nothing about the coefficient in front of them.
-   With our parameters, $\Delta t + \Delta x^2 \approx 2\times 10^{-3}$.
-   Measuring the actual maximum error at $n = 20$ steps gives approximately $3\times 10^{-3}$.
    The coefficient is greater than 1, so the raw sum $\Delta t + \Delta x^2$ underestimates the true error.
-   The tolerance of $5\times 10^{-3}$ is about 1.7 times the measured error.
    This is a modest safety margin: large enough to absorb minor floating-point variation
    between platforms, small enough that a factor-of-2 regression would still be caught.
-   The factor 1.7 is empirical, not derived mathematically.
    Any tolerance between roughly $4\times 10^{-3}$ and $10^{-2}$ would be defensible here.
    What matters is that it is documented alongside the reasoning,
    so a future reader can judge whether a failing test signals a real problem or an overly tight bound.

[%inc test_diffusion.py%]

<div class="forma-numeric-entry" data-correct="0.169" data-tolerance="0.005" data-lang="en" markdown="1">

Using the analytical formula $\sigma^2(t) = \sigma_0^2 + 2Dt$, compute $\sigma^2$ after `N_STEPS` = 500 steps.
Use `PULSE_WIDTH` = 0.05 for $\sigma_0$, `DIFFUSIVITY` = 0.1, `GRID_POINTS` = 50, `LENGTH` = 1.0,
and note that `DT` = `STABILITY_RATIO * DX**2 / DIFFUSIVITY`.
Give your answer to three decimal places.

</div>

<section class="exercises" markdown="1">

## Exercises

### Step-function initial condition

Replace the Gaussian initial condition in `make_initial` with a step function:
$c(x) = 1$ for $x < 0.5$ and $c(x) = 0$ for $x \ge 0.5$.
Run the simulation and plot the results.
Does `test_mass_conservation` still pass?
Does `test_symmetry` pass or fail, and why?

### Absorbing boundaries

Change the boundary conditions from zero-flux to absorbing:
set `c[0] = 0` and `c[-1] = 0` after each update instead of using ghost cells.
Run the simulation and observe how the total mass changes over time.
Modify `test_mass_conservation` to check that mass decreases monotonically
rather than remaining constant.

### Demonstrating instability

Set `STABILITY_RATIO = 0.6` (above the stability limit of 0.5) and run the simulation for 20 steps.
Describe what happens to the concentration values.
Confirm that `test_stability_ratio` catches this before any time-stepping occurs.

### Grid refinement and convergence

Double `GRID_POINTS` to 100 (leaving `STABILITY_RATIO` unchanged so `DT` is recalculated automatically).
Measure the new maximum error in `test_matches_analytical` at $n = 20$ steps.
The truncation error scales as $O(\Delta t + \Delta x^2)$; with twice as many points,
$\Delta x$ halves and $\Delta t$ (derived from $\Delta x^2$) quarters.
Is the observed reduction in error consistent with this prediction?

</section>
