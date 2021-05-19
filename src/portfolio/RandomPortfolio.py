import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.pyplot import MultipleLocator
from tqdm import tqdm
import random

from ..dataset import Dataset
from ..portfolio.base import Portfolio

class RandomPortfolio(Portfolio):

    def __init__(self, dataset: Dataset) -> None:
        super().__init__(dataset)

        self.dataset = dataset
        self.portfolio_value = None
        self.portfolio_weight = None

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
        indexs = random.sample(list(weight.index), self.n_stocks)
        if self.fix:
            value = [1 + np.random.choice([-1, 1]) * self.max_modify_portion for _ in range(self.n_stocks)]
        else:
            value = [1 + (np.random.random() * 2 - 1) * self.max_modify_portion for _ in range(self.n_stocks)]
        weight = weight.copy()
        weight.loc[indexs, 'weight'] = weight.loc[indexs, 'weight'] * value
        return weight

    def build_portfolio(self):
        dates = self.dataset._load_whole_dates()

        res_value, res_weight = [], []
        for date in tqdm(dates, desc='building portfolio'):
            stocks = self.dataset._load_daily_stocks(date)
            weight = self.dataset._load_daily_weight(date)

            weight = self._modify(weight)

            df = pd.merge(stocks, weight, how='inner',on='code')
            df['weighted_price'] = df['close'] * df['weight']
            res_value.append(pd.DataFrame([df['weighted_price'].sum()], index=[date], columns=['value']))
            res_weight.append(weight)

        self.portfolio_value = pd.concat(res_value, axis=0)
        self.portfolio_weight = pd.concat(res_weight, axis=0)

        return self.portfolio_value

    def _plot_value(self):
        x_major_locator= MultipleLocator(self.portfolio_value.shape[0] // 5)
        ax=plt.gca()
        ax.xaxis.set_major_locator(x_major_locator)
        plt.plot(self.portfolio_value)
        
    def _plot_diff(self):
        diff = self.portfolio_value['value'] - self.dataset.index_value['value']
        x_major_locator= MultipleLocator(diff.shape[0] // 5)
        ax=plt.gca()
        ax.xaxis.set_major_locator(x_major_locator)
        plt.plot(diff)