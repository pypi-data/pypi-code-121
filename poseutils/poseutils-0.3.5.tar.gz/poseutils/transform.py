import numpy as np
from poseutils.constants import *

def root_center(X, root_idx=0):
    """Subtract the value at root index to make the coordinates center around root. Useful for hip-centering the skeleton.

        :param X: Position of joints (NxMx2) or (NxMx3)
        :type X: numpy.ndarray
        :param root_idx: Root/Hip index, defaults to 0
        :type root_idx: int, optional
        :return: New position of joints (NxMx2) or (NxMx3)
        :rtype: numpy.ndarray
    """

    assert len(X.shape) == 3 or len(X.shape) == 2

    if len(X.shape) == 3:
        return X - X[:, root_idx:root_idx+1, :]
    else:
        return X - X[root_idx:root_idx+1, :]

def normalize_zscore(X, mean, std, skip_root=False):
    """Normalize position of joints using z-score normalization. Subtracts mean and divides by standard devation. Metrics are ideally collected from the training set.

        :param X: Position of joints (NxMx2) or (NxMx3)
        :type X: numpy.ndarray
        :param mean: Mean joint position (Mx2) or (Mx3)
        :type mean: numpy.ndarray
        :param std: Standard deviation of joint positions (Mx2) or (Mx3)
        :type std: [type]
        :param skip_root: Whether to skip over the root/hip when normalizing, defaults to False
        :type skip_root: bool, optional
        :return: New position of joints (NxMx2) or (NxMx3)
        :rtype: numpy.ndarray
    """

    for i in range(X.shape[0]):
        if not skip_root:
            X[i, :] = np.divide(X[i, :] - mean[:], std[:])
        else:
            X[i, 1:] = np.divide(X[i, 1:] - mean[1:], std[1:])
    
    return X

def unnormalize_zscore(X, mean, std, skip_root=False):
    """Reverses normalized position of joints using z-score normalization. Multiplies by standard devation and adds the mean. Metrics are ideally collected from the training set.

        :param X: Position of joints (NxMx2) or (NxMx3)
        :type X: numpy.ndarray
        :param mean: Mean joint position (Mx2) or (Mx3)
        :type mean: numpy.ndarray
        :param std: Standard deviation of joint positions (Mx2) or (Mx3)
        :type std: [type]
        :param skip_root: Whether to skip over the root/hip when unnormalizing, defaults to False
        :type skip_root: bool, optional
        :return: New position of joints (NxMx2) or (NxMx3)
        :rtype: numpy.ndarray
    """

    XX = np.zeros(X.shape)

    for i in range(X.shape[0]):
        if not skip_root:
            XX[i, :] = np.multiply(X[i, :], std[:]) + mean[:]
        else:
            XX[i, 1:] = np.multiply(X[i, 1:], std[1:]) + mean[1:]

    return XX

def scale_bounding_area_to(X, bbox, low=0, high=256):
    """Scales up or down the bounding box enclosed region to fit in a (high-low) sided square while preserving aspect ratio.

        :param X: Position of joints (NxMx2)
        :type X: numpy.ndarray
        :param bbox: Bounding box coordinates (Nx4) where columns are stacked as [lx, ly, rx, ry]. (lx, ly) is the coordinate for top-left corner whereas (rx, ry) is the coordinate of the bottom-right corner 
        :type bbox: numpy.ndarray
        :param low: Lowest value of the bounding box, defaults to 0
        :type low: int, optional
        :param high: Highest value of the bounding box, defaults to 256
        :type high: int, optional
        :return: New position of joints (NxMx2)
        :rtype: numpy.ndarray
    """

    assert len(X.shape) == 3
    assert X.shape[-1] == 2
    assert bbox.shape[-1] == 4

    half_max = (high - low)/2

    half_width = (bbox[:, 2] - bbox[:, 0])/2
    half_height = (bbox[:, 3] - bbox[:, 1])/2

    X_new = X - bbox[:, :2].reshape((-1, 1, 2))

    for i in range(X.shape[0]):
        
        scale_x = 1.0
        scale_y = 1.0

        offset_x = 0
        offset_y = 0

        if half_width[i] > half_height[i]:
            scale_x = half_max / half_width[i]
            scale_y = (half_height[i] / half_width[i]) * scale_x
            offset_y = half_max - half_height[i] * scale_y
        else:
            scale_y = half_max / half_height[i]
            scale_x = (half_width[i] / half_height[i]) * scale_y
            offset_x = half_max - half_width[i] * scale_x

        X_new[i, :, 0] = X_new[i, :, 0] * scale_x + offset_x
        X_new[i, :, 1] = X_new[i, :, 1] * scale_y + offset_y

    return X_new

def normalize_torso_2d(torso):
    """Takes in the torso coordinates and normalizes it. Takes the distance of each torso joint from the Right Hip joint position. Each distance is then normalized with the distance along the diagonal connecting Right Hip to Left Shoulder. A small value is added to the diagonal distance to avoid divide-by-zero error.

        :param torso: Torso joint positions (Nx4x2), with arranged in order: Right Hip, Left Hip, Left Shoulder, Right Shoulder
        :type torso: numpy.ndarray
        :return:
            - New torso positions (Nx4x2)
            - Width of right hip to left hip, right hip to left shoulder, right hip to right shoulder (Nx3)
            - List of names of the widths
        :rtype: tuple(numpy.narray, numpy.ndarray, list(str))
    """
    #0: RH 1: LH 2: LS 3: RS

    assert len(torso.shape) == 3
    assert torso.shape[1] == 4 and torso.shape[-1] == 2

    torso_ = torso.copy()
    
    widths = [[], [], []]
    names = ["RH -> LH", "RH -> LS", "RH -> RS"]

    torso1_4u = torso_[:, 1, :] - torso_[:, 0, :]
    torso1_8u = torso_[:, 2, :] - torso_[:, 0, :]
    torso1_11u = torso_[:, 3, :] - torso_[:, 0, :]

    torso1_4l = np.linalg.norm(torso1_4u, axis=1).reshape(-1, 1)
    torso1_8l = np.linalg.norm(torso1_8u, axis=1).reshape(-1, 1)
    torso1_11l = np.linalg.norm(torso1_11u, axis=1).reshape(-1, 1)

    torso1_4u = torso1_4u / torso1_4l
    torso1_8u = torso1_8u / torso1_8l
    torso1_11u = torso1_11u / torso1_11l
    
    torso_[:, 0, :] = np.zeros((torso_.shape[0], 2))
    torso_[:, 1, :] = (torso1_4l / torso1_8l+1e-8)*torso1_4u
    torso_[:, 2, :] = torso1_8u
    torso_[:, 3, :] = (torso1_11l / torso1_8l+1e-8)*torso1_11u
    
    widths[0].append(torso1_4l)
    widths[1].append(torso1_8l)
    widths[2].append(torso1_11l)

    return torso_, np.array(widths), names

def normalize_skeleton(joints):
    """Normalizes joint positions (NxMx2 or NxMx3, where M is 14 or 16) from parent to child order. Each vector from parent to child is normalized with respect to it's length.

        :param joints: Position of joints (NxMx2) or (NxMx3)
        :type joints: numpy.ndarray
        :return: Normalzed position of joints (NxMx2) or (NxMx3)
        :rtype: numpy.ndarray
    """

    assert len(joints.shape) == 3
    assert joints.shape[1] == 14 or joints.shape[1] == 16
    assert joints.shape[-1] == 2 or joints.shape[-1] == 3

    hip = 0

    if joints.shape[1] == 14:
        names = NAMES_14
    else:
        names = NAMES_16
    
    neck = names.index('Neck')

    joints_ = joints.copy()
    joints_ -= joints_[:, :1, :]

    spine = joints_[:, neck, :] - joints_[:, hip, :]
    spine_norm = np.linalg.norm(spine, axis=1).reshape(-1, 1)

    adjacency = adjacency_list(joints_.shape[1])

    queue = []

    queue.append(0)

    while len(queue) > 0:
        current = queue.pop(0)

        for child in adjacency[current]:
            queue.append(child)
            prnt_to_chld = joints[:, child, :] - joints[:, current, :]
            prnt_to_chld_norm = np.linalg.norm(prnt_to_chld, axis=1).reshape(-1, 1)
            prnt_to_chld_unit = prnt_to_chld / prnt_to_chld_norm
            joints_[:, child, :] = joints_[:, current, :] + (prnt_to_chld_unit * (prnt_to_chld_norm / (spine_norm + 1e-8)))

    return joints_