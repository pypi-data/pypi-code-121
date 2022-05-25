"""
Useful methods of algorithm classes
"""
import numpy as np


def box_constraints(x, x_bounds):
    """Corrects violated dimensions to box constraints limits.

    Args:
        x       : (n x 1)-array with point inside hypercube.
        x_bounds: (n x 2)-array with upper and lower bounds

    Returns:
        xc: projected point

    """

    # input check
    n = x.shape[0]  # dimension
    m, b = x_bounds.shape
    if not isinstance(x, np.ndarray) or not isinstance(x_bounds, np.ndarray):
        raise Warning("Input must be a numpy instance!")

    if b != 2 or n != m:
        raise Warning("x_bounds must be a {}x{}-array.".format(n, 2))

    # corrected x
    xc = .5*(x_bounds[:, 1] + x_bounds[:, 0])  # centers

    # corrects x_min violations
    il = np.where(np.less(x, x_bounds[:, [0]]))[0]
    x[il, :] = xc[il].reshape(-1, 1)

    # corrects x_max violations
    ig = np.where(np.greater(x, x_bounds[:, [1]]))[0]
    x[ig, :] = xc[ig].reshape(-1, 1)

    return x


def hypercube_intersection(x, d, x_bounds):
    """Intersection with a hypercube facets.

    Args:
        x: (n x 1)-array with point inside hypercube.
        d: (n x 1)-array with direction.
        x_bounds: (n x 2)-array with upper and lower bounds

    Returns:
        a: non-negative constant such that x + a*d lies on one face of the hypercube.
        tight_dim: dimension that represents the first face towards d from x.

    """

    # input check
    n = x.shape[0]  # dimension
    m, b = x_bounds.shape
    if not isinstance(x, np.ndarray) or not isinstance(d, np.ndarray) or not isinstance(x_bounds, np.ndarray):
        raise Warning("Input must be a numpy instance!")

    if n != d.shape[0]:
        raise Warning("Point x and direction d must have the same dimension.")

    if b != 2 or n != m:
        raise Warning("x_bounds must be a {}x{}-array.".format(n, 2))

    # lower bounds are towards negative components of d, upper bounds are towards positive components of d
    c = x_bounds[:, 0].copy()
    igz = np.where(d > 0)[0]
    c[igz] = x_bounds[igz, 1].copy()

    # neglect null utils of d
    inz = np.where(d != 0)[0]

    # find a and tight dim
    a_set = (c[inz] - x[inz].ravel()) / d[inz].ravel()
    a = np.min(a_set)
    tight_dim = inz[np.argmin(a_set)]

    return a, tight_dim


def pareto_set(fx):
    """Identification of a Pareto subset.

        Args:
            fx: (n x m)-array of n functions and m points.

        Output
            ip: (m)-list of booleans indicating whether i in [0,m-1] is non-dominated.

    """

    # number of points
    m = fx.shape[1]

    # Pareto comparison
    ip = [True] * m
    for i in range(m):
        fxm = np.tile(fx[:, i].reshape(-1, 1), (1, m))
        if np.any(np.all(fxm >= fx, 0) & np.any(fxm != fx, 0)):
            ip[i] = False  # is non-dominated

    return ip


def pareto_sort(fx):
    """Sort points according to Pareto dominance.

        Args:
            fx: (n x m)-array of n functions and m points.

        Output
            F: (k)-list containing sorted k non-dominated fronts.

    """

    # aux variable
    fxa = fx.copy()
    n = fxa.shape[1]

    # main loop
    F = []  # fronts
    while n:
        # i-th Pareto front
        ip = pareto_set(fxa)

        # append front
        F.append(fxa[:, ip])

        # remove found front
        fxa = fxa[:, np.logical_not(ip)]
        n = fxa.shape[1]

    return F


def sequence_patterns(fx, x):
    """Finds a-v-patterns in a sequence of points.

    Args:
        fx: (n,)-array with function evaluations
        x : (n,)-array with an ordered sequence.

    Returns:
        ivp: indices of v-patterns
        iap: indices of a-patterns
    """

    # numpy check
    if not isinstance(x, np.ndarray):
        raise Warning("Input must be a numpy instance!")

    # dimension check
    d = x.shape
    if len(d) > 2:
        raise ValueError("x must be a sequence!")
    elif d[0] < 3:
        raise ValueError("x must be a sequence with more than three elements!")
    elif d != fx.shape:
        raise ValueError("x and fx must have the same dimension!")

    # ordering check
    if np.diff(a=x).any() < 0:
        raise ValueError("x must be an increasing sequence.")

    # cardinalities
    n = d[0]

    # possible patterns
    s = np.c_[np.arange(0, n-2).reshape(-1, 1), np.arange(1, n-1).reshape(-1, 1), np.arange(2, n).reshape(-1, 1)]
    patterns = np.sign(np.diff(a=fx[s], n=1, axis=1))

    # v-a-patterns
    ip = np.prod(a=patterns, axis=1) <= 0  # index of patterns
    i = np.arange(0, len(ip))
    i = i[ip]
    ivp = s[i[patterns[i, 0] < 0], 1]
    iap = s[i[patterns[i, 0] > 0], 1]

    return ivp, iap
