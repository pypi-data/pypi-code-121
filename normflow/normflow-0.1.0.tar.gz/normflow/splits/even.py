
import torch

from typing import Tuple

from .base import Split


class EvenSplit(Split):
    """
    Split input into sections of even size along the given dimension
    """
    def __init__(self, sections: int = 2, dim: int = -1):
        super().__init__()
        self.sections = sections
        self.dim = dim

    def forward(self, x: torch.Tensor) -> Tuple[torch.Tensor, ...]:
        return torch.tensor_split(x, self.sections, self.dim)

    def inverse(self, zs: Tuple[torch.Tensor, ...]) -> torch.Tensor:
        return torch.cat(zs, dim=self.dim)
