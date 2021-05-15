import pandas as pd
import numpy as np
from tqdm import tqdm

class Trade(object):

    def __init__(self, signal: pd.DataFrame) -> None:
        super().__init__()

        self.data = signal

        self.init_value = None
        self.tax_fee = None

    def set_parameters(self, 
                      init_value: float = 1000000,
                      tax_fee: float = 0.0013) -> None:
        self.init_value = init_value
        self.tax_fee = tax_fee
    
    def backtest(self) -> pd.DataFrame:
        self.data['profit'] = 0

        position, holding_price = 0, 0

        for i in tqdm(range(1, self.data.shape[0])):
            self.data.loc[self.data.index[i], 'profit'] = self.data.loc[self.data.index[i-1], 'profit']

            # open long
            if position == 0 and self.data.loc[self.data.index[i], 'signal'] == 2:
                position = 1
                holding_price = self.data.loc[self.data.index[i], 'value']
                fee = (self.data.loc[self.data.index[i], 'value1'] + self.data.loc[self.data.index[i], 'value2']) * self.tax_fee
                self.data.loc[self.data.index[i], 'profit'] -= fee
            
            # close long
            if position == 1 and self.data.loc[self.data.index[i], 'signal'] == 1:
                position = 0
                profit = self.data.loc[self.data.index[i], 'value'] - holding_price
                self.data.loc[self.data.index[i], 'profit'] += profit
            
            # open short
            if position == 0 and self.data.loc[self.data.index[i], 'signal'] == -2:
                position = 1
                holding_price = self.data.loc[self.data.index[i], 'value']
                fee = (self.data.loc[self.data.index[i], 'value1'] + self.data.loc[self.data.index[i], 'value2']) * self.tax_fee
                self.data.loc[self.data.index[i], 'profit'] -= fee
            
            # close short
            if position == 1 and self.data.loc[self.data.index[i], 'signal'] == -1:
                position = 0
                profit = holding_price - self.data.loc[self.data.index[i], 'value']
                self.data.loc[self.data.index[i], 'profit'] += profit
        
        return self.data





