
import numpy as np


def rastrigin(args, constant: float = 10) -> np.ndarray:
    """
    Rastrigin function

    Features
    -------
    * non-convex function
    * non-linear multimodal function
    * large number of local minima
    * global minima is at zero
    * typical x range [-5.12, 5.12]

    Parameters
    ----------
    args: array
        [x[:], y[:], z[:], ...]
        the number of values determines dimensionality
    constant: float

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

    sum_ = 0
    if isinstance(args, np.ndarray) and args.shape[1] >= 2:
        for i in range(args.shape[1]):
            sum_ += args[:, i]**2 - constant * np.cos(2 * np.pi * args[:, i])
    if isinstance(args, list):
        for x in args:
            sum_ += x**2 - constant * np.cos(2 * np.pi * x)

    return constant*d + sum_


def local_run():
    n = 100
    x = np.linspace(-5.12, 5.12, n)
    y = np.linspace(-5.12, 5.12, n)
    xx, yy = np.meshgrid(x, y)

    xx = xx.T.reshape(n*n)
    yy = yy.T.reshape(n*n)
    zz = rastrigin([xx, yy])

    import plotly.graph_objs as go
    fig = go.Figure(go.Surface(x=x, y=y, z=zz.T.reshape(n, n)))
    fig.show()


def local_run2():
    n = 25
    x = np.linspace(-5.12, 5.12, n)
    y = np.linspace(-5.12, 5.12, n)
    z = np.linspace(-5.12, 5.12, n)
    xx, yy, zz = np.meshgrid(x, y, z)

    xx = xx.T.reshape(n*n*n)
    yy = yy.T.reshape(n*n*n)
    zz = zz.T.reshape(n*n*n)
    aa = rastrigin([xx, yy, zz])

    import plotly.express as px
    import pandas as pd
    df = pd.DataFrame(np.stack((xx, yy, zz, aa), axis=1))
    fig = px.scatter_3d(df, x=0, y=1, z=2, color=3)
    fig.show()


if __name__ == "__main__":
    local_run2()
