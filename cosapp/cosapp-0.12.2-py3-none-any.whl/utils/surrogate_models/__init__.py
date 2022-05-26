"""
Copyright (c) 2016-2018, openmdao.org

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this software except in compliance with the License.
You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

This package comes from OpenMDAO 2.2.0. It was modified for CoSApp integration.
"""

from.base import (
    SurrogateModel,
    MultiFiSurrogateModel,
)
from .kriging import (
    KrigingSurrogate,
    FloatKrigingSurrogate,
)
from .multifi_cokriging import (
    MultiFiCoKrigingSurrogate,
    FloatMultiFiCoKrigingSurrogate,
)
from .nearest_neighbor import (
    NearestNeighbor,
    LinearNearestNeighbor,
    WeightedNearestNeighbor,
    RBFNearestNeighbor,
)
from .response_surface import ResponseSurface

__all__ = [
    "SurrogateModel",
    "MultiFiSurrogateModel",
    "KrigingSurrogate",
    "FloatKrigingSurrogate",
    "MultiFiCoKrigingSurrogate",
    "FloatMultiFiCoKrigingSurrogate",
    "NearestNeighbor",
    "LinearNearestNeighbor",
    "WeightedNearestNeighbor",
    "RBFNearestNeighbor",
    "ResponseSurface",
]