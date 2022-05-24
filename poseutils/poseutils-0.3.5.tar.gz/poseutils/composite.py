import numpy as np
from poseutils.props import get_bounding_box_2d
from poseutils.transform import scale_bounding_area_to

def scale_into_bounding_box_2d(joints, low=0, high=256):
    """Composite function to do cropping and scaling in one routine. Given an array of joint positions, it first extracts bounding box information. Then uses it to scale up/down in range [low, high] while preserving aspect ratio.

        :param joints: Positions of joints (NxMx2), where M = 14 or 16
        :type joints: numpy.ndarray
        :param low: Lowest coordinate of the bounding box, defaults to 0
        :type low: int, optional
        :param high: Highest coordinates of the bounding box, defaults to 256
        :type high: int, optional
        :return: Scaled joint positions (NxMx2), where M = 14 or 16
        :rtype: numpy.ndarray
    """

    lx, ly, rx, ry = get_bounding_box_2d(joints)
    stacked_bbox = np.vstack((lx, ly, rx, ry)).T
    joints_scaled = scale_bounding_area_to(joints, stacked_bbox, low, high)

    return joints_scaled