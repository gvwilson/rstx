# Spatial Clustering of Archaeological Sites

## The Problem

-   Archaeological surveys record the locations of sites
    (settlements, hearths, burial mounds) as 2-D coordinates on a map
-   Sites are rarely distributed uniformly:
    -   Concentrations may represent settlements around a water source,
        nodes in a trade network,
        or ritual landscapes
-   [%g spatial_clustering "Spatial clustering" %] groups sites by proximity
    without requiring the analyst to specify the number of groups in advance
-   The approach here:
    -   Generate a synthetic set of site locations in which clusters at known centers
        are surrounded by random background noise
    -   Divide the survey region into a regular grid and count sites per cell
    -   Mark cells whose count meets a density threshold as "hot"
    -   Find [%g connected_component "connected components" %] of hot cells
        using [%g depth_first_search "depth-first search" %] (DFS) with 8-connectivity
    -   Assign each site the label of the component containing its cell
    -   Compute the centroid of each cluster

<div class="forma-multiple-choice" data-lang="en" markdown="1">

Why does a grid-cell density approach label some sites as noise (label -1)?

Because noise sites are placed outside the survey region.
:   Wrong: all sites in the synthetic data lie within the region bounds;
    noise sites land in cells just like cluster sites do.

Because any site whose cell has fewer than HOT_THRESHOLD sites is treated as
background, not part of any cluster.
:   Correct: a cell below the threshold is not hot, so sites in that cell
    receive label -1 regardless of how close they are to a cluster cell.

Because the DFS algorithm cannot reach sites at the edge of the grid.
:   Wrong: the DFS visits all hot cells, including those on the grid boundary;
    edge position alone does not determine whether a cell is hot.

Because cluster sites always outnumber noise sites.
:   Wrong: in the synthetic data there are 20 noise points and 60 cluster sites,
    but the labelling depends on cell density, not overall counts.

</div>

## Dividing the Region into a Grid

-   The survey region spans $[\text{region\_min}, \text{region\_max}]$ in both easting and northing
-   Divide each axis into `grid_size` equal-width cells of width
    $w = (\text{region\_max} - \text{region\_min}) / \text{grid\_size}$
-   The cell index along one axis for a coordinate $v$ is:

<p>$$\text{cell} = \left\lfloor \frac{v - \text{region\_min}}{w} \right\rfloor$$</p>

-   Sites exactly on the upper boundary would map to index `grid_size`
    -   Clip to `grid_size - 1` to keep them inside the array
-   Count the number of sites in each cell; the result is a 2D integer array of shape `(grid_size, grid_size)`

[%inc archcluster.py mark="grid"%]

## Identifying Concentration Cells

-   A cell with `count >= HOT_THRESHOLD` is called a "hot" cell
    -   It represents a local concentration of sites
-   Cells below the threshold are background
    -   Isolated or sparse finds that do not indicate a settlement pattern
-   The Boolean mask of hot cells is straightforward:

[%inc archcluster.py mark="hot-cells"%]

-   Raising `HOT_THRESHOLD` requires denser concentrations before a cell qualifies,
    which can split a real cluster into fragments or eliminate it entirely
-   Lowering `HOT_THRESHOLD` to 1 makes every occupied cell hot,
    merging isolated noise points into spurious clusters

<div class="forma-multiple-choice" data-lang="en" markdown="1">

What happens to the number of detected clusters when `GRID_SIZE` is halved
(from 20 to 10)?

The number of clusters always increases, because there are more cells to label.
:   Wrong: halving `GRID_SIZE` reduces the number of cells, not increases them;
    each coarser cell aggregates more sites.

Each cell covers four times the area and accumulates more sites, so cells are
more likely to meet HOT_THRESHOLD and previously separate clusters may merge.
:   Correct: coarser cells combine sites from a wider area; two formerly distinct
    concentration zones may land in the same or adjacent hot cells and merge into
    one connected component.

The number of clusters is unaffected because HOT_THRESHOLD does not change.
:   Wrong: cell size and threshold interact; the same threshold applied to cells
    of different sizes produces different hot-cell patterns.

Each cluster splits into more fragments because the cells are larger.
:   Wrong: larger cells aggregate more sites; the tendency is to merge clusters,
    not split them.

</div>

## Finding Clusters with Depth-First Search

-   Two hot cells belong to the same cluster if they are connected through a chain of adjacent hot cells
-   8-connectivity counts all eight neighbors (four cardinal, four diagonal),
    so clusters that touch only at corners are still merged
-   The same iterative DFS used in the `porous` lesson labels connected components
-   Here it assigns cluster IDs instead of testing for top-to-bottom percolation

[%inc archcluster.py mark="dfs"%]

-   `labels` is initialized to -1
    -   Only hot cells receive a non-negative label
-   Each cell is pushed onto the stack at most once (when first labelled),
    so the algorithm runs in $O(\text{grid\_size}^2)$ time

<div class="forma-ordering" data-lang="en" markdown="1">

Put these steps of the DFS connected-component labelling in the correct order.

1.  Scan the grid row by row; find the first hot cell with label -1
1.  Assign the current cluster_id to that cell and push it onto the stack
1.  Pop a cell from the stack; iterate over its 8 neighbors
1.  For each neighbor that is hot and unlabelled, assign cluster_id and push
1.  When the stack empties, increment cluster_id and scan for the next unlabelled hot cell

</div>

<div class="forma-multiple-choice" data-lang="en" markdown="1">

What happens when HOT_THRESHOLD is raised from 2 to 5?

Every cell qualifies as hot, so the entire grid becomes one large cluster.
:   Wrong: raising the threshold makes it harder for cells to qualify; fewer
    cells are hot, not more.

Cells need more sites to qualify, so some former cluster cells become background
and clusters may shrink, split, or disappear.
:   Correct: cells that previously had 2-4 sites are no longer hot; if those
    cells were part of a cluster's boundary or interior, the component may
    fragment into smaller pieces or fall below connectivity.

The cluster boundaries become smoother because the threshold filters outlier cells.
:   Wrong: raising the threshold removes cells from clusters; it can fragment
    boundaries rather than smooth them.

The number of noise sites decreases because more sites fall into hot cells.
:   Wrong: raising the threshold removes cells from the hot set, so more sites
    end up in background cells and are labelled as noise.

</div>

## Assigning Sites to Clusters

-   Each site is mapped to a grid cell using the same floor-division formula as `build_grid`
-   The site receives the cluster label of its cell
-   Sites in background cells receive -1 (noise)

[%inc archcluster.py mark="assign"%]

-   Sites in hot cells that belong to a small disconnected cluster receive a distinct positive label,
    not noise
-   Two sites in adjacent cells may receive different labels if one cell is hot and the other is not,
    even if the sites are physically close

<div class="forma-multiple-choice" data-lang="en" markdown="1">

Site A is at easting 34.0, northing 24.0.  Its cell has a count of 1
and HOT_THRESHOLD is 2.  What label does site A receive?

The label of the nearest hot cell's cluster.
:   Wrong: assign_labels uses the cell containing the site, not the nearest hot
    cell; proximity to a hot cell does not transfer the label.

-1, because its cell does not meet the density threshold.
:   Correct: the cell count (1) is below HOT_THRESHOLD (2), so the cell is not
    hot and every site in it is labelled -1.

0, because it is the first site encountered in the scan.
:   Wrong: label 0 is the first cluster label assigned by find_clusters, not a
    default for unlabelled sites; unlabelled sites receive -1.

The label of the cluster whose centroid is closest to the site.
:   Wrong: the grid method assigns labels by cell membership, not by distance
    to cluster centroids.

</div>

## Cluster Centroids

-   The centroid of a cluster is the mean easting and mean northing of all sites assigned to that cluster
-   Centroids summarize each cluster's geographic location and can be compared with known landscape features

[%inc archcluster.py mark="centroids"%]

-   Noise sites (label -1) are excluded from all centroid calculations
-   The centroid of a cluster recovered from Gaussian-distributed data
    should be close to the planted center
    -   The offset is the estimation error

## Testing

Grid shape and total count
:   `build_grid` must return an array of shape `(grid_size, grid_size)`.
    The sum of all cell counts must equal the total number of sites,
    because every site lands in exactly one cell.

Hot-cell mask
:   `find_hot_cells` must mark cells with count >= threshold as True and all other cells as False.

Two disconnected blocks become two clusters
:   A 3x3 hot mask with True at (0, 0) and True at (2, 2) must receive two distinct non-negative cluster IDs,
    because those cells are not 8-connected.

At least two clusters on synthetic data
:   Running the full pipeline on the synthetic data must produce at least two clusters.
    The four planted concentrations are far enough apart to remain separate under the default parameters.

One centroid per label
:   `cluster_centroids` must return exactly one entry for every unique non-negative label in the input,
    and the centroid coordinates must equal the mean of the corresponding sites.

[%inc test_archcluster.py%]

<div class="forma-flashcard" data-lang="en" markdown="1">

Grid-cell density clustering key terms

Spatial clustering
:   The task of partitioning geographic point locations into groups whose members
    are spatially proximate, without specifying the number of groups in advance

Grid cell
:   One element of a regular lattice that tiles the survey region; sites are
    counted per cell to estimate local density

Hot cell
:   A grid cell whose site count meets or exceeds HOT_THRESHOLD; hot cells
    are the building blocks of detected clusters

Connected component
:   A maximal set of hot cells that are all linked to one another through
    shared edges or corners (8-connectivity); each component is one cluster

Depth-first search
:   A graph traversal that explores as far as possible along each branch before
    backtracking, implemented here with a stack to label connected components
    of hot cells

Cluster centroid
:   The mean easting and northing of all sites assigned to a cluster;
    summarizes the cluster's geographic location

</div>

-   DBSCAN handles clusters of irregular shape and density without discretizing space
-   It requires a more advanced algorithms course.

<section class="exercises" markdown="1">

## Exercises

### Do the math

1.  A survey region runs from 0 to 100 units.  `GRID_SIZE` is 20, so each cell is
    5 units wide.  A site at easting 27.3 maps to which column index?

1.  Four clusters are planted in the synthetic data.  How many entries does the
    dict returned by `cluster_centroids` contain, assuming all four are recovered?

### Parameter sensitivity

Run the pipeline on the synthetic data with `GRID_SIZE` values of 10, 20, and 40
and `HOT_THRESHOLD` values of 1, 2, and 4 (nine combinations in total).
Record the number of clusters and noise sites for each combination.
Which settings merge the four planted clusters into fewer groups?
Which settings fragment them into many small pieces?

### Cluster purity

For each recovered cluster, compute the fraction of its member sites that share
the same `true_cluster` value from the generator.
A perfectly recovered cluster has purity 1.0.
What is the minimum purity across all recovered clusters at the default parameters?

### Boundary sensitivity

Move one planted cluster center 10 units closer to another and regenerate the
synthetic data.
Do the two clusters merge into one under the default parameters?
At what separation distance do they first appear as a single cluster?

### Centroid error

For each recovered cluster, compute the Euclidean distance between its centroid
and the nearest planted cluster center.
Is the error consistent across all four clusters, or does it vary with cluster size?

</section>
