import pandas as pd
import numpy as np


class Strategy(object):

    def __init__(self, series1: pd.DataFrame, series2: pd.DataFrame) -> None:
        super().__init__()

        self.series1 = series1
        self.series2 = series2

        self.frequency = None
        self.sigma_long_open = None
        self.sigma_long_close = None
        self.sigma_short_open = None
        self.sigma_short_close = None

        # output data
        self.signal = None

    def _set_parameters(self, 
                        frequency: int = 1, 
                        sigma_long_open: float = 1.25, 
                        sigma_long_close: float = 0.5, 
                        sigma_short_open: float = 1.25, 
                        sigma_short_close: float = 0.5, 
                        ) -> None:
        self.frequency = frequency
        self.sigma_long_open = sigma_long_open
        self.sigma_long_close = sigma_long_close
        self.sigma_short_open = sigma_short_open
        self.sigma_short_close = sigma_short_close

    def generate_signals(self) -> pd.DataFrame:
        '''
            generate the trading signals.
            2: open long
            1: close long 
            0: nothing
            -1: close short
            -2: open short
        '''

        # date alignment
        data = self._date_alignment(self.series1, self.series2)
        data['signal'] = 0

        # generate signals
        sigma = data['value'].std()

        position = 0
        for i in range(0, data.shape[0], self.frequency):
            if 0 == position and data.loc[data.index[i], 'value'] <= - self.sigma_long_open * sigma:
                position = 1
                data.loc[data.index[i], 'signal'] = 2
            if 1 == position and data.loc[data.index[i], 'value'] >=  - self.sigma_long_close * sigma:
                position = 0
                data.loc[data.index[i], 'signal'] = 1
        
        position = 0
        for i in range(data.shape[0]):
            if 0 == position and data.loc[data.index[i], 'value'] >= self.sigma_short_open * sigma:
                position = 1
                data.loc[data.index[i], 'signal'] = -2
            if 1 == position and data.loc[data.index[i], 'value'] <= self.sigma_short_close * sigma:
                position = 0
                data.loc[data.index[i], 'signal'] = -1
        
        return data

    def _date_alignment(self, series1: pd.DataFrame, series2: pd.DataFrame) -> pd.DataFrame:
        series1 = series1.copy().rename(columns={'value':'value1'})
        series2 = series2.copy().rename(columns={'value':'value2'})

        series_aligned = pd.merge(series1, series2, left_index=True, right_index=True, how='inner')
        series_aligned['value'] = (series_aligned['value1'] - series_aligned['value2'])
        return series_aligned