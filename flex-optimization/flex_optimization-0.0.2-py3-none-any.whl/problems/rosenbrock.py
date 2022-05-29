

import numpy as np

from flex_optimization import OptimizationType
from flex_optimization.problems import ProblemClassification
from flex_optimization.problems.utils import to_numpy_array


def rosenbrock(args, constant: float = 10) -> np.ndarray:
    """
    Rosenbrock function

    Features
    -------
    * non-convex function
    * one of minima
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
    if d % 2 != 0:
        raise ValueError("Rosenbrock requires even dimensions. Use 'rosebrock_varient' for non-even dimensions.")

    sum_ = np.zeros(n)
    for i in range(1, int(d/2)+1):
        sum_ += constant * (args[:, 2*i-2]**2 - args[:, 2*i-1])**2 + (args[:, 2*i-2]-1)**2
    return constant*d + sum_


def goal(d: int):
    return np.ones(d)


classification_class = ProblemClassification(
    name="rosenbrock",
    func=rosenbrock,
    type_=OptimizationType.MIN,
    global_goal=goal,
    range_=(-5, 5),
    local_min=100,
    num_dim=(2, float('inf')),
    convex=False,
    roughness=0,
    symmetric=False,
)


def local_run():
    n = 100
    x = np.linspace(-5, 5, n)
    y = np.linspace(-5, 5, n)
    xx, yy = np.meshgrid(x, y)

    xx = xx.T.reshape(n*n)
    yy = yy.T.reshape(n*n)
    zz = rosenbrock([xx, yy])

    import plotly.graph_objs as go
    fig = go.Figure(go.Surface(x=x, y=y, z=zz.T.reshape(n, n)))
    fig.add_trace(go.Scatter3d(x=[1], y=[1], z=[1], mode="markers", marker=dict(color="white", size=5)))
    # fig.write_image("imgs//rosenbrock.svg")
    fig.show()


if __name__ == "__main__":
    local_run()
