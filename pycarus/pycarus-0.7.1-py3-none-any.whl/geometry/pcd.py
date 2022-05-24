import math
from pathlib import Path
from typing import Callable, Dict, List, Optional, Tuple, Union, cast

import numpy as np
import open3d as o3d  # type: ignore
import pytorch3d.transforms.transform3d as pt3d  # type: ignore
import torch
import torch.nn.functional as F
from einops import repeat  # type: ignore
from pytorch3d.ops import knn_points, sample_farthest_points  # type: ignore
from pytorch3d.transforms.rotation_conversions import _axis_angle_rotation  # type: ignore
from torch import Tensor


def batchify(inputs: List[Tensor], required_dim: int) -> Tuple[bool, List[Tensor]]:
    """Batchify input tensors if needed.

    All the input tensors with a number of dimensions smaller than
    required_dim will be expanded with a leading batch dimension.

    Args:
        inputs: The tensors to batchify.
        required_dim: The required number of dimensions.

    Returns:
        - A flag that indicates wether one of the inputs has been batchified.
        - The batchified tensors.
    """
    results: List[Tensor] = []
    has_changed = False

    for t in inputs:
        has_changed = len(t.shape) < required_dim or has_changed
        batched_t = torch.unsqueeze(t, dim=0) if has_changed else t
        results.append(batched_t)

    return has_changed, results


def unbatchify(inputs: List[Tensor]) -> List[Tensor]:
    """Remove batch dimension from input tensors.

    Args:
        inputs: The tensors to unbatchify.

    Returns:
        The unbatchified tensors.
    """
    results: List[Tensor] = []
    for t in inputs:
        unbatched_t = torch.squeeze(t, dim=0)
        results.append(unbatched_t)

    return results


def read_pcd(pcd_path: Union[str, Path], dtype: torch.dtype = torch.float) -> Tensor:
    """Read a point cloud from a given file.

    The point cloud is returned as a torch tensor with shape (NUM_POINTS, D).
    D can be 3 (only XYZ coordinates), 6 (XYZ coordinates and
    normals/colors) or 9 (XYZ coordinates, normals and colors).

    Args:
        pcd_path: The path of the point cloud file.
        dtype: The data type for the output tensor.

    Raises:
        ValueError: If the given file doesn't exist.

    Returns:
        A torch tensor with the loaded point cloud with shape (NUM_POINTS, D).
    """
    pcd_path = Path(pcd_path)
    if not pcd_path.exists():
        raise ValueError(f"The pcd file {str(pcd_path)} does not exists.")

    pcd_o3d = o3d.io.read_point_cloud(str(pcd_path))
    return get_tensor_pcd_from_o3d(pcd_o3d, dtype)


def get_tensor_pcd_from_o3d(
    pcd_o3d: o3d.geometry.PointCloud,
    dtype: torch.dtype = torch.float,
) -> Tensor:
    """Convert an open3d point cloud to a torch tensor.

    The point cloud is returned as a torch tensor with shape (NUM_POINTS, D).
    D can be 3 (only XYZ coordinates), 6 (XYZ coordinates and
    normals/colors) or 9 (XYZ coordinates, normals and colors).

    Args:
        pcd_o3d: The open3d point cloud.

    Returns:
        A torch tensor with the loaded point cloud with shape (NUM_POINTS, D).
    """
    pcd_torch = torch.tensor(np.asarray(pcd_o3d.points), dtype=dtype)

    if len(pcd_o3d.normals) > 0:
        normals_torch = torch.tensor(np.asarray(pcd_o3d.normals), dtype=dtype)
        pcd_torch = torch.cat((pcd_torch, normals_torch), dim=-1)

    if len(pcd_o3d.colors) > 0:
        colors_torch = torch.tensor(np.asarray(pcd_o3d.colors), dtype=dtype)
        pcd_torch = torch.cat((pcd_torch, colors_torch), dim=-1)

    return pcd_torch


def get_o3d_pcd_from_tensor(
    pcd: Union[Tensor, np.ndarray],
    colors: Optional[Union[Tensor, np.ndarray]] = None,
) -> o3d.geometry.PointCloud:
    """Get open3d point cloud from either numpy array or torch tensor.

    The input point cloud must have shape (NUM_POINTS, D), where D can be 3
    (only XYZ coordinates), 6 (XYZ coordinates and normals) or 9
    (XYZ coordinates, normals and colors). The optional array of colors
    must have shape (NUM_POINTS, 3).

    Args:
        pcd: The numpy array or torch tensor with points with shape (NUM_POINTS, D).
        colors: The optional numpy array or torch tensor with colors with shape (NUM_POINTS, 3).

    Returns:
        The open3d point cloud.
    """
    pcd_o3d = o3d.geometry.PointCloud()

    if isinstance(pcd, Tensor):
        p = pcd.clone().detach().cpu().numpy()
    else:
        p = np.copy(pcd)

    pcd_o3d.points = o3d.utility.Vector3dVector(p[:, :3])

    if pcd.shape[1] >= 6:
        pcd_o3d.normals = o3d.utility.Vector3dVector(p[:, 3:6])

    if pcd.shape[1] == 9:
        pcd_o3d.colors = o3d.utility.Vector3dVector(p[:, 6:])

    if colors is not None:
        if isinstance(colors, Tensor):
            c = colors.clone().detach().cpu().numpy()
        else:
            c = np.copy(colors)

        pcd_o3d.colors = o3d.utility.Vector3dVector(c)

    return pcd_o3d


def normalize_pcd_into_unit_sphere(pcd: Tensor) -> Tensor:
    """Normalize the given point cloud(s) into the unit sphere.

    For each input point cloud, coordinates are first expressed
    wrt to the point cloud centroid. Then, they are normalized
    wrt the maximum distance from the centroid. If present,
    normals and colors are preserved.

    Args:
        pcd: The input point cloud(s) with shape ([B,] NUM_POINTS, D).

    Returns:
        The normalized point cloud(s) with shape ([B,] NUM_POINTS, D).
    """
    pcd_copy = torch.clone(pcd)
    batched, [pcd_copy] = batchify([pcd_copy], 3)

    xyz = pcd_copy[:, :, :3]
    centroid = torch.mean(xyz, dim=1, keepdim=True)
    xyz = xyz - centroid
    distances_from_centroid = torch.norm(xyz, p=2, dim=-1, keepdim=True)  # type: ignore
    max_dist_from_centroid = torch.max(distances_from_centroid, dim=1, keepdim=True)[0]
    xyz = xyz / max_dist_from_centroid

    normalized_pcd = torch.cat((xyz, pcd_copy[:, :, 3:]), dim=-1)

    if batched:
        [normalized_pcd] = unbatchify([normalized_pcd])

    return normalized_pcd


def normalize_pcd_into_unit_cube(pcd: Tensor) -> Tensor:
    """Normalize the given point cloud(s) into the unit cube [0-1].

    For each input point cloud, coordinates are first expressed
    wrt to its bounding box centroid. Then, they are normalized
    so that their bounding boxes fit the unit cube [0-1]. If present,
    normals and colors are preserved.

    Args:
        pcd: The input point cloud(s) with shape ([B,] NUM_POINTS, D).

    Returns:
        The normalized point cloud(s) with shape ([B,] NUM_POINTS, D).
    """
    pcd_copy = torch.clone(pcd)
    batched, [pcd_copy] = batchify([pcd_copy], 3)

    xyz = pcd_copy[:, :, :3]
    centroid = (torch.max(xyz, dim=1, keepdim=True)[0] + torch.min(xyz, dim=1, keepdim=True)[0]) / 2
    xyz = xyz - centroid
    bbox_sides = torch.max(xyz, dim=1, keepdim=True)[0] - torch.min(xyz, dim=1, keepdim=True)[0]
    max_bbox_side = torch.max(bbox_sides, dim=-1, keepdim=True)[0]
    xyz = xyz / max_bbox_side
    xyz += 0.5

    normalized_pcd = torch.cat((xyz, pcd_copy[:, :, 3:]), dim=-1)

    if batched:
        [normalized_pcd] = unbatchify([normalized_pcd])

    return normalized_pcd


def farthest_point_sampling(pcd: Tensor, num_points: int) -> Tensor:
    """Sample the requested number of points from the given point cloud(s).

    Points are sampled using farthest point sampling.
    Each input point is supposed to have (X, Y, Z) coordinates in the first 3
    values of the feature vector, while the remaining values are returned unchanged.

    Args:
        pcd: The input point cloud(s) with shape ([B,] NUM_POINTS, D).
        num_points: The number of points to sample.

    Returns:
        The sampled points with shape ([B,] NUM_SAMPLED_POINTS, D).
    """
    batched, [pcd] = batchify([pcd], 3)

    xyz = pcd[:, :, :3]
    features = pcd[:, :, 3:]

    sampled_points, indices = sample_farthest_points(xyz, K=num_points, random_start_point=True)

    indices = repeat(indices, "b n -> b n r", r=features.shape[-1])
    sampled_features = torch.gather(features, 1, indices)
    sampled_points = torch.cat((sampled_points, sampled_features), dim=-1)

    if batched:
        [sampled_points] = unbatchify([sampled_points])

    return sampled_points


def random_point_sampling(pcd: Tensor, num_points: int) -> Tensor:
    """Sample the requested number of points from the given point cloud(s).

    Points are sampled randomly. If num_points is greater than NUM_POINTS,
    then points are sampled with replacement.

    Args:
        pcd: The input point cloud(s) with shape ([B,] NUM_POINTS, D).
        num_points: The number of points to sample.

    Returns:
        The sampled points with shape ([B,] NUM_SAMPLED_POINTS, D).
    """
    batched, [pcd] = batchify([pcd], 3)

    batch_size, original_num_points, _ = pcd.shape

    weights = torch.ones((batch_size, original_num_points), dtype=torch.float)
    weights = weights.to(pcd.device)

    replacement = original_num_points < num_points
    indices_to_sample = torch.multinomial(weights, num_points, replacement=replacement)

    batch_indices = torch.arange(batch_size).reshape(batch_size, 1)
    sampled_points = pcd[batch_indices, indices_to_sample]

    if batched:
        [sampled_points] = unbatchify([sampled_points])

    return sampled_points


def get_distances_matrix(pcd_src: Tensor, pcd_trg: Tensor) -> Tensor:
    """Get euclidean distances between two point clouds.

    This functions assumes that the first three element of each point are XYZ coordinates.
    It creates a matrix with shape (NUM_POINTS_SRC, NUM_POINTS_TRG), where the i-th row contains
    the euclidean distances between the i-th point of pcd_src and all the other points.

    Args:
        pcd_src: The input point cloud(s) with shape ([B,] NUM_POINTS_SRC, D).
        pcd_trg: The input point cloud(s) with shape ([B,] NUM_POINTS_TRG, D).

    Returns:
        The matrix with distances with shape (NUM_POINTS_SRC, NUM_POINTS_TRG).
    """
    batched, [pcd_src, pcd_trg] = batchify([pcd_src, pcd_trg], 3)

    pcd_src = pcd_src[:, :, :3]
    pcd_trg = pcd_trg[:, :, :3]

    size_batch, num_pts_src, _ = pcd_src.shape
    _, num_pts_trg, _ = pcd_trg.shape

    dot_src_trg = -2 * torch.matmul(pcd_src, pcd_trg.permute(0, 2, 1))
    src_square = torch.sum(pcd_src**2, -1).reshape(size_batch, num_pts_src, 1)
    trg_square = torch.sum(pcd_trg**2, -1).reshape(size_batch, 1, num_pts_trg)

    mat_dist_squared = dot_src_trg + src_square + trg_square
    mat_dist_squared[mat_dist_squared < 0.0] = 0.0
    mat_distances = torch.sqrt(mat_dist_squared)

    if batched:
        [mat_distances] = unbatchify([mat_distances])

    return mat_distances


def get_neighbours_distance(pcd: Tensor, reduce_fn: str) -> Tensor:
    """Compute distance between neighbouring points.

    Args:
        pcd: The input point cloud(s) with shape ([B,] NUM_POINTS, D).
        reduce_fn: The reduce function to apply to neighbours distances.
            Available options are "min", "max", "mean", "median", "std".

    Raises:
        ValueError: If the given reduce function is unknown.

    Returns:
        The distance computed using the specified reduce_fn.
    """
    batched, [pcd] = batchify([pcd], 3)

    num_points = pcd.shape[1]
    distances = get_distances_matrix(pcd, pcd)
    distances[:, torch.eye(num_points).bool()] = float("inf")
    neighbours_distances = torch.min(distances, dim=-1)[0]

    rfns: Dict[str, Callable[[Tensor], Tensor]] = {
        "min": torch.min,
        "max": torch.max,
        "mean": torch.mean,
        "median": torch.median,
        "std": torch.std,
    }

    try:
        rfn = rfns[reduce_fn]
    except KeyError:
        raise ValueError("Unknown reduce function.")

    result = rfn(neighbours_distances)

    if batched:
        [result] = unbatchify([result])

    return result


def shuffle_pcd(pcd: Tensor) -> Tensor:
    """Shuffle the order of the point inside the give point cloud(s).

    Args:
        pcd: The input point cloud(s) with shape ([B,] NUM_POINTS, D).

    Returns:
        The shuffled point cloud(s) with shape ([B,] NUM_POINTS, D).
    """
    pcd_copy = torch.clone(pcd)

    batched, [pcd_copy] = batchify([pcd_copy], 3)

    _, num_points, _ = pcd_copy.shape

    rand_indices = torch.randperm(num_points)
    while torch.all(rand_indices == torch.arange(num_points)):
        rand_indices = torch.randperm(num_points)

    shuffled_pcd = pcd_copy[:, rand_indices]

    if batched:
        [shuffled_pcd] = unbatchify([shuffled_pcd])

    return shuffled_pcd


def jitter_pcd(pcd: Tensor, sigma: float = 0.01, clip: float = 0.05) -> Tensor:
    """Jitter point cloud(s) by adding random noise.

    Add a gaussian noise to each coordinates of each point
    in the input point cloud. The noise is sampled from a normal
    distribution with mean 0 and std 1 multiplied by sigma.
    Finally, the final amount of noise to add is clipped between -clip and clip.

    Args:
        pcd: The input point cloud(s) with shape ([B,] NUM_POINTS, D).
        sigma: The sigma for the gaussian noise.
        clip: The clipping value.

    Returns:
        The jittered point cloud(s) with shape ([B,] NUM_POINTS, D).
    """
    pcd_copy = torch.clone(pcd)

    batched, [pcd_copy] = batchify([pcd_copy], 3)
    size_batch, num_points = pcd_copy.shape[0], pcd_copy.shape[1]

    noise = torch.clip(sigma * torch.randn((size_batch, num_points, 3)), min=-1 * clip, max=clip)
    jittered_pts = pcd_copy[:, :, 0:3] + noise.to(pcd_copy.device)
    jittered_pcd = pcd_copy
    jittered_pcd[:, :, 0:3] = jittered_pts

    if batched:
        [jittered_pcd] = unbatchify([jittered_pcd])

    return jittered_pcd


def random_drop_points(pcd: Tensor, drop_percentage: float) -> Tuple[Tensor, Tensor, Tensor]:
    """Random drop points in the given point cloud(s).

    Args:
        pcd: The input point cloud(s) with shape ([B,] NUM_POINTS, D).
        drop_percentage: The percentage of points to be removed.

    Returns:
        - The dropped point cloud(s) with shape ([B,] NUM_POINTS, D).
        - The indices of points that have been kept.
        - The indices of points that have been removed.
    """
    pcd_copy = torch.clone(pcd)
    batched, [pcd_copy] = batchify([pcd_copy], 3)
    batch_size, num_input_pts, point_dim = pcd_copy.shape
    num_pts_to_remove = math.ceil(num_input_pts * drop_percentage)

    if num_pts_to_remove > 0:
        weights = torch.ones((batch_size, num_input_pts), dtype=torch.float)
        indices_to_remove = torch.multinomial(weights, num_pts_to_remove, replacement=False)
        indices_to_remove = indices_to_remove.to(pcd_copy.device)

        output_shape = (batch_size, num_input_pts - num_pts_to_remove, point_dim)
        pcd_dropped = torch.empty(output_shape, dtype=pcd_copy.dtype)
        indices_to_keep = torch.empty(output_shape[:-1], dtype=torch.long)
        for i in range(batch_size):
            indices_pcd = torch.arange(num_input_pts)
            mask = torch.full((num_input_pts,), True)
            mask[indices_to_remove[i]] = False
            indices_to_keep[i] = indices_pcd[mask]

            pcd_dropped[i] = pcd_copy[i, indices_to_keep[i]]
    else:
        pcd_dropped = pcd_copy
        indices_to_keep = torch.arange(end=num_input_pts).repeat((batch_size,))
        indices_to_remove = torch.tensor([])

    indices_to_keep = indices_to_keep.to(pcd_copy.device)
    pcd_dropped = pcd_dropped.to(pcd_copy.device)

    if batched:
        results = [pcd_dropped, indices_to_keep, indices_to_remove]
        [pcd_dropped, indices_to_keep, indices_to_remove] = unbatchify(results)

    return pcd_dropped, indices_to_keep, indices_to_remove


def _apply_pt3d_transform(
    pcd: Tensor,
    transform: pt3d.Transform3d,
    transform_normals: bool,
) -> Tensor:
    """Apply PyTorch 3D transform to the input point clouds.

    This method is a wrapper to the PyTorch3D Transform3D in order to avoid to call separate
    methods to transform points and normals. If transform_normals is True also the normals are
    transformed, for some rigid transformation such as scale and transation this is not
    necessary.

    Args:
        pcd: The input point clouds with shape (B, NUM_POINTS, D).
        transform: The transform to apply.

    Returns:
        The transformed point clouds.
    """
    batched, [pcd] = batchify([pcd], 3)

    point_dim = pcd.shape[-1]
    pcd_transformed = transform.transform_points(pcd[:, :, :3])

    if point_dim >= 6:
        if transform_normals:
            normals = transform.transform_normals(pcd[:, :, 3:6])
        else:
            normals = pcd[:, :, 3:6]
        pcd_transformed = torch.cat((pcd_transformed, normals), dim=-1)

    if point_dim == 9:
        colors = pcd[:, :, 6:9]
        pcd_transformed = torch.cat((pcd_transformed, colors), dim=-1)

    if batched:
        [pcd_transformed] = unbatchify([pcd_transformed])

    return pcd_transformed


def apply_affine_to_pcd(pcd: Tensor, affine_transform: Tensor) -> Tensor:
    """Apply an affine transformation, typically a rigid motion matrix.

    This method applies a rotation and a translation to the input point cloud. We rely on the same
    convention of PyTorch3D, hence an affine matrix is stored using a row-major order:
      M = [[Rxx, Ryx, Rzx, 0],
           [Rxy, Ryy, Rzy, 0],
           [Rxz, Ryz, Rzz, 0],
           [Tx,  Ty,  Tz,  1],]
    the rows of the matrix represent the bases of a coordinate system and the last row stores
    the translation vector. If the point cloud contains also the normals, only the rotation
    will be applied. Despite operating in with affine matrix the coordinates of the input points
    don't need to be in the affine space.

    Args:
        pcd: The input point cloud(s) with shape ([B,] NUM_POINTS, D).
        affine_transform: The transformation to appyly with shape (4, 4).

    Returns:
        The transformed point cloud(s) with shape ([B,] NUM_POINTS, D).
    """
    transform = pt3d.Transform3d(dtype=pcd.dtype, device=str(pcd.device), matrix=affine_transform)
    return _apply_pt3d_transform(pcd, transform=transform, transform_normals=True)


def rotate_pcd(pcd: Tensor, rotation: Tensor) -> Tensor:
    """Rotate a point cloud give the input matrix.

    Rotate the cloud using the same convention as in PyTorch3D: a right-hand coordinate system,
    meaning that rotation about an axis with a positive angle results in a counter clockwise
    rotation, more info at (https://pytorch3d.readthedocs.io).
    The points are multiplied using post-multiplication: rotated_points = points * rotation.

    Args:
        pcd: The input point cloud(s) with shape ([B,] NUM_POINTS, D).
        rotation: The rotation matrix with shape (3, 3).

    Returns:
        The rotated point cloud(s) with shape ([B,] NUM_POINTS, D).
    """
    transform = pt3d.Rotate(rotation, dtype=pcd.dtype, device=str(pcd.device))
    return _apply_pt3d_transform(pcd, transform, transform_normals=True)


def rotate_pcd_around_axis(pcd: Tensor, axis: str, angle: float) -> Tensor:
    """Rotate a point cloud of the given angle around the given axis.

    Args:
        pcd: The point cloud(s) with shape ([B,] NUM_POINTS, D).
        axis: The axis around which the point cloud(s) will be rotated.
        angle: The required rotation in degrees.

    Returns:
        The rotated point cloud(s).
    """
    assert axis.upper() in ["X", "Y", "Z"]

    batched, [pcd] = batchify([pcd], 3)

    theta = torch.deg2rad(torch.tensor(angle))
    # _axis_angle_rotation returns a rotation matrix thought to operate
    # on column vectors, since we use row vectors we need to transpose
    matrix = _axis_angle_rotation(axis, theta).transpose(0, 1)

    rotated_pcd = rotate_pcd(pcd, matrix)

    if batched:
        [rotated_pcd] = unbatchify([rotated_pcd])

    return rotated_pcd


def scale_pcd(pcd: Tensor, scale_factor: Tensor) -> Tensor:
    """Scale a point cloud given the input scale factor.

    Args:
        pcd: The input point cloud(s) with shape ([B,] NUM_POINTS, D).
        scale: The scale factor for the x, y, z, dimensions with shape (3,).

    Returns:
        The scaled point cloud(s) with shape ([B,] NUM_POINTS, D).
    """
    scale_x, scale_y, scale_z = scale_factor[0], scale_factor[1], scale_factor[2]
    transform = pt3d.Scale(x=scale_x, y=scale_y, z=scale_z, dtype=pcd.dtype, device=str(pcd.device))

    return _apply_pt3d_transform(pcd, transform, transform_normals=False)


def translate_pcd(pcd: Tensor, translation: Tensor) -> Tensor:
    """Translate a point cloud given the input translation.

    Args:
        pcd: The input point cloud(s) with shape ([B,] NUM_POINTS, D).
        translation: The translation offset with shape (3,).

    Returns:
        The translated point cloud(s) with shape ([B,] NUM_POINTS, D).
    """
    x, y, z = translation[0], translation[1], translation[2]
    transform = pt3d.Translate(x=x, y=y, z=z, dtype=pcd.dtype, device=str(pcd.device))

    return _apply_pt3d_transform(pcd, transform, transform_normals=False)


def get_neighbouring_points(
    pcd: Tensor,
    query_points: Tensor,
    max_num_neighbours: int,
    radius: Optional[float] = None,
) -> Tuple[Tensor, Tensor]:
    """Compute neighbouring points using radius search and/or nearest neighbours search.

    This function retrieves the nearest neighbours in a point cloud for each query point
    specified in query_points. In order to arrange the points in batch, a maximum number
    of neighbours (max_num_neighbours) must be specified. If a radius is given,
    only the points within the radius are collected. If, for a query point, there are less
    then max_num_neighbours neighbours, the first retrieved neighbour is used to pad the batch.

    Args:
        pcd: The input point cloud(s) with shape ([B,] NUM_POINTS, D).
        query_points: The input point cloud(s) with shape ([B,] NUM_QUERY_POINTS, D).
        max_num_neighbours: The maximum number of neighbours to return.
        radius: The optional radius to use for the search. Defaults to None.

    Raises:
        ValueError: If max_num_neighbours is zero.

    Returns:
        - The indices of the neighbours collected for each query point,
          with shape ([B,] NUM_QUERY_POINTS, max_num_neighbours). The indices are sorted
          in ascending order according to the euclidean distance from the query points.
        - The points in the pcd indexed by the nearest neihgbors indices, with
          shape ([B,] NUM_QUERY_POINTS, max_num_neighbours, 3).
    """
    if max_num_neighbours == 0:
        raise ValueError("Max number of neighbours is zero.")

    batched, [pcd, query_points] = batchify([pcd, query_points], 3)

    size_batch, _, point_dim = pcd.shape
    _, num_pts_query, _ = query_points.shape

    distances = get_distances_matrix(query_points, pcd)
    indices_nn = torch.empty([])

    if radius is not None:
        distances[distances > radius] = float("inf")
        distances_sorted, indices_nn = torch.sort(distances, dim=-1)
        indices_first_nn = (
            indices_nn[:, :, 0]
            .reshape(size_batch, num_pts_query, 1)
            .repeat([1, 1, max_num_neighbours])
        )
        mask = distances_sorted == float("inf")
        mask = mask[:, :, :max_num_neighbours]
        indices_nn = indices_nn[:, :, :max_num_neighbours]
        indices_nn[mask] = indices_first_nn[mask]
    else:
        _, indices_nn = torch.sort(distances, dim=-1)
        indices_nn = indices_nn[:, :, :max_num_neighbours]

    out_shape = (size_batch, num_pts_query, max_num_neighbours, point_dim)
    points_nn = torch.empty(out_shape, dtype=pcd.dtype, device=pcd.device)
    kpts_indices = torch.arange(num_pts_query)

    for b in range(size_batch):
        points_nn[b, kpts_indices] = pcd[b, indices_nn[b, kpts_indices]]

    if batched:
        [indices_nn, points_nn] = unbatchify([indices_nn, points_nn])

    return indices_nn, points_nn


def voxelize_pcd(
    pcd: Tensor,
    res: int,
    vmin: Optional[float] = None,
    vmax: Optional[float] = None,
) -> Tuple[Tensor, Tensor]:
    """Voxelize point cloud(s).

    Each input cloud is voxelized according to the given resolution,
    i.e. the output voxel grid will have shape (res, res, res) for each cloud.
    If vmin and vmax are passed, the function assumes that the input cloud
    is already centered and scaled properly. Otherwise, the cloud is centered
    and scaled in the unit sphere before computing the voxel grid.

    Args:
        pcd: the input point cloud(s) with shape ([B,] NUM_POINTS, 3).
        res: the resolution for the voxel grid.
        vmin: The minimum value in x, y and z for the bounding box.
        vmax: The maximum value in x, y and z for the bounding box.

    Returns:
        A tuple containing:
        - The voxel grid(s) with shape ([B,] res, res, res).
        - The coordinates of the centroids of each cell of the voxel grid
            with shape (res, res, res, 3). They are the same for each element
            of the batch, so there's no need to return a batched version.
    """
    batched, [pcd] = batchify([pcd], 3)

    if not vmin or not vmax:
        pcd = normalize_pcd_into_unit_sphere(pcd)
        vmin = -1.0
        vmax = 1.0

    xyz_ranges = torch.tensor((vmax, vmax, vmax)) - torch.tensor((vmin, vmin, vmin))
    xyz_ranges = xyz_ranges.to(pcd.device)

    leaf_sizes = xyz_ranges / res
    ijk = ((pcd - vmin) / leaf_sizes.unsqueeze(0)).long()
    ijk = torch.clip(ijk, 0, res - 1)
    i, j, k = ijk[:, :, 0], ijk[:, :, 1], ijk[:, :, 2]
    indices = i * (res**2) + j * res + k

    occupancies = torch.zeros((pcd.shape[0], res**3), device=pcd.device)
    ones = torch.ones_like(occupancies)
    occupancies.scatter_(1, indices, ones)
    occupancies = occupancies.reshape(pcd.shape[0], res, res, res)

    x = torch.arange(vmin, vmax, float(leaf_sizes[0]), device=pcd.device)
    coords_x, coords_y, coords_z = torch.meshgrid(x, x, x, indexing="ij")
    centroids_coords = torch.stack((coords_x, coords_y, coords_z), dim=-1).float()
    centroids_coords += leaf_sizes[0] / 2

    if batched:
        [occupancies] = unbatchify([occupancies])

    return occupancies, centroids_coords


def knn(query: Tensor, target: Tensor, k: int) -> Tuple[Tensor, Tensor, Tensor]:
    """Perform Nearest Neighbours search.

    Args:
        query: The query points with shape ([B,] N, D).
        target: The target points with shape ([B,] M, D).
        k: The required numbers of neighbours.

    Returns:
        - The indices of the returned neighbours in the target cloud(s) with shape ([B,] N, K).
        - The collected neighbours with shape ([B,] N, K, D).
        - The euclidean distances to the returned neighbours with shape ([B,] N, K).
    """
    batched, [query, target] = batchify([query, target], 3)

    distances, indices, nns = knn_points(query, target, K=k, return_nn=True, return_sorted=False)
    distances = torch.sqrt(distances)

    if batched:
        [distances, indices, nns] = unbatchify([distances, indices, nns])

    return indices, nns, distances


def sample_points_around_pcd(
    pcd: Tensor,
    stds: List[float],
    num_points_per_std: List[int],
    coords_range: Tuple[float, float],
    device: str = "cpu",
) -> Tensor:
    """Sample points around the given point cloud.

    Points are sampled by adding gaussian noise to the input cloud,
    according to the given standard deviations. Additionally, points
    are also sampled uniformly in the given range.

    Args:
        pcd: The point cloud tensor with shape (N, 3).
        stds: A list of standard deviations to compute the gaussian noise
            to obtain the points.
        num_points_per_std: A list with the number of points to sample for each
            standard deviation. The last number refers to points sampled uniformly
            in the given range (len(num_points_per_std) = len(stds) + 1).
        coords_range: The range for the points coordinates.
        device: The device for the sampled points. Defaults to "cpu".

    Returns:
        The sampled points with shape (M, 3).
    """
    coords = torch.empty(0, 3).to(device)
    num_points_pcd = pcd.shape[0]

    for sigma, num_points in zip(stds, num_points_per_std[:-1]):
        mul = num_points // num_points_pcd

        if mul > 0:
            coords_for_sampling = repeat(pcd, "n d -> (n r) d", r=mul).to(device)
        else:
            coords_for_sampling = torch.empty(0, 3).to(device)

        still_needed = num_points % num_points_pcd
        if still_needed > 0:
            weights = torch.ones(num_points_pcd, dtype=torch.float).to(device)
            indices_random = torch.multinomial(weights, still_needed, replacement=False)
            pcd_random = pcd[indices_random].to(device)
            coords_for_sampling = torch.cat((coords_for_sampling, pcd_random), dim=0)

        offsets = torch.randn(num_points, 3).to(device) * sigma
        coords_i = coords_for_sampling + offsets

        coords = torch.cat((coords, coords_i), dim=0)

    random_coords = torch.rand(num_points_per_std[-1], 3).to(device)
    random_coords *= coords_range[1] - coords_range[0]
    random_coords += coords_range[0]
    coords = torch.cat((coords, random_coords), dim=0)

    coords = torch.clip(coords, min=coords_range[0], max=coords_range[1])

    return coords


def compute_sdf_from_pcd(
    pcd_o3d: o3d.geometry.PointCloud,
    queries_stds: List[float] = [0.003, 0.01, 0.1],
    num_queries_per_std: List[int] = [5_000, 4_000, 500, 500],
    coords_range: Tuple[float, float] = (-0.5, 0.5),
    max_dist: float = 0.1,
    compute_occupancy: bool = False,
    use_cuda: bool = True,
) -> Tuple[Tensor, Tensor]:
    """Compute the signed distance function or the occupancy field for a given pcd.

    The function works only for cloud with accurate normals.
    Query points are sampled by adding gaussian noise to the cloud, according
    to the given standard deviations. Additionally, query points are also sampled
    uniformly in the given range. Distances are clipped to max_dist.

    Args:
        pcd_o3d: The open3d point cloud.
        queries_stds: A list of standard deviations to compute the gaussian noise
            to obtain query points. Defaults to [0.003, 0.01, 0.1].
        num_queries_per_std: A list with the number of query points to compute for each
            standard deviation. The last number refers to query points sampled
            uniformly in the given range (len(num_queries_per_std) = len(queries_stds) + 1).
            Defaults to [5_000, 4_000, 500, 500].
        coords_range: The range for the queries coordinates.
        max_dist: The clip value for computed distances. Defaults to 0.1.
        compute_occupancy: If True, compute occupancy instead of sdf. Defaults to False.
        use_cuda: If True, use CUDA to speed up KNN. Defaults to True.

    Returns:
        - The tensor with the query coordinates with shape (N, 3).
        - The tensor with the computed sdf or occupancy with shape (N,).
    """
    assert len(pcd_o3d.normals) > 0

    pcd_and_normals = get_tensor_pcd_from_o3d(pcd_o3d)
    pcd = pcd_and_normals[:, :3]
    normals = pcd_and_normals[:, 3:]

    k = 11  # from DeepSDF

    device = "cuda" if use_cuda else "cpu"
    queries = sample_points_around_pcd(pcd, queries_stds, num_queries_per_std, coords_range, device)
    indices, closest_points, distances = knn(queries, pcd.to(device), k)
    queries = queries.cpu()
    indices = indices.cpu()
    closest_points = closest_points.cpu()
    distances = distances.cpu()

    surface_to_queries_vec = queries.unsqueeze(1) - closest_points
    inside = torch.einsum("ijk,ijk->ij", surface_to_queries_vec, normals[indices]) < 0  # type: ignore

    inside = torch.sum(inside, dim=1)
    valid_mask = (inside == k) | (inside == 0)  # take only 100% certain points
    inside = inside[valid_mask] > 0

    sdf = torch.min(distances[valid_mask], dim=-1)[0]
    sdf[inside] *= -1

    if compute_occupancy:
        values = (sdf < 0).float()
    else:
        values = torch.clip(sdf, min=-max_dist, max=max_dist)

    queries = queries[valid_mask]

    if queries.shape[0] != sum(num_queries_per_std):
        queries_and_values = torch.cat((queries, values.unsqueeze(-1)), dim=-1)
        queries_and_values = random_point_sampling(queries_and_values, sum(num_queries_per_std))
        queries = queries_and_values[:, :3]
        values = queries_and_values[:, -1].squeeze(-1)

    return queries, values


def compute_udf_from_pcd(
    pcd: Tensor,
    queries_stds: List[float] = [0.003, 0.01, 0.1],
    num_queries_per_std: List[int] = [5_000, 4_000, 500, 500],
    coords_range: Tuple[float, float] = (-0.5, 0.5),
    max_dist: float = 0.1,
    convert_to_bce_labels: bool = False,
    use_cuda: bool = True,
) -> Tuple[Tensor, Tensor]:
    """Compute the unsigned distance function for a given pcd.

    Query points are sampled by adding gaussian noise to the cloud, according
    to the given standard deviations. Additionally, query points are also sampled
    uniformly in the given range. Distances are clipped to max_dist.

    Args:
        pcd: The tensor with the point cloud with shape (N, 3).
        queries_stds: A list of standard deviations to compute the gaussian noise
            to obtain query points. Defaults to [0.003, 0.01, 0.1].
        num_queries_per_std: A list with the number of query points to compute for each
            standard deviation. The last number refers to query points sampled
            uniformly in the given range (len(num_queries_per_std) = len(queries_stds) + 1).
            Defaults to [5_000, 4_000, 500, 500].
        coords_range: The range for the queries coordinates.
        max_dist: The clip value for computed distances. Defaults to 0.1.
        convert_to_bce_labels: If True, convert distances to labels
            in the [0, 1] range, with 0=max_dist and 1=surface. Defaults to False.
        use_cuda: If True, use CUDA to speed up KNN. Defaults to True.

    Returns:
        - The tensor with the query coordinates with shape (N, 3).
        - The tensor with the computed sdf or occupancy with shape (N,).
    """
    device = "cuda" if use_cuda else "cpu"
    queries = sample_points_around_pcd(pcd, queries_stds, num_queries_per_std, coords_range, device)
    _, _, distances = knn(queries, pcd.to(device), 1)
    queries = queries.cpu()
    distances = distances.cpu().squeeze(-1)

    values = torch.clip(distances, min=0, max=max_dist)

    if convert_to_bce_labels:
        values /= max_dist
        values = 1 - values

    return queries, values


def sample_pcds_from_udfs(
    udfs_func: Callable[[Tensor, List[int]], Tensor],
    num_pcds: int,
    num_samples_forward: int,
    coords_range: Tuple[float, float],
    th_pred: float,
    th_surf: float,
    num_out_points: int,
    num_steps_refinement: int,
) -> Tensor:
    """Sample point clouds from UDFs.

    The function samples num_pcds point clouds in parallel, querying udfs_func with
    batch of coordinates. Thus, udfs_func must support batch forwards.
    udfs_func is provided also with the list of indices of items that are currently computed:
    e.g., if this function is used to sample a batch of 4 point clouds, initially udfs_func
    will be called with indices [0, 1, 2, 3]. If after some iteration, no further sampling is
    needed for clouds 1 and 3, udfs_func will be called with indices [0, 2].
    Each query is moved to the surface of its cloud according to the predicted UDF
    and to the gradient of the computed UDF. Additionally, this procedure is repeated
    iteratively to refine results, since predictions are supposed to be more accurate
    close to the surface.

    Args:
        udfs_func: A function that will be queried with a batch of coordinates and with
            a list of indices indicating to which item is associated each element of the
            batch. The function must return the predicted UDF for each coordinate.
        num_samples_forward: The number of coordinates for each item of the batch when
            querying udfs_func.
        coords_range: The range for the queries coordinates.
        th_pred: The threshold used to keep/discard queries after the first coarse prediction.
            Only queries with predicted UDF <= th_pred are kept.
        th_surf: The threshold used to keep/discard points after refinement. Only points
            with refined UDF <= th_surf are kept.
        num_out_points: The number of points for the sampled clouds.
        num_steps_refinement: The number of refinement steps (at least 1).

    Returns:
        A single tensor with the batch of sampled point clouds.
    """
    assert num_steps_refinement >= 1

    batch_size = num_pcds

    pcds = [torch.empty((0, 3)).cuda() for _ in range(batch_size)]
    remaining = list(range(batch_size))

    while remaining:
        batch_indices = torch.tensor(remaining)
        batch_indices = repeat(batch_indices, "n -> n r", r=num_samples_forward)

        samples = torch.rand(len(remaining), num_samples_forward, 3).cuda()
        samples *= coords_range[1] - coords_range[0]
        samples += coords_range[0]

        for refinement_step in range(num_steps_refinement):
            samples = samples.reshape(len(remaining), -1, 3)
            batch_indices = batch_indices.reshape(len(remaining), -1)

            samples = samples.detach().clone()
            samples.requires_grad = True

            preds = udfs_func(samples, remaining)
            preds.sum().backward()  # type: ignore

            grads = cast(Tensor, samples.grad)
            directions = F.normalize(grads, dim=-1)

            batch_indices = batch_indices.reshape(-1)
            samples = samples.reshape(-1, 3)
            preds = preds.reshape(-1)
            directions = directions.reshape(-1, 3)

            if refinement_step == 0:
                mask = preds <= th_pred
                samples = samples[mask]
                batch_indices = batch_indices[mask]
                preds = preds[mask]
                directions = directions[mask]

                min_taken = min([torch.count_nonzero(batch_indices == i).item() for i in remaining])
                min_taken = cast(int, min_taken)
                new_batch_indices = []
                new_samples = []
                new_preds = []
                new_directions = []

                for i in remaining:
                    mask = batch_indices == i
                    new_batch_indices.append(batch_indices[mask][:min_taken])
                    new_samples.append(samples[mask][:min_taken])
                    new_preds.append(preds[mask][:min_taken])
                    new_directions.append(directions[mask][:min_taken])

                batch_indices = torch.stack(new_batch_indices, dim=0)
                samples = torch.stack(new_samples, dim=0)
                preds = torch.stack(new_preds, dim=0)
                directions = torch.stack(new_directions, dim=0)

            samples = samples - directions * preds.unsqueeze(-1)

        mask = preds <= th_surf
        samples = samples[mask]
        batch_indices = batch_indices[mask]

        for i in remaining:
            available_points = samples[batch_indices == i]
            needed_points = num_out_points - pcds[i].shape[0]
            if available_points.shape[0] > needed_points:
                available_points = random_point_sampling(available_points, needed_points)
            pcds[i] = torch.cat([pcds[i], available_points], dim=0)

        remaining = [i for i in range(batch_size) if pcds[i].shape[0] < num_out_points]

    return torch.stack(pcds, dim=0)
