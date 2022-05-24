from __future__ import print_function, absolute_import, division

import numpy as np
from poseutils.logger import log
from poseutils.datasets.unprocessed.Dataset import Dataset
from poseutils.datasets.transformation.CalculateMetrics import CalculateMetrics

class TransformedDataset(object):
    """This class takes a unprocessed dataset and applies different transformations to it.

        :param dataset: Unprocessed dataset, defaults to None
        :type dataset: poseutils.datasets.unprocessed.Dataset, optional
        :param transformations2d: List of transformations to apply on 2d data
        :type transformations2d: list(poseutils.datasets.transformation.Transformation), defaults to []
        :param transformations3d: List of transformations to apply on 3d data, defaults to []
        :type transformations3d: list(poseutils.datasets.transformation.Transformation), optional
        :param njnts: Number of joints i.e. joint configuration (14 or 16), defaults to 14
        :type njnts: int, optional
    """

    def __init__(self, dataset=None, transformations2d=[], transformations3d=[], njnts=14):
        super(TransformedDataset, self).__init__()

        self._data_train = { "2d": None, "3d": None }
        self._data_valid = { "2d": None, "3d": None }

        if dataset is not None:
            self.set_train(dataset.get_2d_train(njnts), dataset.get_3d_train(njnts))
            self.set_valid(dataset.get_2d_valid(njnts), dataset.get_3d_valid(njnts))

        self.means = {"2d": 0, "3d": 0}
        self.stds = {"2d": 0, "3d": 0}

        self.transformations2d = transformations2d
        self.transformations3d = transformations3d


    def set_train(self, d2d, d3d):
        """Set training data

            :param d2d: 2d data to set (NxMx2), M = 14 or 16
            :type d2d: numpy.ndarray
            :param d3d: 3d data to set (NxMx3), M = 14 or 16
            :type d3d: numpy.ndarray
        """

        self._data_train["2d"] = d2d
        self._data_train["3d"] = d3d

    def set_valid(self, d2d, d3d):
        """Set validation data

            :param d2d: 2d data to set (NxMx2), M = 14 or 16
            :type d2d: numpy.ndarray
            :param d3d: 3d data to set (NxMx3), M = 14 or 16
            :type d3d: numpy.ndarray
        """

        self._data_valid["2d"] = d2d
        self._data_valid["3d"] = d3d

    def calculate_metrics(self):
        """Calculates mean and standard devation from the training dataset (2d and 3d)
        """

        log("Calculating mean and std")

        d2d, d3d = self._data_train['2d'], self._data_train['3d']

        self.means["2d"], self.stds["2d"] = np.mean(d2d, axis=0), np.std(d2d, axis=0)
        self.means["3d"], self.stds["3d"] = np.mean(d3d, axis=0), np.std(d3d, axis=0)

    def transform(self):

        self.apply2d(self.transformations2d)
        self.apply3d(self.transformations3d)

    def apply2d(self, transformations):
        """Applies transformations to the 2d dataset (both training and validation)

            :param transformations: List of transformations to apply on 2d data
            :type transformations: list(poseutils.datasets.transformation.Transformation)
        """

        for transformation in transformations:

            if isinstance(transformation, CalculateMetrics):
                self.calculate_metrics()
            else:
                self._data_train["2d"] = transformation(self._data_train["2d"], mean=self.means["2d"], std=self.stds["2d"])
                self._data_valid["2d"] = transformation(self._data_valid["2d"], mean=self.means["2d"], std=self.stds["2d"])

    def apply3d(self, transformations):
        """Applies transformations to the 3d dataset (both training and validation)

            :param transformations: List of transformations to apply on 3d data
            :type transformations: list(poseutils.datasets.transformation.Transformation)
        """

        for transformation in transformations:

            if isinstance(transformation, CalculateMetrics):
                self.calculate_metrics()
            else:
                self._data_train["3d"] = transformation(self._data_train["3d"], mean=self.means["3d"], std=self.stds["3d"])
                self._data_valid["3d"] = transformation(self._data_valid["3d"], mean=self.means["3d"], std=self.stds["3d"])

    def get_2d_train(self):
        """Returns 2d training data

            :return: Joint positions 2d (NxMx2), M = 14 or 16
            :rtype: numpy.ndarray
        """

        return self._data_train['2d']

    def get_2d_valid(self):
        """Returns 2d validation data

            :return: Joint positions 2d (NxMx2), M = 14 or 16
            :rtype: numpy.ndarray
        """
        
        return self._data_valid['2d']

    def get_3d_train(self):
        """Returns 3d training data

            :return: Joint positions 3d (NxMx3), M = 14 or 16
            :rtype: numpy.ndarray
        """

        return self._data_train['3d']

    def get_3d_valid(self):
        """Returns 3d validation data

            :return: Joint positions 3d (NxMx3), M = 14 or 16
            :rtype: numpy.ndarray
        """

        return self._data_valid['3d']
