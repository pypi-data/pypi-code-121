import torch
import numpy as np

__all__ = ["mpjpe", "p_mpjpe", "n_mpjpe", "weighted_mpjpe", "mean_per_vertex_error"]


def mpjpe(predicted, target):
    """
    Mean per-joint position error (i.e. mean Euclidean distance),
    often referred to as "Protocol #1" in many papers.
    """
    assert predicted.shape == target.shape
    return torch.mean(torch.norm(predicted - target, dim=-1))


def weighted_mpjpe(predicted, target, w):
    """
    Weighted mean per-joint position error (i.e. mean Euclidean distance)
    """
    assert predicted.shape == target.shape
    assert w.shape[0] == predicted.shape[0]
    return torch.mean(w * torch.norm(predicted - target, dim=-1))

def mean_per_vertex_error(pred, gt, has_smpl):
    """
    Compute mPVE
    """
    pred = pred[has_smpl == 1]
    gt = gt[has_smpl == 1]
    with torch.no_grad():
        error = torch.sqrt( ((pred - gt) ** 2).sum(dim=-1)).mean(dim=-1).cpu().numpy()
        return error

def p_mpjpe(predicted, target):
    """
    Pose error: MPJPE after rigid alignment (scale, rotation, and translation),
    often referred to as "Protocol #2" in many papers.
    """
    assert predicted.shape == target.shape
    assert len(predicted.shape) == 3
    assert type(predicted) is np.ndarray
    assert type(target) is np.ndarray

    muX = np.mean(target, axis=1, keepdims=True)
    muY = np.mean(predicted, axis=1, keepdims=True)

    X0 = target - muX
    Y0 = predicted - muY

    normX = np.sqrt(np.sum(X0 ** 2, axis=(1, 2), keepdims=True))
    normY = np.sqrt(np.sum(Y0 ** 2, axis=(1, 2), keepdims=True))

    X0 /= normX
    Y0 /= normY

    H = np.matmul(X0.transpose(0, 2, 1), Y0)
    U, s, Vt = np.linalg.svd(H)
    V = Vt.transpose(0, 2, 1)
    R = np.matmul(V, U.transpose(0, 2, 1))

    # Avoid improper rotations (reflections), i.e. rotations with det(R) = -1
    sign_detR = np.sign(np.expand_dims(np.linalg.det(R), axis=1))
    V[:, :, -1] *= sign_detR
    s[:, -1] *= sign_detR.flatten()
    R = np.matmul(V, U.transpose(0, 2, 1))  # Rotation

    tr = np.expand_dims(np.sum(s, axis=1, keepdims=True), axis=2)

    a = tr * normX / normY  # Scale
    t = muX - a * np.matmul(muY, R)  # Translation

    # Perform rigid transformation on the input
    predicted_aligned = a * np.matmul(predicted, R) + t

    # Return MPJPE
    return np.mean(
        np.linalg.norm(predicted_aligned - target, axis=len(target.shape) - 1)
    )


def n_mpjpe(predicted, target):
    """
    Normalized MPJPE (scale only), adapted from:
    https://github.com/hrhodin/UnsupervisedGeometryAwareRepresentationLearning/blob/master/losses/poses.py

    https://github.com/facebookresearch/VideoPose3D/blob/master/common/loss.py
    """
    assert predicted.shape == target.shape

    # only support len(predicted.shape)=4
    # norm_predicted = torch.mean(
    # torch.sum(predicted**2, dim=3, keepdim=True), dim=2, keepdim=True)
    # norm_target = torch.mean(
    # torch.sum(target*predicted, dim=3, keepdim=True), dim=2, keepdim=True)

    # can support len(predicted.shape) >= 2
    norm_predicted = torch.mean(
        torch.sum(predicted ** 2, dim=-1, keepdim=True), dim=-2, keepdim=True
    )
    norm_target = torch.mean(
        torch.sum(target * predicted, dim=-1, keepdim=True), dim=-2, keepdim=True
    )

    scale = norm_target / norm_predicted
    return mpjpe(scale * predicted, target)


def mean_velocity_error(predicted, target):
    """
    Mean per-joint velocity error (i.e. mean Euclidean distance of the 1st derivative)
    """
    assert predicted.shape == target.shape

    velocity_predicted = np.diff(predicted, axis=0)
    velocity_target = np.diff(target, axis=0)

    return np.mean(
        np.linalg.norm(velocity_predicted - velocity_target, axis=len(target.shape) - 1)
    )


def estimate_pose(points_static, points_to_transform):
    # pdb.set_trace()
    p0 = np.copy(points_static).T
    p1 = np.copy(points_to_transform).T

    t0 = -np.mean(p0, axis=1).reshape(3, 1)
    t1 = -np.mean(p1, axis=1).reshape(3, 1)

    p0c = p0 + t0
    p1c = p1 + t1

    covariance_matrix = p0c.dot(p1c.T)
    U, S, V = np.linalg.svd(covariance_matrix)
    R = U.dot(V)
    if np.linalg.det(R) < 0:
        R[:, 2] *= -1

    rms_d0 = np.sqrt(np.mean(np.linalg.norm(p0c, axis=0) ** 2))
    rms_d1 = np.sqrt(np.mean(np.linalg.norm(p1c, axis=0) ** 2))

    s = rms_d0 / rms_d1
    P = s * np.eye(3).dot(R)

    t_final = P.dot(t1) - t0
    P = np.c_[P, t_final]

    return P


def face_nme(pre_pose_3d, gt_pose_3d, has_3d=None):
    assert pre_pose_3d.shape == gt_pose_3d.shape
    bs = pre_pose_3d.shape[0]

    bs_pre_points = pre_pose_3d.detach().cpu().numpy()
    bs_gt_points = gt_pose_3d.detach().cpu().numpy()

    pose_align_idx = [52, 55, 58, 61, 46, 84, 90]
    full_errors = []
    inner_face_errors = []
    for i in range(bs):
        if has_3d is not None:
            if has_3d[i] == 0.0:
                full_errors.append(0.0)
                inner_face_errors.append(0.0)
                continue

        pre_points = bs_pre_points[i]
        gt_points = bs_gt_points[i]

        Proj = estimate_pose(
            gt_points[pose_align_idx, :], pre_points[pose_align_idx, :]
        )
        pre_points = np.hstack((pre_points, np.ones((pre_points.shape[0], 1))))
        aligned_pre_points = Proj.dot(pre_points.T)
        aligned_pre_points = aligned_pre_points.T
        ## error
        # pdb.set_trace()
        errors = np.linalg.norm(aligned_pre_points - gt_points, axis=1)
        interocular_distance = np.linalg.norm(gt_points[74] - gt_points[77])
        full_errors.append(np.sum(errors) / (106 * interocular_distance))
        inner_face_errors.append(np.sum(errors[33:]) / (73 * interocular_distance))

    full_errors = float(np.mean(np.array(full_errors)))
    inner_face_errors = float(np.mean(np.array(inner_face_errors)))

    return full_errors, inner_face_errors
