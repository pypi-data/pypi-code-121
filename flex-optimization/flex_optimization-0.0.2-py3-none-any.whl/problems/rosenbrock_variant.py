import numpy as np

from flex_optimization import OptimizationType
from flex_optimization.problems import ProblemClassification
from flex_optimization.problems.utils import to_numpy_array


def rosenbrock_variant(args, constant: float = 10) -> np.ndarray:
    """
    Rosenbrock function - variant

    Features
    -------
    * non-convex function
    * one of local minima as [-1,1,1,...]
    * global minima is at 1
    * typical x range [-5, 5]

    Parameters
    ----------
    args: array
        [x[:], y[:], z[:], ...] or np.ndarray[:,:] (second index determines dimensionality)
        the number of values determines dimensionality
    constant: float
        constant

    Returns
    -------
    return: np.ndarray
        z value

    """
    args = to_numpy_array(args)
    d = args.shape[1]
    n = args.shape[0]
    if 3 < d < 7:
        raise ValueError("Rosenbrock requires even dimensions. Use 'rosebrock_varient' for non-even dimensions.")

    sum_ = np.zeros(n)
    for i in range(1, d):
        sum_ += constant * (args[:, i] - args[:, i - 1] ** 2) ** 2 + (1 - args[:, i - 1]) ** 2
    return constant * d + sum_


def goal(d: int):
    return np.zeros(d)


classification_class = ProblemClassification(
    name="rosenbrock_variant",
    func=rosenbrock_variant,
    type_=OptimizationType.MIN,
    global_goal=goal,
    range_=(-5, 5),
    local_min=1,
    num_dim=(3, 7),
    convex=False,
    roughness=0,
    symmetric=False,
)


def local_run2():
    n = 10
    x = np.linspace(-5.12, 5.12, n)
    y = np.linspace(-5.12, 5.12, n)
    z = np.linspace(-5.12, 5.12, n)
    xx, yy, zz = np.meshgrid(x, y, z)

    xx = xx.T.reshape(n * n * n)
    yy = yy.T.reshape(n * n * n)
    zz = zz.T.reshape(n * n * n)
    aa = rosenbrock_variant([xx, yy, zz])

    import plotly.express as px
    import plotly.graph_objs as go
    import pandas as pd
    df = pd.DataFrame(np.stack((xx, yy, zz, aa), axis=1))
    fig = px.scatter_3d(df, x=0, y=1, z=2, color=3)
    fig.add_trace(go.Scatter3d(x=[1], y=[1], z=[1], mode="markers", marker=dict(color="white", size=5)))

    camera = dict(
        up=dict(x=0, y=0, z=1),
        center=dict(x=0, y=0, z=0),
        eye=dict(x=1.8, y=1.58, z=0.45)
    )
    fig.update_layout(scene_camera=camera)
    # fig.write_image("imgs//rosenbrock_variant.svg")
    fig.show()


if __name__ == "__main__":
    local_run2()
