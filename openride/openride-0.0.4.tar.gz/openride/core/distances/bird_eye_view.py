from openride.core.bounding_box import BoundingBox
from openride.core.geometry import Geometry
from openride.core.point import Point
from openride.core.polygon import Polygon
from openride.core.polyline import Polyline

from openride.core.numba.distances import (
    bev_distance_between_box_and_point, bev_distance_between_boxes, 
    bev_distance_between_line_and_box, bev_distance_between_line_and_point, 
    bev_distance_between_line_and_polygon, bev_distance_between_lines, 
    bev_distance_between_points, bev_distance_between_polygon_and_point, 
    bev_distance_between_polygons,
)

from multipledispatch import dispatch



@dispatch(Point, Point)
def bird_eye_view_distance(obj1:Point, obj2:Point) -> float:
    return bev_distance_between_points(obj1.x, obj1.y, obj2.x, obj2.y)


@dispatch(Point, BoundingBox)
def bird_eye_view_distance(obj1:Point, obj2:BoundingBox) -> float:
    return bev_distance_between_box_and_point(obj2.position.x, obj2.position.y, obj2.size.x, obj2.size.y, obj2.rotation.yaw, obj1.x, obj1.y)


@dispatch(Point, Polyline)
def bird_eye_view_distance(obj1:Point, obj2:Polyline) -> float:
    return bev_distance_between_line_and_point(obj2.vertices, obj1.x, obj1.y)


@dispatch(Point, Polygon)
def bird_eye_view_distance(obj1:Point, obj2:Polygon) -> float:
    return bev_distance_between_polygon_and_point(obj2.vertices, obj1.x, obj1.y)


@dispatch(BoundingBox, Point)
def bird_eye_view_distance(obj1:BoundingBox, obj2:Point) -> float:
    return bev_distance_between_box_and_point(obj1.position.x, obj1.position.y, obj1.size.x, obj1.size.y, obj1.rotation.yaw, obj2.x, obj2.y)


@dispatch(BoundingBox, BoundingBox)
def bird_eye_view_distance(obj1:BoundingBox, obj2:BoundingBox) -> float:
    return bev_distance_between_boxes(obj1.bird_eye_view_vertices, obj2.bird_eye_view_vertices)


@dispatch(BoundingBox, Polyline)
def bird_eye_view_distance(obj1:BoundingBox, obj2:Polyline) -> float:
    return bev_distance_between_line_and_box(obj2.vertices, obj1.bird_eye_view_vertices)


@dispatch(BoundingBox, Polygon)
def bird_eye_view_distance(obj1:BoundingBox, obj2:Polygon) -> float:
    return bev_distance_between_polygons(obj1.bird_eye_view_vertices, obj2.vertices)


@dispatch(Polyline, Point)
def bird_eye_view_distance(obj1:Polyline, obj2:Point) -> float:
    return bev_distance_between_line_and_point(obj1.vertices, obj2.x, obj2.y)


@dispatch(Polyline, BoundingBox)
def bird_eye_view_distance(obj1:Polyline, obj2:BoundingBox) -> float:
    return bev_distance_between_line_and_box(obj1.vertices, obj2.bird_eye_view_vertices)


@dispatch(Polyline, Polyline)
def bird_eye_view_distance(obj1:Polyline, obj2:Polyline) -> float:
    return bev_distance_between_lines(obj1.vertices, obj2.vertices)


@dispatch(Polyline, Polygon)
def bird_eye_view_distance(obj1:Polyline, obj2:Polygon) -> float:
    return bev_distance_between_line_and_polygon(obj1.vertices, obj2.vertices)


@dispatch(Polygon, Point)
def bird_eye_view_distance(obj1:Polygon, obj2:Point) -> float:
    return bev_distance_between_polygon_and_point(obj1.vertices, obj2.x, obj2.y)


@dispatch(Polygon, BoundingBox)
def bird_eye_view_distance(obj1:Polygon, obj2:BoundingBox) -> float:
    return bev_distance_between_polygons(obj1.vertices, obj2.bird_eye_view_vertices)


@dispatch(Polygon, Polyline)
def bird_eye_view_distance(obj1:Polygon, obj2:Polyline) -> float:
    return bev_distance_between_line_and_polygon(obj2.vertices, obj1.vertices)


@dispatch(Polygon, Polygon)
def bird_eye_view_distance(obj1:Polygon, obj2:Polygon) -> float:
    return bev_distance_between_polygons(obj1.vertices, obj2.vertices)


# Default, fall back to shapely module if we don't have an implementation above
@dispatch(Geometry, Geometry)
def bird_eye_view_distance(obj1:Geometry, obj2:Geometry) -> float:
    return obj1.to_shapely().distance(obj2.to_shapely())