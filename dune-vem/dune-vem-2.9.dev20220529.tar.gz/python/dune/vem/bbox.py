import numpy
from dune.vem.qhull_2d import *
from dune.vem.min_bounding_rect import *

def rotatedBBox(points,rotate):
    points = numpy.array(points)
    if rotate: # rotated bbox
        # Find convex hull
        hull_points = qhull2D(points)
        # Reverse order of points, to match output from other qhull implementations
        hull_points = hull_points[::-1]
        # Find minimum area bounding rectangle
        (rot_angle, area, width, height, center_point, corner_points) = minBoundingRect(hull_points)
        e0 = corner_points[1]  - corner_points[0]
        e1 = corner_points[-1] - corner_points[0]
        # print( list(corner_points[0]), list(corner_points[2]), list(e0), list(e1), max(height,width), flush=True )
        return list(corner_points[0]), list(corner_points[2]), list(e0), list(e1), max(height,width)
    else: # axis aligned box
        xmin,xmax = min(points[:,0]), max(points[:,0])
        ymin,ymax = min(points[:,1]), max(points[:,1])
        return [xmin,ymin], [xmax,ymax], [xmax-xmin,0], [0,ymax-ymin], min(xmax-xmin,ymax-ymin)
