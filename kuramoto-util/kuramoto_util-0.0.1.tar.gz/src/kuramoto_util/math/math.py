import numpy as np


def torus_distance(shape, point):
    rank = len(shape) 
    r2 = 0
    for i in range(rank):
        ri2 = min(point[i], shape[i]-point[i])**2
        r2 += ri2
    return np.sqrt(r2)

