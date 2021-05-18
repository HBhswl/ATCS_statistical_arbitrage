import matplotlib.pyplot as plt

from dataset import Dataset
from portfolio.RandomPortfolio import RandomPortfolio
from portfolio.PCAPortfolio import PCAPortfolio
from strategy import Strategy
from trade import Trade

if __name__=='__main__':
    # 读取数据集，构建对应的指数
    dataset = Dataset(data_path='daily_jq', index_list='HS300.csv')
    dataset._load_data_all()
    dataset._compose_index_daily()
    # dataset._plot_index()

    # 构建投资组合
    # portfolio = RandomPortfolio(dataset)
    # portfolio.random_modify_weight(n_stocks=10, max_modify_portion=1.0, fix=True)
    # portfolio.build_portfolio()

    portfolio = PCAPortfolio(dataset)
    portfolio.set_parameters()
    portfolio.build_portfolio()

    
    '''
    # 根据投资组合，与指数，构建相应的多空策略
    strategy = Strategy(portfolio.portfolio_value, dataset.index_value)
    strategy._set_parameters()
    data = strategy.generate_signals()
    
    # 进行交易回测0
    trader = Trade(data)
    trader.set_parameters(tax_fee=0.0013)
    res = trader.backtest()
    
    plt.plot(res.profit)
    plt.show()
    '''