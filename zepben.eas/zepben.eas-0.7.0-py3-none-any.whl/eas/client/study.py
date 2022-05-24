#  Copyright 2020 Zeppelin Bend Pty Ltd
#
#  This Source Code Form is subject to the terms of the Mozilla Public
#  License, v. 2.0. If a copy of the MPL was not distributed with this
#  file, You can obtain one at https://mozilla.org/MPL/2.0/.

from dataclasses import dataclass, field
from typing import List, Any

from geojson import GeoJSON

__all__ = ["GeoJsonOverlay", "StateOverlay", "Section", "Result", "Study"]


@dataclass
class GeoJsonOverlay:
    """ A data class representing an Evolve App Server study result GeoJSON overlay """
    data: GeoJSON
    styles: List[str]
    source_properties: Any = None


@dataclass
class StateOverlay:
    """ A data class representing an Evolve App Server study result state overlay """
    data: None
    styles: List[str]


@dataclass
class Section:
    """ A data class representing an Evolve App Server study result data section """
    type: str
    name: str
    description: str
    columns: Any
    data: Any


@dataclass
class Result:
    """ A data class representing an Evolve App Server study result """
    name: str
    geo_json_overlay: GeoJsonOverlay = None
    state_overlay: StateOverlay = None
    sections: List[Section] = field(default_factory=lambda: [])


@dataclass
class Study:
    """ A data class representing an Evolve App Server study """
    name: str
    description: str
    tags: List[str]
    results: List[Result]
    styles: List[Any]
