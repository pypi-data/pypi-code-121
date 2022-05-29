
import numpy as np

from flex_optimization import OptimizationType
from flex_optimization.problems import ProblemClassification
from flex_optimization.problems.utils import to_numpy_array


def ackley(args) -> np.ndarray:
    """
    Ackley function

    References
    ----------
    Ackley, D. H. (1987) "A connectionist machine for genetic hillclimbing", Kluwer Academic Publishers, Boston MA.

    Features:
    --------
    * slightly rough, but mostly smooth optimization
    * single minima at center
    * typical x range [-5, 5]

    Parameters
    ----------
    args: array
        [x[:], y[:], z[:], ...] or np.ndarray[:,:,:] (first index determines dimensionality)
        the number of values determines dimensionality

    Returns
    -------
    return: np.ndarray
        z value

    """
    args = to_numpy_array(args)
    d = args.shape[1]
    n = args.shape[0]

    first_sum = np.zeros(n)
    second_sum = np.zeros(n)
    for i in range(args.shape[1]):
        first_sum += args[:, i]**2
        second_sum += np.cos(2 * np.pi * args[:, i])

    return -20.0*np.exp(-0.2*np.sqrt(first_sum/d)) - np.exp(second_sum/d) + 20 + np.e


def goal(d: int):
    return np.zeros(d)


classification_class = ProblemClassification(
    name="ackley",
    func=ackley,
    type_=OptimizationType.MIN,
    global_goal=goal,
    range_=(-5, 5),
    local_min=100,
    num_dim=(1, float('inf')),
    convex=False,
    roughness=5,
    symmetric=True
)


def local_run():
    n = 100
    x = np.linspace(-5, 5, n)
    y = np.linspace(-5, 5, n)
    xx, yy = np.meshgrid(x, y)

    xx = xx.T.reshape(n*n)
    yy = yy.T.reshape(n*n)
    zz = ackley([xx, yy])

    import plotly.graph_objs as go
    fig = go.Figure(go.Surface(x=x, y=y, z=zz.T.reshape(n, n)))
    # fig.write_image("imgs//ackley.svg")
    fig.show()


def local_run2():
    n = 20
    x = np.linspace(-5, 5, n)
    y = np.linspace(-5, 5, n)
    z = np.linspace(-5, 5, n)
    xx, yy, zz = np.meshgrid(x, y, z)

    xx = xx.T.reshape(n*n*n)
    yy = yy.T.reshape(n*n*n)
    zz = zz.T.reshape(n*n*n)
    aa = ackley([xx, yy, zz])

    import plotly.express as px
    import pandas as pd
    df = pd.DataFrame(np.stack((xx, yy, zz, aa), axis=1))
    fig = px.scatter_3d(df, x=0, y=1, z=2, color=3)
    fig.show()


if __name__ == "__main__":
    local_run()
