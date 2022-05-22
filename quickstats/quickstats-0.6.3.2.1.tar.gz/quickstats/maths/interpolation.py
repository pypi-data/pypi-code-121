import numpy as np

def get_intersections(x:np.ndarray, y:np.ndarray, level:float, delta:float=0.01):
    from scipy.interpolate import interp1d
    func_interp = interp1d(x, y)
    x_interp = np.arange(min(x), max(x), delta)
    y_interp = func_interp(x_interp)

    asign = np.sign(y_interp - level)
    sign_change   = (np.roll(asign, 1) - asign) != 0
    intersections = x_interp[sign_change]
    sign_slope    = asign[sign_change]
    # no intersections
    if len(intersections) == 0:
        return []
    if len(intersections) == 1:
        if sign_slope[0] == -1:
            return np.array([[intersections[0], np.inf]])
        else:
            return np.array([[-np.inf, intersections[0]]])
    else:
        if sign_slope[0] == 1:
            intersections = np.insert(intersections, 0, -np.inf)
        if sign_slope[-1] == -1:
            intersections = np.insert(intersections, intersections.shape[0], np.inf)
        if len(intersections) & 1:
            raise RuntimeError("number of intersections can not be odd")
        n_pairs = len(intersections) // 2
        return intersections.reshape((n_pairs, 2))