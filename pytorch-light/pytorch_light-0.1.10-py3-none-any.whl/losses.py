# -*- coding: utf-8 -*-

from typing import Union

import torch
import torch.nn as nn


def manhattan_similarity(v1: torch.Tensor, v2: torch.Tensor) -> torch.Tensor:
    return torch.exp(-torch.norm(v1 - v2, p=1, dim=-1, keepdim=True))


class ManhattanSimilarity(nn.Module):
    def forward(
        self, v1: torch.Tensor, v2: torch.Tensor
    ) -> torch.Tensor:  # pylint: disable=no-self-use
        return manhattan_similarity(v1, v2)


class HingeLoss(nn.Module):
    def __init__(self, margin: Union[float, torch.Tensor] = 1.0):
        super().__init__()
        self.margin = margin

    def forward(
        self, positive_logits: torch.Tensor, negative_logits: torch.Tensor
    ) -> torch.Tensor:
        return torch.mean(
            torch.clamp(negative_logits + self.margin - positive_logits, 0)
        )
