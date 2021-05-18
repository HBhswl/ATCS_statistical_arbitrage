from unicodedata import decimal
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.pyplot import MultipleLocator
from pandas.core import frame
from tqdm import tqdm
import random

from dataset import Dataset
from portfolio.base import Portfolio

class PCAPortfolio(Portfolio):

    def __init__(self, dataset: Dataset) -> None:
        super().__init__(dataset)

    def set_parameters(self, frequency=100, eigenvectors=15, lookback=200) -> None:
        """
            frequency: how often to recalculate the weight
            eigenvectors: how many eigenvectors you need
            lookback: how many days you lookback
        """
        self.frequency = frequency
        self.eigenvectors = eigenvectors
        self.lookback = lookback

    def build_portfolio(self) -> (pd.DataFrame, pd.DataFrame):
        dates = self.dataset._load_whole_dates()

        res_value, res_weight = [], []
        for index in tqdm(np.arange(self.lookback, len(dates), self.frequency), desc='building portfolio'):
            stocks = self.dataset._load_date_range_stocks(dates[index - self.lookback], dates[index])

            # 存在有前后股票池不对应的问题, 暂时先不考虑这个问题，先用前面的票池构建，后面只取前面票池有的票
            print(len(stocks['code'].unique()))

            # 1. 通过PCA构建factor，但是实际上我们在中国A股上不能构建factor，因为不能做空，所以就只用index作为factor
            # 2. 建模所有的股票与指数之间的相关性
            # 3. 建模residual
            # 4. 然后residual的相关性能进行相应的交易

        return self.portfolio_value, self.portfolio_weight


