from openride.core.numba.interpolation import interpolate_line_index_at_xy, linear_interpolation

import numba
import numpy as np

from typing import Tuple, Union

EPSILON = np.finfo(float).eps


@numba.njit(cache=True)
def vertices_to_distances(vertices:np.ndarray, bird_eye_view:bool=True) -> np.ndarray:
    distances_squared = (vertices[1:,0] - vertices[:-1,0]) ** 2 + (vertices[1:,1] - vertices[:-1,1]) ** 2
    if not bird_eye_view:
        distances_squared += (vertices[1:,2] - vertices[:-1,2]) ** 2
    distances = distances_squared ** 0.5
    distances = np.append(0, distances)
    return np.cumsum(distances)


@numba.njit(cache=True)
def index_to_distance(vertices:np.ndarray, index:float) -> float:
    distances = vertices_to_distances(vertices)
    if index >= vertices.shape[0]-1: return distances[-1]
    return linear_interpolation(distances, index)


@numba.njit(cache=True)
def distance_to_index(vertices:np.ndarray, distance:float) -> float:
    if distance <= 0.0: return 0.0
    distances = vertices_to_distances(vertices)
    index = np.searchsorted(distances - distance, 0)
    if index > distances.size - 1: return distances.size - 1
    index += (distance - distances[index])/(distances[index] - distances[index-1] + EPSILON)
    return index


@numba.njit(cache=True)
def left_or_right_from_line(vertices:np.ndarray, x:float, y:float) -> int:
    i = int(interpolate_line_index_at_xy(vertices, x, y))
    i0 = max([i, 0])
    i1 = min([i + 1, vertices.shape[0] - 1])
    return np.sign((vertices[i1,0] - vertices[i0,0]) * (y - vertices[i0,1]) - (vertices[i1,1] - vertices[i0,1]) * (x - vertices[i0,0]))


@numba.njit(cache=True)
def tangent_angle(vertices:np.ndarray, index:int) -> float:
    i1 = max([0, index-1])
    i2 = min([index+1, vertices.shape[0]-1])
    delta_x = vertices[i2,0] - vertices[i1,0]
    delta_y = vertices[i2,1] - vertices[i1,1]
    ratio = delta_y / (delta_x + 1e-9)
    angle = np.arctan(ratio)
    angle = angle + np.pi if delta_x < 0 else angle
    return angle % (2*np.pi)


@numba.njit(cache=True)
def tangent_angles(vertices:np.ndarray) -> np.ndarray:
    angles = np.zeros(vertices.shape[0])
    delta_x = vertices[2:,0] - vertices[:-2,0]
    delta_y = vertices[2:,1] - vertices[:-2,1]
    ratio = delta_y / (delta_x + 1e-9)
    angles[1:-1] = np.arctan(ratio)
    angles[1:-1][np.where(delta_x < 0)] += np.pi
    angles[1:-1] = angles[1:-1] % (2*np.pi)
    angles[0] = tangent_angle(vertices, 0)
    angles[-1] = tangent_angle(vertices, vertices.shape[0]-1)
    return angles


@numba.njit(cache=True)
def angle_difference(angle1:float, angle2:float) -> float:
    two_pi = 2.0 * np.pi
    return min((two_pi - abs(angle1 - angle2), abs(angle1 - angle2))) % two_pi

@numba.njit(cache=True)
def angle_differences(angles1:float, angles2:float) -> float:
    two_pi = 2.0 * np.pi
    return np.array([min((two_pi - abs(angles1[i] - angles2[i]), abs(angles1[i] - angles2[i]))) % two_pi for i in range(angles1.size)])


@numba.njit(cache=True)
def project_point_on_line(vertices:np.ndarray, x:float, y:float) -> Tuple[float, float, float]:
    """Projection is performed in bird eye view, but the coordinate interpolation is 3D."""
    index = interpolate_line_index_at_xy(vertices, x, y)
    vx = linear_interpolation(vertices[:,0], index)
    vy = linear_interpolation(vertices[:,1], index)
    vz = linear_interpolation(vertices[:,2], index)
    return vx, vy, vz


@numba.njit(cache=True)
def radius_of_curvature(vertices: np.ndarray) -> np.ndarray:
    # https://stackoverflow.com/questions/61945776/curve-radius-in-python
    R = np.full(vertices.shape[0], np.inf)

    dx = vertices[1:,0] - vertices[:-1,0] # First derivative of x (centered)
    dy = vertices[1:,1] - vertices[:-1,1] # First derivative of y (centered)
    ddx = dx[1:] - dx[:-1] # Second derivative of x (centered)
    ddy = dy[1:] - dy[:-1] # Second derivative of y (centered)

    # Remove edges to match shapes
    dx = dx[:-1]
    dy = dy[:-1]

    R[:-2] = (dx**2 + dy**2)**1.5 / (dx*ddy - dy*ddx + EPSILON)

    # Deal with edges
    R[-2:] = R[-3]

    return R


@numba.njit(cache=True)
def apply_lateral_deviations(vertices:np.ndarray, tangent_angles:np.ndarray, lateral_deviations:Union[np.ndarray, float]) -> np.ndarray:
    """Returns the route vertices after applying the lateral deviations"""
    dx = lateral_deviations * np.sin(tangent_angles)
    dy = lateral_deviations * np.cos(tangent_angles)
    shifted_vertices = np.copy(vertices)
    shifted_vertices[:,0] -= dx
    shifted_vertices[:,1] += dy
    return shifted_vertices


@numba.njit(cache=True)
def resample_linear(vertices:np.ndarray, N:int, additionnal_data:tuple=()):
    distances = vertices_to_distances(vertices)
    new_distances = np.linspace(0, distances[-1], N)
    new_vertices = np.zeros((new_distances.size, 3))
    interpolated_arrays = np.zeros((new_distances.size, len(additionnal_data)))

    for i in range(new_distances.size):
        index = distance_to_index(vertices, new_distances[i])
        new_vertices[i,0] = linear_interpolation(vertices[:,0], index)
        new_vertices[i,1] = linear_interpolation(vertices[:,1], index)
        new_vertices[i,2] = linear_interpolation(vertices[:,2], index)

        if len(additionnal_data) > 0:
            for j in range(len(additionnal_data)):
                interpolated_arrays[i,j] = linear_interpolation(additionnal_data[j], index)

    return new_vertices, interpolated_arrays