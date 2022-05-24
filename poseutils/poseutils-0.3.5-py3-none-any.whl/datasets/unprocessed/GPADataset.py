from __future__ import print_function, absolute_import, division

import numpy as np
from poseutils.logger import log
from poseutils.datasets.unprocessed.Dataset import Dataset

class GPADataset(Dataset):
    """Dataset class for handling GPA dataset

        :param path: path to npz file
        :type path: str
    """

    def __init__(self, path):
        super(GPADataset, self).__init__('gpa')

        self.load_data(path)

    def load_data(self, path):

        data = np.load(path, allow_pickle=True, encoding='latin1')['data'].item()

        self._data_train["2d"] = data["train"]["2d"]
        self._data_train["3d"] = data["train"]["3d"]
        self._data_valid["3d"] = data["test"]["3d"]
        self._data_valid["2d"] = data["test"]["2d"]

        log("Loaded raw data")
