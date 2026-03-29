import numpy as np
import matplotlib.pyplot as plt
from scipy import ndimage
from generate_image import make_image, make_pure_noise

# mccole: constants
SMOOTH_SIGMA = 2.0  # std dev of the Gaussian smoothing kernel (pixels)

# After smoothing, cell peak brightness ≈ σ²/(σ²+σ_s²) = 36/40 ≈ 0.90.
# Threshold 0.5 sits comfortably below 0.90 and well above the smoothed-noise
# ceiling (≈ 5× the smoothed-noise std dev of 0.021; see lesson for derivation).
THRESHOLD = 0.50

# Expected cell area at the operating threshold ≈ π·r_t² where
# r_t = sqrt(−2·ln(threshold/peak)) · σ_eff ≈ 1.085 · 6.32 ≈ 6.9 px, area ≈ 148 px².
# MIN_CELL_SIZE is set well below this to keep real cells while removing noise blobs.
MIN_CELL_SIZE = 30  # minimum pixel count for a detected cell
# mccole: /constants


# mccole: smooth
def smooth(image, sigma=SMOOTH_SIGMA):
    """Return the image after 2-D Gaussian smoothing with the given sigma."""
    return ndimage.gaussian_filter(image.astype(float), sigma=sigma)
# mccole: /smooth


# mccole: segment
def segment(image, threshold=THRESHOLD, min_size=MIN_CELL_SIZE):
    """Return (labeled, n_cells) from a smoothed image.

    Steps:
    1. Threshold to a binary mask (pixels above `threshold` → True).
    2. Label connected components with scipy.ndimage.label.
    3. Discard components smaller than `min_size` pixels.

    `labeled` is an integer array where 0 is background and 1..n_cells
    are the detected cells.  Components are re-numbered consecutively
    after size filtering so the label values are always contiguous.
    """
    binary = image > threshold
    raw_labeled, n_raw = ndimage.label(binary)

    # Filter by size and re-number labels.
    filtered = np.zeros_like(raw_labeled)
    new_label = 1
    for old_label in range(1, n_raw + 1):
        if np.sum(raw_labeled == old_label) >= min_size:
            filtered[raw_labeled == old_label] = new_label
            new_label += 1

    return filtered, new_label - 1
# mccole: /segment


# mccole: cell-sizes
def cell_sizes(labeled):
    """Return an array of pixel counts, one per detected cell."""
    n = labeled.max()
    return np.array([np.sum(labeled == i) for i in range(1, n + 1)])
# mccole: /cell-sizes


# mccole: plot
def plot_segmentation(image, labeled, centers, filename):
    """Save a two-panel figure to `filename`.

    Left panel: raw image (greyscale).
    Right panel: segmented image — background black, each detected cell
    a distinct colour from the tab10 palette, true cell centres marked
    with red crosses (when `centers` is not empty).
    """
    fig, axes = plt.subplots(1, 2, figsize=(9, 4))

    axes[0].imshow(image, cmap="gray", vmin=0, vmax=1)
    axes[0].set_title("Raw image")
    axes[0].axis("off")

    n_labels = labeled.max()
    colors = plt.cm.tab10(np.linspace(0, 0.9, max(n_labels, 1)))[:, :3]
    colored = np.zeros((*image.shape, 3))
    for i in range(1, n_labels + 1):
        colored[labeled == i] = colors[(i - 1) % 10]

    axes[1].imshow(colored)
    if centers:
        xs, ys = zip(*centers)
        axes[1].scatter(
            xs,
            ys,
            c="red",
            s=40,
            marker="+",
            linewidths=1.5,
            zorder=5,
            label="true centres",
        )
        axes[1].legend(loc="upper right", fontsize=7)
    axes[1].set_title(f"Segmented: {n_labels} cell(s) found")
    axes[1].axis("off")

    plt.tight_layout()
    plt.savefig(filename, dpi=90)
    plt.close(fig)
# mccole: /plot


if __name__ == "__main__":
    image, centers = make_image()
    smoothed = smooth(image)
    labeled, n_found = segment(smoothed)
    sizes = cell_sizes(labeled)
    print(f"Cells placed: {len(centers)}, cells found: {n_found}")
    print(f"Cell sizes (px): {sizes}")
    plot_segmentation(image, labeled, centers, "cellseg.png")
    print("Saved cellseg.png")

    # Pure-noise demonstration: use a low threshold AND no size filter so that
    # the full extent of false-positive behaviour is visible.
    NOISE_DEMO_THRESHOLD = 0.05
    noise_image = make_pure_noise()
    smoothed_noise = smooth(noise_image)
    labeled_noise, n_false = segment(
        smoothed_noise, threshold=NOISE_DEMO_THRESHOLD, min_size=1
    )
    print(
        f"\nPure noise at threshold {NOISE_DEMO_THRESHOLD} (no size filter): "
        f"{n_false} false cell(s)"
    )
    plot_segmentation(noise_image, labeled_noise, [], "cellseg_noise.png")
    print("Saved cellseg_noise.png")
