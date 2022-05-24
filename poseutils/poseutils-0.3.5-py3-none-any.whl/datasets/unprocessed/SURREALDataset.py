from __future__ import print_function, absolute_import, division

import numpy as np
from poseutils.logger import log
from poseutils.datasets.unprocessed.Dataset import Dataset

class SURREALDataset(Dataset):
    """Dataset class for SURREAL dataset.

        :param path_train: Path to surreal training set npz
        :type path_train: str
        :param path_valid: Path to validation set npz
        :type path_valid: str
    """

    def __init__(self, path_train, path_valid):
        super(SURREALDataset, self).__init__('surreal')

        self.load_data(path_train, path_valid)

    def load_data(self, path_train, path_valid):

        data_train = np.load(path_train, allow_pickle=True)
        data_valid = np.load(path_valid, allow_pickle=True)

        max_idx = data_train["data_3d"].shape[0]//6

        self._data_train['2d'] = data_train['data_2d'][max_idx:3*max_idx, :, :]
        self._data_train['3d'] = data_train['data_3d'][max_idx:3*max_idx, :, :]

        self._data_valid['2d'] = data_valid["data_2d"]
        self._data_valid['3d'] = data_valid["data_3d"]

        log("Loaded raw data")
