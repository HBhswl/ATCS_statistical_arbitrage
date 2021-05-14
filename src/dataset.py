import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.pyplot import MultipleLocator
from tqdm import tqdm

class Dataset(object):

    def __init__(self, data_path, index_list) -> None:
        super().__init__()

        # save the parameter
        self.data_path = data_path
        self.index_list = index_list
        
        # save the data
        self.data = None
        self.index_weight = None
        self.index_value = None

    def _load_data_all(self):
        filenames = sorted(os.listdir(self.data_path))[:1000]
        
        # load data 
        dfs = []
        for filename in tqdm(filenames, desc='load_data'):
            df = pd.read_csv(os.path.join(self.data_path, filename), index_col=0)
            dfs.append(df)

        self.data = pd.concat(dfs, axis=0)
        self.data.index = np.arange(self.data.shape[0])

        # load index data
        self.index_weight = pd.read_csv(self.index_list, index_col=0)
        self.index_weight.rename(columns={'effDate':'Date'}, inplace=True)

    def _compose_index_daily(self):
        unique_dates = sorted(list(self.index_weight.Date.unique()))
        data_partitions = []
        for i in tqdm(range(len(unique_dates)-1), desc='construct index'):
            daily_data = self.data[(self.data['time'] >= unique_dates[i]) & 
                                    (self.data['time'] < unique_dates[i+1])]
            if 0 == daily_data.shape[0]:
                break

            # TODO: Need to fill in the missing data
            daily_data = pd.merge(daily_data, self.index_weight[self.index_weight.Date==unique_dates[i]], how='inner',
                                 on='code')
            daily_data['weighted_price'] = daily_data['close'] * daily_data['weight']
            daily_data = daily_data.groupby(by='time', as_index=True).apply(lambda x: x.weighted_price.sum())
            data_partitions.append(daily_data)
        
        self.index_value = pd.concat(data_partitions, axis=0).to_frame(name='value')
        print(self.index_value.columns)

    def _plot_index(self):
        x_major_locator= MultipleLocator(self.index_value.shape[0] // 5)
        ax=plt.gca()
        ax.xaxis.set_major_locator(x_major_locator)
        plt.plot(self.index_value)

    def _load_daily_stocks(self, date):
        df = self.data[self.data['time'] == date]
        assert df.shape[0] > 0, 'The date is wrong!'

        df = df.sort_values(by=['code'])
        df.index = np.arange(df.shape[0])
        return df
    
    def _load_daily_weight(self, date):
        unique_dates = sorted(list(self.index_weight.Date.unique()))
        for i in range(len(unique_dates) - 1):
            if date >= unique_dates[i] and date < unique_dates[i + 1]:
                df = self.index_weight[self.index_weight.Date==unique_dates[i]]
                df = df.sort_values(by=['code'])
                df.index = np.arange(df.shape[0])
                return df
        assert True, 'The date is wrong!'

    def _load_whole_dates(self):
        unique_dates = list(self.index_value.index)
        return unique_dates