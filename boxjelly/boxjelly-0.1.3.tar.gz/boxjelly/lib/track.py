"""
Track-related models.
"""

from typing import List, Optional
from dataclasses import dataclass

from dataclasses_json import dataclass_json

@dataclass_json
@dataclass
class BoundingBox:
    x: int
    y: int
    w: int
    h: int


@dataclass_json
@dataclass
class Track:
    start_frame: int
    boxes: List[Optional[BoundingBox]]
    
    def __len__(self) -> int:
        return len(self.boxes)
    
    @property
    def slice(self):
        return slice(self.start_frame, self.start_frame + len(self))


@dataclass_json
@dataclass
class IdentifiedTrack(Track):
    id: int
    label: str
