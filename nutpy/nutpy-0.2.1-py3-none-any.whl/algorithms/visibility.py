import numpy as np
import warnings
import scipy.integrate as integrate
import scipy.optimize as opt
import matplotlib.pyplot as plt
import cmath
from nutpy import numeric as nm

def access_time_analytic_profile(SLP, Nr, tf=1, profile_type="TAT", fig_flag=True, precession='trace', delta_detector=None):
    """
    Calculates analytically the demanded quantity from the temporal analysis fo the instrument
    as a function of the angle regarding the precession axis

    Parameters
    ----------
    SLP : list (5)
        Scan Law Parameters (alpha, beta, spin, precesion, delta)/(deg, deg, min, min, deg)
    Nr : int
        Resolution of results
    tf : float
        Total time considered
    profile_type : str
        Quantity to be computed
    fig_flag : bool
        If True, figure is returned
    precession : str
        Method to be used to account for precession
    delta_detector : float
        Used for detector analysis (deg)

    Returns
    -------
    fig : matplotlib figure
        Figure of profile
    T : ndarray (N)
        Results of calculations (profile)
    """

    alpha = SLP[0] * np.pi/180
    beta = SLP[1] * np.pi/180
    delta = SLP[4] * np.pi/180
    
    T = np.zeros(Nr)

    r = np.linspace(0, alpha + beta + delta, Nr)

    if profile_type is "TAT":
        T = total_access_time_profile(SLP, Nr, tf, delta_detector)
    elif profile_type is "MAT":
        T = mean_access_time_profile(SLP, Nr, precession, delta_detector)
    elif profile_type is "MAX":
        T = max_access_time_profile(SLP, Nr, precession, delta_detector)
    elif profile_type is "NOA":
        T = number_access_profile(SLP, Nr, precession, delta_detector)
    else:
        raise()
  
    if fig_flag:    
        fig = plt.plot(r * 180/np.pi, T)
    else:
        fig = None

    return fig, T

def access_time_analytic_profile_sensor(SSP, instrument, Nr, tf=1, profile_type="TAT", fig_flag=True, precession='trace', sensor_id=0):
    """
    Calculates analytically the demanded quantity from the temporal analysis of a sensor
    as a function of the angle regarding the precession axis

    Parameters
    ----------
    SLP : list (5)
        Scan Law Parameters (alpha, beta, spin, precesion, delta)/(deg, deg, min, min, deg)
    instrument : class instance
        nutpy instrument class instance
    Nr : int
        Resolution of results
    tf : float
        Total time considered
    profile_type : str
        Quantity to be computed
    fig_flag : bool
        If True, figure is returned
    precession : str
        Method to be used to account for precession
    sensor_id : int
        Sensor id number

    Returns
    -------
    fig : matplotlib figure
        Figure of profile
    T : ndarray (N)
        Results of calculations (profile)
    """

    #make a copy to modify it later
    SSP_mod = SSP.copy()
    delta_detector = instrument.delta_detector
    delta = SSP[4]

    #adjust beta to account for the sensor location in focal plane
    xd = instrument.xd[sensor_id] * delta
    yd = instrument.yd[sensor_id] * delta

    db = np.sqrt((SSP[1] + xd)**2 + yd**2)

    SSP_mod[1] = db

    fig, T = access_time_analytic_profile(SSP_mod, Nr, tf, profile_type, fig_flag, precession, delta_detector)

    return fig, T
  

def total_access_time_profile(SLP, Nr, tf, delta_detector):
    """
    Calculates analytically the total access time as a function of the angle regarding the precession axis

    Parameters
    ----------
    SLP : list (5)
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

    alpha = SLP[0] * np.pi/180
    beta = SLP[1] * np.pi/180
    delta_r = SLP[4] * np.pi/180

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

def mean_access_time_profile(SLP, Nr, precession, delta_detector):
    """
    Calculates analytically the mean access time as a function of the angle regarding the precession axis

    Parameters
    ----------
    SLP : list (5)
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

    TT = total_access_time_profile(SLP, Nr, tf, delta_detector)
    NA = number_access_profile(SLP, Nr, precession, delta_detector)
    T = TT/NA 

    return T

def number_access_profile(SLP, Nr, precession, delta_detector):
    """
    Calculates analytically the access time ratio as a function of the angle regarding the precession axis

    Parameters
    ----------
    SLP : list (5)
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

    alpha = SLP[0] * np.pi/180
    beta = SLP[1] * np.pi/180
    omega_spin = 2 * np.pi/(60 * SLP[2])
    omega_prec = 2 * np.pi/(60 * SLP[3])

    delta_r = SLP[4] * np.pi/180

    if delta_detector is None:
        delta = delta_r
    else:
        delta = delta_detector * np.pi/180
    
    NA = np.zeros(Nr)

    r = np.linspace(0, alpha + beta + delta_r, Nr)
    if precession is 'trace':
    
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")

            with np.errstate(divide='ignore', invalid='ignore'):
                for i in range(Nr):

                    if r[i]> (alpha + beta - delta):  
                        Theta_ee = 0

                    elif r[i] < np.abs(np.abs(alpha - beta) - delta):
                        #intersection time is found
                        timeext = opt.minimize_scalar(
                                    lambda t: np.abs(nm.Rext(t, alpha, beta, delta, omega_prec, omega_spin) - (np.abs(np.abs(alpha - beta) - delta))), 
                                    bounds=(0., np.pi/omega_spin), 
                                    method='bounded').x

                        Theta_ee = nm.Thetaext(timeext, alpha, beta, delta, omega_prec, omega_spin)

                    else:
                        timeext = opt.minimize_scalar(
                                    lambda t: np.abs(nm.Rext(t, alpha, beta, delta, omega_prec, omega_spin) - r[i]),
                                    bounds=(0.,np.pi/omega_spin),
                                    method='bounded').x

                        Theta_ee = nm.Thetaext(timeext, alpha, beta, delta, omega_prec, omega_spin)
                    
                    if r[i] > (alpha + beta + delta):
                        Theta_ii = 0

                    elif r[i] < (np.abs(alpha - beta) + delta):
                        timeint = opt.minimize_scalar(
                                    lambda t: np.abs(nm.Rint(t, alpha, beta, delta, omega_prec, omega_spin) - (np.abs(alpha - beta) + delta)),
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

            if r[i]> (alpha + beta - delta): 
                Theta_ee = 0

            else:

                Theta_ee = nm.theta_ext_simple(alpha, beta, delta, r[i])
            
            if r[i] > (alpha + beta + delta):
                Theta_ii = 0

            else:

                Theta_ii = nm.theta_int_simple(alpha, beta, delta, r[i])
    
            Delta_Theta = (Theta_ii - Theta_ee)
            NA[i] = 1/(2 * np.pi/omega_spin) * Delta_Theta/np.pi


    elif precession is 'factor':
        rtmax = r_time_max(delta, beta)
        for i in range(Nr):

            if r[i]> (alpha + beta - delta): 
                Theta_ee = 0

            else:

                Theta_ee = nm.theta_ext_simple(alpha, beta, delta, r[i])/ time_factor(omega_spin, omega_prec, alpha, rtmax, r[i])
            
            if r[i] > (alpha + beta + delta):
                Theta_ii = 0

            else:

                Theta_ii = nm.theta_int_simple(alpha, beta, delta, r[i])/ time_factor(omega_spin, omega_prec, alpha, rtmax, r[i])
    
            Delta_Theta = (Theta_ii - Theta_ee)
            NA[i] = 1/(2 * np.pi/omega_spin) * Delta_Theta/np.pi

    return NA

def max_access_time_profile(SLP, Nr, precession, delta_detector):
    """
    Calculates analytically the maximum access time as a function of precession-axis separation angle

    Parameters
    ----------
    SLP : list (4)
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

    alpha = SLP[0] * np.pi/180
    beta = SLP[1] * np.pi/180
    omega_spin = 2 * np.pi/(60 * SLP[2])
    omega_prec = 2 * np.pi/(60 * SLP[3])
    Tspin = SLP[2] * 60

    delta_r = SLP[4] * np.pi/180

    if delta_detector is None:
        delta = delta_r
    else:
        delta = delta_detector * np.pi/180
    
    T = np.zeros(Nr)

    r = np.linspace(0, alpha + beta + delta_r, Nr)
    
    rtmax = r_time_max(delta, beta)
    tmax = access_time_max(Tspin, delta, beta)

    for i in range(Nr):

        if r[i] > (alpha + rtmax): 
            rstar = r[i] - alpha
            T[i] = access_time(Tspin, delta, beta, rstar) * time_factor(omega_spin, omega_prec, alpha, rtmax, r[i])

        elif r[i] < np.abs(alpha - rtmax):
            rstar = alpha - np.sign(alpha - rtmax) * r[i]
            T[i] = access_time(Tspin, delta, beta, rstar) * time_factor(omega_spin, omega_prec, alpha, rtmax, r[i])

        else:
            T[i] = tmax * time_factor(omega_spin, omega_prec, alpha, rtmax, r[i])

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
    
    rstar =  np.arctan(numerator/denominator)
    
    return rstar

def access_time(Tspin, delta, beta, rstar):
    """
    Calculates the access time for defined SLP and r* coordinate

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


def tau(alpha, rtmax, r):
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

    tau_angle = np.real(cmath.acos(numerator/denominator))
    
    return tau_angle

def gamma(tau, phi, alpha):
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
    gamma_angle : float
        gamma angle (rad)
    """

    gamma_angle = np.cos(tau) * np.cos(phi) + np.cos(alpha) * np.sin(tau) * np.sin(phi)

    return gamma_angle

def phi(rtmax, tau, alpha):
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

    phi_angle = np.arctan2(numerator, denominator)
    
    return phi_angle

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

    t = tau(alpha, rtmax, r)
    p = phi(rtmax, t, alpha)
    g = gamma(t, p, alpha)

    k = np.sign(alpha - rtmax)
    
    
    if r > (alpha + rtmax): 
        factor =  (omega_spin * np.sin(r - alpha))/(omega_spin * np.sin(r - alpha) + omega_prec * np.sin(r))

    elif r < np.abs(alpha - rtmax):
        factor =  (omega_spin * np.sin(alpha - r * k))/(omega_spin * np.sin(alpha - r * k) - omega_prec *  np.sin(r * k))

    else:
        factor =  omega_spin * np.sin(rtmax)/(omega_spin * np.sin(rtmax) + omega_prec * np.sin(r) * g)
        
    return factor