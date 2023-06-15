import pandas as pd
import numpy as np
import random
import sklearn

# Constants
spx_path = 'SPX.csv'

# Load S&P 500 dataset into dataframe
spx = pd.read_csv(spx_path)
spx = spx.drop(['Volume'], axis=1)
spx['Pct Change'] = (spx['Adj Close'] - spx['Open']) / spx['Open'] * 100
spx = spx.round(3)

# Create class wrapper to handle specific methods for manipulating dataframe
class StockTools:
    
    def __init__(self, dataframe):
        self.df = dataframe
        
    def sample_range(self, years=10, split=None): 
        '''Sample a time range from a dataframe. Input number of years to sample. \
            Specify split as a list of integers to sample years in different portions.'''
        
        # input checking
        if not isinstance(years, int) or not (split == None or split.isinstance(list)):
            print("Incorrect inputs.")
            return
        
        if split.isinstance(list):
            if not all(isinstance(x, int) for x in split):
                print("Incorrect inputs.")
                return
            
        if years > 95:
            print("Year range too long to sample from.")
            return
            
        # main functionality
        if split:
            pass
            # TODO: implement splitting    
        else:
            pass 
            #TODO: implement base sampling

print(spx.loc[15000:15005])