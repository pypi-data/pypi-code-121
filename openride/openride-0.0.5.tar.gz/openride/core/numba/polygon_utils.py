import numba
import numpy as np


@numba.njit(cache=True)
def polygon_contains_point(vertices:np.ndarray, x:float, y:float) -> bool:
    n = len(vertices)
    inside = False
    p2x = 0.0
    p2y = 0.0
    xints = 0.0
    p1x,p1y = vertices[0,:2]
    for i in range(n+1):
        p2x,p2y = vertices[i % n, :2]
        if y > min(p1y,p2y):
            if y <= max(p1y,p2y):
                if x <= max(p1x,p2x):
                    if p1y != p2y:
                        xints = (y-p1y)*(p2x-p1x)/(p2y-p1y)+p1x
                    if p1x == p2x or x <= xints:
                        inside = not inside
        p1x,p1y = p2x,p2y

    return inside