import numpy as np


def conv_vti_thoms2cij(rho, vp, vs, delT=None, epsT=None, gamT=None):

    if delT is None:
        delT = np.zeros(np.shape(rho))
    if epsT is None:
        epsT = np.zeros(np.shape(rho))
    if gamT is None:
        gamT = np.zeros(np.shape(rho))

    c33 = rho * vp ** 2
    c44 = rho * vs ** 2
    c11 = c33 * (2 * epsT + 1)
    c66 = c44 * (2 * gamT + 1)
    c13 = np.sqrt(2 * c33 * (c33 - c44) * delT + (c33 - c44) ** 2) - c44

    return rho, c11, c13, c33, c44, c66


def conv_vti_cij2_thoms(rho, c11, c13, c33, c44, c66):

    vp = np.sqrt(c33 / rho)  # vertical P-wave velocity (m/s)
    vs = np.sqrt(c44 / rho)  # vertical S-wave velocity (m/s)
    delT = ((c13 + c44) ** 2 - (c33 - c44) ** 2) / (2 * c33 * (c33 - c44))
    epsT = (c11 - c33) / (2 * c33)
    gamT = (c66 - c44) / (2 * c44)

    return vp, vs, delT, epsT, gamT
