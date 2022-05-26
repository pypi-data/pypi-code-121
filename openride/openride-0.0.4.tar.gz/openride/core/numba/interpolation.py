import numba
import numpy as np



@numba.njit(cache=True)
def linear_interpolation(array:np.ndarray, index:float) -> float:
    if index >= array.size-1:
        return array[-1]
    int_index = int(index)
    remainder = index%1
    x0 = array[int_index]
    x1 = array[int_index+1]
    return x0*(1-remainder) + x1*(remainder)


@numba.njit(cache=True)
def linear_interpolation_angle(array:np.ndarray, index:float) -> float:
    if index >= array.size-1:
        return array[-1]
    int_index = int(index)
    remainder = index%1
    x0 = array[int_index]
    x1 = array[int_index+1]
    if x1-x0 > np.pi:
        x1 -= 2*np.pi
    if x1-x0 < - np.pi:
        x1 += 2*np.pi
    return (x0*(1-remainder) + x1*(remainder)) % (2*np.pi)


@numba.njit(cache=True)
def interpolate_line_index_at_xy(vertices:np.ndarray, x:float, y:float, discrete_index:bool=False) -> float:
    """Return the interpolated index (float) of projected (x,y) coordinates onto a line (vertices)."""

    point = np.array([x,y])

    # Find nearest index (integer, not interpolated)
    diff = vertices[:,:2] - point
    distances_sq = (diff[:,0]**2 + diff[:,1]**2)
    index_int = np.argmin(distances_sq)

    if discrete_index: return index_int

    closest_point = vertices[index_int][:2]

    # Try interpolating between closest point and next point
    if index_int + 1 < len(vertices):
        next_point = vertices[index_int+1][:2]
        delta_distance = np.sum((closest_point - next_point) ** 2)
        delta_index = np.sum((point - closest_point) * (next_point - closest_point)) / (delta_distance + 1e-16)
        if delta_index <= 1 and delta_index >= 0:  # This means that point is between the closest point and the next point
            return index_int + delta_index

    # Try interpolating between closest point and previous point
    if index_int >= 1:
        previous_point = vertices[index_int-1][:2]
        delta_distance = np.sum((closest_point - previous_point) ** 2)
        delta_index = max(0, min(1, np.sum((point - closest_point) * (previous_point - closest_point)) / (delta_distance + 1e-16)))
        return index_int - delta_index

    return index_int
    