
import torch

from typing import List, Tuple, Union

from .base import Split


class RandomSelect(Split):
    """
    Split input by selecting the given number of random indices along the given axis
    """
    def __init__(self, sizes: Union[Tuple[int, ...], List[int]], dim: int = -1):
        super().__init__()
        self.sizes = sizes
        self.permutation = torch.randperm(sum(sizes))
        self.inverse_permutation = torch.argsort(self.permutation)
        self.dim = dim

    def forward(self, x: torch.Tensor) -> Tuple[torch.Tensor, ...]:
        permuted = torch.index_select(x, dim=self.dim, index=self.permutation.to(x.device))

        return torch.split(permuted, self.sizes, self.dim)

    def inverse(self, zs: Tuple[torch.Tensor, ...]) -> torch.Tensor:
        z = torch.cat(zs, dim=self.dim)

        return torch.index_select(z, dim=self.dim, index=self.inverse_permutation.to(z.device))

