
import numpy as np

from flex_optimization import OptimizationType
from flex_optimization.problems import ProblemClassification
from flex_optimization.problems.utils import to_numpy_array


def nd_gaussian(args,
                sigma: float | list[float] = None,
                pre_factor: float = 1,
                center: float | list[float] = None) -> np.ndarray:
    """
    n-dimensional Gaussian function

    Features:
    --------
    * smooth optimization
    * single minima at [0,0,..,1]

    Parameters
    ----------
    args: array
        [x[:], y[:], z[:], ...] or np.ndarray[:,:,:] (first index determines dimensionality)
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
    args = to_numpy_array(args)
    d = args.shape[1]
    n = args.shape[0]

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

    def single_dim_exponent(x_, x0, sigma_):
        return (x_-x0)**2/(2*sigma_**2)

    if d == 1:
        return pre_factor*np.exp(-single_dim_exponent(args, center, sigma))

    exponent = np.zeros(n)
    for i in range(args.shape[1]):
        exponent += single_dim_exponent(args[:, i], center[i], sigma[i])

    return pre_factor*np.exp(-exponent)


def goal(d: int):
    values = np.zeros(d)
    values[-1] = 1
    return values


classification_class = ProblemClassification(
    name="gaussian",
    func=nd_gaussian,
    type_=OptimizationType.MAX,
    global_goal=goal,
    range_=(-5, 5),
    local_min=0,
    num_dim=(1, float('inf')),
    convex=True,
    roughness=0,
    symmetric=True
)


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
    fig.add_trace(go.Scatter3d(x=[0], y=[0], z=[1], mode="markers", marker=dict(color="white", size=5)))

    # fig.write_image("imgs//gaussian.svg")
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
    local_run()
