import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import random
import datetime as dt

pd.set_option('mode.chained_assignment', None)

# Constants
SPX_PATH = 'SPX.csv'
START_YEAR = 1928
END_YEAR = 2020

# Load S&P 500 dataset into dataframe and create daily close dataframe
spx = pd.read_csv(SPX_PATH)
spx_daily_close = spx[['Date', 'Adj Close']]

# Convert date column to datetime object
spx_daily_close['Date'] = spx_daily_close['Date'].apply(lambda str_date : dt.datetime.strptime(str_date,'%Y-%m-%d'))

# Select all rows where date is 31st of December
spx_yearly_close = spx_daily_close.loc[(spx_daily_close['Date'].dt.month==12) & (spx_daily_close['Date'].dt.day==31)].reset_index(drop=True).to_string()

# Add missing years where market did not end on 31st of December




# Create yearly returns dataframe
#spx_yearly_returns = pd.DataFrame(data, columns=['Year', 'Return']) # TODO: create data source (list of year, return, i.e. 1982, 0.078)

# Create class wrapper to handle specific methods for manipulating dataframe
class StockTools:
    
    def __init__(self, dataframe):
        self.df = dataframe
        
    # block bootstrapping to obtain historical data
    def sample_range(self, years=40, block=None): 
        '''
        Sample a time range from a dataframe. \
        Specify block as a list of integers to sample years in different portions. \
        Returns a dataframe of daily percent changes of a historical time range.
        
            Parameters:
                years (int): Number of years to sample.
                block (list): List of integers as year lengths to sample in blocks.
        
            Returns:
                range (pd.DataFrame): Dataframe of daily percent changes over sampled years.
        '''
        
        # input/type checking
        if not isinstance(years, int) or not (block == None or block.isinstance(list)):
            print("Incorrect inputs.")
            return
        
        if block.isinstance(list):
            if not all(isinstance(x, int) for x in block):
                print("Incorrect inputs.")
                return
            
        if years > 90:
            print("Year range too long to sample from.")
            return
            
        # main functionality
        if block:
            pass
            # TODO: implement splitting    
        else:
            start_date = random.randint(START_YEAR, END_YEAR - years)
            end_date = start_date + years
            
            range = self.df.iloc[start_date:end_date+1]
            
            return range
            


### TESTING/PRINTS ###

all_years = [x for x in range(1928, 2020)]
current_years = set(spx_yearly_close['Date'].dt.year)

print(spx_daily_close)

### TODO: For some reason spx_yearly_close is not a dataframe? 
### Figure out how to convert it to a dataframe so that the current_years assignment works.
