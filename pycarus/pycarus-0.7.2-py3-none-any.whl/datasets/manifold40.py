from pathlib import Path
from typing import Callable, List, Tuple, Union

import torch
from torch import Tensor
from torch.utils.data import Dataset

from pycarus.geometry.mesh import read_mesh
from pycarus.transforms.var import Compose


class Manifold40(Dataset):
    """Manifold40 Dataset, as proposed in
    Hu, Shi-Min, et al. "Subdivision-Based Mesh Convolution Networks."
    """

    def __init__(
        self,
        root: Union[Path, str],
        split: str,
        only_version: int = -1,
        vertices_transforms: List[Callable] = [],
        triangles_transforms: List[Callable] = [],
        pad_vertices_to: int = 6200,
        pad_triangles_to: int = 12_300,
    ) -> None:
        """Create an instance of Manifold40 dataset.

        Args:
            root: The path to the root directory of the dataset.
            split: The split to use (only "train", "val" and "test" allowed).
            only_version: The original dataset contains 10 versions of each shape,
                numbered from 0 to 9. This argument can be used to get only the
                specified version. If it is equal to -1, then all versions are returned.
                All versions are always returned for the test split.
            vertices_transforms: The transform to apply to the vertices of
                each item. Defaults to [].
            triangles_transforms: The transform to apply to the triangles of
                each item. Defaults to [].
            pad_vertices_to: If greater than 0, the vertices will be padded with
                zeros to obtain a tensor with the required number of vertices.
                Defaults to 6200, which is the maximum number of vertices
                of a shape in the dataset.
            pad_triangles_to: If greater than 0, the triangles will be padded with
                zeros to obtain a tensor with the required number of triangles.
                Defaults to 12_300, which is the maximum number of triangles
                of a shape in the dataset.
        """
        if split not in ["train", "val", "test"]:
            raise ValueError("Only train, val and test splits are available.")

        self.root = Path(root)

        self.classes = sorted([s.name for s in self.root.iterdir()])

        self.paths: List[Path] = []
        self.labels: List[Tensor] = []

        for i, c in enumerate(self.classes):
            class_path = self.root / c / split

            items_paths = sorted(list(class_path.glob("*.obj")))
            for p in items_paths:
                if "test" in split or only_version == -1 or f"-{only_version}.obj" in p.name:
                    self.paths.append(p)
                    self.labels.append(torch.tensor(i, dtype=torch.long))

        self.vertices_transform = Compose(vertices_transforms)
        self.triangles_transform = Compose(triangles_transforms)

        self.pad_vertices_to = pad_vertices_to
        self.pad_triangles_to = pad_triangles_to

    def __len__(self) -> int:
        """Return the number of meshes in the dataset.

        Returns:
            The number of meshes in the dataset.
        """
        return len(self.paths)

    def __getitem__(self, index: int) -> Tuple[Tensor, Tensor, Tensor, int, int]:
        """Return the vertices, the triangles and the label at the given index.

        Args:
            index: The index of the required element.

        Returns:
            - A tensor with the vertices with shape (N, D). D can be 3, 6 or 9
                depending on the availability of normals and colors.
            - A tensor with the triangles with shape (M, D). D can be 3 or 6
                depending on the availability of normals.
            - A tensor with the label.
            - The original number of vertices before padding (if performed).
            - The original number of triangles before padding (if performed).
        """
        vertices, triangles = read_mesh(self.paths[index])
        vertices = self.vertices_transform(vertices)
        triangles = self.triangles_transform(triangles)

        num_vertices = vertices.shape[0]
        num_triangles = triangles.shape[0]

        if self.pad_vertices_to > 0:
            padded_vertices = torch.zeros((self.pad_vertices_to, 3))
            padded_vertices[:num_vertices] = vertices
            vertices = padded_vertices

        if self.pad_triangles_to > 0:
            padded_triangles = torch.zeros((self.pad_triangles_to, 3))
            padded_triangles[:num_triangles] = triangles
            triangles = padded_triangles

        return vertices, triangles, self.labels[index], num_vertices, num_triangles

    def get_class(self, label: int) -> str:
        """Return the name of the class with the given label.

        Args:
            label: The numeric label of the required class.

        Returns:
            The name of the class corresponding to the given label.
        """
        return self.classes[label]
