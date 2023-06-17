import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import random
import datetime as dt

# Suppresses warning, fix later?
pd.set_option('mode.chained_assignment', None)

### consider creating utility class to wrap functions ###   
    
# block bootstrapping to obtain historical data
def block_bootstrap(sample_data, n, column_names, block_size=1): 
    
    '''
    Resample data points from a dataframe. \
    Specify block_size as an integer to sample data points in different portions. \
    Returns a dataframe of resampled data points.
    
        Parameters:
                n (int): Number of data points to sample.
                block_size (int): Defines number of data points to sample as a block.
    
        Returns:
                range (pd.DataFrame): Dataframe of resampled data points.
    '''
    
    # input/type checking
    if not isinstance(n, int) or not block_size.isinstance(int):
        print("Incorrect inputs.")
        return
        
    if n > len(sample_data.columns):
        print("Too many datapoints to sample.")
        return
        
    # main functionality
    
    # create list of index labels and resampled dataframe
    samples_index = [x for x in range(n)]
    new_sample = pd.DataFrame(columns=column_names, index=samples_index)
    
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
            new_sample = new_sample.append(sample_data.iloc[start:end+1])
        
    return new_sample

# Constants
SPX_PATH = 'SPX.csv'
START_YEAR = 1928
END_YEAR = 2020

# load S&P 500 dataset into dataframe and create daily close dataframe
spx = pd.read_csv(SPX_PATH)
spx_daily_close = spx[['Date', 'Adj Close']]

# convert date column to datetime object
spx_daily_close['Date'] = spx_daily_close['Date'].apply(lambda str_date : dt.datetime.strptime(str_date,'%Y-%m-%d'))

# select all rows where date is 31st of December
spx_yearly_close = spx_daily_close.loc[(spx_daily_close['Date'].dt.month==12) & (spx_daily_close['Date'].dt.day==31)].reset_index(drop=True)

# add missing years where market did not end on 31st of December



# create yearly returns dataframe
#spx_yearly_returns = pd.DataFrame(data, columns=['Year', 'Return']) # TODO: create data source (list of year, return, i.e. 1982, 0.078)

    

                   
# remember to pass this for column_names ['Year', 'Adj Close']


### TESTING/PRINTS ###

all_years = set(x for x in range(1928, 2020))
current_years = set(spx_yearly_close['Date'].dt.year)

print(all_years - current_years)
