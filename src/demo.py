from dataset import Dataset

if __name__=='__main__':
    dataset = Dataset(data_path='daily', index_list='HS300.csv')
    dataset._load_data_all()
    dataset._compose_index_daily()
    dataset._plot_index()