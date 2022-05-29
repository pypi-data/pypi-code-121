from __future__ import print_function

import sys
import numpy

import dune.geometry

def voronoiDomain(N, boundingBox, seed=None):
    # Generate N random points within the bounding box
    if not isinstance(boundingBox, numpy.ndarray):
        boundingBox = numpy.array(boundingBox)
    if not boundingBox.shape == (2, 2):
        raise ValueError("Bounding box must be convertible into a numpy array of shape (2, 2).")

    if seed is not None:
        numpy.random.seed(seed)
    points = numpy.random.rand(N, 2) * (boundingBox[1] - boundingBox[0]) + boundingBox[0]

    # Mirror points and border of bounding box
    points_center = points
    for i in range(2):
        for j in range(2):
            points_mirror = numpy.copy(points_center)
            points_mirror[:, j] = 2*boundingBox[i][j] - points_mirror[:, j]
            points = numpy.append(points, points_mirror, axis=0)

    # Compute Voronoi diagram
    import scipy.spatial
    voronoi = scipy.spatial.Voronoi(points)

    # Filter regions
    eps = sys.float_info.epsilon
    regions = []
    for region in voronoi.regions:
        if len(region) == 0 or -1 in region:
            continue
        xs = voronoi.vertices[region, :]
        if numpy.all(xs >= boundingBox[0] - eps) and numpy.all(xs <= boundingBox[1] + eps):
            regions.append(region)

    # Filter vertices
    indices = numpy.unique(numpy.array([i for r in regions for i in r]))
    vertices = voronoi.vertices[indices, :]

    # Generate polygons from regions
    newIndex = numpy.zeros(len(voronoi.vertices), int)
    newIndex[indices] = range(len(indices))
    gt = dune.geometry.none(2)
    elements = [(gt, newIndex[r].tolist()) for i, r in enumerate(regions)]

    return {"vertices": vertices, "elements": elements}


if __name__ == "__main__":
    from dune.polygongrid import polygonGrid

    boundingBox = numpy.array([[0, 0], [1, 1]])
    grid = polygonGrid(voronoiDomain(100, boundingBox, seed=1234))
    grid.plot()
