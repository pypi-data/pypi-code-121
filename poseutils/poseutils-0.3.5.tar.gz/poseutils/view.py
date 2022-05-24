from poseutils.constants import *

def draw_axes(R, t, ax, scale=0.5):
    """Draw xyz axes centered at a position.

    :param R: Rotation matrix (3,3) with columns representing xyz columns respectively
    :type R: numpy.ndarray
    :param t: Position t (3,) acting as the origin of the xyz axes
    :type t: numpy.ndarray
    :param ax: Matplotlib subplot reference
    :type ax: matplotlib.pyplot.subplot
    :param scale: To scale up the axes, defaults to 0.5
    :type scale: float, optional
    """

    x, y, z = R[:, 0], R[:, 1], R[:, 2]

    x = t + scale*x
    y = t + scale*y
    z = t + scale*z

    ax.plot([t[0], x[0]], [t[1], x[1]], [t[2], x[2]], color='r')
    ax.plot([t[0], y[0]], [t[1], y[1]], [t[2], y[2]], color='g')
    ax.plot([t[0], z[0]], [t[1], z[1]], [t[2], z[2]], color='b')

def draw_skeleton(pose, ax, jnts_14=True):
    """Draws a skeleton from joints 

    :param pose: Joint positions either 2d (Nx2) or 3d (Nx3) where N = 14 or 16
    :type pose: numpy.ndarray
    :param ax: Matplotlib subplot reference
    :type ax: matplotlib.pyplot.subplot
    :param jnts_14: Flag to specify whether to use 14 joint (True) or 16 joint (False) configuration, defaults to True
    :type jnts_14: bool, optional
    """

    assert len(pose.shape) == 2
    assert pose.shape[-1] == 3 or pose.shape[-1] == 2 

    if jnts_14:
        edges = EDGES_14
        lefts = LEFTS_14
        rights = RIGHTS_14

    is_3d = False
    if pose.shape[-1] == 3:
        is_3d = True

    col_right = 'b'
    col_left = 'r'

    if is_3d:
        ax.scatter(pose[:, 0], pose[:, 1], zs=pose[:, 2], color='k')
    else:
        ax.scatter(pose[:, 0], pose[:, 1], color='k')

    for u, v in edges:
        col_to_use = 'k'

        if u in lefts and v in lefts:
            col_to_use = col_left
        elif u in rights and v in rights:
            col_to_use = col_right

        if is_3d:
            ax.plot([pose[u, 0], pose[v, 0]], [pose[u, 1], pose[v, 1]], zs=[pose[u, 2], pose[v, 2]], color=col_to_use)
        else:
            ax.plot([pose[u, 0], pose[v, 0]], [pose[u, 1], pose[v, 1]], color=col_to_use)

def draw_bounding_box(lx, ly, rx, ry, ax):
    """Draws bounding box

    :param lx: X coordinates (Nx1) for top-left corner of the box
    :type lx: numpy.ndarray
    :param ly: Y coordinates (Nx1) for top-left corner of the box
    :type ly: numpy.ndarray
    :param rx: X coordinates (Nx1) for bottom-right corner of the box
    :type rx: numpy.ndarray
    :param ry: Y coordinates (Nx1) for bottom-right corner of the box
    :type ry: numpy.ndarray
    :param ax: Matplotlib subplot reference
    :type ax: matplotlib.pyplot.subplot
    """

    ax.plot([lx, rx, rx, lx, lx], [ly, ly, ry, ry, ly], color='g')