
import numpy as np

from flex_optimization import OptimizationType
from flex_optimization.problems import ProblemClassification
from flex_optimization.problems.utils import to_numpy_array


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
        [x[:], y[:], z[:], ...] or np.ndarray[:,:] (second index determines dimensionality)
        the number of values determines dimensionality
    constant: float

    Returns
    -------
    return: np.ndarray
        z value

    """
    args = to_numpy_array(args)
    d = args.shape[1]
    n = args.shape[0]

    sum_ = np.zeros(n)
    for i in range(args.shape[1]):
        sum_ += args[:, i]**2 - constant * np.cos(2 * np.pi * args[:, i])

    return constant*d + sum_


def goal(d: int):
    return np.zeros(d)


classification_class = ProblemClassification(
    name="rastrigin",
    func=rastrigin,
    type_=OptimizationType.MIN,
    global_goal=goal,
    range_=(-5.12, 5.12),
    local_min=100,
    num_dim=(1, float('inf')),
    convex=False,
    roughness=7,
    symmetric=True
)


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
    fig.add_trace(go.Scatter3d(x=[0], y=[0], z=[0], mode="markers", marker=dict(color="white", size=5)))
    # fig.write_image("imgs//rastrigin.svg")
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
    import plotly.graph_objs as go
    import pandas as pd
    df = pd.DataFrame(np.stack((xx, yy, zz, aa), axis=1))
    fig = px.scatter_3d(df, x=0, y=1, z=2, color=3)
    fig.add_trace(go.Scatter3d(x=[0], y=[0], z=[0], mode="markers", marker=dict(color="white", size=5)))
    fig.show()


if __name__ == "__main__":
    local_run()
