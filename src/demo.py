from dataset import Dataset
from portfolio import Portfolio

if __name__=='__main__':
    dataset = Dataset(data_path='daily_jq', index_list='HS300.csv')
    dataset._load_data_all()
    dataset._compose_index_daily()
    # dataset._plot_index()

    df = dataset._load_daily_stocks('2010-02-03')
    print(df.head())

    df = dataset._load_daily_weight('2010-02-03')
    print(df.head())

    dates = dataset._load_whole_dates()
    print(dates)

    portfolio = Portfolio(dataset)
    portfolio.random_modify_weight(n_stocks=10, max_modify_portion=1.0, fix=True)
    portfolio.build_portfolio()
    portfolio._plot_value()