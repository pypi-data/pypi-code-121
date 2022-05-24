import numpy as np

from poseutils.logger import log
from poseutils.transform import normalize_zscore
from poseutils.datasets.transformation.Transformation import Transformation

class Normalize(Transformation):
    """Applies z-score normalize transformation on the data.

        :param skip_root: Whether to skip root/hip, defaults to True
        :type skip_root: bool, optional
    """

    def __init__(self, skip_root=True):
        super(Normalize, self).__init__()

        self.skip_root = skip_root

    def __call__(self, X, mean, std, **kwds):
        """Applies transformation

            .. math::

                \\hat{\\bm{X}} = \\frac{\\bm{X} - \\bm{\\mu}}{\\bm{\\sigma}}

            :param X: Joint positions (NxMxI), M = 14 or 16, I = 2 or 3
            :type X: numpy.ndarray
            :param mean: Mean values to use when normalizing (MxI)
            :type mean: numpy.ndarray
            :param std: Standard deviation values to use when normalizing (MxI)
            :type std: numpy.ndarray
            :return: Transformed joint positions (NxMx2), M = 14 or 16
            :rtype: numpy.ndarray
        """

        log("Normalizing")

        return normalize_zscore(X, mean, std, self.skip_root)