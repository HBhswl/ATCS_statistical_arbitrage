from matplotlib.pyplot import axis
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
        df = None
        for index, data in tqdm(enumerate(self.data)):
            data['profit'] = 0

            position, holding_price = 0, 0

            for i in range(1, data.shape[0]):
                data.loc[data.index[i], 'profit'] = data.loc[data.index[i-1], 'profit']

                # open long
                if position == 0 and data.loc[data.index[i], 'signal'] == 2:
                    position = 1
                    holding_price = data.loc[data.index[i], 'close'] - data.loc[data.index[i], 'value'] * data.loc[data.index[i], 'correlation']
                    fee = (data.loc[data.index[i], 'close'] + data.loc[data.index[i], 'value'] * data.loc[data.index[i], 'correlation']) * self.tax_fee
                    # data.loc[data.index[i], 'profit'] -= fee
                    
                # close long
                if position == 1 and data.loc[data.index[i], 'signal'] == 1:
                    position = 0
                    profit = data.loc[data.index[i], 'close'] - data.loc[data.index[i], 'value'] * data.loc[data.index[i-1], 'correlation'] - holding_price
                    data.loc[data.index[i], 'profit'] += profit - fee
                
                if position == 1 and (data.loc[data.index[i], 'correlation'] != data.loc[data.index[i-1], 'correlation']):
                    holding_price -= (data.loc[data.index[i], 'correlation'] - data.loc[data.index[i-1], 'correlation']) * data.loc[data.index[i], 'value']
            
            data.index = data.time
            
            if index == 0:
                df = data['profit']
            else:
                df = pd.merge(df, data['profit'], how='outer', left_index=True, right_index=True)
        df['profit'] = df.sum(axis=1)
        return df




