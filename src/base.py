import pandas as pd

from src.dataset import Dataset

class Portfolio(object):

    def __init__(self, dataset: Dataset) -> None:
        super().__init__()

        self.dataset = dataset
        self.portfolio_value = None
        self.portfolio_weight = None
    
    def build_portfolio(self):

        raise NotImplementedError

    
    