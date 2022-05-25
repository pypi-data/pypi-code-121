from typing import List
from pydantic import BaseModel

from .scene import Scene


class Tile(BaseModel):
    tile_name: str
    scenes: List[Scene]
    intersection_w_aoi: float = None
    best_scene: Scene = None