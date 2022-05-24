import numpy as np

from poseutils.logger import log
from poseutils.composite import scale_into_bounding_box_2d
from poseutils.datasets.transformation.Transformation import Transformation

class CropAndScale(Transformation):
    """Class to apply crop and scale transformation. Makes call to `poseutils.composite.scale_into_bounding_box_2d`.

        :param low: Lowest value of the bounding box range, defaults to 0
        :type low: int, optional
        :param high: Highest value of the bounding box range, defaults to 256
        :type high: int, optional
    """

    def __init__(self, low=0, high=256, *args, **kwds):
        super(CropAndScale, self).__init__()

        self.low = low
        self.high = high

    def __call__(self, X, **kwds):
        """Applies transformation

            :param X: Joint positions (NxMx2), M = 14 or 16
            :type X: numpy.ndarray
            :return: Scaled joint positions (NxMx2), M = 14 or 16
            :rtype: numpy.ndarray
        """

        log("Applying crop and scale")

        return scale_into_bounding_box_2d(X, self.low, self.high)