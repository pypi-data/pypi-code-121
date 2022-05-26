from openride.core.numba.interpolation import interpolate_line_index_at_xy, linear_interpolation
from openride.core.numba.polygon_utils import polygon_contains_point

from typing import Tuple

import numba
import numpy as np



@numba.njit(cache=True)
def bev_distance_between_points(x1:float, y1:float, x2:float, y2:float) -> float:
    return ((x1-x2)**2 + (y1-y2)**2)**0.5


@numba.njit(cache=True)
def bev_distance_between_box_and_point(box_position_x:float, box_position_y:float, box_size_x:float, box_size_y:float, box_yaw:float, point_x:float, point_y:float) -> float:
    relx = point_x - box_position_x
    rely = point_y - box_position_y
    rotx = relx*np.cos(-box_yaw) - rely*np.sin(-box_yaw)
    roty = relx*np.sin(-box_yaw) + rely*np.cos(-box_yaw)
    dx = max(abs(rotx) - box_size_x, 0)
    dy = max(abs(roty) - box_size_y, 0)
    return (dx * dx + dy * dy)**0.5


@numba.njit(cache=True)
def bev_project_point_on_line(vertices:np.ndarray, x:float, y:float) -> Tuple[float, float]:
    index = interpolate_line_index_at_xy(vertices, x, y)
    vx = linear_interpolation(vertices[:,0], index)
    vy = linear_interpolation(vertices[:,1], index)
    return vx, vy


@numba.njit(cache=True)
def bev_distance_between_line_and_point(vertices:np.ndarray, x:float, y:float) -> float:
    return min([point_segment_distance(x, y, vertices[i,0], vertices[i,1], vertices[i+1,0], vertices[i+1,1]) for i in range(vertices.shape[0]-1)])


@numba.njit(cache=True)
def bev_distance_between_polygon_and_point(vertices:np.ndarray, x:float, y:float) -> float:
    if polygon_contains_point(vertices, x, y): return 0.0
    return bev_distance_between_line_and_point(np.vstack((vertices, vertices[:0])), x, y)


@numba.njit(cache=True)
def bev_distance_between_line_and_polygon(line_vertices:np.ndarray, poly_vertices:np.ndarray) -> float:
    N1 = line_vertices.shape[0]
    N2 = poly_vertices.shape[0]
    
    distances = np.zeros((N1-1,N2))
    for i1 in range(N1-1):
        x11, y11 = line_vertices[i1,:2]
        x12, y12 = line_vertices[(i1+1),:2]

        if polygon_contains_point(poly_vertices, x11, y11): return 0.0

        for i2 in range(N2):
            x21, y21 = poly_vertices[i2%N2,:2]
            x22, y22 = poly_vertices[(i2+1)%N2,:2]

            distances[i1,i2] = segments_distance(x11, y11, x12, y12, x21, y21, x22, y22)
            if distances[i1,i2] == 0.0: return 0.0

    return np.min(distances)


@numba.njit(cache=True)
def bev_distance_between_line_and_box(line_vertices:np.ndarray, box_vertices:np.ndarray) -> float:
    return bev_distance_between_line_and_polygon(line_vertices, box_vertices)


@numba.njit(cache=True)
def bev_distance_between_polygons(vertices1:np.ndarray, vertices2:np.ndarray) -> float:

    for x, y in vertices1[:,:2]:
        if polygon_contains_point(vertices2, x, y): return 0.0
    for x, y in vertices2[:,:2]:
        if polygon_contains_point(vertices1, x, y): return 0.0

    N1 = vertices1.shape[0]
    N2 = vertices2.shape[0]
    
    distances = np.zeros((N1,N2))
    for i1 in range(N1):
        x11, y11 = vertices1[i1%N1,:2]
        x12, y12 = vertices1[(i1+1)%N1,:2]

        for i2 in range(N2):
            x21, y21 = vertices2[i2%N2,:2]
            x22, y22 = vertices2[(i2+1)%N2,:2]

            distances[i1,i2] = segments_distance(x11, y11, x12, y12, x21, y21, x22, y22)
            if distances[i1,i2] == 0.0: return 0.0

    return np.min(distances)


@numba.njit(cache=True)
def bev_distance_between_boxes(vertices1:np.ndarray, vertices2:np.ndarray) -> float:
    return bev_distance_between_polygons(vertices1, vertices2)


@numba.njit(cache=True)
def bev_distance_between_lines(vertices1:np.ndarray, vertices2:np.ndarray) -> float:
    N1 = vertices1.shape[0]
    N2 = vertices2.shape[0]

    if N1 == 1 and N2 == 1:
        return bev_distance_between_points(vertices1[0,0], vertices1[0,1], vertices1[1,0], vertices1[1,1])
    elif N1 == 1:
        return bev_distance_between_line_and_point(vertices2, vertices1[0,0], vertices1[0,1])
    elif N2 == 1:
        return bev_distance_between_line_and_point(vertices1, vertices2[1,0], vertices2[1,1])
    
    distances = np.zeros((N1-1, N2-1))
    for i1 in range(N1-1):
        x11, y11 = vertices1[i1,:2]
        x12, y12 = vertices1[(i1+1),:2]

        for i2 in range(N2-1):
            x21, y21 = vertices2[i2,:2]
            x22, y22 = vertices2[(i2+1),:2]

            distances[i1,i2] = segments_distance(x11, y11, x12, y12, x21, y21, x22, y22)
            if distances[i1,i2] == 0.0: return 0.0

    return np.min(distances)


@numba.njit(cache=True)
def segments_distance(x11, y11, x12, y12, x21, y21, x22, y22):
    """ distance between two segments in the plane:
        one segment is (x11, y11) to (x12, y12)
        the other is   (x21, y21) to (x22, y22)
    """
    if segments_intersect(x11, y11, x12, y12, x21, y21, x22, y22): return 0.0
    # try each of the 4 vertices w/the other segment
    distances = (
        point_segment_distance(x11, y11, x21, y21, x22, y22),
        point_segment_distance(x12, y12, x21, y21, x22, y22),
        point_segment_distance(x21, y21, x11, y11, x12, y12),
        point_segment_distance(x22, y22, x11, y11, x12, y12),
    )
    return min(distances)


@numba.njit(cache=True)
def segments_intersect(x11, y11, x12, y12, x21, y21, x22, y22):
    """ whether two segments in the plane intersect:
        one segment is (x11, y11) to (x12, y12)
        the other is   (x21, y21) to (x22, y22)
    """
    dx1 = x12 - x11
    dy1 = y12 - y11
    dx2 = x22 - x21
    dy2 = y22 - y21
    delta = dx2 * dy1 - dy2 * dx1
    if delta == 0: return False  # parallel segments
    s = (dx1 * (y21 - y11) + dy1 * (x11 - x21)) / delta
    t = (dx2 * (y11 - y21) + dy2 * (x21 - x11)) / (-delta)
    return (0 <= s <= 1) and (0 <= t <= 1)


@numba.njit(cache=True)
def point_segment_distance(px, py, x1, y1, x2, y2):
    dx = x2 - x1
    dy = y2 - y1
    if dx == dy == 0:  # the segment's just a point
        return ((px-x1)**2 + (py-y1)**2)**0.5 

    # Calculate the t that minimizes the distance.
    t = ((px - x1) * dx + (py - y1) * dy) / (dx * dx + dy * dy)

    # See if this represents one of the segment's
    # end points or a point in the middle.
    if t < 0:
        dx = px - x1
        dy = py - y1
    elif t > 1:
        dx = px - x2
        dy = py - y2
    else:
        near_x = x1 + t * dx
        near_y = y1 + t * dy
        dx = px - near_x
        dy = py - near_y

    return (dx**2+dy**2)**0.5
    