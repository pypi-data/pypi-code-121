from typing import Tuple

import pytorch3d.transforms.transform3d as pt3d  # type: ignore
import torch
from pytorch3d.transforms.rotation_conversions import _axis_angle_rotation  # type: ignore
from torch import Tensor

from pycarus.geometry.pcd import apply_affine_to_pcd, farthest_point_sampling
from pycarus.geometry.pcd import get_neighbouring_points, jitter_pcd, normalize_pcd_into_unit_cube
from pycarus.geometry.pcd import normalize_pcd_into_unit_sphere, random_drop_points
from pycarus.geometry.pcd import random_point_sampling, rotate_pcd, scale_pcd, shuffle_pcd
from pycarus.geometry.pcd import translate_pcd


class SamplePcd:
    def __init__(self, num_points: int, algorithm: str) -> None:
        """Subsample the input point cloud(s) using the given algorithm.

        Args:
            num_points: Number of point to sample.
            algorithm: the algorithm to use for the subsampling between ["fps", "random"].
        """
        self.num_points = num_points
        self.algorithm = algorithm

        if self.algorithm not in ["fps", "random"]:
            raise ValueError(f"Expected type to be one of [fps, random], got {algorithm}")

    def __call__(self, pcd: Tensor) -> Tensor:
        """Sample point cloud.

        Args:
            pcd: The input point cloud with shape (NUM_POINTS, D).

        Returns:
            The sampled point cloud.
        """
        pcd_ss = torch.tensor([])
        if self.algorithm == "fps":
            pcd_ss = farthest_point_sampling(pcd, self.num_points)

        if self.algorithm == "random":
            pcd_ss = random_point_sampling(pcd, self.num_points)

        return pcd_ss

    def __repr__(self) -> str:
        format_string = f"{self.__class__.__name__}: num_points: {self.num_points}"
        format_string += f" - algorithm: {self.algorithm}."
        return format_string


class NormalizePcdIntoUnitSphere:
    """Normalize a given point cloud into the unit sphere."""

    def __call__(self, pcd: Tensor) -> Tensor:
        """Normalize a point cloud.

        Args:
            pcd: The input point cloud with shape (NUM_POINTS, D).

        Returns:
            The normalized point cloud.
        """
        return normalize_pcd_into_unit_sphere(pcd)


class NormalizePcdIntoUnitCube:
    """Normalize a given point cloud into the unit cube."""

    def __call__(self, pcd: Tensor) -> Tensor:
        """Normalize a point cloud.

        Args:
            pcd: The input point cloud with shape (NUM_POINTS, D).

        Returns:
            The normalized point cloud.
        """
        return normalize_pcd_into_unit_cube(pcd)


class AffinePcd(pt3d.Transform3d):
    def __init__(self, matrix: Tensor) -> None:
        """Transform to apply an affine transformation, i.e. rotation plus a translation.

        Args:
            matrix: The motion matrix with shape (4, 4).
        """
        self.matrix = matrix
        super().__init__(matrix=self.matrix)

    def __call__(self, pcd: Tensor) -> Tensor:
        return apply_affine_to_pcd(pcd, self.matrix)


class RotatePcd(pt3d.Rotate):
    def __init__(self, rotation: Tensor) -> None:
        """Transform to rotate a point cloud.

        Args:
            rotation: The rotation matrix with shape (3, 3).
        """
        self.rotation = rotation
        super().__init__(self.rotation)

    def __call__(self, pcd: Tensor) -> Tensor:
        return rotate_pcd(pcd, self.rotation)


class RandomRotatePcdAroundAxis:
    def __init__(self, axis: str, min_angle: float = 0, max_angle: float = 180):
        """Rotate a point cloud around one axis by a random angle sampled within a range.

        Args:
            min_angle: the lower bound for the angle in radians.
            max_angle: the upper bound for the angle in radians.
            axis: the axis of rotation.

        Raises:
            ValueError: if the required axis is different from [X, Y, Z].
        """
        self.axis = axis.upper()

        if axis not in ["X", "Y", "Z"]:
            raise ValueError(f"Expected axis to be one of [X, Y, Z], got {axis}")

        self.min_angle = float(torch.deg2rad(torch.tensor(float(min_angle))).item())
        self.max_angle = float(torch.deg2rad(torch.tensor(float(max_angle))).item())
        self.last_matrix = torch.eye(3)

    @staticmethod
    def _get_params(min_angle: float, max_angle: float, axis: str) -> Tensor:
        """Get random rotation matrix with an angle in the range min_angle - max_angle.

        Args:
            min_angle: the lower bound for the angle in radians.
            max_angle: the upper bound for the angle in radians.
            axis: the axis of rotation.

        Returns:
            The rotation matrix with shape (3, 3).
        """
        theta = torch.FloatTensor(1).uniform_(min_angle, max_angle)
        matrix = _axis_angle_rotation(axis, theta)[0]
        # _axis_angle_rotation returns a rotation matrix thought to operate
        # on column vectors, since we use row vectors we need to transpose
        matrix = matrix.transpose(0, 1)
        return matrix

    def __call__(self, pcd: Tensor) -> Tensor:
        self.last_matrix = self._get_params(self.min_angle, self.max_angle, self.axis)
        return rotate_pcd(pcd, self.last_matrix)

    def __repr__(self) -> str:
        format_string = f"{self.__class__.__name__}: min_angle: {self.min_angle}"
        format_string += f" - max_angle: {self.max_angle} - axis: {self.axis}."

        return format_string


class TranslatePcd(pt3d.Translate):
    def __init__(self, translation: Tensor) -> None:
        """Transform to translate a point cloud.

        Args:
            translation: The translation offset with shape (3,).
        """
        self.translation = translation
        x, y, z = translation[0], translation[1], translation[2]
        super().__init__(x=x, y=y, z=z)

    def __call__(self, pcd: Tensor) -> Tensor:
        return translate_pcd(pcd, self.translation)


class RandomTranslatePcd:
    def __init__(self, min_tr: float = -0.5, max_tr: float = 0.5) -> None:
        """Transform to translate randomly a point cloud.

        Args:
            min_tr: The minimum translation.
            max_tr: The maximum translation.
        """
        self.min_tr = min_tr
        self.max_tr = max_tr

    def __call__(self, pcd: Tensor) -> Tensor:
        transl = torch.rand((3,)) * (self.max_tr - self.min_tr) + self.min_tr
        return translate_pcd(pcd, transl)


class ScalePcd(pt3d.Scale):
    def __init__(self, scale_factor: Tensor) -> None:
        """Transform to scale a point cloud.

        Args:
            scale_factor: The scale factor for the x, y, z, dimensions with shape (3,).
        """
        self.scale_factor = scale_factor
        x, y, z = scale_factor[0], scale_factor[1], scale_factor[2]
        super().__init__(x=x, y=y, z=z)

    def __call__(self, pcd: Tensor) -> Tensor:
        return scale_pcd(pcd, self.scale_factor)


class RandomScalePcd:
    def __init__(self, min_scale: float = 0.5, max_scale: float = 1.5) -> None:
        """Transform to scale randomly a point cloud.

        Args:
            min_scale: The minimum scale factor.
            max_scale: The maximum scale factor.
        """
        self.min_scale = min_scale
        self.max_scale = max_scale

    def __call__(self, pcd: Tensor) -> Tensor:
        scale = torch.rand((3,)) * (self.max_scale - self.min_scale) + self.min_scale
        return scale_pcd(pcd, scale)


class JitterPcd:
    def __init__(self, sigma: float, clip: float) -> None:
        """Jitter point cloud by adding random noise.

        Args:
            sigma: The sigma for the gaussian noise.
            clip: The clipping value.
        """
        self.sigma = sigma
        self.clip = clip

    def __call__(self, pcd: Tensor) -> Tensor:
        return jitter_pcd(pcd, self.sigma, self.clip)


class RandomDropPcd:
    def __init__(self, min_percentage: float, max_percentage: float) -> None:
        """Remove random percentage of points from a point cloud. The number of points is uniformly
        sampled in the range min_percentage - max_percentage.

        Args:
            min_percentage: The lower bound for the percentage of points to remove.
            max_percentage: The upper bound for the percentage of points to remove.
        """
        self.min_percentage = min_percentage
        self.max_percentage = max_percentage
        self.drop_percentage = 0.0
        self.last_kept = torch.tensor([])
        self.last_removed = torch.tensor([])

    @staticmethod
    def _get_params(min_percentage: float, max_percentage: float) -> float:
        """Get random number in the range min_percentage - max_percentage.

        Args:
            min_percentage: the lower bound for the percentage.
            max_percentage: the upper bound for the percentage.

        Returns:
            A random number in the specified range.
        """
        random_percentage = torch.FloatTensor(1).uniform_(min_percentage, max_percentage)[0].item()
        return float(random_percentage)

    def __call__(self, pcd: Tensor) -> Tensor:
        self.last_drop_percentage = self._get_params(self.min_percentage, self.max_percentage)
        points, indices_kept, indices_removed = random_drop_points(pcd, self.last_drop_percentage)
        self.last_kept = indices_kept
        self.last_removed = indices_removed

        return points

    def __repr__(self) -> str:
        format_string = f"{self.__class__.__name__}: min_percentage: {self.min_percentage}"
        format_string += f" - max_percentage: {self.max_percentage}."

        return format_string


class ShufflePcd:
    """Shuffle the order of the points inside the point cloud."""

    def __call__(self, pcd: Tensor) -> Tensor:
        return shuffle_pcd(pcd)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}"


class Patcher:
    """Extract patches from a point cloud."""

    def __init__(self, num_points_per_patch: int, radius: float) -> None:
        """Create a Patcher.

        Args:
            num_points_per_patch: The number of points for each patch.
            radius: Radius for the for radius based search.
        """
        self.num_points_per_patch = num_points_per_patch
        self.radius = radius

    def __call__(self, pcd: Tensor, kpts: Tensor) -> Tuple[Tensor, Tensor]:
        """Get a predefined number of patches from given point cloud(s).
        Each patch will have the same number of points with coordinates
        centered on the patch keypoint.

        Args:
            pcd: The input point cloud(s) with shape ([B,] NUM_POINTS, D).
            kpts: The selected keypoints, one for each patch, with shape ([B,] NUM_PATCHES, 3).

        Returns:
            - The global indices with shape ([B,] NUM_PATCHES, NUM_POINTS_PER_PATCH).
            - The patches with shape ([B,] NUM_PATCHES, NUM_POINTS_PER_PATCH, D).
        """
        indices, patches = get_neighbouring_points(
            pcd,
            kpts,
            self.num_points_per_patch,
            self.radius,
        )

        patches -= kpts.unsqueeze(-2)

        return indices, patches
