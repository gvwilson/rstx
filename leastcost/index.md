# Least-Cost Path Analysis for Trade Routes

## The Problem

-   Modern roads follow valleys and passes because crossing ridges is slow and exhausting,
    and ancient routes did the same
-   [%g landscape_archaeology "Landscape archaeology" %] asks
    where historical travelers and traders were most likely to move through a terrain
-   [%g least_cost_path "Least-cost path analysis" %] formalises this idea
    -   Represent the terrain as a 2-D grid in which each cell has an elevation value
    -   Define a [%g cost_surface "cost surface" %] that translates elevation into travel difficulty
    -   Apply [%g dijkstras_algorithm "Dijkstra's algorithm" %] to find the path
        from a source cell to a destination cell that minimises the total accumulated cost
    - Visualize the terrain and overlay the optimal route

<div class="forma-multiple-choice" data-lang="en" markdown="1">

Why does least-cost path analysis assign lower cost to valley cells than
to ridge cells?

Because valleys are always closer to water sources.
:   Wrong: proximity to water is a separate consideration that is not part
    of the elevation-based cost model used here.

Because the model uses elevation as a proxy for travel effort: crossing
high terrain requires more energy than traversing low terrain.
:   Correct: the cost of an edge is proportional to the average elevation
    of its two endpoints, so paths that stay in valleys accumulate less cost
    than paths that cross ridges.

Because valley cells are always larger on the grid.
:   Wrong: all cells have the same size on a uniform grid; the cost difference
    comes from their elevation values, not their physical extent.

Because Dijkstra's algorithm always prefers shorter paths.
:   Wrong: Dijkstra's minimises accumulated cost, not geometric length; a
    longer valley path can beat a shorter ridge path if the valley cost is low enough.

</div>

## The Cost Surface

-   The elevation grid is a 2-D array with values normalised to $[0, 1]$
    -   0 is the lowest point in the landscape, 1 is the highest
-   Moving from cell $A$ to an adjacent cell $B$ incurs an edge cost:

<p>$$\text{edge\_cost}(A, B) = \frac{\text{elev}(A) + \text{elev}(B)}{2} \times d(A, B)$$</p>

-   Averaging the endpoint elevations penalises entering a ridge from a valley proportionally
    (and vice versa).
-   $d(A, B) = 1$ for orthogonal moves and $\sqrt{2}$ for diagonal moves,
    so longer edges cost proportionally more.

<div class="forma-numeric-entry" data-correct="0.75" data-tolerance="0.001" data-lang="en" markdown="1">

Cell A has elevation 0.5 and orthogonally adjacent cell B has elevation 1.0.
What is the edge cost from A to B?

</div>

## Generating Synthetic Terrain

-   The terrain is a superposition of sinusoidal waves at four octaves
-   Each successive octave has half the amplitude and twice the spatial frequency of the previous,
    producing a fractal-like surface of ridges and valleys
-   The result is normalised to $[0, 1]$ so that cost surface values are comparable
    regardless of the raw wave amplitudes

[%inc generate_leastcost.py mark="terrain"%]

## Dijkstra's Algorithm on a Grid

-   [%g dijkstras_algorithm "Dijkstra's algorithm" %] maintains a priority queue of cells
    ordered by their current best-known distance from the source
-   At each step it pops the cheapest cell,
    examines its eight neighbors,
    and updates any neighbor whose new cost would be lower than its current best
-   When the destination is popped from the queue,
    its accumulated cost is optimal
    and the shortest-path tree stored in `prev` can be traced back to recover the route

[%inc leastcost.py mark="dijkstra"%]

<div class="forma-ordering" data-lang="en" markdown="1">

Order the steps of Dijkstra's algorithm as applied to this terrain grid.

Initialize all distances to infinity; set distance of start cell to 0 and push it onto the priority queue.
Pop the cell with the lowest accumulated cost from the priority queue.
For each unvisited neighbor, compute the edge cost and update distance if the new route is cheaper.
Stop when the destination cell is popped; trace back through the predecessor map to recover the path.

</div>

## Visualizing the Path

[%inc leastcost.py mark="plot"%]

[%figure
  slug="leastcost-path"
  img="leastcost-path.svg"
  alt="A terrain colour map ranging from dark blue (low elevation) to white (high elevation). A red line traces a route from the top-left corner to the bottom-right corner, winding through the darker low-elevation regions and avoiding the bright high-elevation ridges."
  caption="Least-cost trade route through a synthetic 40x60 terrain grid. The path avoids the high-elevation ridges (bright) and follows valley corridors (dark) to minimise accumulated travel cost."
%]

## Testing

Terrain shape
:   `make_terrain(rows, cols)` must return an array of exactly that shape.

Terrain bounds
:   After normalisation the minimum must be 0.0 and the maximum must be 1.0.

Terrain reproducibility
:   Calling `make_terrain` twice with the same seed must return identical arrays.

Path endpoints
:   The first cell of the returned path must equal `START`; the last must equal `END`.

Path connectivity
:   Every consecutive pair of cells in the path must be 8-connected neighbors,
    i.e., their offsets must appear in `STEP_LEN`.

Flat terrain takes the diagonal
:   On a uniform-elevation 5x5 grid, the cheapest route from $(0,0)$ to $(4,4)$
    is the main diagonal (cost $4\sqrt{2} \approx 5.66$)
    rather than the 8-step orthogonal route (cost 8.0),
    so the path must visit exactly 5 cells.

Valley preferred over ridge
:   A 3x3 grid with a zero-elevation valley row in the middle
    must route the path through that row rather than across the high-elevation rows.

Low-cost path beats ridge traverse
:   On a 3x5 grid with an all-zero middle row,
    the Dijkstra path must cost strictly less than an all-ridge orthogonal traverse.

[%inc test_leastcost.py%]

<div class="forma-flashcard" data-lang="en" markdown="1">

Least-cost path key terms

Landscape archaeology
:   A subfield of archaeology that studies how human activities are distributed
    across and shaped by the physical environment, including terrain, water, and
    vegetation; least-cost path analysis is one of its standard spatial methods

Cost surface
:   A 2-D grid in which each cell stores the difficulty of moving through that
    location; derived from elevation, slope, land cover, or other terrain attributes;
    used as input to path-finding algorithms

Least-cost path
:   The route through a cost surface that minimises the total accumulated cost
    from a source location to a destination; need not be the geometrically shortest
    path if shorter routes cross high-cost terrain

Dijkstra's algorithm
:   A graph search algorithm that finds shortest (or least-cost) paths from a
    source node to all other nodes by iteratively relaxing edges in order of
    increasing cost; runs in $O((V + E)\log V)$ time with a binary heap

Edge cost (terrain)
:   The cost assigned to moving from one grid cell to an adjacent cell; computed
    here as the average of the two cells' elevations times the step distance
    ($1$ for orthogonal, $\sqrt{2}$ for diagonal moves)

</div>

<section class="exercises" markdown="1">

## Exercises

### Slope-based cost

Replace the elevation-averaging cost with a slope-based cost: the absolute
elevation difference between the two cells divided by the step distance.
Compare the resulting path to the elevation-average path.
Does the slope cost prefer steeper or gentler routes?

### Anisotropic cost

Historical travelers going downhill moved faster than travelers going uphill.
Modify the edge cost so that moving to a lower cell costs less than moving to
a higher cell (for example, multiply by a factor of 0.5 for downhill moves).
How does the preferred route change?

### Multiple waypoints

Extend `least_cost_path` to accept a list of waypoints and return the path
that passes through every waypoint in order at minimum total cost.
Apply this to the synthetic terrain with two intermediate waypoints and
compare the total cost to the direct source-to-destination path.

### Sensitivity to epsilon

Generate terrain at three different random seeds and run least-cost path
analysis on each.
For each terrain, compute the total path cost and the fraction of cells on
the path that lie below the mean elevation.
Does a lower mean elevation on the path reliably predict lower total cost?

</section>
