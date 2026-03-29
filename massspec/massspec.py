import numpy as np
import polars as pl
import altair as alt
from generate_spectrum import make_spectrum, make_pure_noise, PEAKS

# mccole: constants
SMOOTH_WINDOW = 5  # number of points in the moving-average filter;
# wide enough to suppress point-to-point noise,
# narrow enough not to blur nearby peaks
THRESHOLD = 0.10  # minimum smoothed intensity to be reported as a peak;
# chosen to be roughly 2× the smoothed-noise standard
# deviation (see "Choosing the threshold" in lesson)
MIN_DISTANCE = 15  # minimum index separation between reported peaks;
# at 500 points over 500 Da this equals 1 Da per index,
# so MIN_DISTANCE = 15 means peaks must be ≥ 15 Da apart
# mccole: /constants


# mccole: smooth
def smooth(intensity, window=SMOOTH_WINDOW):
    """Return the moving-average of `intensity` over `window` points.

    Uses np.convolve with mode='same', which zero-pads at both ends.
    The first and last floor(window/2) values are therefore attenuated;
    this is acceptable because real spectra rarely have peaks at the
    very edge of the m/z range.
    """
    kernel = np.ones(window) / window
    return np.convolve(intensity, kernel, mode="same")
# mccole: /smooth


# mccole: detect
def detect_peaks(mz, intensity, threshold=THRESHOLD, min_distance=MIN_DISTANCE):
    """Return the m/z positions of peaks in `intensity`.

    A candidate peak must satisfy two conditions:
    1. Its smoothed intensity exceeds `threshold`.
    2. It is a strict local maximum (greater than both neighbours).

    When two candidates are within `min_distance` indices of each other,
    only the taller one is kept.  This non-maximum suppression prevents
    a single broad peak from being reported multiple times.
    """
    # Step 1: strict local maxima above threshold.
    is_max = (intensity[1:-1] > intensity[:-2]) & (intensity[1:-1] > intensity[2:])
    above = intensity[1:-1] > threshold
    candidates = np.where(is_max & above)[0] + 1  # +1: offset for the slice

    if len(candidates) == 0:
        return np.array([])

    # Step 2: non-maximum suppression — greedily keep tallest in each neighbourhood.
    order = np.argsort(-intensity[candidates])
    kept = []
    for i in order:
        idx = candidates[i]
        if all(abs(idx - k) >= min_distance for k in kept):
            kept.append(idx)

    kept.sort()
    return mz[np.array(kept)]
# mccole: /detect


# mccole: plot
def plot_spectrum(mz, raw, smoothed, detected_mz, filename):
    """Save a layered Altair chart to `filename`.

    Three layers:
    - raw intensity (grey, semi-transparent)
    - smoothed intensity (blue)
    - detected peaks (red vertical rules)
    """
    signal_df = pl.DataFrame({"mz": mz, "raw": raw, "smoothed": smoothed})
    base = alt.Chart(signal_df).encode(x=alt.X("mz:Q", title="m/z (Da)"))

    raw_layer = base.mark_line(color="lightgrey", opacity=0.7).encode(
        y=alt.Y("raw:Q", title="Intensity")
    )
    smooth_layer = base.mark_line(color="steelblue").encode(y="smoothed:Q")

    layers = [raw_layer, smooth_layer]
    if len(detected_mz) > 0:
        peak_df = pl.DataFrame({"mz": detected_mz})
        peak_layer = (
            alt.Chart(peak_df)
            .mark_rule(color="firebrick", strokeWidth=1.5, opacity=0.8)
            .encode(x="mz:Q")
        )
        layers.append(peak_layer)

    chart = alt.layer(*layers).properties(width=500, height=250)
    chart.save(filename)
# mccole: /plot


if __name__ == "__main__":
    mz, raw = make_spectrum()
    smoothed = smooth(raw)
    detected = detect_peaks(mz, smoothed)
    print(f"Detected peaks at m/z: {detected.round(1)}")
    true_centers = [p[0] for p in PEAKS]
    print(f"True peak centers:     {true_centers}")
    plot_spectrum(mz, raw, smoothed, detected, "massspec.svg")
    print("Saved massspec.svg")

    # Pure-noise demonstration.
    mz_n, raw_n = make_pure_noise()
    smoothed_n = smooth(raw_n)
    # Low threshold to make false positives visible.
    NOISE_DEMO_THRESHOLD = 0.04
    false_peaks = detect_peaks(mz_n, smoothed_n, threshold=NOISE_DEMO_THRESHOLD)
    print(
        f"\nPure noise: {len(false_peaks)} false peak(s) at threshold {NOISE_DEMO_THRESHOLD}"
    )
    plot_spectrum(mz_n, raw_n, smoothed_n, false_peaks, "massspec_noise.svg")
    print("Saved massspec_noise.svg")
