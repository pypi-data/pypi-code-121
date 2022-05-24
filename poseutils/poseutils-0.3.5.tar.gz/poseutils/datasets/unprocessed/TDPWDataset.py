from __future__ import print_function, absolute_import, division

import numpy as np
from poseutils.logger import log
from poseutils.datasets.unprocessed.Dataset import Dataset

class TDPWDataset(Dataset):
    """Dataset class for handling 3DPW dataset

        :param path: path to npz file
        :type path: str
    """

    def __init__(self, path):
        super(TDPWDataset, self).__init__('3dpw')

        self.load_data(path)

    def load_data(self, path):

        data = np.load(path, allow_pickle=True, encoding='latin1')['data'].item()

        data_train = data['train']
        data_valid = data['test']

        self._data_train['2d'] = data_train["combined_2d"]
        self._data_train['3d'] = data_train["combined_3d_cam"]*1000

        self._data_valid['2d'] = data_valid["combined_2d"]
        self._data_valid['3d'] = data_valid["combined_3d_cam"]*1000

        log("Loaded raw data")