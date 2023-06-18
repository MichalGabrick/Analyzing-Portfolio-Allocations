import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import random
import datetime as dt

# Suppresses warning, fix later?
pd.set_option('mode.chained_assignment', None)

### consider creating utility class to wrap functions ###   
    
# block bootstrapping to obtain historical data
def block_bootstrap(sample_data: pd.DataFrame, n: int, block_size: int = 1) -> pd.DataFrame: 
    
    '''
    Resample data points from a dataframe.
    Specify block_size as an integer to sample data points in different portions.
    Returns a dataframe of resampled data points.
    
        Parameters:
                sample_data (pd.DataFrame): Dataframe to sample from.
                n (int): Number of data points to sample.
                block_size (int): Defines number of data points to sample as a block.
    
        Returns:
                range (pd.DataFrame): Dataframe of resampled data points.
    '''
    
    # input/type checking
    if not isinstance(n, int) or not isinstance(block_size, int):
        raise TypeError
        
    if n > len(sample_data.columns):
        print("Too many datapoints to sample.")
        return
        
    ## main functionality
    
    # create list of index labels and resampled dataframe
    samples_index = [x for x in range(n)]
    new_sample = pd.DataFrame(columns=list(sample_data.columns), index=samples_index)
    
    if block_size == 1: # standard bootstrap, no blocks
        
        # sample each datapoint from sample_data and place into new_sample
        for x in range(n):  
            new_sample.iloc[x] = [sample_data.iloc[random.randint(0, n-1)]]
         
    else:
        
        # sample (n // block_size) blocks
        for x in range(n // block_size):
            
            # randomly select start and end of a block of datapoints
            start = random.randint(0, n-1 - block_size)
            end = start + block_size
            
            # sample block from sample_data and append to new_sample
            new_sample = pd.concat([new_sample, sample_data.iloc[start:end+1]], ignore_index=True)
            
    return new_sample


### SEPARATE CODE

# Constants
SPX_PATH = 'SPX.csv'

# load S&P 500 dataset into dataframe and create daily close dataframe
spx = pd.read_csv(SPX_PATH)
spx_daily_close = spx[['Date', 'Adj Close']]

# convert date column to datetime object
spx_daily_close['Date'] = spx_daily_close['Date'].apply(lambda str_date : dt.datetime.strptime(str_date,'%Y-%m-%d'))

# select all rows where date is Dec. 31
spx_yearly_close = spx_daily_close.loc[
    (spx_daily_close['Date'].dt.month==12) & 
    (spx_daily_close['Date'].dt.day==31)
    ].reset_index(drop=True)

print(spx_yearly_close)

# add missing years where market did not end on Dec. 31
all_years = set(x for x in range(1928, 2020))
current_years = set(spx_yearly_close['Date'].dt.year)
missing_years = all_years - current_years

spx_missing_years = spx_daily_close.loc[
    (spx_daily_close['Date'].dt.year.isin(missing_years)) & 
    (spx_daily_close['Date'].dt.month==12) &
    (spx_daily_close['Date'].dt.day==29)
    ].reset_index(drop=True)

spx_yearly_close = pd.concat([spx_yearly_close, spx_missing_years], ignore_index=True)

# replace data column with year and sort by year
spx_yearly_close['Date'] = spx_yearly_close['Date'].dt.year
spx_yearly_close = spx_yearly_close.sort_values(by=['Date']).reset_index(drop=True)

# create yearly returns dataframe
spx_yearly_returns = spx_yearly_close.copy()
spx_yearly_returns['Adj Close'] = spx_yearly_returns['Adj Close'].pct_change()
spx_yearly_returns = spx_yearly_returns.rename(columns={'Date': 'Year', 'Adj Close': 'Returns'})

# fill in missing years (1928, 2020, 2021, 2022)
# FIXME: spx_yearly_returns.loc[['Year']  1928]['Returns'] = 0.3788

### TESTING/PRINTS ###
print(spx_yearly_returns)