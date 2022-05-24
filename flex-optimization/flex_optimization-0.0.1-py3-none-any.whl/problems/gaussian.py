from typing import Union

import numpy as np


def nd_gaussian(args,
                sigma: Union[float, list[float]] = None,
                pre_factor: float = 1,
                center:  Union[float, list[float]] = None) -> np.ndarray:
    """
    n-dimensional Gaussian function

    Features:
    --------
    * smooth optimization
    * single minima at center

    Parameters
    ----------
    args: array
        [x[:], y[:], z[:], ...]
        the number of values determines dimensionality
    sigma: float, list[float]
        standard deviation
    pre_factor: float
        pre-factor
    center: float, list[float]
        center of distribution

    Returns
    -------
    return: np.ndarray
        z value

    """
    if not isinstance(args, (list, tuple, np.ndarray)):
        raise ValueError("Invalid args.")

    # determine dimensionality
    if isinstance(args, (list, tuple)):
        d = len(args)
    else:  # np.ndarray
        if len(args.shape) == 1:
            d = args.size
        else:
            d = args.shape[1]

    if sigma is not None:
        if len(sigma) != d:
            raise ValueError(f"args suggests a {d}-distribution, but {len(sigma)} sigma where provided.")
    else:
        sigma = np.ones(d)

    if center is not None:
        if len(center) != d:
            raise ValueError(f"args suggests a {d}-distribution, but {len(center)} center where provided.")
    else:
        center = np.zeros(d)

    def single_dim_exponent(x, x0, sigma_):
        return (x-x0)**2/(2*sigma_**2)

    exponent = 0
    for i in range(d):
        exponent += single_dim_exponent(args[i], center[i], sigma[i])

    return pre_factor*np.exp(-exponent)


def local_run():
    n = 100
    x = np.linspace(-5, 5, n)
    y = np.linspace(-5, 5, n)
    xx, yy = np.meshgrid(x, y)

    xx = xx.T.reshape(n*n)
    yy = yy.T.reshape(n*n)
    zz = nd_gaussian([xx, yy])

    import plotly.graph_objs as go
    fig = go.Figure(go.Surface(x=x, y=y, z=zz.T.reshape(n, n)))
    fig.show()


def local_run2():
    n = 7
    x = np.linspace(-5, 5, n)
    y = np.linspace(-5, 5, n)
    z = np.linspace(-5, 5, n)
    xx, yy, zz = np.meshgrid(x, y, z)

    xx = xx.T.reshape(n*n*n)
    yy = yy.T.reshape(n*n*n)
    zz = zz.T.reshape(n*n*n)
    aa = nd_gaussian([xx, yy, zz], sigma=[2, 2, 2])

    import plotly.express as px
    import pandas as pd
    df = pd.DataFrame(np.stack((xx, yy, zz, aa), axis=1))
    fig = px.scatter_3d(df, x=0, y=1, z=2, color=3)
    fig.show()


if __name__ == "__main__":
    local_run2()
