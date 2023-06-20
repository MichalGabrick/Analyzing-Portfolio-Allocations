import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import datetime as dt
import time
from random import randint


st = time.time()

# Suppresses warning, fix later?
pd.set_option("mode.chained_assignment", None)

### consider creating utility class to wrap functions ###


# block bootstrapping to obtain historical data
def block_bootstrap(
    sample_data: pd.DataFrame, n: int, block_size: int = 1
) -> pd.DataFrame:
    """
    Resample data points from a dataframe.

        Parameters:
                sample_data (pd.DataFrame): Dataframe to sample from.
                n (int): Number of data points to sample.
                block_size (int): Defines number of data points to sample as a block.

        Returns:
                range (pd.DataFrame): Dataframe of resampled data points.
    """

    # input/type checking
    if not isinstance(n, int) or not isinstance(block_size, int):
        raise TypeError

    if n > len(sample_data.values):
        print("Too many datapoints to sample.")
        raise ValueError
    
    if n % block_size != 0:
        print("Make sure that n is a multiple of block_size.")
        raise ValueError

    # create resampled dataframe
    new_sample = pd.DataFrame(columns=list(sample_data.columns))

    # sample (n // block_size) blocks of data points
    for _ in range(n // block_size):
        # randomly select start and end of a block of data points (used to sample from sample_data)
        start = randint(0, len(sample_data.values) - block_size - 1)
        end = start + block_size

        # sample block from sample_data and append to new_sample
        new_sample = pd.concat(
            [new_sample, sample_data.iloc[start:end]], ignore_index=True
        )

    return new_sample


# simulation of an investment over a time range using a dataframe of returns
def portfolio_sim(
    equity_historical_returns: pd.DataFrame,
    bond_historical_returns: pd.DataFrame,
    allocation: int,
    principal: int,
    yearly_contribution: int,
    rebalancing: bool,
    rebalancing_band: int,
):
    """
    Simulate the future values of a portfolio of securities.

        Parameters:
                equity_historical_returns (pd.DataFrame): Dataframe of yearly historical returns of equities.
                bond_historical_returns (pd.DataFrame): Dataframe of yearly historical returns of bonds.
                allocation (int): Percentage of stocks in portfolio.
                principal (int): Initial value of portfolio.
                yearly_contribution (int): Amount to increase principal by annually.
                rebalancing (bool): Choose whether or not to rebalance portfolio annually.
                rebalancing_band (int): Fixed band, which rebalances only once an asset has deviated in allocation beyond the band.


        Returns:
                future_values (pd.DataFrame): Dataframe of the values of the portfolio through time.
    """

    pass


### SEPARATE CODE

# Constants
SPX_PATH = "SPX.csv"

# load S&P 500 dataset into dataframe and create daily close dataframe
spx = pd.read_csv(SPX_PATH)
spx_daily_close = spx[["Date", "Close"]]

# convert date column to datetime object
spx_daily_close["Date"] = spx_daily_close["Date"].apply(
    lambda str_date: dt.datetime.strptime(str_date, "%Y-%m-%d")
)

# select all rows where date is Dec. 31
spx_yearly_close = spx_daily_close.loc[
    (spx_daily_close["Date"].dt.month == 12) & (spx_daily_close["Date"].dt.day == 31)
].reset_index(drop=True)

# add missing years where market did not end on Dec. 31
all_years = set(x for x in range(1928, 2020))
current_years = set(spx_yearly_close["Date"].dt.year)
missing_years = all_years - current_years

spx_missing_years = spx_daily_close.loc[
    (spx_daily_close["Date"].dt.year.isin(missing_years))
    & (spx_daily_close["Date"].dt.month == 12)
    & (spx_daily_close["Date"].dt.day == 29)
].reset_index(drop=True)

spx_yearly_close = pd.concat([spx_yearly_close, spx_missing_years], ignore_index=True)

# replace data column with year and sort by year
spx_yearly_close["Date"] = spx_yearly_close["Date"].dt.year
spx_yearly_close = spx_yearly_close.sort_values(by=["Date"]).reset_index(drop=True)

# create yearly returns dataframe
spx_yearly_returns = spx_yearly_close.copy()
spx_yearly_returns["Close"] = spx_yearly_returns["Close"].pct_change().round(4)
spx_yearly_returns = spx_yearly_returns.rename(
    columns={"Date": "Year", "Close": "Returns"}
)

# fill in missing years (1928, 2020, 2021, 2022)
spx_yearly_returns.at[0, "Returns"] = 0.3788
spx_yearly_returns.loc[len(spx_yearly_returns.index)] = [2020, 0.1806]
spx_yearly_returns.loc[len(spx_yearly_returns.index)] = [2021, 0.2850]
spx_yearly_returns.loc[len(spx_yearly_returns.index)] = [2022, -0.1804]

# convert year column to int type
spx_yearly_returns = spx_yearly_returns.astype({"Year": "int"})


### TESTING/PRINTS ###

# print(spx_yearly_returns.to_string())

# print(block_bootstrap(spx_yearly_returns, 10, 1))

""" sims = []

for _ in range(5000):
    sims.append(block_bootstrap(sample_data=spx_yearly_returns, n=45, block_size=10))

et = time.time()

elapsed = et - st
print("Execution time:", elapsed, "seconds")

ret = []

for x in sims:
    total_return = 1
    returns = x["Returns"].tolist()

    for i in returns:
        total_return *= i + 1

    ret.append(total_return)

print(sum(ret) / len(ret)) """
