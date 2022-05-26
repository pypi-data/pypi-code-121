import os
import pandas as pd
import numpy as np

from .dataloader import DataLoader

class ETHLoader(DataLoader):
    """
    Our example implementation of :py:class:`DataLoader` class. We use the Ethereum history data from the coinmetrics repo. See https://raw.githubusercontent.com/coinmetrics/data for more details.
    """

    def __init__(self, base_dir, start_idx, end_idx, features: list, dropna=False, download=True,
                 url="https://raw.githubusercontent.com/coinmetrics/data/master/csv/eth.csv"):
        """__init__

        Args:
            base_dir (str): Directory to save the download data
            start_idx (int): Where to start in the data source
            end_idx (int): Where to end in the data source
            features (list): Input variables for the environment
            dropna (bool, optional): Whether to drop lines including empty values. Defaults to False.
            download (bool, optional): Whether to re-download the data. Defaults to True.
            url (str, optional): Link to the data source. Defaults to "https://raw.githubusercontent.com/coinmetrics/data/master/csv/eth.csv".
        """        
        self._dir = os.path.join(base_dir, 'eth_data')
        self._features = features
        addr = None
        if download:
            addr = url
        else:
            addr = os.path.join(self._dir, 'data.csv')
        self._data = pd.read_csv(addr)[[*features]].iloc[start_idx:end_idx]
        if dropna:
            self._data = self._data.dropna().reset_index()
        else:
            self._data = self._data.reset_index()

        if not os.path.isdir(self._dir):
            os.mkdir(self._dir)
        if 'index' in self._data.columns:
            self._data.drop('index', axis=1, inplace=True)
        self._data.to_csv(os.path.join(self._dir, 'data.csv'))
        # var for the iterator
        self._idx = 0
        self._duration = len(self._data)

    def __len__(self):
        """Number of items

        Returns:
            int
        """        
        return len(self._data)

    def __next__(self):
        # end of the iteration
        if self._idx == len(self._data):
            raise StopIteration()

        payload = self._data.iloc[self._idx]
        self._idx += 1
        return self._idx - 1, payload

    def get_feature(self, feature_name):
        return self._data[feature_name]

    def get_duration(self):
        return self._duration
    
    def get_idx(self):
        return pd.Series(np.arange(len(self)))

    def reset(self):
        self._idx = 0
        