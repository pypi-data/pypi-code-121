from poseutils.logger import log
from poseutils.transform import root_center
from poseutils.datasets.transformation.Transformation import Transformation

class RootCenter(Transformation):
    """Subtracts the root/hip position from the rest of the joints

        :param root_idx: Root/hip index, defaults to 0
        :type root_idx: int, optional
    """

    def __init__(self, root_idx=0):
        super(RootCenter, self).__init__()

        self.root_idx = root_idx

    def __call__(self, X, **kwds):
        """Applies tranfrormation

            :param X: Joint positions (NxMxI), M = 14 or 16, I = 2 or 3
            :type X: numpy.ndarray
            :return: Root/hip centered joint positions (NxMxI)
            :rtype: numpy.ndarray
        """

        log("Applying root centering")
        
        return root_center(X, self.root_idx)