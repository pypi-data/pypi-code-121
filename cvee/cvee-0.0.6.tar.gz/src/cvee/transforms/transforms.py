from typing import Union

import numpy as np
import torch

from cvee.types import ArrayOrTensor


# TODO: change the order of parameters
def transform(
    pts: Union[np.ndarray, torch.Tensor], tf_mat: Union[np.ndarray, torch.Tensor]
) -> Union[np.ndarray, torch.Tensor]:
    """
    Apply a transformation matrix on a set of 3D points.

    Args:
        pts (np.ndarray, torch.Tensor): 3D points, could be Nx3 or BxNx3.
        tf_mat (np.ndarray, torch.Tensor): Transformation matrix, could be 4x4 or Bx4x4.
        The types of tf_mat and pts should be consistent.
        pts and tf_mat should be in the batch version at the same time, i.e., it's invalid for Nx3 pts and Bx4x4 tf_mat.

    Returns:
        Transformed pts. Return torch.Tensor if matrix or points are torch.Tensor, else np.ndarray.
    """
    return_tensor = isinstance(tf_mat, torch.Tensor) or isinstance(pts, torch.Tensor)

    if not return_tensor:
        padding = np.ones(pts.shape[:-1] + (1,), dtype=pts.dtype)
        homo_pts = np.concatenate([pts, padding], axis=-1)
        # `homo_pts @ tf_mat.T` or `(tf_mat @ homo_pts.T).T`
        new_pts = np.matmul(homo_pts, np.swapaxes(tf_mat, -2, -1))
        new_pts = new_pts[..., :3]
    else:
        padding = torch.ones(pts.shape[:-1] + (1,), dtype=pts.dtype, device=pts.device)
        homo_pts = torch.cat([pts, padding], dim=-1)
        new_pts = torch.matmul(homo_pts, torch.transpose(tf_mat, -2, -1))
        new_pts = new_pts[..., :3]
    return new_pts


def rotate(
    pts: Union[np.ndarray, torch.Tensor], rot_mat: Union[np.ndarray, torch.Tensor]
) -> Union[np.ndarray, torch.Tensor]:
    """Apply a rotation matrix on a set of 3D points.

    Args:
        pts (np.ndarray, torch.Tensor): 3D points, could be Nx3 or BxNx3.
        rot_mat (np.ndarray, torch.Tensor): Rotation matrix, could be 3x3 or Bx3x3.

        The types of rot_mat and pts should be consistent.
        pts and rot_mat should be in the batch version at the same time,
            i.e., it's invalid for Nx3 pts and Bx4x4 rot_mat.
    Returns:
        Rotated pts. Return torch.Tensor if matrix or points are torch.Tensor, else np.ndarray.
    """
    return_tensor = isinstance(rot_mat, torch.Tensor) or isinstance(pts, torch.Tensor)
    if not return_tensor:
        # `pts @ tf_mat.T` or `(tf_mat @ pts.T).T`
        new_pts = np.matmul(pts, np.swapaxes(rot_mat, -2, -1))
    else:
        new_pts = torch.matmul(pts, torch.transpose(rot_mat, -2, -1))
    return new_pts


# TODO: write test cases
# TODO: add 4 x 4 input
def project(pts, intr_mat):
    """Project 3D points in the camera space to the image plane. Note that this function is not differentiable.

    Args:
        pts (np.ndarray, torch.Tensor): 3D points, could be Nx3 or BxNx3 (tensor only).
        intr_mat (np.ndarray, torch.Tensor): Intrinsic matrix, could be 3x3 or Bx3x3 (tensor only).

        The types of pts and intr_mat should be consistent.
    Returns:
        pixels, the order is uv other than xy.
        depth, depth in the camera space.
    """
    return_tensor = isinstance(intr_mat, torch.Tensor) or isinstance(pts, torch.Tensor)

    if not return_tensor:  # return np.ndarray
        pts = pts / pts[:, 2:3]
        new_pts = np.dot(intr_mat, pts.T).T
        return new_pts[:, :2]
    else:  # return torch.tensor
        if intr_mat.ndim == 2 and pts.ndim == 2:
            pts = pts.clone()
            pts = pts / pts[:, 2:3]
            new_pts = torch.mm(pts, torch.transpose(intr_mat, 0, 1))
            return new_pts[:, :2]
        elif intr_mat.ndim == 3 and pts.ndim == 3:
            pts = pts.clone()
            pts = pts / pts[..., 2:3]
            new_pts = torch.bmm(pts, torch.transpose(intr_mat, 1, 2))
            return new_pts[..., :2]
        else:
            raise RuntimeError(f"Incorrect size of intr_mat or pts: {intr_mat.shape}, {pts.shape}")


# TODO: implement this
def unproject():
    raise NotImplementedError()


# Ref: https://math.stackexchange.com/a/1315407/757569
def inverse(rot_or_tf_mat: ArrayOrTensor) -> ArrayOrTensor:
    if isinstance(rot_or_tf_mat, np.ndarray):
        if rot_or_tf_mat.shape[-1] == 3:
            new_mat = np.swapaxes(rot_or_tf_mat, -2, -1)
        else:
            new_mat = rot_or_tf_mat.copy()
            new_mat[..., :3, :3] = np.swapaxes(rot_or_tf_mat[..., :3, :3], -2, -1)
            if new_mat.ndim == 2:
                # reuse transpose rot here
                new_mat[:3, 3] = -rotate(new_mat[:3, 3], new_mat[:3, :3])
            else:
                new_mat[..., :3, 3] = -rotate(new_mat[..., None, :3, 3], new_mat[..., :3, :3]).squeeze(-2)
        return new_mat
    elif isinstance(rot_or_tf_mat, torch.Tensor):
        if rot_or_tf_mat.shape[-1] == 3:
            new_mat = torch.transpose(rot_or_tf_mat, -2, -1)
        else:
            new_mat = rot_or_tf_mat.clone()
            new_mat[..., :3, :3] = torch.transpose(rot_or_tf_mat[..., :3, :3], -2, -1)
            if new_mat.ndim == 2:
                # reuse transpose rot here
                new_mat[:3, 3] = -rotate(new_mat[:3, 3], new_mat[:3, :3])
            else:
                new_mat[..., :3, 3] = -rotate(new_mat[..., None, :3, 3], new_mat[..., :3, :3]).squeeze(-2)
        return new_mat
    else:
        raise TypeError(f"rot_or_tf_mat should be np.ndarray or torch.Tensor, but got {type(rot_or_tf_mat)}")


# Ref: https://www.scratchapixel.com/lessons/mathematics-physics-for-computer-graphics/geometry/row-major-vs-column-major-vector
def swap_major(rot_or_tf_mat: ArrayOrTensor) -> ArrayOrTensor:
    if isinstance(rot_or_tf_mat, np.ndarray):
        return np.swapaxes(rot_or_tf_mat, -2, -1)
    elif isinstance(rot_or_tf_mat, torch.Tensor):
        return torch.transpose(rot_or_tf_mat, -2, -1)
    else:
        raise TypeError(f"rot_or_tf_mat should be np.ndarray or torch.Tensor, but got {type(rot_or_tf_mat)}")


def rot_tl_to_tf_mat(rot_mat: ArrayOrTensor, tl: ArrayOrTensor = None) -> ArrayOrTensor:
    """Build transformation matrix with rotation matrix and translation vector.

    Args:
        rot_mat (np.ndarray, torch.Tensor): rotation matrix, could be (..., 3, 3)
        tl (np.ndarray, torch.Tensor): translation vector, could be (..., 3). If None, translation will be 0.
        The types of rot_mat and tl should be consistent.
    Returns:
        tf_mat, transformation matrix. Return torch.Tensor if rot_mat and tl are torch.Tensor, else np.ndarray.
    """
    if isinstance(rot_mat, np.ndarray):
        # not np.repeat()
        tf_mat = np.tile(np.eye(4, dtype=rot_mat.dtype), rot_mat.shape[:-2] + (1, 1))
        tf_mat[..., :3, :3] = rot_mat
        if tl is not None:
            tf_mat[..., :3, 3] = tl
        return tf_mat
    elif isinstance(rot_mat, torch.Tensor):
        # not expand()
        tf_mat = torch.eye(4, device=rot_mat.device, dtype=rot_mat.dtype).repeat(rot_mat.shape[:-2] + (1, 1))
        tf_mat[..., :3, :3] = rot_mat
        if tl is not None:
            tf_mat[..., :3, 3] = tl
        return tf_mat
    else:
        raise TypeError(f"rot_mat should be np.ndarray or torch.Tensor, but got {type(rot_mat)}")


# TODO: write test cases
def cart_to_homo(pts_3d):
    """Convert Cartesian 3D points to Homogeneous 4D points.

    Args:
      pts_3d (np.ndarray, torch.Tensor): 3D points in Cartesian coord, could be Nx3 or BxNx3 (tensor only).
    Returns:
      nx4 points in Homogeneous coord.
    """
    if isinstance(pts_3d, torch.Tensor):  # return np.ndarray
        return np.concatenate([pts_3d, np.ones([pts_3d.shape[0], 1])], axis=1)
    else:
        if pts_3d.ndim == 2:
            return torch.cat([pts_3d, torch.ones(pts_3d.shape[0], 1).to(pts_3d.device)], dim=1)
        else:
            padding = torch.ones(pts_3d.shape[0], pts_3d.shape[1], 1).to(pts_3d.device)
            return torch.cat([pts_3d, padding], dim=2)
