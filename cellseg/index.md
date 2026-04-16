# Cell Segmentation in Microscopy Images

## The Problem

-   Fluorescence microscopy makes individual cells visible as bright spots on a dark background
-   Counting cells and measuring their sizes by hand is impractical at scale
-   Automated segmentation identifies which pixels belong to which cell using image processing
-   The same pipeline is used in drug-discovery assays, developmental biology, and pathology

## Representing a Fluorescence Image

-   Each cell is modelled as a 2-D Gaussian blob centred at $(x_c, y_c)$:

<p>$$I(x, y) = B \exp\!\left(-\frac{(x - x_c)^2 + (y - y_c)^2}{2\sigma^2}\right)$$</p>

-   $B$ is the peak brightness and $\sigma$ is the width of the cell in pixels
-   Multiple cells are summed,
    independent Gaussian noise is then added and intensities are clipped to zero
    -   A negative photon count is unphysical
-   Cells are placed so that no two centres are closer than `MIN_SEPARATION` pixels
    -   This separation is chosen large enough that
        the midpoint intensity between two adjacent cells falls below the operating threshold (below)

[%inc generate_image.py mark="constants"%]
[%inc generate_image.py mark="make-image"%]

## Step 1: Smoothing

-   Raw images are noisy,
    so the [%g gaussian_filter "Gaussian filter" %] replaces each pixel with
    a weighted average of its neighbourhood, suppressing point-to-point fluctuations
-   [%g convolution "Convolving" %] the signal Gaussian ($\sigma$) with the filter Gaussian ($\sigma_s$)
    gives a smoothed cell with sigma $\sqrt{\sigma^2 + \sigma_s^2}$ and peak brightness:

<p>$$B_\text{smooth} = B \cdot \frac{\sigma^2}{\sigma^2 + \sigma_s^2}$$</p>

-   With $\sigma = 6$ and $\sigma_s = 2$ this gives $B_\text{smooth} = 36/40 = 0.90$

[%inc cellseg.py mark="smooth"%]

## Step 2: Thresholding and Labelling

-   Pixels above a threshold form a [%g binary_mask "binary mask" %]
    -   Connected regions in the mask are individual cells
-   `scipy.ndimage.label` assigns a unique integer to each [%g connected_component "connected component" %]
-   Components smaller than `MIN_CELL_SIZE` pixels are discarded to remove noise artefacts

[%inc cellseg.py mark="segment"%]
[%inc cellseg.py mark="cell-sizes"%]

<div class="forma-ordering" data-lang="en" markdown="1">

Put these cell-segmentation steps in the correct order.

1.  Place Gaussian blobs at random non-overlapping positions
1.  Add Gaussian noise and clip pixel values to zero
1.  Apply 2-D Gaussian smoothing
1.  Threshold the smoothed image to produce a binary mask
1.  Label connected components with `scipy.ndimage.label`
1.  Discard components smaller than `MIN_CELL_SIZE` pixels

</div>

## Choosing the Threshold

-   The smoothed noise has standard deviation:

<p>$$\sigma_\text{noise,smooth} = \frac{\sigma_\text{noise}}{2\sqrt{\pi}\,\sigma_s} \approx \frac{0.15}{2\sqrt{\pi}\cdot 2} \approx 0.021$$</p>

-   The operating threshold of 0.50 is approximately $24\,\sigma_\text{noise,smooth}$,
    so the probability of a noise pixel exceeding it is vanishingly small
-   The minimum cell separation (24 px) ensures the midpoint between two adjacent cells
    has intensity $2 B \exp(-d^2 / 8\sigma^2) = 2 \exp(-2.25) \approx 0.21$,
    well below the threshold,
    so adjacent cells are never merged into one component

[%inc cellseg.py mark="constants"%]

<div class="forma-multiple-choice" data-lang="en" markdown="1">

`MIN_SEPARATION` is set to 24 pixels rather than a smaller value. Why?

scipy.ndimage.label cannot separate components closer than 24 pixels
:   Wrong: label works at pixel level and separates any two components that do not touch.

At smaller separations the midpoint intensity between two adjacent cells exceeds the threshold, merging them into one component
:   Correct: two Gaussians 24 px apart have midpoint intensity ≈ 0.21, safely below the threshold of 0.50; closer cells would merge.

The Gaussian smoothing filter blurs cells together unless they are at least $4\sigma$ apart
:   Wrong: `SMOOTH_SIGMA` = 2, so $4\sigma = 8$ pixels — much less than 24; blurring is not the limiting factor.

24 pixels is the minimum required by the physical image resolution in microns
:   Wrong: the separation is derived from the threshold and cell brightness, not from physical calibration of the microscope.

</div>

## What the Segmenter Finds in Pure Noise

-   The same pipeline applied to an image with no cells at all produces false detections
    when the threshold is too low

[%inc generate_image.py mark="make-noise"%]

[%figure
  slug="cellseg-noise"
  img="cellseg_noise.png"
  alt="Pure-noise image with 4 false cell detections shown in colour."
  caption="Pure Gaussian noise (no cells) smoothed and segmented at threshold 0.05 with no size filter. Four spurious regions are labelled. The same image at the operating threshold of 0.50 produces zero detections."
%]

-   At threshold 0.05 ($\approx 2.4\,\sigma_\text{noise,smooth}$)
    roughly 0.8% of pixels exceed the threshold
    -   These cluster into a handful of connected blobs
-   The size filter (MIN_CELL_SIZE = 30 px) removes most noise blobs in practice
    because genuine noise blobs are usually smaller than real cells
-   The operating threshold makes the size filter a secondary defence rather than the primary one

[%figure
  slug="cellseg-signal"
  img="cellseg.png"
  alt="Left: raw synthetic image with 8 Gaussian blobs. Right: segmented image with each cell in a different colour and true centres marked with red crosses."
  caption="Eight synthetic cells recovered by the segmentation pipeline. All 8 are found; cell areas range from 143 to 150 pixels squared, close to the analytic value of 148 pixels squared."
%]

<div class="forma-multiple-choice" data-lang="en" markdown="1">

The noise demonstration shows 4 false cells at threshold 0.05 (no size filter)
and 0 false cells at threshold 0.50. What roles do the threshold and `MIN_CELL_SIZE` play?

The size filter is the primary defence; the threshold only speeds up computation
:   Wrong: without an adequate threshold, large noise clusters pass the size filter too; the threshold does the main work.

The threshold and the size filter are equally important and interchangeable
:   Wrong: they address different failure modes — one filters by intensity, the other by area — and are not interchangeable.

The threshold is irrelevant as long as the size filter is strict enough
:   Wrong: a very low threshold lets many noise pixels cluster into large components that pass the size filter.

The threshold is the primary defence; the size filter removes small noise blobs that slip past a well-chosen threshold
:   Correct: at 0.50 $\approx 24\sigma$, noise exceedances are vanishingly rare; the size filter is a secondary backstop for the few that remain.

</div>

## Testing

Noise reduction
:   Smoothing must reduce pixel-to-pixel variance; an increase would indicate a bug or wrong kernel mode.

Shape preservation
:   `scipy.ndimage.gaussian_filter` must not change the array shape.

Constant image
:   A uniform image has no gradients,
    so smoothing must leave its interior values unchanged.
    The boundary is affected by zero-padding,
    so only interior pixels are checked.

Cell count
:   With default parameters the pipeline must find exactly `N_CELLS = 8` cells.
    This pins the full pipeline against a reproducible result.

Cell sizes
:   All detected cell areas must fall in the range 50-350 $\text{px}^2$.
    The analytic value is 148 $\text{px}^2$;
    the bounds give a factor of 3 on each side to absorb noise, overlap, and discretisation effects.

Empty result above maximum
:   Setting the threshold above the maximum pixel value must return zero cells.

Pure noise
:   At threshold 0.05 pure noise must produce at least one false detection,
    showing that parameter choice matters.
    At the operating threshold it must produce none, showing the threshold is adequate.

[%inc test_cellseg.py%]

<section class="exercises" markdown="1">

## Exercises

### Do the math

A cell has peak brightness $B = 1.0$ and Gaussian width $\sigma = 6$ pixels.
After smoothing with a Gaussian filter of width $\sigma_s = 2$ pixels,
the smoothed peak brightness is $B \cdot \sigma^2 / (\sigma^2 + \sigma_s^2)$.
What is the result? Give your answer to two decimal places.

### Watershed segmentation

The thresholding approach fails when two cells overlap and merge into a single connected
component.  Implement watershed segmentation: compute the distance transform of the
binary mask (`scipy.ndimage.distance_transform_edt`), find local maxima of the distance
map as seed points, and use `scipy.ndimage.watershed_ift` (or `skimage.segmentation.watershed`)
to split overlapping regions.  Demonstrate that it correctly separates two cells whose
centres are only 14 pixels apart (closer than `MIN_SEPARATION`).

### Intensity-based cell classification

Add a second cell type to `make_image`: dim cells with `brightness=0.4` alongside the
standard bright cells with `brightness=1.0`.  Extend `segment` to return a label array
and a list of per-cell mean intensities, then classify each detected cell as bright or
dim using a simple intensity threshold.  Report precision and recall for each class.

### Effect of noise on count accuracy

Generate 50 images for each of five noise levels:
$\sigma_\text{noise} \in \{0.05, 0.10, 0.15, 0.20, 0.25\}$.
Run the full pipeline on each image and record the number of cells found.
Plot mean and standard deviation of the cell count as a function of noise level and
identify the noise level at which the pipeline begins to fail consistently.

### Adaptive thresholding

Real microscopy images often have uneven illumination: the background is brighter in some
regions than others.  Simulate this by adding a low-frequency gradient:

<p>$G(x,y) = 0.2 \cdot x / \text{IMAGE\_SIZE}$</p>

to the synthetic image before adding noise.
Show that the global threshold misses cells in dark regions or over-detects in bright
regions, then implement local thresholding (`scipy.ndimage.generic_filter` with a
percentile-based local estimate) and show that it restores accurate cell counts.

</section>
