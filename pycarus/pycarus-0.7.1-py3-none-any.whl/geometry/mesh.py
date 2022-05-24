from pathlib import Path
from typing import Callable, List, Tuple, Union

import numpy as np
import open3d as o3d  # type: ignore
import torch
from skimage.measure import marching_cubes as sk_marching_cubes  # type: ignore
from torch import Tensor

from pycarus.geometry.pcd import compute_sdf_from_pcd, get_tensor_pcd_from_o3d
from pycarus.geometry.pcd import sample_points_around_pcd


def read_mesh(
    mesh_path: Union[str, Path],
    dtype: torch.dtype = torch.float,
) -> Tuple[Tensor, Tensor]:
    """Read a mesh from a given file.

    The mesh is returned as a tuple of torch tensors, containing:
    - The vertices with shape (N, D). D can be 3 if only coordinates are available,
        6 if also normals or colors are available, 9 if both normals and colors are available.
    - The trianges with shape (M, D). D can be 3 if normals are not available, 6 otherwise.

    Args:
        mesh_path: The path of the mesh file.
        dtype: The data type for the output tensors.

    Raises:
        ValueError: If the given file doesn't exist.

    Returns:
        - The tensor with the mesh vertices with shape (N, D).
        - The tensor with the mesh triangles with shape (M, D).
    """
    mesh_path = Path(mesh_path)
    if not mesh_path.exists():
        raise ValueError(f"The mesh file {str(mesh_path)} does not exists.")

    mesh_o3d = o3d.io.read_triangle_mesh(str(mesh_path))
    return get_tensor_mesh_from_o3d(mesh_o3d, dtype)


def get_tensor_mesh_from_o3d(
    mesh_o3d: o3d.geometry.TriangleMesh,
    dtype: torch.dtype = torch.float,
) -> Tuple[Tensor, Tensor]:
    """Convert an open3d mesh to a tuple of torch tensors.

    The mesh is returned as a tuple of torch tensors, containing:
    - The vertices with shape (N, D). D can be 3 if only coordinates are available,
        6 if also normals or colors are available, 9 if both normals and colors are available.
    - The trianges with shape (M, D). D can be 3 if normals are not available, 6 otherwise.

    Args:
        mesh_o3d: The open3d mesh.

    Returns:
        - The tensor with the mesh vertices with shape (N, D).
        - The tensor with the mesh triangles with shape (M, D).
    """
    vertices = torch.tensor(np.asarray(mesh_o3d.vertices), dtype=dtype)

    if len(mesh_o3d.vertex_normals) > 0:
        vertices_normals = torch.tensor(np.asarray(mesh_o3d.vertex_normals), dtype=dtype)
        vertices = torch.cat((vertices, vertices_normals), dim=-1)

    if len(mesh_o3d.vertex_colors) > 0:
        vertices_colors = torch.tensor(np.asarray(mesh_o3d.vertex_colors), dtype=dtype)
        vertices = torch.cat((vertices, vertices_colors), dim=-1)

    triangles = torch.tensor(np.asarray(mesh_o3d.triangles), dtype=dtype)

    if len(mesh_o3d.triangle_normals) > 0:
        triangles_normals = torch.tensor(np.asarray(mesh_o3d.triangle_normals), dtype=dtype)
        triangles = torch.cat((triangles, triangles_normals), dim=-1)

    return vertices, triangles


def get_o3d_mesh_from_tensors(
    vertices: Union[Tensor, np.ndarray],
    triangles: Union[Tensor, np.ndarray],
) -> o3d.geometry.TriangleMesh:
    """Get open3d mesh from either numpy arrays or torch tensors.

    The input vertices must have shape (NUM_VERTICES, D), where D can be 3 (only X,Y,Z),
    6 (X,Y,Z and normals) or 9 (X,Y,Z, normals and colors). The input triangles
    must have shape (NUM_TRIANGLES, D), where D can be 3 (only vertex indices)
    or 6 (vertex indices and normals).

    Args:
        vertices: The numpy array or torch tensor with vertices with shape (NUM_VERTICES, D).
        triangles: The numpy array or torch tensor with triangles with shape (NUM_TRIANGLES, D).

    Returns:
        The open3d mesh.
    """
    mesh_o3d = o3d.geometry.TriangleMesh()

    if isinstance(vertices, Tensor):
        v = vertices.clone().detach().cpu().numpy()
    else:
        v = np.copy(vertices)

    if isinstance(triangles, Tensor):
        t = triangles.clone().detach().cpu().numpy()
    else:
        t = np.copy(triangles)

    mesh_o3d.vertices = o3d.utility.Vector3dVector(v[:, :3])

    if v.shape[1] == 6:
        mesh_o3d.vertex_normals = o3d.utility.Vector3dVector(v[:, 3:6])

    if v.shape[1] == 9:
        mesh_o3d.vertex_colors = o3d.utility.Vector3dVector(v[:, 6:9])

    mesh_o3d.triangles = o3d.utility.Vector3iVector(t[:, :3])

    if t.shape[1] == 6:
        mesh_o3d.triangle_normals = o3d.utility.Vector3dVector(t[:, 3:6])

    return mesh_o3d


@torch.no_grad()  # type: ignore
def marching_cubes(
    levelset_func: Callable[[Tensor], Tensor],
    coords_range: Tuple[float, float] = (-1, 1),
    resolution: int = 256,
    max_batch: int = 100_000,
    level: float = 0.0,
) -> Tuple[Tensor, Tensor]:
    """Perform marching cubes to obtain the surface corresponding
    to the level set represented by levelset_func.

    Args:
        levelset_func: A function that can be called with a tensor containing some
            coordinates to evaluate the level set at those coordinates.
        coords_range: The range for the coordinates to query levelset_func with.
        resolution: The SDF sampling resolution. Defaults to 256.
        max_batch: The max batch size used to query levelset_func. Defaults to 100_000.
        level: The surface level set. Defaults to 0.

    Returns:
        - The vertices of the computed mesh as a torch tensor with shape (N, 6).
            The first 3 values are X,Y,Z coordinates, while the last 3 are the normals.
        - The faces of the computed mesh as a torch tensor with shape (M, 3).
    """
    origin = [coords_range[0]] * 3
    spacing = (coords_range[1] - coords_range[0]) / (resolution - 1)

    coords_indices = torch.arange(0, resolution**3, 1)
    coords = torch.zeros(resolution**3, 4)

    coords[:, 2] = coords_indices % resolution
    coords[:, 1] = (coords_indices.long() / resolution) % resolution
    coords[:, 0] = ((coords_indices.long() / resolution) / resolution) % resolution

    coords[:, 0] = (coords[:, 0] * spacing) + origin[2]
    coords[:, 1] = (coords[:, 1] * spacing) + origin[1]
    coords[:, 2] = (coords[:, 2] * spacing) + origin[0]

    num_samples = resolution**3
    start = 0

    while start < num_samples:
        end = min(start + max_batch, num_samples)
        coords_subset = coords[start:end, :3].cuda()
        sdf = levelset_func(coords_subset).squeeze(-1).cpu()
        coords[start:end, 3] = sdf
        start += max_batch

    sdf = coords[:, 3].reshape(resolution, resolution, resolution)

    verts, faces, v_normals, _ = sk_marching_cubes(sdf.numpy(), level=level, spacing=[spacing] * 3)

    verts += coords_range[0]

    vertices = torch.tensor(verts.copy())
    normals = torch.tensor(v_normals.copy())
    vertices = torch.cat((vertices, normals), dim=-1)

    faces = torch.tensor(faces.copy())

    return vertices, faces


def compute_sdf_from_mesh(
    mesh_o3d: o3d.geometry.TriangleMesh,
    method: str = "raycasting",
    num_surface_points: int = 10_000,
    queries_stds: List[float] = [0.003, 0.01, 0.1],
    num_queries_per_std: List[int] = [5_000, 4_000, 500, 500],
    coords_range: Tuple[float, float] = (-1.0, 1.0),
    max_dist: float = 0.1,
    compute_occupancy: bool = False,
    use_cuda: bool = True,
) -> Tuple[Tensor, Tensor]:
    """Compute the signed distance function or the occupancy field for a given mesh.

    Query points are sampled by adding gaussian noise to points sampled
    on the surface of the mesh, according to the given standard deviations.
    Additionally, query points are also sampled uniformly in the given range.
    Distances are clipped to max_dist.

    Two methods are available:
    - raycasting: it works only for watertight meshes.
    - normals: it works also for non-watertight meshes, but only
        if accurate normals are provided.

    Args:
        mesh_o3d: The open3d mesh.
        method: The method to be used between "raycasting" and "normals".
        num_surface_points: The number of points to sample from the surface.
        queries_stds: A list of standard deviations to compute the gaussian noise
            to obtain query points. Defaults to [0.003, 0.01, 0.1].
        num_queries_per_std: A list with the number of query points to compute for each
            standard deviation. The last number refers to query points sampled
            uniformly in the given range (len(num_queries_per_std) = len(queries_std) + 1).
            Defaults to [5_000, 4_000, 500, 500].
        coords_range: The range for the queries coordinates.
        max_dist: The clip value for computed distances. Defaults to 0.1.
        compute_occupancy: If True, compute occupancy instead of sdf. Defaults to False.
        use_cuda: If True, use CUDA to speed up KNN (for method "normals"). Defaults to True.

    Returns:
        - The tensor with the query coordinates with shape (N, 3).
        - The tensor with the computed sdf or occupancy with shape (N,).
    """
    assert method.lower() in ["raycasting", "normals"]

    if method.lower() == "raycasting":
        scene = o3d.t.geometry.RaycastingScene()
        vertices = np.asarray(mesh_o3d.vertices, dtype=np.float32)
        triangles = np.asarray(mesh_o3d.triangles, dtype=np.uint32)
        _ = scene.add_triangles(vertices, triangles)

        pcd_o3d = mesh_o3d.sample_points_uniformly(number_of_points=num_surface_points)
        pcd = get_tensor_pcd_from_o3d(pcd_o3d)[:, :3]

        queries = sample_points_around_pcd(pcd, queries_stds, num_queries_per_std, coords_range)

        if compute_occupancy:
            occ_o3d = scene.compute_occupancy(queries.numpy())
            values = torch.tensor(occ_o3d.numpy())
        else:
            sdf_o3d = scene.compute_signed_distance(queries.numpy())
            sdf = torch.tensor(sdf_o3d.numpy())
            values = torch.clip(sdf, min=-max_dist, max=max_dist)
    else:
        pcd_o3d = mesh_o3d.sample_points_uniformly(
            number_of_points=num_surface_points,
            use_triangle_normal=True,
        )

        queries, values = compute_sdf_from_pcd(
            pcd_o3d,
            queries_stds,
            num_queries_per_std,
            coords_range,
            max_dist,
            compute_occupancy,
            use_cuda,
        )

    return queries, values
