import numpy as np


def parse_box3d(box3d):
    """
    Args:
        box3d (dict, list, ndarray): convert box3d to 7 numbers in the order of
            `center_x, center_y, center_z, height, width, length, heading`.
            If it's a dict, it should contain these keys;
            if it's a list or ndarray, it should be in this order.

    Returns:
        7 numbers
    """
    if isinstance(box3d, dict):
        return (
            box3d["center_x"],
            box3d["center_y"],
            box3d["center_z"],
            box3d["height"],
            box3d["width"],
            box3d["length"],
            box3d["heading"],
        )
    elif isinstance(box3d, list) or isinstance(box3d, np.ndarray):
        return box3d[0], box3d[1], box3d[2], box3d[3], box3d[4], box3d[5], box3d[6]
    else:
        raise TypeError("Not supported box3d type")


def box3d2tf_mat(box3d):
    """
    Convert the box to transformation matrix.
    Args:
        box3d: see parse_box3d for detailed format.

    Returns:
        a 4x4 tf_mat
    """
    center_x, center_y, center_z, height, width, length, heading = parse_box3d(box3d)

    tf_mat = np.array(
        [
            [np.cos(heading), -np.sin(heading), 0, center_x],
            [np.sin(heading), np.cos(heading), 0, center_y],
            [0, 0, 1, center_z],
            [0, 0, 0, 1],
        ]
    )
    return tf_mat


# https://github.com/open-mmlab/mmdetection3d/blob/master/mmdet3d/core/bbox/structures/lidar_box3d.py
def box3d2corners(box3d):
    """
    Convert the box to corners.
                                           up z
                            front x           ^
                                 /            |
                                /             |
                  (x1, y0, z1) + -----------  + (x1, y1, z1)
                              /|            / |
                             / |  ori.     /  |
               (x0, y0, z1) + ----------- +   + (x1, y1, z0)
                            |  /         |  /
                            | /          | /
            left y<-------- + ----------- + (x0, y1, z0)
                (x0, y0, z0)
    Args:
        box3d: see parse_box3d for detailed format.

    Returns:
        corners: 8 corners in clockwise order, in form of
            (x0y0z0, x0y0z1, x0y1z1, x0y1z0, x1y0z0, x1y0z1, x1y1z1, x1y1z0)
    """
    center_x, center_y, center_z, height, width, length, heading = parse_box3d(box3d)

    center = np.array([center_x, center_y, center_z])
    bottom_center = np.array([center_x, center_y, center_z - height / 2])

    pc0 = np.array(
        [
            center_x + np.cos(heading) * length / 2 + np.sin(heading) * width / 2,
            center_y + np.sin(heading) * length / 2 - np.cos(heading) * width / 2,
            center_z - height / 2,
        ]
    )
    pc1 = np.array(
        [
            center_x + np.cos(heading) * length / 2 - np.sin(heading) * width / 2,
            center_y + np.sin(heading) * length / 2 + np.cos(heading) * width / 2,
            center_z - height / 2,
        ]
    )
    pc2 = 2 * bottom_center - pc0
    pc3 = 2 * bottom_center - pc1

    bottom_corners = np.stack([pc0, pc1, pc2, pc3], axis=0)
    up_corners = 2 * center - bottom_corners
    corners = np.concatenate([bottom_corners, up_corners], axis=0)
    corners = corners[[3, 5, 4, 2, 0, 6, 7, 1]]

    return corners
