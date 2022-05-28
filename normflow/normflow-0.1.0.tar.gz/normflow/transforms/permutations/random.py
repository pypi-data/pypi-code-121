
import torch

from .index import IndexPermutation


class RandomPermutation(IndexPermutation):
    """ Applies a Fixed Random Shuffle on Input """
    def __init__(self, features: int, dim: int = -1) -> None:
        permutation = torch.randperm(features)
        super().__init__(permutation, dim)
