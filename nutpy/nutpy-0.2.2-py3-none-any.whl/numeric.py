import cmath
import numpy as np
from numba import jit


def Rint(ts, alpha, beta, delta, omega_prec, omega_spin):
    """
    Computes r coordinate of the interior curve for the instant ts

    Parameters
    ----------
    ts : float
        Time of interest (s)
    alpha : float
        SSP parameter (rad)
    beta : float
        SSP parameter (rad)
    delta : float
        SSP parameter (rad)
    omega_prec : float
        Precession motion speed (rad/s)
    omega_spin : float
        Spin motion speed (rad/s)

    Returns
    -------
    R : float
        Value of the r coordinate for the interior curve (rad)
    """

    def x(t):
        x = (np.cos(omega_prec * t) * np.sin(beta) * np.sin(omega_spin * t)
             + np.sin(omega_prec * t) * (np.cos(alpha) * np.sin(beta) * np.cos(omega_spin * t)
             + np.sin(alpha) * np.cos(beta)))
        return x

    def y(t):
        y = (np.cos(alpha) * np.cos(beta)
             - np.sin(alpha) * np.sin(beta) * np.cos(omega_spin * t))
        return y

    def z(t):
        z = (- np.sin(omega_prec * t) * (np.sin(beta) * np.sin(omega_spin * t))
             + np.cos(omega_prec * t) * (np.cos(alpha) * np.sin(beta) * np.cos(omega_spin * t)
             + np.sin(alpha) * np.cos(beta)))
        return z

    def dx(t):
        dx = (- np.sin(omega_prec * t) * omega_prec * np.sin(beta) * np.sin(omega_spin * t)
              + np.cos(omega_prec * t) * (np.sin(beta) * np.cos(omega_spin * t)) * omega_spin
              + np.cos(omega_prec * t) * omega_prec * np.cos(alpha) * np.sin(beta) * np.cos(omega_spin * t)
              - np.sin(omega_prec * t) * np.cos(alpha) * np.sin(beta) * np.sin(omega_spin * t) * omega_spin
              + np.cos(omega_prec * t) * omega_prec * np.sin(alpha) * np.cos(beta))
        return dx

    def dy(t):
        dy = np.sin(alpha) * np.sin(beta) * np.sin(omega_spin * t) * omega_spin
        return dy

    def dz(t):
        dz = (- np.cos(omega_prec * t) * omega_prec * (np.sin(beta) * np.sin(omega_spin * t))
              - np.sin(omega_prec * t) * (np.sin(beta) * np.cos(omega_spin * t)) * omega_spin
              - np.sin(omega_prec * t) * omega_prec * np.cos(alpha) * np.sin(beta) * np.cos(omega_spin * t)
              - np.cos(omega_prec * t) * np.cos(alpha) * np.sin(beta) * np.sin(omega_spin * t) * omega_spin
              - np.sin(omega_prec * t) * omega_prec * np.sin(alpha) * np.cos(beta))
        return dz

    dx_s = dx(ts)/np.sqrt((dx(ts))**2 + (dy(ts))**2 + (dz(ts))**2)
    # dy_s = dy(ts)/np.sqrt((dx(ts))**2 + (dy(ts))**2 + (dz(ts))**2)
    dz_s = dz(ts)/np.sqrt((dx(ts))**2 + (dy(ts))**2 + (dz(ts))**2)

    # nx = y(ts) * dz_s-z(ts) * dy_s
    ny = -x(ts) * dz_s+z(ts) * dx_s
    # nz = x(ts) * dy_s-y(ts) * dx_s

    # xi_s = x(ts) * np.cos(delta) - nx * np.sin(delta)
    yi_s = y(ts) * np.cos(delta) - ny * np.sin(delta)
    # zi_s = z(ts) * np.cos(delta) - nz * np.sin(delta)

    R = np.arccos(yi_s)

    return R


def Rext(ts, alpha, beta, delta, omega_prec, omega_spin):
    """
    Computes r coordinate of the exterior curve for the instant ts

    Parameters
    ----------
    ts : float
        Time of interest (s)
    alpha : float
        SSP parameter (rad)
    beta : float
        SSP parameter (rad)
    delta : float
        SSP parameter (rad)
    omega_prec : float
        Precession motion speed (rad/s)
    omega_spin : float
        Spin motion speed (rad/s)

    Returns
    -------
    R : float
        Value of the r coordinate for the exterior curve (rad)
    """

    def x(t):
        x = (np.cos(omega_prec * t) * (np.sin(beta) * np.sin(omega_spin * t))
             + np.sin(omega_prec * t) * (np.cos(alpha) * np.sin(beta) * np.cos(omega_spin * t)
             + np.sin(alpha) * np.cos(beta)))
        return x

    def y(t):
        y = (np.cos(alpha) * np.cos(beta)
             - np.sin(alpha) * np.sin(beta) * np.cos(omega_spin * t))
        return y

    def z(t):
        z = (- np.sin(omega_prec * t) * (np.sin(beta) * np.sin(omega_spin * t))
             + np.cos(omega_prec * t) * (np.cos(alpha) * np.sin(beta) * np.cos(omega_spin * t)
             + np.sin(alpha) * np.cos(beta)))
        return z

    def dx(t):
        dx = (- np.sin(omega_prec * t) * omega_prec * np.sin(beta) * np.sin(omega_spin * t)
              + np.cos(omega_prec * t) * (np.sin(beta) * np.cos(omega_spin * t)) * omega_spin
              + np.cos(omega_prec * t) * omega_prec * np.cos(alpha) * np.sin(beta) * np.cos(omega_spin * t)
              - np.sin(omega_prec * t) * np.cos(alpha) * np.sin(beta) * np.sin(omega_spin * t) * omega_spin
              + np.cos(omega_prec * t) * omega_prec * np.sin(alpha) * np.cos(beta))
        return dx

    def dy(t):
        dy = np.sin(alpha) * np.sin(beta) * np.sin(omega_spin * t) * omega_spin
        return dy

    def dz(t):
        dz = (- np.cos(omega_prec * t) * omega_prec * (np.sin(beta) * np.sin(omega_spin * t))
              - np.sin(omega_prec * t) * (np.sin(beta) * np.cos(omega_spin * t)) * omega_spin
              - np.sin(omega_prec * t) * omega_prec * np.cos(alpha) * np.sin(beta) * np.cos(omega_spin * t)
              - np.cos(omega_prec * t) * np.cos(alpha) * np.sin(beta) * np.sin(omega_spin * t) * omega_spin
              - np.sin(omega_prec * t) * omega_prec * np.sin(alpha) * np.cos(beta))
        return dz

    dx_s = dx(ts)/np.sqrt((dx(ts))**2+(dy(ts))**2+(dz(ts))**2)
    # dy_s = dy(ts)/np.sqrt((dx(ts))**2+(dy(ts))**2+(dz(ts))**2)
    dz_s = dz(ts)/np.sqrt((dx(ts))**2+(dy(ts))**2+(dz(ts))**2)

    # nx = y(ts) * dz_s-z(ts) * dy_s
    ny = -x(ts) * dz_s+z(ts) * dx_s
    # nz = x(ts) * dy_s-y(ts) * dx_s

    # xe_s = x(ts) * np.cos(delta)+nx * np.sin(delta)
    ye_s = y(ts) * np.cos(delta)+ny * np.sin(delta)
    # ze_s = z(ts) * np.cos(delta)+nz * np.sin(delta)

    R = np.arccos(ye_s)

    return R


def Thetaint(ts, alpha, beta, delta, omega_prec, omega_spin):
    """
    Computes theta coordinate of the interior curve for the instant ts

    Parameters
    ----------
    ts : float
        Time of interest (s)
    alpha : float
        SSP parameter (rad)
    beta : float
        SSP parameter (rad)
    delta : float
        SSP parameter (rad)
    omega_prec : float
        Precession motion speed (rad/s)
    omega_spin : float
        Spin motion speed (rad/s)

    Returns
    -------
    theta : float
        Value of the theta coordinate for the interior curve (rad)
    """

    def x(t):
        x = (np.cos(omega_prec * t) * (np.sin(beta) * np.sin(omega_spin * t))
             + np.sin(omega_prec * t) * (np.cos(alpha) * np.sin(beta) * np.cos(omega_spin * t)
             + np.sin(alpha) * np.cos(beta)))
        return x

    def y(t):
        y = (np.cos(alpha) * np.cos(beta)
             - np.sin(alpha) * np.sin(beta) * np.cos(omega_spin * t))
        return y

    def z(t):
        z = (- np.sin(omega_prec * t) * (np.sin(beta) * np.sin(omega_spin * t))
             + np.cos(omega_prec * t) * (np.cos(alpha) * np.sin(beta) * np.cos(omega_spin * t)
             + np.sin(alpha) * np.cos(beta)))
        return z

    def dx(t):
        dx = (- np.sin(omega_prec * t) * omega_prec * np.sin(beta) * np.sin(omega_spin * t)
              + np.cos(omega_prec * t) * (np.sin(beta) * np.cos(omega_spin * t)) * omega_spin
              + np.cos(omega_prec * t) * omega_prec * np.cos(alpha) * np.sin(beta) * np.cos(omega_spin * t)
              - np.sin(omega_prec * t) * np.cos(alpha) * np.sin(beta) * np.sin(omega_spin * t) * omega_spin
              + np.cos(omega_prec * t) * omega_prec * np.sin(alpha) * np.cos(beta))
        return dx

    def dy(t):
        dy = np.sin(alpha) * np.sin(beta) * np.sin(omega_spin * t) * omega_spin
        return dy

    def dz(t):
        dz = (- np.cos(omega_prec * t) * omega_prec * (np.sin(beta) * np.sin(omega_spin * t))
              - np.sin(omega_prec * t) * (np.sin(beta) * np.cos(omega_spin * t)) * omega_spin
              - np.sin(omega_prec * t) * omega_prec * np.cos(alpha) * np.sin(beta) * np.cos(omega_spin * t)
              - np.cos(omega_prec * t) * np.cos(alpha) * np.sin(beta) * np.sin(omega_spin * t) * omega_spin
              - np.sin(omega_prec * t) * omega_prec * np.sin(alpha) * np.cos(beta))
        return dz

    dx_s = dx(ts)/np.sqrt((dx(ts))**2 + (dy(ts))**2 + (dz(ts))**2)
    dy_s = dy(ts)/np.sqrt((dx(ts))**2 + (dy(ts))**2 + (dz(ts))**2)
    dz_s = dz(ts)/np.sqrt((dx(ts))**2 + (dy(ts))**2 + (dz(ts))**2)

    nx = y(ts) * dz_s - z(ts) * dy_s
    ny = -x(ts) * dz_s + z(ts) * dx_s
    nz = x(ts) * dy_s - y(ts) * dx_s

    xi_s = x(ts) * np.cos(delta) - nx * np.sin(delta)
    yi_s = y(ts) * np.cos(delta) - ny * np.sin(delta)
    zi_s = z(ts) * np.cos(delta) - nz * np.sin(delta)

    R = cmath.acos(yi_s)

    if np.sign(xi_s) >= 0:
        Theta = np.real(cmath.acos(zi_s/np.sin(R)))
    else:
        Theta = 2 * np.pi - np.real(cmath.acos(zi_s/np.sin(R)))

    return Theta


def Thetaext(ts, alpha, beta, delta, omega_prec, omega_spin):
    """
    Computes theta coordinate of the exterior curve for the instant ts

    Parameters
    ----------
    ts : float
        Time of interest (s)
    alpha : float
        SSP parameter (rad)
    beta : float
        SSP parameter (rad)
    delta : float
        SSP parameter (rad)
    omega_prec : float
        Precession motion speed (rad/s)
    omega_spin : float
        Spin motion speed (rad/s)

    Returns
    -------
    theta : float
        Value of the theta coordinate for the exterior curve (rad)
    """

    def x(t):
        x = (np.cos(omega_prec * t) * (np.sin(beta) * np.sin(omega_spin * t))
             + np.sin(omega_prec * t) * (np.cos(alpha) * np.sin(beta) * np.cos(omega_spin * t)
             + np.sin(alpha) * np.cos(beta)))
        return x

    def y(t):
        y = np.cos(alpha) * np.cos(beta)-np.sin(alpha) * np.sin(beta) * np.cos(omega_spin * t)
        return y

    def z(t):
        z = (- np.sin(omega_prec * t) * (np.sin(beta) * np.sin(omega_spin * t))
             + np.cos(omega_prec * t) * (np.cos(alpha) * np.sin(beta) * np.cos(omega_spin * t)
             + np.sin(alpha) * np.cos(beta)))
        return z

    def dx(t):
        dx = (- np.sin(omega_prec * t) * omega_prec * np.sin(beta) * np.sin(omega_spin * t)
              + np.cos(omega_prec * t) * (np.sin(beta) * np.cos(omega_spin * t)) * omega_spin
              + np.cos(omega_prec * t) * omega_prec * np.cos(alpha) * np.sin(beta) * np.cos(omega_spin * t)
              - np.sin(omega_prec * t) * np.cos(alpha) * np.sin(beta) * np.sin(omega_spin * t) * omega_spin
              + np.cos(omega_prec * t) * omega_prec * np.sin(alpha) * np.cos(beta))
        return dx

    def dy(t):
        dy = np.sin(alpha) * np.sin(beta) * np.sin(omega_spin * t) * omega_spin
        return dy

    def dz(t):
        dz = (- np.cos(omega_prec * t) * omega_prec * (np.sin(beta) * np.sin(omega_spin * t))
              - np.sin(omega_prec * t) * (np.sin(beta) * np.cos(omega_spin * t)) * omega_spin
              - np.sin(omega_prec * t) * omega_prec * np.cos(alpha) * np.sin(beta) * np.cos(omega_spin * t)
              - np.cos(omega_prec * t) * np.cos(alpha) * np.sin(beta) * np.sin(omega_spin * t) * omega_spin
              - np.sin(omega_prec * t) * omega_prec * np.sin(alpha) * np.cos(beta))
        return dz

    dx_s = dx(ts)/np.sqrt((dx(ts))**2 + (dy(ts))**2 + (dz(ts))**2)
    dy_s = dy(ts)/np.sqrt((dx(ts))**2 + (dy(ts))**2 + (dz(ts))**2)
    dz_s = dz(ts)/np.sqrt((dx(ts))**2 + (dy(ts))**2 + (dz(ts))**2)

    nx = y(ts) * dz_s - z(ts) * dy_s
    ny = -x(ts) * dz_s + z(ts) * dx_s
    nz = x(ts) * dy_s - y(ts) * dx_s

    xe_s = x(ts) * np.cos(delta) + nx * np.sin(delta)
    ye_s = y(ts) * np.cos(delta) + ny * np.sin(delta)
    ze_s = z(ts) * np.cos(delta) + nz * np.sin(delta)

    R = np.arccos(ye_s)

    # REVISE AND ADAPT
    if np.sign(xe_s) >= 0:
        Theta = np.real(cmath.acos(ze_s/np.sin(R)))
    else:
        Theta = 2 * np.pi - np.real(cmath.acos(ze_s/np.sin(R)))

    return Theta


def theta_ext_simple(alpha, beta, delta, r):
    """
    Computes exterior theta for negligible precession

    Parameters
    ----------
    alpha : float
        SSP parameter (rad)
    beta : float
        SSP parameter (rad)
    delta : float
        SSP parameter (rad)
    r : float
        Angle with precesion axis (rad)

    Returns
    -------
    theta_e : float
        Value of exterior theta
    """

    theta_e = np.real(cmath.acos((np.cos(beta - delta) - np.cos(alpha) * np.cos(r))/(np.sin(alpha) * np.sin(r))))

    return theta_e


def theta_int_simple(alpha, beta, delta, r):
    """
    Computes interior theta for negligible precession

    Parameters
    ----------
    alpha : float
        SSP parameter (rad)
    beta : float
        SSP parameter (rad)
    delta : float
        SSP parameter (rad)
    r : float
        Angle with precesion axis (rad)

    Returns
    -------
    theta_i : float
        Value of interior theta
    """

    theta_i = np.real(cmath.acos((np.cos(beta + delta) - np.cos(alpha) * np.cos(r))/(np.sin(alpha) * np.sin(r))))

    return theta_i


def norm(v):
    """
    Calculates norm of vector

    Parameters
    ----------
    v : ndarray (3x1)
        Input vector

    Returns
    -------
    mod : float
        Norm of vector
    """

    mod = np.sqrt(v[0]**2 + v[1]**2 + v[2]**2)

    return mod


def perpendicular_vector(u):
    """
    Finds an arbitrary perpendicular vector

    Parameters
    ----------
    u : ndarray/list (n,)
        Input sequence of numbers

    Returns
    -------
    v : ndarray (n,)
        Resulting sequence
    """

    ux = u[0, 0]
    uy = u[1, 0]
    uz = u[2, 0]

    if ux == uy == uz == 0:
        raise NameError('zero-vector')

    if ux == 0:
        return np.array([1, 0, 0]).reshape(-1, 1)
    if uy == 0:
        return np.array([0, 1, 0]).reshape(-1, 1)
    if uz == 0:
        return np.array([0, 0, 1]).reshape(-1, 1)

    v = np.array([1, 1, -1.0 * (ux + uy) / uz]).reshape(-1, 1)

    return v


def pol2cart(rho, phi):
    """
    Transform polar coordinates to cartesian coordinates

    Parameters
    ----------
    rho : ndarray (1xn)
        radius
    phi : ndarray (1xn)
        polar angle (rad)

    Returns
    -------
    x, y : tuple (2)
        cartesian coordinates

    """

    x = rho * np.cos(phi)
    y = rho * np.sin(phi)

    return (x, y)


@jit
def g_alpha(Ep, enter):
    """
    Computes G(alpha) parameter for a given sensor.

    G(alpha) parameter indicates if the signal has arrived to the sensor
    with different orientations regarding the sensor frame. Similar orientations
    bring the parameter closer to 1 and different orientations make the
    parameter closer to 0.

    Parameters
    ----------
    Ep : 1D-array
        Polarization of the arriving signal measured in the sensor frame
    enter : 1D-array
        Indexes of sensor access starting instant

    Returns
    -------
    G : float
        Value of parameter
    """

    # Get polarization vector over sensor (only one value per sensor access)
    Ep_sensor_access = Ep[:, enter]

    # Compute measured polarization
    alpha = np.arctan2(Ep_sensor_access[2], Ep_sensor_access[1])

    G = np.sin(2 * alpha).mean()**2 + np.cos(2 * alpha).mean()**2

    return G


@jit(nopython=True)
def circle_check(x, y, xref, yref, r):
    """
    Checks if coordinates are inside circle or radius r.

    Parameters
    ----------
    x : 1D-array
        X coordinates
    y : 1D-array
        Y coordinates
    r : float
        Radius of circle

    Returns
    -------
    check_result : 1D-array of booleans
        If True, coordinates are inside circle
    """

    check_result = (x - xref)**2 + (y - yref)**2 < r**2

    return check_result
