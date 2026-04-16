# Pollutant Spread in a River Network

## The Problem

-   River networks branch and merge: pollutant introduced at one node is carried to all nodes reachable from it
-   We want to track the concentration at each node over time to predict when downstream communities are affected
-   This is a [%g flow_network "flow network" %] problem:
    a directed graph where edges carry material from node to node

## Representing the River Network

-   The network is a directed tree: water flows from headwaters to an outlet, with no cycles
-   Nodes represent measurement stations or junctions; edges represent river reaches
-   Edge weights record relative discharge (i.e., mean flow rate)

[%inc pollute.py mark="constants"%]

[%inc pollute.py mark="build-network"%]

-   `upstream_a` (node 0) is the spill site
-   `upstream_b` (node 1) is an uncontaminated headwater
-   Both drain into `junction` (node 2), which drains to `reach` (node 3), which drains to `outlet` (node 4)
-   Node 4 is the sink
    -   Pollutant that arrives there accumulates and is not transported further

<div class="forma-multiple-choice" data-lang="en" markdown="1">

Why is a river network represented as a directed graph rather than an undirected graph?

Water can flow in either direction between any two connected nodes.
:   Wrong: rivers flow in one direction, from higher to lower elevation; edges must be directed to encode this.

The direction of each edge encodes which way water (and pollutant) flows.
:   Correct: directed edges from upstream to downstream nodes capture the unidirectional nature of river flow.

Directed graphs are always faster to compute with than undirected graphs.
:   Wrong: the choice of directed vs. undirected is based on the physical system, not computational speed.

Edge weights cannot be stored on undirected graphs.
:   Wrong: undirected graphs support weighted edges just as directed graphs do.

</div>

## The Transport Model

-   At each time step, a fraction `TRANSPORT_RATE` of the concentration at each non-sink node moves downstream
-   The remaining fraction $(1 - \text{TRANSPORT\_RATE})$ stays at the node
    (representing mixing and retention in the water column)
-   For a node $v$ with upstream neighbours $u_1, u_2, \ldots$ each contributing fraction $f_k$,
    the update rule is:

<p>$$c_v^{n+1} = (1 - \alpha)\,c_v^n + \sum_k f_k\,c_{u_k}^n$$</p>

-   $\alpha = \text{TRANSPORT\_RATE}$
    and $f_k = \alpha / \text{(number of downstream neighbours of } u_k\text{)}$
-   When a node drains into a single successor, $f_k = \alpha$
-   When a node splits equally among two successors, each receives $\alpha / 2$

## Building the Upstream Table

-   Rather than building a matrix,
    we pre-compute the list of $(u, f)$ pairs for each node $v$,
    where $u$ is an upstream neighbour and $f$ is the fraction of $u$'s concentration that flows into $v$
-   This list is empty for headwater nodes (no upstream neighbours) and for isolated nodes

[%inc pollute.py mark="build-upstream"%]

<div class="forma-ordering" data-lang="en" markdown="1">

Put these steps in the correct order to fill in the upstream table for one non-sink node u.

1.  Find the list of downstream successors of u in the graph G
1.  Compute fraction = TRANSPORT_RATE / number of successors
1.  For each successor v, append (u, fraction) to upstream[v]
1.  Check that the fractions appended for u sum to TRANSPORT_RATE (conservation check)

</div>

<div class="forma-multiple-choice" data-lang="en" markdown="1">

In our 5-node tree every non-sink node has exactly one downstream successor.
What fraction of its concentration does each non-sink node send downstream per step?

0.0
:   Wrong: that would mean no pollutant is ever transported.

TRANSPORT_RATE / 2
:   Wrong: dividing by 2 would only apply if the node had two successors.

TRANSPORT_RATE
:   Correct: with one successor, fraction = TRANSPORT_RATE / 1 = TRANSPORT_RATE.

1.0
:   Wrong: 1.0 would mean all concentration moves downstream and none is retained.

</div>

## Running the Simulation

[%inc pollute.py mark="simulate"%]

-   For each time step and each node $v$,
    `retained` is the fraction staying put
    and `inflow` is the sum of fractions arriving from upstream neighbours
-   The loop saves a snapshot every `SNAPSHOT_INTERVAL` steps so that only a small table is stored

## Visualizing the Results

[%inc pollute.py mark="plot"%]

[%figure
  slug="pollute-concentrations"
  img="pollute.svg"
  alt="Line chart showing concentration at each node over 20 time steps. upstream_a decays from 1.0; junction and reach rise then fall; outlet rises monotonically."
  caption="Concentration at each node over 20 time steps. The pollutant pulse travels from the spill site (upstream_a) through the network toward the outlet."
%]

## Testing

-   Mass conservation
    -   At every step,
        each unit of concentration is either retained at its node or forwarded to a downstream neighbour.
    -   No mass is created or destroyed, so the sum over all nodes must equal 1.0 throughout.
    -   Floating-point addition of 5 small numbers over 20 steps introduces rounding of at most $10^{-12}$.

-   Non-negativity
    -   Every update is a weighted sum of non-negative concentrations with non-negative fractions.
    -   Concentration cannot go negative; a negative value would indicate a code error.

-   Monotone decay at the spill node
    -   `upstream_a` has no upstream neighbours, so each step it retains only $(1 - \alpha)$ of whatever it holds.
    -   Starting from $c_0 = 1$, its concentration decays as $(1 - \alpha)^n$, which is strictly decreasing.

-   Uncontaminated node stays zero
    -   `upstream_b` also has no upstream neighbours and starts at zero concentration.
    -   Each step it retains $(1 - \alpha) \times 0 = 0$, so it remains zero throughout.

-   Monotone accumulation at the outlet
    -   The outlet (sink) only receives mass and never releases it, so its concentration is non-decreasing.

-   Upstream fractions sum to transport rate
    -   For each non-sink node $u$ that has downstream successors,
        the fractions stored in the upstream table must sum to exactly `TRANSPORT_RATE`,
        confirming that all transported mass is accounted for

[%inc test_pollute.py%]

<section class="exercises" markdown="1">

## Exercises

### Do the math

Starting from $c = [1, 0, 0, 0, 0]$ and using `TRANSPORT_RATE` = 0.4, what is the concentration at
`junction` (node 2) after exactly 2 time steps?
Give your answer to two decimal places.

Hint: trace through the update rule step by step.
At step 1, junction receives $0.4 \times c_0[\text{upstream\_a}]$ from upstream_a.
At step 2, junction retains $0.6$ of its step-1 value and receives another inflow from upstream_a.

### Adding a tributary

Add a sixth node `tributary` (node 5) that joins at `reach` (node 3) with edge weight 2.0.
Update `build_network` and rerun the simulation.
Does `test_mass_conservation` still pass?
Does the pollutant reach the outlet faster or slower?

### Variable transport rate

Replace the uniform `TRANSPORT_RATE` with per-edge rates stored in a dictionary keyed by `(src, dst)`.
Assign higher rates to high-flow edges (e.g., rate proportional to edge weight / max edge weight).
Modify `build_upstream` to use per-edge rates and update `simulate` accordingly.
How does the arrival time at the outlet change compared to the uniform-rate model?

### Continuous spill

Change the initial condition so that `upstream_a` receives a constant input of 0.1 concentration units per step
(a continuous source rather than an instantaneous spill).
Modify `simulate` to add this source term to `new_c[SPILL_NODE]` after each update step.
Is mass still conserved?
At what step does the outlet concentration stabilise?

### Two-spill comparison

Run two separate simulations: one with the spill at `upstream_a` and one with a spill at `upstream_b`.
Add the two concentration lists at each step.
Compare the result to a single simulation that starts with concentration 1.0 at both headwater nodes simultaneously.
Are the results identical?
Explain why in terms of the structure of the update rule.

</section>
