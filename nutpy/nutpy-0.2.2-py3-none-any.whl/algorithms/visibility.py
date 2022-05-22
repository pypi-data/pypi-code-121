import cmath
import warnings
import numpy as np
import scipy.integrate as integrate
from scipy.interpolate import interp1d
import scipy.optimize as opt
import matplotlib.pyplot as plt
from astropy_healpix import HEALPix
from astropy import units as u
import pandas as pd
from tqdm.autonotebook import tqdm
from numba import jit

from nutpy import numeric as nm
import nutpy.constants as cte
from nutpy.core.kinematics import rotations as kr
from nutpy.postprocessing import pgraph


def analytical_profile(SSP,
                       Nr,
                       tf,
                       quantity,
                       fig_flag,
                       precession,
                       delta_detector
                       ):
    """
    Calculates analytically the demanded quantity from the temporal analysis for
    the instrument as a function of the angle regarding the precession axis

    Parameters
    ----------
    SSP : list (5)
        Scan Strategy Parameters (alpha, beta, spin, precesion, delta)/
        (deg, deg, min, min, deg)
    Nr : int
        Resolution of results
    tf : float
        Total time considered
    quantity : str
        Quantity to be computed
    fig_flag : bool
        If True, figure is returned
    precession : str
        Method used to account for precession
    delta_detector : float
        Used for detector analysis (deg)

    Returns
    -------
    fig : matplotlib figure
        Figure of profile
    T : ndarray (N)
        Results of calculations (profile)
    """

    alpha = SSP[0]
    beta = SSP[1]
    delta = SSP[4]

    T = np.zeros(Nr)

    r = np.linspace(0, alpha + beta + delta, Nr) * np.pi/180

    if quantity == "TAT":
        T = total_access_time_profile(SSP, Nr, tf, delta_detector)
    elif quantity == "MAT":
        T = mean_access_time_profile(SSP, Nr, precession, delta_detector)
    elif quantity == "MAX":
        T = max_access_time_profile(SSP, Nr, precession, delta_detector)
    elif quantity == "NOA":
        T = number_access_profile(SSP, Nr, precession, delta_detector)
    else:
        Exception("Such result does not exist")

    if fig_flag:
        fig = plt.plot(r * 180/np.pi, T)
    else:
        fig = None

    return fig, T


def analytical_map(SSP,
                   quantity,
                   N,
                   tf,
                   fig_flag,
                   precession,
                   delta_detector,
                   nside=256,
                   units='s',
                   **kwargs
                   ):
    """
    Calculates analytically the demanded quantity for all the celestial
    sphere and plots it.

    Parameters
    ----------
    SSP : list (5)
        Scan Strategy Parameters (alpha, beta, spin, precesion, delta)/
        (deg, deg, min, min, deg)
    N : int
        Resolution of results
    tf : float
        Total time considered
    quantity : str
        Quantity to be computed
    fig_flag : bool
        If True, figure is returned
    precession : str
        Method to be used to account for precession
    delta_detector : float
        Used for detector analysis (deg)
    units : str
        Time units for the output
    cbar_size : float
        Size of the colorbar
    nside : int
        Size of healpix sphere

    Returns
    -------
    fig : matplotlib figure
        Figure of profile
    data : ndarray (N)
        Results of calculations (value per pixel for Healpix scheme)
    """

    alpha = SSP[0]
    beta = SSP[1]
    delta = SSP[4]

    Nr = N

    T = np.zeros(Nr)

    r = np.linspace(0, alpha + beta + delta, Nr) * np.pi/180

    _, T = analytical_profile(SSP, Nr, tf, quantity, False, precession, delta_detector)

    hp = HEALPix(nside=nside)
    npix = hp.npix

    T_complete = np.concatenate([np.flip(T[1:]), T], axis=0)
    r_complete = np.concatenate([np.flip(r[1:]), r], axis=0)

    f = interp1d(r_complete, T_complete, bounds_error=False, fill_value=0)

    data = np.zeros(npix)

    # generate grid over the sky
    lon, lat = hp.healpix_to_lonlat(np.arange(npix))

    # compute angle with precession axis
    x = np.cos(lon.value) * np.cos(lat.value)
    s = np.arccos(x)

    data = f(s)

    factor = 1.

    if quantity in cte.tags_dict:
        pass
    else:
        raise NameError(f"'{quantity}' result does not exist")

    main_label = cte.tags_dict[quantity]
    default_units = cte.units_dict[quantity]

    if default_units is None:
        units_label = ''
    else:
        if units == 's':
            factor = 1.
        elif units == 'min':
            factor = 60.
        elif units == 'h':
            factor = 3600.
        units_label = ' (' + units + ')'
        data = data * 1. / factor

    label = main_label + units_label

    if fig_flag:
        fig = pgraph.plot_map(data, label, N, **kwargs)
    else:
        fig = None

    return fig, data


def total_access_time_profile(SSP, Nr, tf, delta_detector):
    """
    Calculates analytically the total access time as a function of the angle regarding the precession axis

    Parameters
    ----------
    SSP : list (5)
        Scan Law Parameters (alpha, beta, spin, precesion, delta)/(deg, deg, min, min, deg)
    Nr : integer
        Discretization parameter of r coordinate
    tf : float
        Total time of simulation
    delta_detector : float
        Detector FOV half-angle

    Returns
    -------
    T : ndarray (N)
        Results of calculations (profile)
    """

    alpha = SSP[0] * np.pi/180
    beta = SSP[1] * np.pi/180
    delta_r = SSP[4] * np.pi/180

    if delta_detector is None:
        delta = delta_r
    else:
        delta = delta_detector * np.pi/180

    T = np.zeros(Nr)
    r = np.linspace(0, alpha + beta + delta_r, Nr)
    theta = np.linspace(0, np.pi, 1000)
    q = np.zeros_like(theta)

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        for i in range(Nr):
            for j, th in enumerate(theta):

                q[j] = time_ratio(th, r[i], alpha, beta, delta)

            T[i] = tf * integrate.trapz(q, x=theta)/np.pi

    return T


def time_ratio(theta, r, alpha, beta, delta):
    """
    Calculates time ratio for a given point in the sky and a SSP set.

    Parameters
    ----------
    theta : float
        Coordinate for the sky point (rad)
    r : float
        Coordinate for the sky point (rad)
    alpha : float
        Scan law parameter (rad)
    beta : float
        Scan law parameter (rad)
    delta : float
        Field of view semiangle (rad)

    Returns
    -------
    ratio : float
        Percentage of time that points with r coordinate are viewed
    """

    R = np.arccos(np.cos(alpha) * np.cos(beta) - np.sin(alpha) * np.sin(beta) * np.cos(theta))
    numerator = np.cos(delta) - np.cos(R) * np.cos(r)
    denominator = np.sin(R) * np.sin(r)

    ratio = (1/np.pi) * np.real(cmath.acos(numerator/denominator))

    return ratio


def mean_access_time_profile(SSP, Nr, precession, delta_detector):
    """
    Calculates analytically the mean access time as a function of the angle regarding the precession axis

    Parameters
    ----------
    SSP : list (5)
        Scan Law Parameters (alpha, beta, spin, precesion, delta)/(deg, deg, min, min, deg)
    Nr : integer
        Discretization parameter for r coordinate
    precession : str
        Indicates type of method used for precession aproximation trace/None/factor
    delta_detector : float/None
        Detector FOV half-angle

    Returns
    -------
    T : ndarray (N)
        Results of calculations (profile)
    """

    tf = 1

    TT = total_access_time_profile(SSP, Nr, tf, delta_detector)
    NA = number_access_profile(SSP, Nr, precession, delta_detector)
    T = TT/NA

    return T


def number_access_profile(SSP, Nr, precession, delta_detector):
    """
    Calculates analytically the access time ratio as a function of the angle regarding the precession axis

    Parameters
    ----------
    SSP : list (5)
        Scan Law Parameters (alpha, beta, spin, precesion, delta)/(deg, deg, min, min, deg)
    Nr : integer
        Discretization parameter fpr r coordinate
    precession : str
        Indicates type of method used for precession aproximation trace/None/factor
    delta_detector : float/None
        Detector FOV half-angle

    Returns
    -------
    NA : ndarray (N)
        Results of calculations (profile)
    """

    alpha = SSP[0] * np.pi/180
    beta = SSP[1] * np.pi/180
    omega_spin = 2 * np.pi/(60 * SSP[2])
    omega_prec = 2 * np.pi/(60 * SSP[3])

    delta_r = SSP[4] * np.pi/180

    if delta_detector is None:
        delta = delta_r
    else:
        delta = delta_detector * np.pi/180

    NA = np.zeros(Nr)

    r = np.linspace(0, alpha + beta + delta_r, Nr)
    if precession == 'trace':

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")

            with np.errstate(divide='ignore', invalid='ignore'):
                for i in range(Nr):

                    if r[i] > (alpha + beta - delta):
                        Theta_ee = 0

                    elif r[i] < np.abs(np.abs(alpha - beta) - delta):
                        # intersection time is found
                        timeext = opt.minimize_scalar(
                                    lambda t: (np.abs(nm.Rext(t, alpha, beta, delta, omega_prec, omega_spin)
                                               - (np.abs(np.abs(alpha - beta) - delta)))),
                                    bounds=(0., np.pi/omega_spin),
                                    method='bounded').x

                        Theta_ee = nm.Thetaext(timeext, alpha, beta, delta, omega_prec, omega_spin)

                    else:
                        timeext = opt.minimize_scalar(
                                    lambda t: np.abs(nm.Rext(t, alpha, beta, delta, omega_prec, omega_spin) - r[i]),
                                    bounds=(0., np.pi/omega_spin),
                                    method='bounded').x

                        Theta_ee = nm.Thetaext(timeext, alpha, beta, delta, omega_prec, omega_spin)

                    if r[i] > (alpha + beta + delta):
                        Theta_ii = 0

                    elif r[i] < (np.abs(alpha - beta) + delta):
                        timeint = opt.minimize_scalar(
                                    lambda t: (np.abs(nm.Rint(t, alpha, beta, delta, omega_prec, omega_spin)
                                               - (np.abs(alpha - beta) + delta))),
                                    bounds=(0., np.pi/omega_spin),
                                    method='bounded').x

                        Theta_ii = nm.Thetaint(timeint, alpha, beta, delta, omega_prec, omega_spin)

                    else:
                        timeint = opt.minimize_scalar(
                                    lambda t: np.abs(nm.Rint(t, alpha, beta, delta, omega_prec, omega_spin) - r[i]),
                                    bounds=(0., np.pi/omega_spin),
                                    method='bounded').x

                        Theta_ii = nm.Thetaint(timeint, alpha, beta, delta, omega_prec, omega_spin)

                    Delta_Theta = (Theta_ii - Theta_ee)
                    NA[i] = 1/(2 * np.pi/omega_spin) * Delta_Theta/np.pi

    elif precession is None:
        for i in range(Nr):

            if r[i] > (alpha + beta - delta):
                Theta_ee = 0

            else:
                Theta_ee = nm.theta_ext_simple(alpha, beta, delta, r[i])

            if r[i] > (alpha + beta + delta):
                Theta_ii = 0

            else:
                Theta_ii = nm.theta_int_simple(alpha, beta, delta, r[i])

            Delta_Theta = (Theta_ii - Theta_ee)
            NA[i] = 1/(2 * np.pi/omega_spin) * Delta_Theta/np.pi

    elif precession == 'factor':
        rtmax = r_time_max(delta, beta)
        for i in range(Nr):

            if r[i] > (alpha + beta - delta):
                Theta_ee = 0

            else:
                Theta_ee = (nm.theta_ext_simple(alpha, beta, delta, r[i])
                            / time_factor(omega_spin, omega_prec, alpha, rtmax, r[i]))

            if r[i] > (alpha + beta + delta):
                Theta_ii = 0

            else:
                Theta_ii = (nm.theta_int_simple(alpha, beta, delta, r[i])
                            / time_factor(omega_spin, omega_prec, alpha, rtmax, r[i]))

            Delta_Theta = (Theta_ii - Theta_ee)
            NA[i] = 1/(2 * np.pi/omega_spin) * Delta_Theta/np.pi

    return NA


def max_access_time_profile(SSP, Nr, precession, delta_detector):
    """
    Calculates analytically the maximum access time as a function of precession-axis separation angle

    Parameters
    ----------
    SSP : list (4)
        Scan Law Parameters (alpha, beta, spin, precesion)/(deg, deg, min, min)
    FOV : float
        Field of view total amplitude (deg)
    Nr : integer
        Discretization parameter of r coordinate
    precession : str
        Indicates type of method used for precession aproximation trace/None/factor
    delta_detector : float
        Detector FOV half-angle

    Returns
    -------
    T : ndarray (N)
        Results of calculations (profile)
    """

    alpha = SSP[0] * np.pi/180
    beta = SSP[1] * np.pi/180
    omega_spin = 2 * np.pi/(60 * SSP[2])
    omega_prec = 2 * np.pi/(60 * SSP[3])
    Tspin = SSP[2] * 60

    delta_r = SSP[4] * np.pi/180

    if delta_detector is None:
        delta = delta_r
    else:
        delta = delta_detector * np.pi/180

    T = np.zeros(Nr)

    r = np.linspace(0, alpha + beta + delta_r, Nr)

    rtmax = r_time_max(delta, beta)
    tmax = access_time_max(Tspin, delta, beta)

    if precession == 'trace':
        for i in range(Nr):

            if r[i] > (alpha + rtmax):
                rstar = r[i] - alpha
                T[i] = (access_time(Tspin, delta, beta, rstar)
                        * time_factor(omega_spin, omega_prec, alpha, rtmax, r[i]))

            elif r[i] < np.abs(alpha - rtmax):
                rstar = alpha - np.sign(alpha - rtmax) * r[i]
                T[i] = (access_time(Tspin, delta, beta, rstar)
                        * time_factor(omega_spin, omega_prec, alpha, rtmax, r[i]))

            else:
                T[i] = tmax * time_factor(omega_spin, omega_prec, alpha, rtmax, r[i])
    else:
        raise NotImplementedError("Only trace method is avaiable.")

    return T


def r_time_max(delta, beta):
    """
    Returns r* coordinate that produces maximum time access

    Parameters
    ----------
    delta : float
        Field of view half-angle (rad)
    beta : float
        Scan law parameter (rad)

    Returns
    -------
    rstar : float
        r* coordinate for maximum access time
    """

    numerator = np.sqrt(np.cos(delta)**2 - np.cos(beta)**2)
    denominator = np.cos(beta)

    rstar = np.arctan(numerator/denominator)

    return rstar


def access_time(Tspin, delta, beta, rstar):
    """
    Calculates the access time for defined SSP and r* coordinate

    Parameters
    ----------
    Tspin : float
        Period of spin motion (sec)
    delta : float
        Field of view half-angle (rad)
    beta : float
        Scan law parameter (rad)
    rstar : float
        r* coordinate (rad)

    Returns
    -------
    t_access : float
        Time of access (sec)
    """

    t_access = (Tspin/np.pi) * theta_access(delta, beta, rstar)

    return t_access


def access_time_max(Tspin, delta, beta):
    """
    Calculates maximum access time achievable for pure spin motion

    Parameters
    ----------
    Tspin : float
        Period of spin motion (sec)
    delta : float
        Field of view half-angle (rad)
    beta : float
        Scan law parameter (rad)

    Returns
    -------
    time_access_max : float
        Maximum time of access (sec)
    """

    numerator = np.sqrt(np.cos(delta)**2 - np.cos(beta)**2)
    denominator = np.sin(beta)

    time_access_max = (Tspin/np.pi) * np.real(cmath.acos(numerator/denominator))

    return time_access_max


def theta_access(delta, beta, rstar):
    """
    Calculates theta coordinate of access condition

    Parameters
    ----------
    delta : float
        Field of view half-angle (rad)
    beta : float
        Scan law parameter (rad)
    rstar : float
        r* coordinate (rad)

    Returns
    -------
    theta : float
        Theta coordinate when access condition is met
    """

    numerator = np.cos(delta) - np.cos(beta) * np.cos(rstar)
    denominator = np.sin(beta) * np.sin(rstar)
    theta = np.real(cmath.acos(numerator/denominator))

    return theta


def tau_f(alpha, rtmax, r):
    """
    Calculates tau angle for direction defined by r coordinate

    Parameters
    ----------
    alpha : float
        Scan law parameter (rad)
    rtmax : float
        r* coordinate for maximum time (rad)
    r : float
        r coordinate of direction of interest (rad)

    Returns
    -------
    tau_angle : float
        tau angle of direcction with r coordinate (rad)
    """

    numerator = np.cos(alpha) * np.cos(rtmax) - np.cos(r)
    denominator = np.sin(alpha) * np.sin(rtmax)

    tau = np.real(cmath.acos(numerator/denominator))

    return tau


def gamma_f(tau, phi, alpha):
    """
    Calculates gamma angle

    Parameters
    ----------
    tau : float
        tau angle (rad)
    phi : float
        phi angle (rad)
    alpha : float
        Scan law parameter (rad)

    Returns
    -------
    gamma : float
        gamma angle (rad)
    """

    gamma = (np.cos(tau) * np.cos(phi)
             + np.cos(alpha) * np.sin(tau) * np.sin(phi))

    return gamma


def phi_f(rtmax, tau, alpha):
    """
    Calculates phi angle

    Parameters
    ----------
    rtmax : float
        r* coordinate for maximum access time (rad)
    tau : float
        tau angle (rad)
    alpha : float
        Scan law parameter (rad)

    Returns
    -------
    phi_angle : float
        phi angle (rad)
    """

    numerator = np.sin(rtmax) * np.sin(tau)
    denominator = np.cos(alpha) * np.sin(rtmax) * np.cos(tau) + np.sin(alpha) * np.cos(rtmax)

    phi = np.arctan2(numerator, denominator)

    return phi


def time_factor(omega_spin, omega_prec, alpha, rtmax, r):
    """
    Calculates the correction factor for access time when precession motion is present

    Parameters
    ----------
    omega_spin : float
        Scan law parameter (rad)
    omega_prec : float
        Scan law parameter (rad)
    alpha : float
        Scan law parameter (rad)
    rtmax : float
        r* coordinate for maximum time (rad)
    r : float
        r coordinate of direction of interest (rad)

    Returns
    -------
    factor : float
        correction factor
    """

    t = tau_f(alpha, rtmax, r)
    p = phi_f(rtmax, t, alpha)
    g = gamma_f(t, p, alpha)

    k = np.sign(alpha - rtmax)

    if r > (alpha + rtmax):
        factor = (omega_spin * np.sin(r - alpha)
                  / (omega_spin * np.sin(r - alpha) + omega_prec * np.sin(r)))

    elif r < np.abs(alpha - rtmax):
        factor = (omega_spin * np.sin(alpha - r * k)
                  / (omega_spin * np.sin(alpha - r * k) - omega_prec * np.sin(r * k)))

    else:
        factor = (omega_spin * np.sin(rtmax)
                  / (omega_spin * np.sin(rtmax) + omega_prec * np.sin(r) * g))

    return factor


def numerical_analysis(instrument, nside, bar, detailed, dense, border_angle):
    """
    Performs numerical analysis

    Parameters
    ----------
    attitude_df : pandas DataFrame
        Attitude evolution expressed as quaternions stored in a DataFrame
    u0 : ndarray (3,n)
        Pointing direction in body frame
    fov : float
        Instrument field of view (degrees)
    nside : integer
        Number of divisions of the sky sphere
    bar : bool
        If True, shows progress bar

    Returns
    -------
    numerical_results_df :  pandas DataFrame
        Results of temporal analysis
    """

    hp = HEALPix(nside=nside)
    npix = hp.npix

    time, pointing = kr.pointing(instrument.attitude_df, instrument.u0)

    if bar:
        pbar = tqdm(total=npix)

    u = np.zeros((3, 1))

    rows_list = []
    sensors_results_detailed_dict = {}

    lon, lat = hp.healpix_to_lonlat(range(npix))
    lon = lon.value
    lat = lat.value

    for i in range(npix):

        row_dict = {}

        u[0, 0] = np.cos(lat[i]) * np.cos(lon[i])
        u[1, 0] = np.cos(lat[i]) * np.sin(lon[i])
        u[2, 0] = np.sin(lat[i])

        if u[0, 0] > np.cos(border_angle):
            _, visibility = visibility_analysis(pointing, time, u, instrument.fov)

            access_count, each_access_time, start_access_time, _ = process_visibility(time, visibility)
        else:
            access_count, each_access_time, start_access_time, _ = (0, [], [], None)

        total_access_time = np.sum(each_access_time)

        row_dict['TAT'] = total_access_time
        row_dict['NOA'] = access_count

        if access_count == 0:
            row_dict['MAT'] = 0
            row_dict['MAX'] = 0
        else:
            row_dict['MAT'] = total_access_time/access_count
            row_dict['MAX'] = each_access_time.max()

        if dense:
            row_dict['Accesses_list'] = each_access_time
            row_dict['Start access time'] = start_access_time

        if detailed:
            sensors_results_df = process_sensors(visibility,
                                                 instrument,
                                                 u,
                                                 i
                                                 )

            n_viewed_sensors = sum(sensors_results_df['TAT'].values != 0)
            row_dict['PVS'] = 100 * n_viewed_sensors/(instrument.nd)

            if n_viewed_sensors == 0:
                row_dict['SGA'] = None
            else:
                row_dict['SGA'] = (sensors_results_df['SGA'].values.sum() /
                                   n_viewed_sensors)

            if dense:
                sensors_results_detailed_dict[str(i)] = sensors_results_df
            else:
                sensors_results_detailed_dict[str(i)] = None

        rows_list.append(row_dict)

        if bar:
            pbar.update(1)

    if detailed and dense:
        numerical_results_detailed_df = pd.concat(sensors_results_detailed_dict.values(),
                                                  ignore_index=True).astype({'pixel_id': 'uint32',
                                                                             'sensor_id': 'uint16',
                                                                             'TAT': 'float32',
                                                                             'MAT': 'float16',
                                                                             'MAX': 'float16',
                                                                             'NOA': 'uint16',
                                                                             'SGA': 'float16'})

    numerical_results_df = pd.DataFrame(rows_list)
    numerical_results_df = numerical_results_df.astype({'TAT': 'float32',
                                                        'MAT': 'float16',
                                                        'MAX': 'float16',
                                                        'NOA': 'uint16'})

    if bar:
        pbar.close()

    return numerical_results_df, numerical_results_detailed_df


def visibility_analysis(pointing, time, u, fov):
    """
    Visibility for a given direction

    Parameters
    ----------
    pointing : ndarry (3,n)
        Pointing over time
    u : ndarray (3x1)
        Direction of study
    fov : float
        Field of view (deg)

    Returns
    -------
    time :  1D array (n,)
        Time period analized
    visibility :  1D array (n,)
        1-> direction inside fov, 0-> out of fov
    """

    delta_c = np.cos(fov * np.pi/180/2)

    dot = np.dot(pointing.T, u)
    angle = dot.flatten()

    visibility = np.where(angle > delta_c, 1, 0)

    return time, visibility


@jit(nopython=True)
def process_visibility(time, visibility):
    """
    Process raw visibility data

    Parameters
    ----------
    time :  1D array (n,)
        Time period analized
    visibility :  1D array (n,)
        1-> direction inside fov, 0-> out of fov

    Returns
    -------
    ct :  int
        Number of accesses
    each_access_time :  1D array (ct,)
        Duration of each access
    start_access_time :  1D array (ct,)
        Start time of each access
    """

    dT = time[1]

    ct = 0

    visibility_n = np.concatenate((np.array([0]), visibility, np.array([0])))
    # access_io = np.where(np.sign(visibility_n[:-1]) != np.sign(visibility_n[1:]))[0]
    acs = visibility_n[:-1] < visibility_n[1:]
    ace = visibility_n[:-1] > visibility_n[1:]

    data = np.logical_or(acs, ace)
    access_io = data.nonzero()[0]

    enter = access_io[0::2]
    each_access_time = (access_io[1::2] - access_io[0::2]) * dT
    start_access_time = enter * dT

    ct = int(len(access_io)/2)

    return ct, each_access_time, start_access_time, enter


def process_sensors(visibility, instrument, u, idx):
    """
    Detects which sensors are viewed and computes the figures of merit.
    The results

    Parameters
    ----------
    visibility : 1-D array (n)
        Indicates if there is instrument access with 1/0 in each step time
    inst_att_df : pandas dataframe
        Instrument attitude in each time step (quaternion)
    u: ndarray (3xn)
        Position in the sky
    instrument : class
        Instrument class instance

    Returns
    -------
    df : pandas dataframe
        Results of calculations
    """

    # get index of accesses
    visibility_mask = visibility.astype(bool)

    time = instrument.attitude_df.index.values

    # number of sensors
    nd = instrument.nd

    sensor_id = np.arange(nd)
    pixel_id = np.ones(nd, dtype='int16') * idx

    # if no sensor is viewed, the corresponding dataframe is full of zeros
    if visibility.sum() == 0:
        data = np.concatenate((pixel_id.reshape(-1, 1), sensor_id.reshape(-1, 1), np.zeros((nd, 5), dtype='int16')),
                              axis=1)

    else:
        # attitude of inst when there are accesses
        quats = instrument.attitude_df.values[visibility_mask, :].T

        v = kr.quat_trans_v(quats, u)

        # polarization vector
        E = nm.perpendicular_vector(u)

        # transform polarization vector to instrument axes
        Ep = kr.quat_trans_v(quats, E)

        # pointing direction in local frame
        vx = np.array([1, 0, 0])

        # calculation of polar coordinates
        rho = np.arccos(vx @ v)/(instrument.fov/2 * np.pi/180)
        phi = np.arctan2(v[2, :], v[1, :])

        # location of impacts
        x, y = nm.pol2cart(rho, phi)

        sensors_g_alpha = np.zeros(nd)

        sensors_tat = np.zeros(nd)
        sensors_mat = np.zeros(nd)
        sensors_max = np.zeros(nd)
        sensors_n = np.zeros(nd)
        sensors_g_alpha = np.zeros(nd)

        # loop over each sensor
        for i in range(nd):
            # filter time steps where trace is over sensor i
            sensors_visibility = nm.circle_check(x, y, instrument.xd[i], instrument.yd[i], instrument.r)

            access_count, each_access_time, _, enter = process_visibility(time, sensors_visibility)

            if access_count > 0:
                sensors_tat[i] = each_access_time.sum()
                sensors_mat[i] = each_access_time.mean()
                sensors_max[i] = each_access_time.max()
                sensors_n[i] = access_count
                sensors_g_alpha[i] = nm.g_alpha(Ep, enter)

        data = np.vstack((pixel_id, sensor_id, sensors_tat, sensors_mat, sensors_max, sensors_n, sensors_g_alpha)).T

    data_df = pd.DataFrame(columns=['pixel_id', 'sensor_id', 'TAT', 'MAT', 'MAX', 'NOA', 'SGA'], data=data)

    return data_df


def numerical_profile(mission, quantity, unit, N, Nth, fig_flag, sensor_id):
    """
    Process temporal analysis results to obtain value along r coordinate

    Parameters
    ----------
    mission : Mission class
        Mission with temporal analysis results
    quantity : str
        Result to be processed
    unit : str
        Time units for the output
    Nr : integer
        Discretization parameter for r coordinate
    Nth : integer
        Discretizatio parameter for theta coordinate

    Returns
    -------
    fig : matplotlib figure
        Figure of profile
    T : ndarray (N)
        Results of calculations (profile)
    """

    data_df = mission.numerical_results_df
    alpha = mission.SSP[0]
    beta = mission.SSP[1]
    delta = mission.SSP[4]

    npix = len(data_df.index.values)
    nside = int(np.sqrt(npix/12))

    r = np.linspace(0, alpha + beta + delta, N) * np.pi/180
    theta = np.linspace(0, 2 * np.pi, Nth)

    hp = HEALPix(nside=nside)

    T = np.zeros(N)

    ftime = 1
    if unit == 's':
        ftime = 1
    elif unit == 'min':
        ftime = 60
    elif unit == 'h':
        ftime = 3600

    factor = 1/ftime

    data = mission.visibility_results(quantity, sensor_id)

    lon = np.zeros((N, Nth))
    lat = np.zeros((N, Nth))

    for i in range(N):

        x = np.cos(r[i])
        y = np.sin(r[i]) * np.sin(theta)
        z = np.sin(r[i]) * np.cos(theta)

        lat[i, :] = np.arcsin(z)
        lon[i, :] = np.arctan2(y, x)

    lon[lon < 0] += 2 * np.pi

    interpolated_data = hp.interpolate_bilinear_lonlat(lon * u.rad, lat * u.rad, data)

    for i in range(N):
        T[i] = factor * interpolated_data[i, :].mean()

        if quantity == 'MAX':
            T[i] = factor * interpolated_data[i, :].max()

    x_plot = r * 180/np.pi
    y_plot = T

    if fig_flag:
        fig = plt.plot(x_plot, y_plot)
    else:
        fig = None

    return fig, T


def numerical_map(mission, quantity, N, units, sensor_id, **kwargs):
    """
    Plot temporal analysis results

    Parameters
    ----------
    quantity : str
        Result to be plotted
    N : int
        Mesh for plotting

    Returns
    -------
    fig :  matplotlib figure
        Plotted figure

    """

    factor = 1.

    if quantity in cte.tags_dict:
        pass
    else:
        raise NameError(f"'{quantity}' result does not exist")

    data = mission.visibility_results(quantity, sensor_id)

    main_label = cte.tags_dict[quantity]
    default_units = cte.units_dict[quantity]

    if default_units is None:
        units_label = ''
    else:
        if units == 's':
            factor = 1.
        elif units == 'min':
            factor = 60.
        elif units == 'h':
            factor = 3600.
        units_label = ' (' + units + ')'
        data = data * 1. / factor

    label = main_label + units_label

    fig = pgraph.plot_map(data, label, N, **kwargs)

    return fig, data
