import numpy as np


def to_numpy_array(args) -> np.ndarray:
    if not isinstance(args, (list, tuple, np.ndarray)):
        raise ValueError("Invalid args.")

    if isinstance(args, np.ndarray):
        if len(args.shape) == 1:
            return np.array(args).reshape(1, 2)
        return args

    if not isinstance(args[0], (list, tuple, np.ndarray)):
        return np.array(args).reshape(1, 2)

    return np.array(args).T


def get_dimensionality(args) -> int:
    """determine dimensionality"""
    if isinstance(args, (list, tuple)):
        return len(args)
    else:  # np.ndarray
        if len(args.shape) == 1:
            return 1
        else:
            return args.shape[1]


def get_num_points(args) -> int:
    """determine number of points"""
    if isinstance(args, (list, tuple)):
        if isinstance(args[0], (list, tuple, np.ndarray)):
            return len(args[0])
        else:
            return 1  # float, int
    else:  # np.ndarray
        if len(args.shape) == 1:
            return args.shape
        else:
            return args.shape[0]
