# Spatial Interpolation of Climate Data

## The Problem

-   Weather stations record temperature and precipitation at discrete locations,
    but models and maps need values everywhere in the study region
-   [%g spatial_interpolation "Spatial interpolation" %] estimates the value at unsampled locations
    by combining observations from nearby stations
-   Our approach:
    -   Generate a synthetic network of weather stations
        whose values are sampled from a known smooth field
        so that errors can be measured exactly
    -   Apply [%g inverse_distance_weighting "inverse-distance weighting" %] (IDW)
        to estimate temperature on a regular covering the same region
    -   Evaluate the interpolated surface against the true field using
        [%g mean_absolute_error "mean absolute error" %] (MAE).
    -   Estimate prediction skill at new locations using
        [%g cross_validation_loo "leave-one-out cross-validation" %]

<div class="forma-multiple-choice" data-lang="en" markdown="1">

Why should interpolation give more weight to nearby stations than to distant ones?

Because distant stations use different instruments and are less accurate.
:   Wrong: instrument quality is not related to distance; the justification is
    that nearby locations tend to have more similar values than distant ones,
    a property called spatial autocorrelation.

Because nearby locations tend to have more similar values (spatial
autocorrelation), so closer stations carry more information about the
unsampled point.
:   Correct: spatial autocorrelation means that the correlation between two
    location values decreases with distance; IDW formalises this by assigning
    weights that shrink as distance grows.

Because nearby stations have more recent observations.
:   Wrong: observation time is not part of the IDW model; only Euclidean
    distance affects the weights.

Because averaging all stations equally would always overestimate the value.
:   Wrong: an equal-weight average is not systematically biased, but it ignores
    spatial structure and produces poor local estimates when the field varies
    across the region.

</div>

## Inverse-Distance Weighting

-   For a query point $\mathbf{q}$, let $d_i = \|\mathbf{q} - \mathbf{s}_i\|$ be
    the Euclidean distance to station $i$ with observed value $z_i$
-   The IDW estimate is:

<p>$$\hat{z}(\mathbf{q}) = \frac{\displaystyle\sum_{i=1}^{n} w_i\, z_i}{\displaystyle\sum_{i=1}^{n} w_i}, \qquad w_i = d_i^{-p}$$</p>

-   The power parameter $p$ controls how fast influence falls off with distance
    -   $p = 2$ is standard in environmental science
-   A small constant $\varepsilon = 10^{-10}$ is added to each $d_i$
    to prevent division by zero when a query point coincides with a station
-   Because the weights are non-negative and sum to one after normalization,
    IDW is a [%g convexity "convex combination" %]:
    all estimates lie within $[\min_i z_i,\, \max_i z_i]$

## Generating Synthetic Station Data

-   The true temperature field is $T(x, y) = \sin(3\pi x)\cos(2\pi y)$ on $[0,1]^2$,
    producing three warm-cool bands in $x$ and two in $y$
-   Station locations are drawn uniformly at random
    -   Values are exact samples from this field with no added noise
-   Using a noise-free reference separates interpolation error from measurement error
    when evaluating the method

[%inc generate_interp.py mark="generate"%]

## Computing the IDW Grid

-   Each of the grid points is treated as an independent query
-   All $(m \times n)$ distances are computed at once by broadcasting:
    `diff = query_xy[:, newaxis, :] - station_xy[newaxis, :, :]` yields an $(m, n, 2)$ array
-   Summing squared differences along the last axis
    gives the $(m, n)$ distance matrix in a single expression

[%inc interp.py mark="idw"%]

[%inc interp.py mark="grid"%]

<div class="forma-ordering" data-lang="en" markdown="1">

Order the steps to compute an IDW estimate at a single query point.

Compute the Euclidean distance from the query point to each station, adding epsilon to prevent division by zero.
Compute inverse-distance weights: w_i = d_i^(-p).
Form the weighted sum of station values.
Divide by the total weight to obtain the normalized estimate.

</div>

## Visualizing the Interpolation

[%inc interp.py mark="plot"%]

[%figure
  slug="interp-fields"
  img="interp-fields.svg"
  alt="Two side-by-side heatmaps on a unit square. The left panel shows the true sinusoidal temperature field as alternating red and blue bands. The right panel shows the IDW interpolation, which broadly reproduces the band pattern with some blurring near the edges. Black crosses mark the 30 station locations."
  caption="True temperature field (left) and IDW interpolation from 30 synthetic weather stations (right, p = 2). The interpolation captures the large-scale structure but smooths detail in regions with sparse station coverage."
%]

## Cross-Validation

-   Leave-one-out cross-validation (LOO-CV) measures how well the interpolation predicts the value
    at a completely unsampled location
-   For each of the $n$ stations:
    -   Remove it
    -   Interpolate its value from the remaining $n - 1$ stations
    -   Record the absolute error
-   The mean of the $n$ absolute errors (the LOO-CV MAE) estimates
    the expected prediction error at a new station location
-   LOO-CV is necessary because IDW nearly reproduces the training value
    at any station included in the computation
    -   Evaluating accuracy on training data
        would systematically underestimate the true prediction error

## Testing

Station count
:   `make_stations()` must return exactly `N_STATIONS` rows.

Exact recovery at station location
:   IDW at a station's own coordinates must return approximately that station's value.
    The tolerance $10^{-4}$ is justified by the EPSILON perturbation,
    which gives the co-located station a weight ratio of roughly $10^{20}$:1.

Grid shape
:   `interpolate_grid` with `rows=10, cols=15` must return an array of shape $(10, 15)$.

Interpolated values in range
:   Every IDW estimate must lie within $[\min z_i, \max z_i]$.
    This is a consequence of IDW being a convex combination of the station values.

Weights decrease with distance
:   A query point 0.2 units from station A and 0.8 units from station B
    must produce an estimate closer to A's value.

Cross-validation MAE below threshold
:   LOO-CV MAE must be below 0.3 on the synthetic data.
    the true field amplitude is 1.0,
    and 30 stations on this smooth field should achieve well under 30% relative error.

[%inc test_interp.py%]

<div class="forma-flashcard" data-lang="en" markdown="1">

Spatial interpolation key terms

Spatial interpolation
:   The estimation of a continuous field at unsampled locations from observations
    at a discrete set of known locations; methods range from inverse-distance
    weighting to kriging, which additionally accounts for the spatial covariance
    structure of the field

Inverse-distance weighting
:   An interpolation method that estimates the value at a query point as the
    weighted average of all station values, with each station's weight equal to
    its inverse distance to the query point raised to a power p; larger p
    concentrates influence on the nearest stations

Leave-one-out cross-validation
:   A model-evaluation procedure in which each observation is held out in turn,
    the model is fitted on the remaining observations, and the error for the
    held-out point is recorded; averaging over all held-out points estimates
    prediction skill on new data without requiring a separate test set

</div>

<section class="exercises" markdown="1">

## Exercises

### Do the math

Station A is 1 unit from the query point and has value 1.0.
Station B is 2 units away and has value 0.0.
Using p = 2, what is the IDW estimate at the query point?

### Effect of the power parameter

Run IDW with $p$ values of 1, 2, 4, and 8 on the synthetic station data.
For each value compute the LOO-CV MAE and plot the interpolated field.
How does the surface change as $p$ increases?
Which $p$ minimises LOO-CV error on this dataset?

### Nearest-neighbour interpolation

Implement nearest-neighbour interpolation: assign each grid point the value of
its closest station, equivalent to IDW as $p \to \infty$.
Compare the MAE and visual appearance of the nearest-neighbour field to the
IDW field at $p = 2$.

### Station density sensitivity

Generate station sets of size 5, 15, 30, and 60, each with a different random
seed, and compute the LOO-CV MAE for each.
Plot MAE as a function of station count.
Does the error halve when the station count doubles?

### Measurement noise

Modify the generator to add Gaussian noise with standard deviation 0.1 to each
station's observed value.
How does the LOO-CV MAE change compared to the noise-free case?
Is there an optimal $p$ that reduces the impact of measurement noise?

</section>
