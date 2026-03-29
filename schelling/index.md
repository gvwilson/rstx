# Schelling Segregation Model

## The Problem

-   In 1971, economist Thomas Schelling asked whether mild individual preferences for
    similar neighbours could produce large-scale residential segregation
-   The answer is yes:
    even when each agent requires only 30% of occupied neighbours to share its type,
    the population self-organises into sharply segregated clusters
-   The [%g schelling_model "Schelling model" %] is an [%g agent_based_model "agent-based model" %]:
    -   Place two types of agents on a grid, leaving some cells empty
    -   At each step, identify dissatisfied agents and move each to a random empty cell
    -   Repeat until no agent moves, or for a fixed number of steps
-   The model is a landmark result in computational social science because it shows that
    macro-level patterns can emerge from micro-level rules without central coordination.

<div class="forma-multiple-choice" data-lang="en" markdown="1">

Which of the following best explains why the Schelling model produces segregation
even at a low threshold such as 30%?

Agents actively seek to be surrounded entirely by their own type.
:   Wrong: agents only require that a minimum fraction of neighbours are the same type;
    they do not seek any particular neighbourhood composition beyond that.

Dissatisfied agents move to random empty cells, but satisfied agents stay put,
so same-type clusters accumulate around contented individuals.
:   Correct: movement is triggered by dissatisfaction alone.  Once a cluster forms,
    its interior agents are satisfied and stop moving, reinforcing the boundary.

The grid is too small for the two types to mix uniformly.
:   Wrong: the result holds for grids of many sizes and is not a finite-size effect.

Random movement eventually produces uniform mixing.
:   Wrong: random movement does not preserve spatial structure; systematic movement
    away from dissatisfying neighbourhoods does.

</div>

## The Grid and Neighbourhood

-   The grid is an $N \times N$ array.  Each cell holds one of three values:
    0 (empty), 1 (red agent), or 2 (blue agent)
-   The [%g moore_neighborhood "Moore neighbourhood" %] of a cell is the set of up to
    eight surrounding cells (horizontal, vertical, and diagonal)
-   The same-neighbour fraction for an agent at position $(r, c)$ is:

<p>$$f(r,c) = \frac{\text{occupied neighbours of the same type}}{\text{total occupied neighbours}}$$</p>

-   An agent is satisfied when $f(r,c) \geq \theta$, where $\theta$ is the threshold
-   An agent with no occupied neighbours is treated as satisfied ($f = 1$)
    so that isolated agents do not drift endlessly across empty space

<div class="forma-numeric-entry" data-correct="0.375" data-tolerance="0.001" data-lang="en" markdown="1">

An agent has 8 fully occupied Moore neighbours, of which 3 are the same type.
What is its same-neighbour fraction?

</div>

## Initializing the Grid

-   Equal numbers of red and blue agents are placed at random in a fraction
    $(1 - p_e)$ of cells, where $p_e$ is the empty fraction
-   The empty cells provide the vacancies that dissatisfied agents move into

[%inc schelling.py mark="grid"%]

## Computing the Same-Neighbour Fraction

-   Iterating over the 8 relative offsets $(\Delta r, \Delta c) \in \{-1,0,1\}^2 \setminus \\{(0,0)\\}$
    visits each neighbour exactly once
-   Grid boundaries are handled by checking that the neighbour index lies within $[0, N)$

[%inc schelling.py mark="neighbors"%]

## One Simulation Step

-   All dissatisfied agents are identified first, then all empty cells
-   Both lists are shuffled independently and paired in order
-   Each dissatisfied agent moves to the corresponding empty cell if one exists
-   Shuffling before pairing ensures no agent is systematically favoured

[%inc schelling.py mark="step"%]

## Measuring Segregation

-   The satisfaction rate (i.e., the fraction of agents that meet the threshold)
    rises as the grid segregates
    and reaches 1.0 when every agent is happy with its neighbourhood

[%inc schelling.py mark="segregation"%]

<div class="forma-multiple-choice" data-lang="en" markdown="1">

After 20 steps with threshold 0.3, the satisfaction rate is 0.92.
What does this mean?

92% of agents have at least 30% same-type neighbours.
:   Correct: satisfaction rate counts the fraction of agents whose same-neighbour
    fraction meets or exceeds the threshold.

92% of cells are occupied.
:   Wrong: the fraction of occupied cells is fixed by the initial empty fraction
    and does not change during the simulation.

The two agent types are 92% spatially separated.
:   Wrong: satisfaction rate measures individual agent happiness, not a global
    spatial segregation index.

92% of agents are surrounded entirely by same-type neighbours.
:   Wrong: the threshold is 0.3, not 1.0; an agent with even one same-type
    neighbour out of three total may already be satisfied.

</div>

## Running the Simulation

[%inc schelling.py mark="run"%]

[%inc schelling.py mark="plot"%]

[%figure
  slug="schelling-grid"
  img="schelling-grid.svg"
  alt="Four grid snapshots at steps 0, 5, 10, and 20. Step 0 shows a random mix of red and blue. By step 20 large patches of each colour have formed."
  caption="Grid state at steps 0, 5, 10, and 20 (GRID_SIZE=50, EMPTY_FRACTION=0.2, THRESHOLD=0.3). The initially random arrangement self-organises into large segregated clusters. The satisfaction rate rises from 0.832 at step 0 to 1.000 at step 20."
%]

## Testing

-   Grid shape and contents
    -   `make_grid` must produce a $(50 \times 50)$ array whose cells are all in $\{0, 1, 2\}$

-   Balanced agent counts
    -   Red and blue agents are built as equal halves of the occupied pool,
        so their counts differ by at most 1
        (an off-by-one when the total number of agents is odd)

-   Neighbour fractions
    -   An isolated agent (no occupied neighbours) must return 1.0,
        matching the convention that isolated agents are considered satisfied
    -   An agent surrounded entirely by the same type returns 1.0
    -   One surrounded entirely by the opposite type returns 0.0

-   Stable segregated grid
    -   A $4 \times 4$ grid with red in the left two columns and blue in the right two columns
        is fully satisfied
    -   Border agents have $5/8 = 0.625$ same-type neighbours which exceeds the threshold of 0.3
    -   One step must leave the grid unchanged

-   Satisfaction increases
    -   Starting from the random initial grid,
        the satisfaction rate after 20 steps must exceed the initial rate
        because agents self-organise into clusters

[%inc test_schelling.py%]

<div class="forma-flashcard" data-lang="en" markdown="1">

Schelling model key terms

Schelling model
:   An agent-based simulation in which agents on a grid move to random empty cells
    when fewer than a threshold fraction of their occupied neighbours share their type;
    even a low threshold produces large-scale segregation

Moore neighbourhood
:   The set of up to 8 cells immediately surrounding a grid cell (horizontal, vertical,
    and diagonal); cells on the boundary have fewer than 8 neighbours

Same-neighbour fraction
:   $f = \text{same-type occupied neighbours} / \text{total occupied neighbours}$;
    defined as 1.0 for isolated agents; an agent is satisfied when $f \geq \theta$

Satisfaction rate
:   The fraction of agents whose same-neighbour fraction meets the threshold;
    increases as the grid segregates toward a stable clustered state

Emergent segregation
:   Large-scale spatial separation of agent types arising from individual satisfaction
    rules without any global coordination or explicit goal of segregation

</div>

<section class="exercises" markdown="1">

## Exercises

### Effect of threshold

Run the simulation with thresholds of 0.1, 0.3, 0.5, and 0.7.
Plot the satisfaction rate over time for each threshold on the same axes.
At what threshold does the model fail to reach a satisfaction rate above 0.95
within 50 steps?

### Asymmetric populations

Modify `make_grid` so that red agents make up 70% of the occupied cells and
blue agents make up 30%.
Run the simulation with threshold 0.3 and compare the final satisfaction rate
with the balanced case.
Which type ends up more satisfied, and why?

### Segregation index

The satisfaction rate measures individual happiness, not the spatial extent of
clustering.
Implement a `mean_cluster_size` function that computes the mean size of same-type
connected components using `scipy.ndimage.label`.
Plot mean cluster size over time alongside the satisfaction rate.

### Convergence detection

Add a `converged` parameter to `run` that stops early when fewer than 1% of
agents are dissatisfied.
How many steps are needed to converge at threshold 0.3 for a 100x100 grid?

</section>
