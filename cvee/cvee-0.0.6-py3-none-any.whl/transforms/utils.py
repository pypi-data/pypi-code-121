import math
from typing import Union

import numpy as np
import torch
import torch.nn.functional as F

from cvee.transforms import rot_tl_to_tf_mat
from cvee.types import ArrayOrTensor, ArrayLikeOrTensor, ArrayLike

common_coords = {
    "opencv": "x: right, y: down, z: front",
    "opengl": "x: right, y: up, z: back",
    "pytorch3d": "x: left, y: up, z: front",
}


def coord_conversion(
    rule: str = "opencv -> opengl", return_tensor: bool = False, check_handness: bool = True
) -> ArrayOrTensor:
    """
    Construct a rotation matrix based on a given rule.

    Following rules are equivalent:
        - "x: right, y: down, z: front -> x: right, y: up, z: back"
        - "right, down, front -> right, up, back"
        - "opencv -> opengl"
        - "x, -y, -z"

    Args:
        rule: rule string
        return_tensor: if True return torch.Tensor, else return np.ndarray
        check_handness: if True check if the handness of the rotation matrix is correct

    Returns:
        rot_mat
    """
    if "->" in rule:
        # replace_list = [("backward", "back"), ("forward", "front")]
        # rule = [rule.replace(*item) for item in replace_list][0]
        coords = rule.split("->")
        coords = [coord.strip().lower() for coord in coords]
        coords = [common_coords.get(coord, coord) for coord in coords]

        for idx, coord in enumerate(coords):
            if "x" in coord:
                dirs = {item.split(":")[0]: item.split(":")[1] for item in coord.split(",")}
                dirs = {k.strip(): v.strip() for k, v in dirs.items()}
                dirs = [dirs[axis] for axis in ["x", "y", "z"]]
                coords[idx] = dirs
            else:
                coords[idx] = [x.strip() for x in coord.split(",")]

        src_coord, dst_coord = coords

        opp_dirs = {"left": "right", "right": "left", "up": "down", "down": "up", "front": "back", "back": "front"}
        src_axes = [
            "xyz"[src_coord.index(dir)] if dir in src_coord else "-" + "xyz"[src_coord.index(opp_dirs[dir])]
            for dir in dst_coord
        ]
    else:
        src_axes = rule.split(",")
        src_axes = [axis.strip().lower() for axis in src_axes]

    negs = [-1 if "-" in axis else 1 for axis in src_axes]
    axes = ["xyz".index(axis.replace("-", "")) for axis in src_axes]
    rot_mat = np.zeros((3, 3), np.float32)
    rot_mat[np.arange(3), axes] = negs

    if check_handness:
        if np.linalg.det(rot_mat) < 0:
            raise RuntimeWarning("The rotation matrix is not right-hand.")

    if return_tensor:
        return torch.from_numpy(rot_mat)
    else:
        return rot_mat


# Ref: https://github.com/facebookresearch/pytorch3d/blob/main/pytorch3d/renderer/cameras.py
def camera_position_from_spherical_angles(
    distance: ArrayLikeOrTensor, elevation: ArrayLikeOrTensor, azimuth: ArrayLikeOrTensor, degrees: bool = True
) -> ArrayOrTensor:
    """
    Calculate the location of the camera based on the distance away from
    the target point, the elevation and azimuth angles.

    We use the OpenGL coordinate in this function, i.e. x -> right, y -> up, z -> backward.
    The azimuth reference direction is +z, i.e. distance: 1, elevation: 0, azimuth: 0 -> pos: (0, 0, 1).

    The inputs distance, elevation and azimuth can be one of the following:
        - int float, tuple or list
        - numpy array of any shape
        - torch tensor of any shape

    Args:
        distance: distance of the camera from the origin.
        elevation: angle between the camera-origin segment and the bottom (x-z) plane.
        azimuth: signed angle between the azimuth reference direction (+z) and the orthogonal projection of
            the camera-origin segment on the bottom (x-z) plane. The positive direction of azimuth is counterclockwise.
        degrees: bool, whether the angles are specified in degrees or radians.
    Returns:
        camera_position (np.ndarray or torch.tensor): (3) or (..., 3) xyz location of the camera.
    """
    if isinstance(distance, ArrayLike.__args__):
        distance, elevation, azimuth = np.asarray(distance), np.asarray(elevation), np.asarray(azimuth)
        if degrees:
            elevation = np.pi / 180.0 * elevation
            azimuth = np.pi / 180.0 * azimuth

        x = distance * np.cos(elevation) * np.sin(azimuth)
        y = distance * np.sin(elevation)
        z = distance * np.cos(elevation) * np.cos(azimuth)
        return np.stack([x, y, z], axis=-1)
    elif isinstance(distance, torch.Tensor):
        if degrees:
            elevation = math.pi / 180.0 * elevation
            azimuth = math.pi / 180.0 * azimuth

        x = distance * torch.cos(elevation) * torch.sin(azimuth)
        y = distance * torch.sin(elevation)
        z = distance * torch.cos(elevation) * torch.cos(azimuth)
        return torch.stack([x, y, z], dim=-1)
    else:
        raise TypeError(f"parameters should be np.ndarray, torch.Tensor, list or number, but got {type(distance)}")


# Ref: https://github.com/facebookresearch/pytorch3d/blob/main/pytorch3d/renderer/cameras.py
def look_at_rotation(
    camera_position: Union[list, tuple, ArrayOrTensor],
    at: Union[list, tuple, ArrayOrTensor] = (0, 0, 0),
    up: Union[list, tuple, ArrayOrTensor] = (0, 1, 0),
) -> ArrayOrTensor:
    """
    This function takes a vector `camera_position` which specifies the location of the camera in world coordinates and
    two vectors `at` and `up` which indicate the position of the object and the up directions of the world
    coordinate system respectively.

    The output is a rotation matrix representing the rotation from camera coordinates to world coordinates.

    We use the OpenGL coordinate in this function, i.e. x -> right, y -> up, z -> backward.
    Hence, z_axis: pos - at, x_axis: cross(up, z_axis), y_axis: cross(z_axis, x_axis)

    Note that our implementation differs from pytorch3d.
        1. our matrix is in the OpenGL coordinate
        2. our matrix is column-major
        3. our matrix is camera-to-world

    Args:
        camera_position: position of the camera in world coordinates
        at: position of the object in world coordinates
        up: vector specifying the up direction in the world coordinate frame.
    The input camera_position, at and up can each be a
        - 3 element tuple/list
        - np.ndarray of shape (3) or (N, 3)
        - torch.tensor of shape (3) or (N, 3)
    Returns:
        R: rotation matrices of shape (3, 3) or (N, 3, 3)
    """
    if isinstance(camera_position, ArrayLike.__args__):

        def _normalize(x):
            return x / np.clip(np.linalg.norm(x, axis=-1, keepdims=True), a_min=1e-5, a_max=None)

        pos = np.asarray(camera_position)
        at, up = np.asarray(at), np.asarray(up)
        at, up = np.broadcast_to(at, pos.shape), np.broadcast_to(up, pos.shape)

        z_axis = _normalize(pos - at)
        x_axis = _normalize(np.cross(up, z_axis, axis=-1))
        y_axis = _normalize(np.cross(z_axis, x_axis, axis=-1))

        is_close = np.isclose(x_axis, 0.0, atol=5e-3).all(axis=-1, keepdims=True)
        if is_close.any():
            replacement = _normalize(np.cross(y_axis, z_axis, axis=-1))
            x_axis = np.where(is_close, replacement, x_axis)
        rot_mat = np.concatenate((x_axis[..., None, :], y_axis[..., None, :], z_axis[..., None, :]), axis=-2)
        return rot_mat.swapaxes(-2, -1)
    if isinstance(camera_position, torch.Tensor):
        dtype, device = camera_position.dtype, camera_position.device
        at, up = torch.as_tensor(at, dtype=dtype, device=device), torch.as_tensor(up, dtype=dtype, device=device)
        at, up = torch.broadcast_to(at, camera_position.shape), torch.broadcast_to(up, camera_position.shape)

        z_axis = F.normalize(camera_position - at, eps=1e-5, dim=-1)
        x_axis = F.normalize(torch.cross(up, z_axis, dim=-1), eps=1e-5, dim=-1)
        y_axis = F.normalize(torch.cross(z_axis, x_axis, dim=-1), eps=1e-5, dim=-1)
        is_close = torch.isclose(x_axis, torch.tensor(0.0, dtype=dtype, device=device), atol=5e-3)
        is_close = is_close.all(dim=-1, keepdim=True)
        if is_close.any():
            replacement = F.normalize(torch.cross(y_axis, z_axis, dim=-1), eps=1e-5)
            x_axis = torch.where(is_close, replacement, x_axis)
        rot_mat = torch.cat((x_axis[..., None, :], y_axis[..., None, :], z_axis[..., None, :]), dim=-2)
        return rot_mat.transpose(-2, -1)
    else:
        msg = f"parameters should be np.ndarray, torch.Tensor or list, but got {type(camera_position)}"
        raise TypeError(msg)


# Ref: https://github.com/facebookresearch/pytorch3d/blob/main/pytorch3d/renderer/cameras.py
def look_at_view_transform(
    dist: ArrayLikeOrTensor = 1.0,
    elev: ArrayLikeOrTensor = 0.0,
    azim: ArrayLikeOrTensor = 0.0,
    degrees: bool = True,
    eye: Union[list, tuple, ArrayOrTensor] = None,
    at: Union[list, tuple, ArrayOrTensor] = (0, 0, 0),
    up: Union[list, tuple, ArrayOrTensor] = (0, 1, 0),
):
    """
    This function returns transformation matrix to apply the 'Look At' transformation
    from camera coordinates to world coordinates.

    We use the OpenGL coordinate in this function, i.e. x -> right, y -> up, z -> backward.

    Note that our implementation differs from pytorch3d.
        1. our matrix is in the OpenGL coordinate
        2. our matrix is column-major
        3. our matrix is camera-to-world

    `p_wld = tf_mat @ p_opengl_cam`

    References:
    1. https://www.scratchapixel.com

    Args:
        dist: distance of the camera from the object
        elev: angle in degrees or radians. This is the angle between the vector from the object to the camera,
            and the bottom plane (xz-plane).
        azim: angle in degrees or radians. The vector from the object to the camera is projected onto the bottom plane.
            azim is the angle between the projected vector and a reference vector at (0, 0, 1).
        dist, elev and azim can be of shape (1), (N).
        degrees: boolean flag to indicate if the elevation and azimuth angles are specified in degrees or radians.
        eye: the position of the camera(s) in world coordinates. If eye is not None,
            it will override the camera position derived from dist, elev, azim.
        up: the direction of the x axis in the world coordinate system.
        at: the position of the object(s) in world coordinates.
        eye, up and at can be of shape (3) or (N, 3).

    Returns:
        tf_mat: the translation matrix to apply to apply the 'Look At' transformation
            from camera coordinates to world coordinates.
    """
    if eye is not None:
        cam_pos = eye
    else:
        cam_pos = camera_position_from_spherical_angles(dist, elev, azim, degrees=degrees)
        if isinstance(cam_pos, np.ndarray):
            cam_pos = cam_pos + np.broadcast_to(np.asarray(at), cam_pos.shape)
        else:
            cam_pos = cam_pos + torch.broadcast_to(torch.as_tensor(at), cam_pos.shape)
    rot_mat = look_at_rotation(cam_pos, at, up)
    tf_mat = rot_tl_to_tf_mat(rot_mat, cam_pos)
    return tf_mat


# TODO: change to np.mgrid
def create_grid(origin=None, size=None, resolution=None, return_tensor=False):
    """Create a 3D grid.

    Args:
        origin (list, optional): The (bottom, left, back) corner of the grid,
            note that it's not the center
        size (list, optional): The 3D size of the grid.
        resolution (list, optional): The resolution of the grid.
        return_tensor (bool, optional): Return `torch.tensor` or `np.array`.

    Returns:
        The points in the 3D grid.
    """

    if origin is None:
        origin = [-0.5, -0.5, -0.5]
    if size is None:
        size = [1.0, 1.0, 1.0]
    if resolution is None:
        resolution = [64, 64, 64]

    x = np.linspace(origin[0], origin[0] + size[0], resolution[0])
    y = np.linspace(origin[1], origin[1] + size[1], resolution[1])
    z = np.linspace(origin[2], origin[2] + size[2], resolution[2])

    xv, yv, zv = np.meshgrid(x, y, z, indexing="ij")
    points = np.concatenate([xv[..., None], yv[..., None], zv[..., None]], axis=-1).astype(np.float32)

    if return_tensor:
        # we do not use `torch.meshgrid` since its api is not stable currently
        points = torch.from_numpy(points).float()

    return points


# TODO: implement this
def fov_to_intrinsic(fov, width, height):
    pass


# TODO: implement this
def intrinsic_to_fov(matrix):
    pass
