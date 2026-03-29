import numpy as np
import polars as pl

# mccole: constants
SEED = 7493418  # RNG seed for reproducibility
N_POINTS = 80  # number of price-quantity observations
TRUE_ELASTICITY = -1.5  # true price elasticity (slope in log-log space)
TRUE_INTERCEPT = 5.0  # true log-scale intercept
PRICE_MIN = 1.0  # minimum price ($)
PRICE_MAX = 20.0  # maximum price ($)
# Log-quantity noise: chosen so that ~95% of observed quantities fall within
# exp(±2 * NOISE_STD) ≈ ±35% of the true quantity at each price.
NOISE_STD = 0.15
# mccole: /constants


# mccole: generate
def make_elasticity_data(
    n=N_POINTS,
    true_elasticity=TRUE_ELASTICITY,
    true_intercept=TRUE_INTERCEPT,
    price_min=PRICE_MIN,
    price_max=PRICE_MAX,
    noise_std=NOISE_STD,
    seed=SEED,
):
    """Return a Polars DataFrame with columns 'price' and 'quantity'.

    Prices are drawn uniformly from [price_min, price_max].
    Log-quantities follow:

        log(quantity) = true_intercept + true_elasticity * log(price) + noise

    where noise ~ N(0, noise_std^2), so quantities are log-normally distributed
    around the true power-law demand curve.
    """
    rng = np.random.default_rng(seed)
    prices = rng.uniform(price_min, price_max, n)
    log_quantities = (
        true_intercept
        + true_elasticity * np.log(prices)
        + rng.normal(0.0, noise_std, n)
    )
    quantities = np.exp(log_quantities)
    return pl.DataFrame({"price": prices, "quantity": quantities})
# mccole: /generate


if __name__ == "__main__":
    df = make_elasticity_data()
    print(f"Points: {len(df)}")
    print(f"Price range:    [{df['price'].min():.2f}, {df['price'].max():.2f}]")
    print(f"Quantity range: [{df['quantity'].min():.2f}, {df['quantity'].max():.2f}]")
