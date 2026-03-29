import numpy as np
import polars as pl

SEED = 7493418

# mccole: constants
# True log-normal parameters used to generate the synthetic flow record.
# Annual maximum flows X are modelled as log-normal: ln(X) ~ Normal(mu_y, sigma_y).
# With TRUE_MU_LOG = 4.8 and TRUE_SIGMA_LOG = 0.4 the median flow is
# exp(4.8) ~ 121 m^3/s and the geometric coefficient of variation is
# exp(0.4) - 1 ~ 49%, giving realistic variability for a mid-size river.
TRUE_MU_LOG = 4.8  # mean of log-flows (dimensionless, logs of m^3/s)
TRUE_SIGMA_LOG = 0.4  # standard deviation of log-flows (dimensionless)

N_YEARS = 50  # years of annual maximum flow record
# mccole: /constants


# mccole: generate
def generate(mu_log=TRUE_MU_LOG, sigma_log=TRUE_SIGMA_LOG, n=N_YEARS, seed=SEED):
    """Return a DataFrame with synthetic annual maximum flows.

    Draws n values from a log-normal distribution with log-mean mu_log
    and log-standard-deviation sigma_log.  Equivalently, the natural
    logarithms of the flows are drawn from Normal(mu_log, sigma_log).
    """
    rng = np.random.default_rng(seed)
    log_flows = rng.normal(loc=mu_log, scale=sigma_log, size=n)
    flows = np.exp(log_flows)
    return pl.DataFrame({"year": np.arange(1, n + 1), "annual_max_flow": flows})
# mccole: /generate


if __name__ == "__main__":
    df = generate()
    df.write_csv("flood_data.csv")
    print(f"Saved flood_data.csv ({len(df)} rows)")
    print(f"Mean: {df['annual_max_flow'].mean():.1f} m^3/s")
    print(f"Std:  {df['annual_max_flow'].std():.1f} m^3/s")
    log_flows = np.log(df["annual_max_flow"].to_numpy())
    print(f"Mean of log-flows:  {log_flows.mean():.3f}")
    print(f"Std of log-flows:   {log_flows.std(ddof=1):.3f}")
