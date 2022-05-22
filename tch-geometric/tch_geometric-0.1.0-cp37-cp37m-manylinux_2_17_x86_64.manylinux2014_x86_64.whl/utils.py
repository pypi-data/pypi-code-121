from dataclasses import dataclass
from typing import List
from typing import Union, Dict, Tuple

import torch
from torch import Tensor
from torch_geometric.typing import EdgeType

NumNeighbors = Union[List[int], Dict[EdgeType, List[int]]]

MixedData = Union[Tensor, Dict[str, Tensor]]
HeteroTensor = Dict[str, Tensor]

Timerange = Tuple[int, int]


def validate_mixeddata(data: MixedData, hetero: bool = False, dtype=None):
    if hetero:
        assert isinstance(data, dict)
        for v in data.values():
            assert v.dtype == dtype
    else:
        assert data.dtype == dtype


@dataclass
class EdgeSampler:
    def validate(self, hetero: bool = False) -> None:
        raise NotImplementedError


@dataclass
class UniformEdgeSampler(EdgeSampler):
    with_replacement: bool = False

    def validate(self, hetero: bool = False) -> None:
        pass


@dataclass
class WeightedEdgeSampler(EdgeSampler):
    weights: MixedData

    def validate(self, hetero: bool = False) -> None:
        validate_mixeddata(self.weights, hetero=hetero, dtype=torch.float64)


TEMPORAL_SAMPLE_STATIC: int = 0
TEMPORAL_SAMPLE_RELATIVE: int = 1
TEMPORAL_SAMPLE_DYNAMIC: int = 2


@dataclass
class EdgeFilter:
    def validate(self, hetero: bool = False) -> None:
        raise NotImplementedError


@dataclass
class TemporalEdgeFilter:
    window: Tuple[int, int]
    timestamps: MixedData
    forward: bool = False
    mode: int = TEMPORAL_SAMPLE_STATIC

    def validate(self, hetero: bool = False) -> None:
        validate_mixeddata(self.timestamps, hetero=hetero, dtype=torch.int64)
