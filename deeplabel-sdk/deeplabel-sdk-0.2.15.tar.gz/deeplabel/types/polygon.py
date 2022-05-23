from pydantic import BaseModel, confloat
from typing import List
from shapely.geometry import Polygon as ShapelyPolygon, Point as ShapelyPoint

class Point(BaseModel):
    x:confloat(le=1,ge=0)
    y:confloat(le=1,ge=0)

    def to_shapely(self, scale_x:int, scale_y:int):
        return ShapelyPoint(int(self.x*scale_x), int(self.y*scale_y))

class Polygon(BaseModel):
    points:List[Point]

    def to_shapely(self, scale_x:int, scale_y:int):
        """Case Polygon to Shapely polygon with scaled form 0-1 coordinates to pixel coordinates"""
        return ShapelyPolygon([point.to_shapely(scale_x, scale_y) for point in self.points])
