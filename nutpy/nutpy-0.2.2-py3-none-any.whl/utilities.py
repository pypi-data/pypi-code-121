import numpy as np


def read_detectors_coordinates(file_name):
    """
    Read detectors coordinates from file

    The file must be in the working directory. Two columns separated by white space,
    comma as decimal separator

    Parameters
    ----------
    file_name : str
        Name of the file with the detectors coordinates

    Returns
    -------
    x : 1D-array
        X-axis coordinates of the detectors
    y : 1D-array
        Y-axis coordinates of the detectors
    """

    with open(file_name, 'r', encoding='UTF-8') as data:
        x = []
        y = []
        for line in data:
            p = line.replace(',', '.').split()
            x.append(float(p[0]))
            y.append(float(p[1]))

    x = np.asarray(x)
    y = np.asarray(y)

    # coordinates are scaled so farthest point is at a radial distance of 0.9
    rmax = np.sqrt((x**2 + y**2)).max()
    ratio = (1/rmax) * 0.9

    x *= ratio
    y *= ratio

    return x, y
