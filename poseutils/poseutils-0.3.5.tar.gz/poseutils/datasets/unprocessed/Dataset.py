from __future__ import print_function, absolute_import, division

import numpy as np
from poseutils.constants import dataset_indices

class Dataset(object):
    """Unprocessed dataset base class. Contains common methods shared across all dataset classes.
    """

    def __init__(self, dataset_name):
        super(Dataset, self).__init__()

        self.dataset_name = dataset_name

        self.cameras = None

        self._data_train = { "2d": None, "3d": None, "raw": None }
        self._data_valid = { "2d": None, "3d": None, "raw": None }

    def get_2d_valid(self, jnts=14):
        """Returns 2d valid data.

            :param jnts: Joint configuration (14 or 16), defaults to 14
            :type jnts: int, optional
            :return: Selected and sorted joint positions (NxMx2), M = 14 or 16
            :rtype: numpy.ndarray
        """

        to_select, to_sort = dataset_indices(self.dataset_name, jnts)

        return self._data_valid['2d'][:, to_select, :][:, to_sort, :]

    def get_3d_valid(self, jnts=14):
        """Returns 3d valid data.

            :param jnts: Joint configuration (14 or 16), defaults to 14
            :type jnts: int, optional
            :return: Selected and sorted joint positions (NxMx3), M = 14 or 16
            :rtype: numpy.ndarray
        """

        to_select, to_sort = dataset_indices(self.dataset_name, jnts)

        return self._data_valid['3d'][:, to_select, :][:, to_sort, :]
    
    def get_2d_train(self, jnts=14):
        """Returns 2d train data.

            :param jnts: Joint configuration (14 or 16), defaults to 14
            :type jnts: int, optional
            :return: Selected and sorted joint positions (NxMx2), M = 14 or 16
            :rtype: numpy.ndarray
        """

        to_select, to_sort = dataset_indices(self.dataset_name, jnts)

        return self._data_train['2d'][:, to_select, :][:, to_sort, :]

    def get_3d_train(self, jnts=14):
        """Returns 3d train data.

            :param jnts: Joint configuration (14 or 16), defaults to 14
            :type jnts: int, optional
            :return: Selected and sorted joint positions (NxMx3), M = 14 or 16
            :rtype: numpy.ndarray
        """

        to_select, to_sort = dataset_indices(self.dataset_name, jnts)

        return self._data_train['3d'][:, to_select, :][:, to_sort, :]