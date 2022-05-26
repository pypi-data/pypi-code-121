from openride.core.numba.transforms import transform_vertices

import numba
import numpy as np



@numba.njit(cache=True)
def bev_box_vertices(position_x, position_y, sixe_z, size_y, matrix) -> np.ndarray:
    vertices = np.array([[ sixe_z, size_y, 0]
                        ,[ sixe_z,-size_y, 0]
                        ,[-sixe_z,-size_y, 0]
                        ,[-sixe_z, size_y, 0]])
    matrix4x4 = np.eye(4)
    matrix4x4[:3,:3] = matrix
    vertices = transform_vertices(vertices, matrix4x4)
    vertices[:,0] += position_x
    vertices[:,1] += position_y
    return vertices[:,:2]


@numba.njit(cache=True)
def box_vertices(position_x, position_y, position_z, size_x, size_y, size_z, matrix) -> np.ndarray:
    vertices = np.array([[-size_x, size_y,-size_z]
                        ,[-size_x, size_y, size_z]
                        ,[ size_x, size_y,-size_z]
                        ,[ size_x, size_y, size_z]
                        ,[ size_x,-size_y,-size_z]
                        ,[ size_x,-size_y, size_z]
                        ,[-size_x,-size_y,-size_z]
                        ,[-size_x,-size_y, size_z]])
    matrix4x4 = np.eye(4)
    matrix4x4[:3,:3] = matrix
    vertices = transform_vertices(vertices, matrix4x4)
    vertices[:,0] += position_x
    vertices[:,1] += position_y
    vertices[:,2] += position_z
    return vertices