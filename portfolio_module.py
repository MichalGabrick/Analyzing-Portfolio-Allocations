import pandas as pd
from random import randint

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
    stock_historical_returns: pd.DataFrame,
    bond_historical_returns: pd.DataFrame,
    stock_allocation: int,
    principal: int,
    annual_contribution: int,
    rebalance: bool,
    rebalancing_band: int,
):
    """
    Simulate the future values of a portfolio of securities.

        Parameters:
                stock_historical_returns (pd.DataFrame): Dataframe of annual historical returns of stocks.
                bond_historical_returns (pd.DataFrame): Dataframe of annual historical returns of bonds.
                stock_allocation (int): Percentage of assets in portfolio allocated to stocks.
                principal (int): Initial value of portfolio.
                annual_contribution (int): Amount to increase principal by annually.
                rebalance (bool): Choose whether or not to rebalance portfolio annually.
                rebalancing_band (int): Fixed band; rebalances once an asset has deviated in allocation past the band.

        Returns:
                future_values (pd.DataFrame): Dataframe of the values of the portfolio through time.
    """

    # create future_values dataframe and initialize 'year 0' values
    future_values = pd.DataFrame(
        columns=["Year", "Total Value", "Stock Value", "Bond Value", "Stock Allocation"]
    )
    future_values.loc[len(future_values)] = {
        "Year": 0,
        "Total Value": principal + annual_contribution,
        "Stock Value": (principal + annual_contribution) * stock_allocation,
        "Bond Value": (principal + annual_contribution) * (1 - stock_allocation),
        "Stock Allocation": stock_allocation,
    }

    # iterate through historical returns of stocks and bonds, append values for each year in data
    for x in range(1, len(stock_historical_returns) + 1):
        # asset value for 'year n' is (value for 'year n-1' + annual contribution) * asset returns for that year
        stock_value = (
            future_values.loc(x - 1)["Stock Value"] + annual_contribution
        ) * stock_historical_returns.loc[x]["Returns"]

        bond_value = (
            future_values.loc(x - 1)["Bond Value"] + annual_contribution
        ) * bond_historical_returns.loc[x]["Returns"]

        current_allocation = stock_value / (stock_value + bond_value)

        # FIXME: WRITE COMMENT
        if rebalance:
            # check whether assets have exceeeded band
            if (current_allocation > (stock_allocation + rebalancing_band)) or (
                current_allocation < (stock_allocation - rebalancing_band)
            ):
                # rebalanced asset value is total value times inflation
                stock_value = (stock_value + bond_value) * stock_allocation
                bond_value = (stock_value + bond_value) * (1 - stock_allocation)

        future_values.loc[len(future_values)] = {
            "Year": x,
            "Total Value": stock_value + bond_value,
            "Stock Value": stock_value,
            "Bond Value": bond_value,
            "Stock Allocation": current_allocation,
        }

    return future_values
