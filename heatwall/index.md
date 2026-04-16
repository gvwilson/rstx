# Heat Conduction Through a Composite Wall

## The Problem

-   A wall made of layers of different materials like brick or insulation
    conducts heat from the warm interior of a building to the cold exterior
-   Given the thickness and [%g thermal_conductivity "thermal conductivity" %] of each layer
    and the temperatures at the two surfaces,
    we want the steady-state temperature at every point in the wall
    and the [%g heat_flux "heat flux" %] (power per unit area) passing through it
-   This calculation is used to size insulation and check compliance with building codes

## The Physics

-   In steady state the temperature $T(x)$ no longer changes with time,
    so the heat equation reduces to:

<p>$$\frac{d}{dx}\!\left(k(x)\,\frac{dT}{dx}\right) = 0$$</p>

-   $k(x)$ is the thermal conductivity at position $x$
-   It is piecewise constant, i.e., has one value per layer
-   Within each uniform layer $d^2T/dx^2 = 0$,
    so $T$ is linear
    -   The slope (and therefore the flux) is constant within any single material
-   At every layer interface both the temperature and the heat flux must be continuous:
    $T$ does not jump and $k_L\,dT/dx$ on the left equals $k_R\,dT/dx$ on the right

## Thermal Resistance

-   The [%g thermal_resistance "thermal resistance" %] of a uniform layer
    is $R_i = L_i / k_i$ ($\text{m}^2\,\text{K}\,\text{W}^{-1}$)
-   For layers in series the resistances add: $R_\text{total} = \sum_i R_i$.
-   The uniform heat flux through the wall is:

<p>$$q = \frac{T_\text{left} - T_\text{right}}{R_\text{total}}$$</p>

-   The temperature at each interface follows by subtracting $q\,R_i$ from the previous value

[%inc heatwall.py mark="analytic"%]

<div class="forma-matching" data-lang="en" markdown="1">

Match each physical quantity to its definition.

| Quantity | Definition |
| -------- | ---------- |
| Thermal conductivity $k$ | Material property: heat flow per unit area per unit temperature gradient ($\text{W}\,\text{m}^{-1}\,\text{K}^{-1}$) |
| Thermal resistance $R$ | Geometry + material: temperature drop per unit flux for one layer ($\text{m}^2\,\text{K}\,\text{W}^{-1}$) |
| Heat flux $q$ | Power per unit wall area flowing through the wall in steady state ($\text{W}\,\text{m}^{-2}$) |
| Steady state | Condition where $\partial T/\partial t = 0$ everywhere in the wall |

</div>

## Discretizing the Wall

-   We place $n_\text{per layer}$ cells in each layer
    -   Nodes sit at cell boundaries,
        including the shared interface between adjacent layers),
        giving $n_\text{layers} \times n_\text{per layer} + 1$ nodes in total
-   Because every segment between neighbouring nodes lies entirely inside one material,
    each segment has a well-defined conductivity
    -   So no averaging formula is needed at layer interfaces

[%inc heatwall.py mark="constants"%]
[%inc heatwall.py mark="grid"%]

<div class="forma-ordering" data-lang="en" markdown="1">

Put these grid-construction steps in the correct order.

1.  Compute node positions within each layer using `np.linspace`
1.  Skip the first node of each layer after the first (it is shared with the previous layer)
1.  Record the conductivity of each inter-node segment
1.  Concatenate node arrays to form the full grid `x`

</div>

## Iterative Relaxation

-   Rather than assembling and solving a linear system,
    we find the steady-state temperatures by repeatedly applying a simple averaging rule
    until the profile stops changing
-   This is the same "keep updating until convergence" strategy
    as [%g eulers_method "Euler's method" %] for ordinary differential equations.
-   At each interior node $i$, the steady-state heat balance requires:

<p>$$k_{i-1}\,\frac{T_{i-1} - T_i}{\Delta x_\text{left}} + k_i\,\frac{T_{i+1} - T_i}{\Delta x_\text{right}} = 0$$</p>

-   Solving for $T_i$ gives an update rule that is a weighted average of the two neighbours:

<p>$$a = \frac{k_{i-1}}{\Delta x_\text{left}}, \quad b = \frac{k_i}{\Delta x_\text{right}}, \quad T_i \leftarrow \frac{a\,T_{i-1} + b\,T_{i+1}}{a + b}$$</p>

-   $k_{i-1}$ is the conductivity of the segment to the left of node $i$,
    $k_i$ is the conductivity of the segment to the right,
    and $\Delta x_\text{left}$ and $\Delta x_\text{right}$ are the distances to the neighbouring nodes
-   Both conductivity and spacing appear in the weights
    -   A high-conductivity or narrow segment "pulls" the node temperature toward the neighbour on that side
        more strongly
-   The two boundary temperatures $T_0 = T_\text{left}$ and $T_N = T_\text{right}$ are fixed throughout
-   After each full sweep over all interior nodes, we check the maximum change
    -   If $\max_i |T_i^\text{new} - T_i^\text{old}| < \varepsilon$ we stop
-   The threshold $\varepsilon$ (`TOLERANCE`) is set to $10^{-6}$ °C,
    which is far smaller than any physical measurement uncertainty
-   This method is called [%g jacobi_iteration "Jacobi iteration" %]

[%inc heatwall.py mark="jacobi"%]

<div class="forma-multiple-choice" data-lang="en" markdown="1">

After many Jacobi sweeps on a single uniform layer (one conductivity, equal node spacing throughout),
what temperature profile does the solution converge to?

A straight line from $T_\text{left}$ to $T_\text{right}$.
:   Correct: with equal conductivities and equal spacing, the weights $a = b = k/\Delta x$
    cancel and the update rule reduces to $T_i \leftarrow (T_{i-1} + T_{i+1})/2$, so every
    interior node ends up exactly halfway between its two neighbours — the discrete condition
    for a linear profile.

The temperature of the warmer boundary at every interior node.
:   Wrong: the boundary conditions fix only the two end nodes; interior nodes are updated
    by averaging neighbours, which pulls them toward an intermediate value.

An exponential decay from $T_\text{left}$ to $T_\text{right}$.
:   Wrong: exponential profiles arise in transient (time-dependent) heat conduction, not
    in the steady state of a uniform material.

A profile that depends on the initial guess and never changes.
:   Wrong: Jacobi iteration converges to the same steady-state solution regardless of the
    starting guess (as long as the boundary conditions are fixed).

</div>

## Convergence Behaviour

-   A good starting guess speeds convergence
-   We use a linear profile from $T_\text{left}$ to $T_\text{right}$,
    which is already the exact answer for a uniform wall
-   For the three-layer wall the iteration typically converges in a few hundred sweeps
-   The figure below shows snapshots at iterations 0, 10, 100, and the converged solution

[%figure
  slug="heatwall-convergence"
  img="heatwall_convergence.svg"
  alt="Temperature profiles at iterations 0, 10, 100, and converged for a brick-insulation-concrete wall."
  caption="Convergence of Jacobi iteration for a brick-insulation-concrete wall. The initial guess is a straight line. After 10 sweeps the profile is already bending toward the correct shape; after 100 sweeps it is nearly indistinguishable from the converged solution."
%]

## Solving and Plotting the Profile

[%inc heatwall.py mark="solve"%]

[%figure
  slug="heatwall-profile"
  img="heatwall.svg"
  alt="Temperature profile through a three-layer wall. The slope is gentle in the high-conductivity layers and steep in the insulation layer."
  caption="Steady-state temperature profile for a brick-insulation-concrete wall with inner surface at 20°C and outer surface at −10°C. Grey dashed lines mark the layer interfaces. The steep slope in the insulation ($0.04\,\text{W}\,\text{m}^{-1}\,\text{K}^{-1}$) reflects its high thermal resistance."
%]

## Heat Flux Through Each Layer

-   In steady state the heat flux $q = -k\,dT/dx$ is the same in every layer
-   We compute it directly from the numerical temperature gradient in each layer's segments

[%inc heatwall.py mark="flux"%]

## Testing

Grid node count
:   With $n$ layers and $n_\text{per layer}$ cells each,
    the grid must contain exactly $n \times n_\text{per layer} + 1$ nodes.
    The $+1$ accounts for the shared right-boundary node.

Grid extent
:   The first node must be at $x = 0$ and the last at $x = \sum_i L_i$.
    An off-by-one in the grid construction would violate this.

Boundary temperatures
:   The solver must return exactly `T_LEFT` and `T_RIGHT` at the two ends.
    these are fixed throughout the iteration, not approximations.

Single layer is linear
:   For a single uniform layer the exact solution is a straight line from $T_\text{left}$ to $T_\text{right}$.
    Jacobi iteration converges to this profile because
    the update rule $T_i \leftarrow (T_{i-1} + T_{i+1})/2$ has the linear profile as its only fixed point.

Convergence is reached
:   After the solver returns,
    applying one more Jacobi sweep must produce a change smaller than `TOLERANCE`.
    This directly tests the stopping criterion.

Flux constant across layers
:   Conservation of energy in steady state requires the same heat flux in every layer.
    Per-layer flux averages must match the analytic value within 1%.

Interface temperature matches analytic
:   The temperatures at the layer boundaries returned by the solver
    must match the analytic values from the thermal-resistance formula to better than $10^{-3}$ °C.
    The remaining error is dominated by the finite node spacing,
    not by iteration error,
    so any deviation larger than this indicates a conductivity-assignment or grid-construction bug.

Linearity in $\Delta T$
:   Doubling the temperature difference across the wall must double the heat flux.
    This tests that `analytic_solution` is free of any nonlinear terms.

Flux continuity at interfaces
:   At every layer interface,
    the heat flux computed from the last segment of the left layer
    must equal the flux computed from the first segment of the right layer
    to within 0.1% of the analytic flux.
    This verifies that Jacobi iteration correctly enforces
    $k_1\,\Delta T_1 / \Delta x_1 = k_2\,\Delta T_2 / \Delta x_2$
    at each boundary.

[%inc test_heatwall.py%]

<div class="forma-flashcard" data-lang="en" markdown="1">

Heat conduction key terms

Thermal conductivity $k$
:   Material property giving heat flux per unit temperature gradient; high $k$ means heat flows easily ($\text{W}\,\text{m}^{-1}\,\text{K}^{-1}$)

Thermal resistance $R = L/k$
:   Layer property: larger $R$ means a greater temperature drop for the same flux; used to design insulation ($\text{m}^2\,\text{K}\,\text{W}^{-1}$)

Heat flux $q$
:   Power flowing through a unit area of wall ($\text{W}\,\text{m}^{-2}$); uniform throughout the wall in steady state

Steady state
:   Condition where $\partial T/\partial t = 0$ everywhere; temperatures are constant in time

Jacobi iteration
:   An iterative relaxation method in which each interior node is repeatedly updated to the weighted average of its neighbours; iteration stops when successive sweeps change any node by less than a tolerance

</div>

<section class="exercises" markdown="1">

## Exercises

### Do the math

1.  Compute the total thermal resistance ($\text{m}^2\,\text{K}\,\text{W}^{-1}$) of a three-layer wall with:
    brick 0.10 m at $0.72\,\text{W}\,\text{m}^{-1}\,\text{K}^{-1}$,
	insulation 0.05 m at $0.04\,\text{W}\,\text{m}^{-1}\,\text{K}^{-1}$,
    concrete 0.15 m at $1.20\,\text{W}\,\text{m}^{-1}\,\text{K}^{-1}$.
    Use $R = \sum_i L_i / k_i$ and give your answer to three decimal places.

1.  Using the thermal resistance formula with the constants defined above
    ($L_\text{brick} = 0.10$ m, $k_\text{brick} = 0.72\,\text{W}\,\text{m}^{-1}\,\text{K}^{-1}$;
    $L_\text{ins} = 0.05$ m, $k_\text{ins} = 0.04\,\text{W}\,\text{m}^{-1}\,\text{K}^{-1}$;
    $L_\text{conc} = 0.15$ m, $k_\text{conc} = 1.20\,\text{W}\,\text{m}^{-1}\,\text{K}^{-1}$;
    $T_\text{left} = 20$°C, $T_\text{right} = -10$°C),
    what is the heat flux $q$ in $\text{W}\,\text{m}^{-2}$?
    Give your answer to two decimal places.

### Grid refinement study

Double `N_PER_LAYER` four times (from 5 to 80) and record the maximum absolute difference
between the numerical and analytic interface temperatures at each refinement level.
Plot the error versus `N_PER_LAYER` on a log-log scale.
Explain the observed convergence order.

### Radiation and convection boundary conditions

Real walls exchange heat with the air by convection, not at a fixed surface temperature.
The convective boundary condition on the inner surface is:

$$q = h\,(T_\text{air,in} - T_0)$$

where $h$ is the convective heat-transfer coefficient ($\text{W}\,\text{m}^{-2}\,\text{K}^{-1}$).
Modify `jacobi_solve` to accept inner and outer convective coefficients instead of
fixed temperatures by updating the boundary nodes using this relation at each sweep,
and verify that as $h \to \infty$ the solution approaches the fixed-temperature result.

### Transient heat conduction

Remove the steady-state assumption and discretize the full 1D heat equation
$\rho c_p \partial T / \partial t = \partial (k \partial T / \partial x) / \partial x$
using the explicit Euler method.
Use $\rho = 1800\,\text{kg}\,\text{m}^{-3}$ and $c_p = 900\,\text{J}\,\text{kg}^{-1}\,\text{K}^{-1}$ for all layers (representative brick).
Start from a uniform initial temperature of 20°C, apply $T_\text{right} = -10$°C at $t=0$,
and run until the solution is within 1°C of the steady state everywhere.
Verify the stability condition $\Delta t \le \Delta x^2 / (2 \alpha)$ where
$\alpha = k / (\rho c_p)$ is the thermal diffusivity.

### Optimal insulation placement

Fix the total insulation thickness at 5 cm and split it between two locations: one slab
immediately inside the brick and one immediately inside the concrete.
Let the inner slab have thickness $t$ ($0 \le t \le 0.05$ m) and the outer slab $(0.05 - t)$ m.
Compute the heat flux for each split and show that the total resistance — and therefore
the heat flux — is independent of how the insulation is distributed.
Explain this result using the series-resistance formula.

</section>
