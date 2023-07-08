import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import datetime as dt
import time
import portfolio_module as pm


st = time.time()

# Suppresses warning, fix later
pd.set_option("mode.chained_assignment", None)

# Constants
SPX_PATH = "SPX.csv"
BOND_PATH = "MSECUSCB.csv"

# load S&P 500 dataset and Morningstar US Core Bond Index dataset into dataframes and create daily close dataframe
spx = pd.read_csv(SPX_PATH)
spx_daily_close = spx[["Date", "Close"]]

uscb = pd.read_csv(BOND_PATH)
uscb_monthly_close = uscb[["Date", "Close"]]

# convert date column to datetime object
spx_daily_close["Date"] = spx_daily_close["Date"].apply(
    lambda str_date: dt.datetime.strptime(str_date, "%Y-%m-%d")
)

uscb_monthly_close["Date"] = uscb_monthly_close["Date"].apply(
    lambda str_date: dt.datetime.strptime(str_date, "%m-%d-%Y")
)

# select all rows where date is Dec. 31
spx_annual_close = spx_daily_close.loc[
    (spx_daily_close["Date"].dt.month == 12) & (spx_daily_close["Date"].dt.day == 31)
].reset_index(drop=True)

# add missing years where market did not end on Dec. 31
all_years = set(x for x in range(1928, 2020))
current_years = set(spx_annual_close["Date"].dt.year)
missing_years = all_years - current_years

spx_missing_years = spx_daily_close.loc[
    (spx_daily_close["Date"].dt.year.isin(missing_years))
    & (spx_daily_close["Date"].dt.month == 12)
    & (spx_daily_close["Date"].dt.day == 29)
].reset_index(drop=True)

spx_annual_close = pd.concat([spx_annual_close, spx_missing_years], ignore_index=True)

# select december rows from bond dataframe
uscb_annual_close = uscb_monthly_close.loc[
    (uscb_monthly_close["Date"].dt.month == 12)
].reset_index(drop=True)

# replace data column with year and sort by year
spx_annual_close["Date"] = spx_annual_close["Date"].dt.year
spx_annual_close = spx_annual_close.sort_values(by=["Date"]).reset_index(drop=True)

uscb_annual_close["Date"] = uscb_annual_close["Date"].dt.year
uscb_annual_close = uscb_annual_close.sort_values(by=["Date"]).reset_index(drop=True)

# create annual returns dataframes
spx_annual_returns = spx_annual_close.copy()
spx_annual_returns["Close"] = spx_annual_returns["Close"].pct_change().round(4)
spx_annual_returns = spx_annual_returns.rename(
    columns={"Date": "Year", "Close": "Returns"}
)

uscb_annual_returns = uscb_annual_close.copy()
uscb_annual_returns["Close"] = uscb_annual_returns["Close"].pct_change().round(4)
uscb_annual_returns = uscb_annual_returns.drop(0)
uscb_annual_returns = uscb_annual_returns.rename(
    columns={"Date": "Year", "Close": "Returns"}
)

# fill in missing years (1928, 2020, 2021, 2022)
spx_annual_returns.at[0, "Returns"] = 0.3788
spx_annual_returns.loc[len(spx_annual_returns.index)] = [2020, 0.1806]
spx_annual_returns.loc[len(spx_annual_returns.index)] = [2021, 0.2850]
spx_annual_returns.loc[len(spx_annual_returns.index)] = [2022, -0.1804]

# convert year column to int type
spx_annual_returns = spx_annual_returns.astype({"Year": "int"})
uscb_annual_returns = uscb_annual_returns.astype({"Year": "int"})


### TESTING/PRINTS ###

# print(uscb_annual_returns.to_string())
# print(pm.block_bootstrap(uscb_annual_returns, 10, 1))

### RUN SIMS OF STOCK
""" sims = []

for _ in range(1000):
    sims.append(pm.block_bootstrap(sample_data=spx_annual_returns, n=40, block_size=5))

et = time.time()

elapsed = et - st
print("Execution time:", elapsed, "seconds")

### TESTING RETURNS
ret = []

for x in sims:
    total_return = 1
    returns = x["Returns"].tolist()

    for i in returns:
        total_return *= i + 1

    ret.append(total_return)

print(sum(ret) / len(ret))

 """