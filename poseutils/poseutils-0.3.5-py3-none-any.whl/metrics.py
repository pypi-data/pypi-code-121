import numpy as np

def calculate_jpe(pred, target):
    """Given prediction and ground truth 3d position calculates joint position error.

        :param pred: Predicted 3d joint positions (NxMx3), where M = 14 or 16
        :type pred: numpy.ndarray
        :param target: Ground truth 3d joint positions (NxMx3), where M = 14 or 16
        :type target: numpy.ndarray
        :return:
            - MPJPE: Mean per joint position error
            - PJPE: Per joint position error (Mx1)
            - PPJPE: Per point joint position error (Nx1)
        :rtype: tuple(float, numpy.ndarray, numpy.ndarray)
    """

    assert pred.shape == target.shape
    assert pred.shape[1] == 14 or pred.shape[1] == 16

    target_ = target.copy()
    pred_ = pred.copy()

    target_ -= target_[:, :1, :]
    
    sqerr = (pred_ - target_)**2
    dists = np.zeros((sqerr.shape[0], pred.shape[1]))

    dist_idx = 1
    for k in range(1, pred.shape[1]):
        dists[:, dist_idx] = np.sqrt(np.sum(sqerr[:, k, :], axis=1))
        dist_idx += 1
    
    mpjpe = np.mean(dists)
    pjpe = np.mean(dists, axis=0)
    ppmjpe = np.mean(dists, axis=1)

    return mpjpe, pjpe, ppmjpe, dists