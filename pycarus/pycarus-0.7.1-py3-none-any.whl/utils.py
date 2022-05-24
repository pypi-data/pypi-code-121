"""
Module containing generic utils functions.
"""
import hashlib
import ssl
from pathlib import Path
from shutil import unpack_archive
from typing import Callable, Iterable, List, Optional, Tuple, Union
from urllib import request

import matplotlib.pyplot as plt  # type: ignore
import numpy as np
import open3d as o3d  # type: ignore
import torch
from matplotlib import cm
from matplotlib.colors import Normalize  # type: ignore
from PIL import Image  # type: ignore
from sklearn.manifold import TSNE  # type: ignore
from torch import Tensor
from tqdm import tqdm  # type: ignore

from pycarus.geometry.pcd import get_o3d_pcd_from_tensor


def download_file(url: str, path: Path, print_progress: bool) -> None:
    """Download file from URL to path.

    Args:
        url: the url from which to download the file.
        path: the path and file name for the downloaded file.
        print_progress: if True print a progress bar while downloading the file.
    """

    def updater_callback() -> Callable[[int, int, int], None]:
        pbar = tqdm(total=None)

        def bar_update(count: int, block_size: int, total_size: int) -> None:
            if pbar.total is None and total_size:
                pbar.total = total_size
            progress_bytes = count * block_size
            pbar.update(progress_bytes - pbar.n)

        return bar_update

    ssl._create_default_https_context = ssl._create_unverified_context
    fn_callback = updater_callback() if print_progress else None
    request.urlretrieve(url, path, reporthook=fn_callback)


def check_integrity(path: Path, md5_hash: Optional[str] = None) -> bool:
    """Check the integrity of a file.

    The integrity of the file is ensured by checking if the path points to a file. Eventually,
    the md5 digest will be checked if it is not None.

    Args:
        path: the path to the file.
        md5_hash: the md5_hash has to check. the Defaults to None.

    Returns:
        True if the check is passed.
    """
    if not path.is_file:
        return False

    if md5_hash is not None:
        return md5_hash == get_md5(path)

    return True


def get_md5(path: Path, chunk_size: int = 1024 * 1024) -> str:
    """Compute the MD5 hash value, to handle big files the function splits the file in chunks.

    Args:
        path: the path to the file.
        chunk_size: the size for the chunk (multiple of 128). Defaults to 1024*1024.

    Returns:
        The hex string representation for the MD5 digest.
    """
    hash_md5 = hashlib.md5()

    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(chunk_size), b""):
            hash_md5.update(chunk)

    return hash_md5.hexdigest()


def download_and_extract(
    url: str,
    path_file_downloaded: Path,
    path_destination: Path,
    md5_hash: Optional[str] = None,
) -> None:
    """Download a compressed file from the url and extract it into path_destination.

    Args:
        url: the url from which download the file.
        path_file_downloaded: the path in which to save the downloaded file.
        path_destination: the path in which extract the content of the file.
        md5_hash (optional): the hash digest to use to check the integrity of the file.

    Raises:
        RuntimeError: if the downloaded file is not correct.
    """
    path_file_downloaded.parent.mkdir(exist_ok=True)
    download_file(url, path_file_downloaded, True)

    if not check_integrity(path_file_downloaded, md5_hash):
        raise RuntimeError(f"File {str(path_file_downloaded)} not found or corrupted.")

    unpack_archive(str(path_file_downloaded), path_destination)
    path_file_downloaded.unlink()


def get_tsne(
    data: Union[torch.Tensor, np.ndarray],
    n_components: int = 1,
    verbose: int = 1,
    perplexity: float = 40.0,
    n_iter: int = 300,
    random_state: int = 0,
) -> torch.Tensor:
    """Compute the t-SNE for each sample. NaN values converted to zero.

    Args:
        data: The input data with shape (N, N_DIMS)
        n_components: The component for the embedded space. Defaults to 1.
        verbose: The verbosity. Defaults to 1.
        perplexity: The perplexity is related to the number of nearest neighbors used.
                    Defaults to 40.0.
        n_iter: Maximum iterations for the optimization. Should be at least 250. Defaults to 300.
        random_state: The random number generator. Defaults to 0.

    Returns:
        The computed t-SNE with shape (N, n_components) normalized.
    """
    if isinstance(data, torch.Tensor):
        data = data.cpu().numpy()

    data = np.nan_to_num(data)
    tsne = TSNE(
        n_components=n_components,
        verbose=verbose,
        perplexity=perplexity,
        n_iter=n_iter,
        random_state=random_state,
    )
    results = np.squeeze(tsne.fit_transform(data))
    min_val = np.min(results)
    max_val = np.max(results)
    normalized_results = (results - min_val) / (max_val - min_val)

    return torch.tensor(normalized_results)


def apply_color_map(
    values: Union[torch.Tensor, np.ndarray],
    vmin: Optional[float] = None,
    vmax: Optional[float] = None,
    name_map: str = "Spectral",
) -> torch.Tensor:
    """Map each scalar value in values to a color using a color map in matplotlib.

    Args:
        values: The input values as a torch tensor with shape (N,).
        vmin: The minimum value to normalize values. If None, it is computed
              directly on values.
        vmax: The maximum value to normalize values. If None, it is computed
              directly on values.
        name_map: The color map to use. Defaults to "Spectral".

    Returns:
        RGB color for each sample with shape (N, 3).
    """
    if isinstance(values, torch.Tensor):
        values = values.cpu().numpy()
    cmap = cm.get_cmap(name_map)

    normalize = Normalize(vmin, vmax)
    values = normalize(values)
    colored = cmap(values)[:, :3]

    return torch.Tensor(colored)


def get_conf_matrix_img(conf_matrix: np.ndarray, size: int = 600) -> Image.Image:
    """Create a confusion matrix image.

    Args:
        conf_matrix: The confusion matrix.
        size: The output image size in pixels. Defaults to 600.

    Returns:
        The confusion matrix image as PIL Image.
    """
    c_mat = np.nan_to_num(conf_matrix).astype(np.float32)
    h, w = c_mat.shape[0], c_mat.shape[1]

    for i in range(h):
        vmin = np.min(c_mat[i, :])
        vmax = np.max(c_mat[i, :])
        if vmax > 0:
            c_mat[i, :] = (c_mat[i, :] - vmin) / (vmax - vmin)

    zoom = size // h

    img = np.empty((h * zoom, w * zoom), dtype=np.float32)

    for i in range(h):
        for j in range(w):
            hstart = i * zoom
            hend = (i + 1) * zoom
            wstart = j * zoom
            wend = (j + 1) * zoom
            img[hstart:hend, wstart:wend] = c_mat[i, j]

    normalize = Normalize()
    cmap = cm.get_cmap("Blues")
    img = cmap(normalize(img))

    dpi = 100
    figsize = ((w * zoom) / dpi, (h * zoom) / dpi)
    fig, ax = plt.subplots(figsize=figsize, dpi=dpi)

    fontsize = max(zoom / 10, 8)

    ax.set_xticks(np.arange(0, w) * zoom + (zoom / 2))
    ax.set_xticklabels([str(i) for i in range(w)], fontsize=fontsize)
    ax.set_yticks(np.arange(0, h) * zoom + (zoom / 2))
    ax.set_yticklabels([str(i) for i in range(h)], fontsize=fontsize)

    ax.imshow(img)

    for i in range(h):
        ax.plot(
            [0, w * zoom - 1],
            [(i * zoom + (zoom / 2)), (i * zoom + (zoom / 2))],
            linestyle=":",
            c="black",
            alpha=0.1,
        )

    for i in range(w):
        ax.plot(
            [(i * zoom + (zoom / 2)), (i * zoom + (zoom / 2))],
            [0, h * zoom - 1],
            linestyle=":",
            c="black",
            alpha=0.1,
        )

    fig.tight_layout()
    fig.canvas.draw()
    pilimg = Image.frombytes("RGB", fig.canvas.get_width_height(), fig.canvas.tostring_rgb())

    plt.close(fig)

    return pilimg


def progress_bar(iterable: Iterable, desc: str = "", num_cols: int = 60) -> Iterable:
    """Decorate an iterable object using a progress bar.

    Args:
        iterable: the iterable to decorate.
        desc: the description to print. Defaults to "".
        num_cols: The width of the entire output message. Defaults to 60.

    Returns:
        The decorated iterable.
    """
    bar_format = "{percentage:.0f}%|{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}]"
    if len(desc) > 0:
        bar_format = "{desc}: " + bar_format
    return tqdm(iterable, desc=desc, bar_format=bar_format, ncols=num_cols, leave=False)


def get_points_as_o3d_spheres(
    pcd: Union[Tensor, np.ndarray],
    radius: float,
    color: Tuple[float, float, float] = (1.0, 0.0, 0.0),
    colors: Optional[List[Tuple[float, float, float]]] = None,
) -> List[o3d.geometry.TriangleMesh]:
    """Get one sphere for each point of the given point cloud.

    Args:
        pcd: The input point cloud either as a numpy array or torch tensor.
        radius: The radius for each sphere.
        color: The color for all the spheres.
        colors: The list of colors, one for each sphere (optional).

    Returns:
        The list of spheres as o3d meshes.
    """
    pcd_o3d = get_o3d_pcd_from_tensor(pcd)
    spheres: List[o3d.geometry.TriangleMesh] = []

    for i, point in enumerate(pcd_o3d.points):
        sphere = o3d.geometry.TriangleMesh.create_sphere(radius=radius)
        sphere_color = colors[i] if colors else color
        sphere.paint_uniform_color(sphere_color)

        sphere.translate(np.asarray(point))

        spheres.append(sphere)

    return spheres


def get_o3d_cube(vmin: float = 0, vmax: float = 1) -> o3d.geometry.LineSet:
    """Get the o3d object corresponding to an empty cube.

    Args:
        vmin: Minimum value for the cube coordinates. Defaults to 0.
        vmax: Maximum value for the cube coordinates. Defaults to 1.

    Returns:
        The o3d LineSet corresponing to the empty cube.
    """
    points = [
        [vmin, vmin, vmin],
        [vmin, vmin, vmax],
        [vmin, vmax, vmin],
        [vmin, vmax, vmax],
        [vmax, vmin, vmin],
        [vmax, vmin, vmax],
        [vmax, vmax, vmin],
        [vmax, vmax, vmax],
    ]

    lines = [
        [0, 1],
        [0, 2],
        [0, 4],
        [1, 3],
        [1, 5],
        [2, 3],
        [2, 6],
        [3, 7],
        [4, 5],
        [4, 6],
        [5, 7],
        [6, 7],
    ]

    colors = [[0, 0, 0] for _ in lines]

    cube_o3d = o3d.geometry.LineSet()
    cube_o3d.points = o3d.utility.Vector3dVector(points)
    cube_o3d.lines = o3d.utility.Vector2iVector(lines)
    cube_o3d.colors = o3d.utility.Vector3dVector(colors)

    return cube_o3d
