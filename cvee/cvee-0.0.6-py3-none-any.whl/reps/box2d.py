import numpy as np


def parse_box2d(box2d):
    """
    Args:
        box2d (dict, list, ndarray): convert box2d to 4 numbers in the order of
            `center_x, center_y, width, length`.
            If it's a dict, it should contain these keys;
            if it's a list or ndarray, it should be in this order.

    Returns:
        4 numbers
    """
    if isinstance(box2d, dict):
        return (
            box2d["center_x"],
            box2d["center_y"],
            box2d["width"],
            box2d["length"],
        )
    elif isinstance(box2d, list) or isinstance(box2d, np.ndarray):
        return box2d[0], box2d[1], box2d[2], box2d[3]
    else:
        raise TypeError("Not supported box3d type")


def box2d2corners(box2d):
    """
    Convert the box to corners.

    Args:
        box2d: see parse_box2d for detailed format

    Returns:
        corners (np.ndarray): 4 numbers, left-top x, left-top y, right-bottom x, right-bottom y
    """
    x, y, w, l = parse_box2d(box2d)
    return np.array([int(x - l / 2), int(y - w / 2), int(x + l / 2), int(y + w / 2)])
