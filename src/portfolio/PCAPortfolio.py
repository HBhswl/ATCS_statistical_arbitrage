from os import close
from unicodedata import decimal
import numpy as np
from numpy.lib.arraysetops import _intersect1d_dispatcher
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.pyplot import MultipleLocator, axis, plot
from pandas.core import frame
from pandas.core.groupby import grouper
from tqdm import tqdm
import random
from sklearn import linear_model

from ..dataset import Dataset
from ..portfolio.base import Portfolio



class PCAPortfolio(Portfolio):

    def __init__(self, dataset: Dataset) -> None:
        super().__init__(dataset)

    def set_parameters(self, frequency=60, eigenvectors=15, lookback=60) -> None:
        """
            frequency: how often to recalculate the weight
            eigenvectors: how many eigenvectors you need
            lookback: how many days you lookback
        """
        self.frequency = frequency
        self.eigenvectors = eigenvectors
        self.lookback = lookback

    def build_portfolio(self) -> pd.DataFrame:
        dates = self.dataset._load_whole_dates()

        res_value = []
        for index in tqdm(np.arange(self.lookback, len(dates) - self.lookback, self.frequency), desc='building portfolio'):
            
            # 1. 通过PCA构建factor，但是实际上我们在中国A股上不能构建factor，因为不能做空，所以就只用index作为factor
            stocks = self.dataset._load_date_range_stocks(dates[index - self.lookback], dates[index])
            indexs = self.dataset._load_date_range_index(dates[index - self.lookback], dates[index])
            
            # 2. 建模所有的股票与指数的return
            stocks = pd.merge(stocks, indexs, how='inner', left_on='time', right_index=True)
            groups = []
            for _, group in stocks.groupby(by='code', as_index=True): 
                group['close_return'] = (group['close'] - group['close'].shift(1)) / group['close'].shift(1)
                group['value_return'] = (group['value'] - group['value'].shift(1)) / group['value'].shift(1)
                group = group.dropna(how='any')
                groups.append(group)
            stocks = pd.concat(groups, axis=0)
            stocks = stocks.sort_index()

            # 3. 根据相关性建模residual
            groups = []
            for name, group in stocks.groupby(by='code', as_index=True):
                if group.shape[0] < 5:
                    continue
                
                # model OU process
                model1 = linear_model.LinearRegression()
                model1.fit(group[['value_return']], group['close_return'])
                group['correlation'] = model1.coef_[0]
                group['residual'] = group['close_return'] - model1.coef_[0] * group['value_return'] - model1.intercept_
                group['auxiliary'] = group['residual'].cumsum()
                
                # model auxiliary process
                model2 = linear_model.LinearRegression()
                model2.fit(group[['auxiliary']].iloc[:-1, :], group['auxiliary'].iloc[1:])
                a, b = model2.intercept_, model2.coef_[0]
                std = (group['auxiliary'].iloc[1:] - a - b * group['auxiliary'].iloc[:-1]).std()
                kappa = - np.log(b) * 252
                m = a / (1 - b)
                sigma = std * np.sqrt(2 * kappa / (1 - b**2))
                sigma_eq  = std * np.sqrt(1 / (1 - b**2))

                groups.append(pd.DataFrame([[model1.coef_[0], model1.intercept_, kappa, m, sigma, sigma_eq]], index=[name], columns=['correlation', 'shift', 'kappa', 'm', 'sigma', 'sigma_eq']))

            weights = pd.concat(groups, axis=0)
            weights = weights.sort_index()
            
            # 4. 然后residual的相关性能进行相应的交易
            # 这里需要选择，选择kappa大于252/(self.lookback / 2)的
            weights = weights[weights['kappa'] > 252 / (self.lookback / 2)]

            stocks = self.dataset._load_date_range_stocks(dates[index], dates[index + self.lookback])
            indexs = self.dataset._load_date_range_index(dates[index], dates[index + self.lookback])
            stocks = pd.merge(stocks, indexs, how='inner', left_on='time', right_index=True)
            groups = []
            for _, group in stocks.groupby(by='code', as_index=True): 
                group['close_return'] = (group['close'] - group['close'].shift(1)) / group['close'].shift(1)
                group['value_return'] = (group['value'] - group['value'].shift(1)) / group['value'].shift(1)
                group = group.dropna(how='any')
                groups.append(group)
            stocks = pd.concat(groups, axis=0)
            stocks = stocks.sort_index()
            stocks = pd.merge(stocks, weights, how='inner', left_on='code', right_index=True)

            groups = []
            for _, group in stocks.groupby(by='code', as_index=True):
                group['portfolio'] = group['close_return'] - group['correlation'] * group['value_return'] - group['shift']
                group['portfolio'] = group['portfolio'].cumsum()
                group['portfolio'] = (group['portfolio'] - group['m']) / group['sigma_eq']
                groups.append(group)
            stocks = pd.concat(groups, axis=0)
            stocks = stocks.sort_index() 
            res_value.append(stocks)

        portfolio = pd.concat(res_value, axis=0)
        portfolio.index = np.arange(portfolio.shape[0])
        # portfolio['portfolio'] = (portfolio['close_return'] - portfolio['m']) / portfolio['sigma_eq']

        self.portfolio_value = []
        for _, group in portfolio.groupby(by='code', as_index=True):
            self.portfolio_value.append(group)
        
        print(self.portfolio_value[0].head(0))
        plt.plot(self.portfolio_value[0].portfolio.values)
        plt.show()
        
        return self.portfolio_value

    def generate_signals(self, open_thresh=1.25, close_thresh=0.75, frequency=1):
        for data in self.portfolio_value:
            data['signal'] = 0
            data.loc[data['portfolio'] <= - open_thresh, 'signal'] = 2
            data.loc[data['portfolio'] >= - close_thresh, 'signal'] = 1
        
        print(self.portfolio_value[0].head())
        
