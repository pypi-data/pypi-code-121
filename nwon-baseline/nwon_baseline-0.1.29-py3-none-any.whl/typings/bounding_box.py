from typing import NewType, Tuple

from pydantic import BaseModel

BoundingBoxTuple = NewType("BoundingBoxTuple", Tuple[int, int, int, int])


class BoundingBoxCoordinates(BaseModel):
    top: int
    right: int
    bottom: int
    left: int
