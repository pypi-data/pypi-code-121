import numpy as np


def generate_test_model(model_version=1):
    """Generates a test model for synthmod 1d

    Parameters
    ----------
    model_version : int, optional
        Model version, by default 1

    Returns
    -------
    Tuple[np.ndarray]
        depth, vp, vs, rhob, delta, epsilon, gamma
    """
    if model_version == 1:

        vp = [1480, 3000, 3200, 3500]
        vs = [0, 1500, 1900, 2000]
        rhob = [1, 2.55, 2.2, 2.6]
        delta = [0, 0.1, 0, 0.08]
        thickness = [300, 1000, 200, 1000]

    elif model_version == 2:
        # hard layer creating critical angle
        vp = [1480, 3000, 5500, 3200, 3500]
        vs = [0, 1500, 3500, 1900, 2000]
        rhob = [1, 2.55, 2.9, 2.2, 2.6]
        delta = [0, 0.1, 0, 0, 0.08]
        thickness = [300, 1000, 200, 200, 1000]

    epsilon = list(2 * np.array(delta))
    gamma = list(3 * np.array(delta))
    depth = np.cumsum(thickness)

    # double first layer (values defined as down-to)
    vp = np.insert(vp, 0, vp[0])
    vs = np.insert(vs, 0, vs[0])
    rhob = np.insert(rhob, 0, rhob[0])
    delta = np.insert(delta, 0, delta[0])
    epsilon = np.insert(epsilon, 0, epsilon[0])
    gamma = np.insert(gamma, 0, gamma[0])
    depth = np.insert(depth, 0, 0)

    return depth, vp, vs, rhob, delta, epsilon, gamma
