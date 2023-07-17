import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import datetime as dt
import portfolio_module as pm
import seaborn as sns


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


# function to run a set of simulations with meta parameters
def allocation_sims(config: list, allocations: list, sims: int):
    sims_by_allocation = pd.DataFrame(dtype="float64")

    for x in allocations:
        final_values = pd.Series(dtype="float64")

        for _ in range(sims):
            # sample stock and bond dataframes
            spx_bootstrap = pm.block_bootstrap(
                data=spx_annual_returns, n=config[0], block_size=5
            )
            uscb_bootstrap = pm.block_bootstrap(
                data=uscb_annual_returns, n=config[0], block_size=5
            )

            # simulate a portfolio with x percentage stock allocation
            sim = pm.portfolio_sim(
                spx_bootstrap,
                uscb_bootstrap,
                x,
                1000,
                config[1],
                rebalance=config[2],
                rebalancing_band=config[2],
            )

            # save final value of each simulation in final_values series
            final_values.loc[len(final_values)] = sim.loc[len(sim) - 1]["Total Value"]

        # store each final_value series as a row, differentiated by allocation
        sims_by_allocation = pd.concat(
            [sims_by_allocation, final_values.to_frame().T], ignore_index=True
        )

    # rename indices to represent asset allocations
    sims_by_allocation = sims_by_allocation.rename(
        index={
            a: f"{int(b * 100)}/{int((1-b) * 100)}"
            for (a, b) in zip(list(range(len(sims_by_allocation))), allocations)
        }
    )

    return sims_by_allocation


######################### TESTING/PRINTS ############################################

""" # 20 year period, 0 annual contribution, rebalancing with 5% band
config_1 = [20, 0, True, 0.05]  
allocation_values_1 = [0, 0.3, 0.5, 0.7, 1]
sims_1 = allocation_sims(config_1, allocation_values_1, sims=10000)

# 40 year period, 0 annual contribution, rebalancing with 5% band
config_2 = [40, 0, True, 0.05]  
allocation_values_2 = [0, 0.3, 0.5, 0.7, 1]
sims_2 = allocation_sims(config_2, allocation_values_2, sims=10000)

# 20 year period, 0 annual contribution, no rebalancing
config_3 = [20, 0, False, 0.05]  
allocation_values_3 = [0, 0.3, 0.5, 0.7, 1]
sims_3 = allocation_sims(config_3, allocation_values_3, sims=10000)

# 20 year period, 0 annual contribution, strict rebalancing
config_4 = [20, 0, True, 0]  
allocation_values_4 = [0, 0.3, 0.5, 0.7, 1]
sims_4 = allocation_sims(config_4, allocation_values_4, sims=10000)

# create figure and kdeplot
fig, ax = plt.subplots(2, 2, figsize=(16, 8), layout="constrained", sharey='row')
fig.suptitle("Distribution of Portfolio Values", fontsize=16)
sns.set_palette("colorblind")

sns.kdeplot(ax=ax[0, 0], data=sims_1.T, log_scale=True, lw=2)
ax[0, 0].set(
    xlabel="Total Value [$]", title=f"{config_1[0]} Year Period with 5% Rebalancing Band"
)
ax[0, 0].get_legend().set_title("Stocks/Bonds")

sns.kdeplot(ax=ax[0, 1], data=sims_2.T, log_scale=True, lw=2)
ax[0, 1].set(
    xlabel="Total Value [$]", title=f"{config_2[0]} Year Period with 5% Rebalancing Band"
)
ax[0, 1].get_legend().set_title("Stocks/Bonds")

sns.kdeplot(ax=ax[1, 0], data=sims_3.T, log_scale=True, lw=2)
ax[1, 0].set(
    xlabel="Total Value [$]", title=f"{config_3[0]} Year Period without Rebalancing"
)
ax[1, 0].get_legend().set_title("Stocks/Bonds")

sns.kdeplot(ax=ax[1, 1], data=sims_4.T, log_scale=True, lw=2)
ax[1, 1].set(
    xlabel="Total Value [$]", title=f"{config_4[0]} Year Period with Strict Rebalancing"
)
ax[1, 1].get_legend().set_title("Stocks/Bonds")

ax[1, 1].annotate(
    "10000 portfolios per allocation ratio were simulated with 1000 principal and no annual contribution.",
    xy=(1.0, -0.2),
    xycoords="axes fraction",
    ha="right",
    va="center",
    fontsize=10,
)

plt.savefig(f"kde.png")
plt.show()

for x in [0, .2, .4, .6, .8, 1]:
    tvals = pd.Series(dtype='float64')
    
    for _ in range(1000):
        spx_bootstrap = pm.block_bootstrap(sample_data=spx_annual_returns, n=60, block_size=5)
        uscb_bootstrap = pm.block_bootstrap(sample_data=uscb_annual_returns, n=60, block_size=5)

        sim = pm.portfolio_sim(spx_bootstrap, uscb_bootstrap, x, 1000, 0, True, .05)

        tvals.loc[len(tvals)] = sim.loc[39]["Total Value"]
    
    print(f'Stock/Bond Split: {x}:{int((10-(x*10)))/10}')
    print(f'Min: {tvals.min()}')
    print(f'Max: {tvals.max()}')
    print(f'Avg: {tvals.mean()}')
    print(f'SD: {tvals.std()}')
    print()

# sns lineplot, mean line w/ 95% confidence bound
simulations = pd.DataFrame(columns=["Year", "Total Value"])
for _ in range(500):
    spx_bootstrap = pm.block_bootstrap(sample_data=spx_annual_returns, n=40, block_size=5)
    uscb_bootstrap = pm.block_bootstrap(sample_data=uscb_annual_returns, n=40, block_size=5)
    
    sim = pm.portfolio_sim(spx_bootstrap, uscb_bootstrap, 1, 1000, 0, True, .05)
    
    for x in range(len(sim)):
        simulations.loc[len(simulations)] = {"Year": sim.loc[x]["Year"], "Total Value": sim.loc[x]["Total Value"]}

sns.lineplot(data=simulations, x="Year", y="Total Value")
plt.show()

# regular multicolor plot
fig, ax = plt.subplots()
fig.suptitle("Monte Carlo Simulation of Portfolio Values", fontsize=14)
sns.set_palette("colorblind")
ax.set(xlabel='Time', ylabel="Total Value [$]")

for _ in range(100):
    spx_bootstrap = pm.block_bootstrap(data=spx_annual_returns, n=40, block_size=5)
    uscb_bootstrap = pm.block_bootstrap(data=uscb_annual_returns, n=40, block_size=5)
    
    sim = pm.portfolio_sim(spx_bootstrap, uscb_bootstrap, .5, 1000, 0, True, .05)
    ax = plt.plot(sim["Year"], sim["Total Value"])

plt.savefig("montecarlo_sim.png")
plt.show() """
