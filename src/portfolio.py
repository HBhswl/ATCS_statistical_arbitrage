import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.pyplot import MultipleLocator
from tqdm import tqdm

from dataset import Dataset


class Portfolio(object):

    def __init__(self, dataset: Dataset) -> None:
        super().__init__()

        self.dataset = dataset
        self.portfolio_value = None

    def random_modify_weight(self, n_stocks, max_modify_portion, fix=True):
        """
            randomly modify '$n_stocks' stocks's weight, 
            the maximum modified ratio is '$max_modify_portion',
            if fix is True, then always modify '$max_modify_portion', or with partly.
        """
        self.n_stocks = n_stocks
        self.max_modify_portion = max_modify_portion
        self.fix = fix

    def _modify(self, weight):
        pass

    def build_portfolio(self):
        dates = self.dataset._load_whole_dates()

        res_value = []
        for date in tqdm(dates, desc='building portfolio'):
            stocks = self.dataset._load_daily_stocks(date)
            weight = self.dataset._load_daily_weight(date)

            df = pd.merge(stocks, weight, how='inner',on='code')
            df['weighted_price'] = df['close'] * df['weight']
            res_value.append(pd.DataFrame([df['weighted_price'].sum()], index=[date], columns=['value']))
        
        self.portfolio_value = pd.concat(res_value, axis=0)

        return self.portfolio_value

    def _plot_value(self):
        x_major_locator= MultipleLocator(self.portfolio_value.shape[0] // 5)
        ax=plt.gca()
        ax.xaxis.set_major_locator(x_major_locator)
        plt.plot(self.portfolio_value)
        plt.show()
        
        