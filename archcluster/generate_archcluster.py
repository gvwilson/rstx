import numpy as np
import polars as pl

SEED = 7493418

# Known cluster centers in a 100x100 coordinate space (easting, northing).
CLUSTER_CENTERS = [
    (20.0, 25.0),
    (70.0, 30.0),
    (35.0, 75.0),
    (75.0, 80.0),
]

# Standard deviation of Gaussian scatter of sites around each center (same units
# as the coordinates).  5 units produces clearly visible clusters that are well-
# separated from one another and from the noise points.
CLUSTER_SPREAD = 5.0

# Sites per cluster and number of random background noise points.
SITES_PER_CLUSTER = 15
N_NOISE = 20

# Coordinate bounds for the survey region.
REGION_MIN = 0.0
REGION_MAX = 100.0


# mccole: generate
def make_sites(
    centers=CLUSTER_CENTERS,
    spread=CLUSTER_SPREAD,
    sites_per_cluster=SITES_PER_CLUSTER,
    n_noise=N_NOISE,
    region_min=REGION_MIN,
    region_max=REGION_MAX,
    seed=SEED,
):
    """Return a Polars DataFrame of synthetic archaeological site locations.

    Columns:
        easting   -- x-coordinate in the survey region
        northing  -- y-coordinate in the survey region
        true_cluster -- integer cluster index (0, 1, ...) for clustered sites;
                        -1 for noise points

    Clustered sites are drawn from isotropic Gaussian distributions centred on
    each entry in centers.  Noise points are placed uniformly at random within
    the survey region.
    """
    rng = np.random.default_rng(seed)
    records = []

    for cluster_id, (cx, cy) in enumerate(centers):
        offsets = rng.normal(scale=spread, size=(sites_per_cluster, 2))
        for dx, dy in offsets:
            records.append(
                {
                    "easting": float(cx + dx),
                    "northing": float(cy + dy),
                    "true_cluster": cluster_id,
                }
            )

    for _ in range(n_noise):
        records.append(
            {
                "easting": float(rng.uniform(region_min, region_max)),
                "northing": float(rng.uniform(region_min, region_max)),
                "true_cluster": -1,
            }
        )

    return pl.DataFrame(records)
# mccole: /generate


if __name__ == "__main__":
    df = make_sites()
    n_clustered = df.filter(pl.col("true_cluster") >= 0).height
    n_noise = df.filter(pl.col("true_cluster") < 0).height
    print(f"Total sites: {df.height}  (clustered: {n_clustered}, noise: {n_noise})")
    print(df.head(5))
