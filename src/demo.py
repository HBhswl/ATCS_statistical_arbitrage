import matplotlib.pyplot as plt
from matplotlib.pyplot import MultipleLocator

from dataset import Dataset
from portfolio.RandomPortfolio import RandomPortfolio
from portfolio.PCAPortfolio import PCAPortfolio
from strategy import Strategy
from trade import Trade

import warnings
warnings.filterwarnings('ignore')

if __name__=='__main__':
    # 读取数据集，构建对应的指数
    dataset = Dataset(data_path='daily_jq', index_list='HS300.csv')
    dataset._load_data_all()
    dataset._compose_index_daily()

    # 构建投资组合
    # portfolio = RandomPortfolio(dataset)
    # portfolio.random_modify_weight(n_stocks=10, max_modify_portion=1.0, fix=True)
    # portfolio.build_portfolio()

    # PCA方法
    portfolio = PCAPortfolio(dataset)
    portfolio.set_parameters()
    portfolio.build_portfolio()
    portfolio.generate_signals()

    # 进行交易回测0
    trader = Trade(portfolio.portfolio_value)
    trader.set_parameters(tax_fee=0.0013)
    res = trader.backtest()
    
    x_major_locator=  MultipleLocator(res.shape[0] // 5)
    ax=plt.gca()
    ax.xaxis.set_major_locator(x_major_locator)
    plt.plot(res.profit)
    plt.show()
    