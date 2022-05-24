import numpy as np


def lda_slater_x(n, alpha=2 / 3):
    '''
        Slater exchange functional (spin-paired).
        Latex: Eq. 2.11
    '''
    third = 1 / 3
    pi34 = (3 / (4 * np.pi))**third
    f = -9 / 8 * (3 / (2 * np.pi))**(2 / 3)
    rs = pi34 / n**third

    ex = f * alpha / rs
    vx = 4 / 3 * ex
    return ex, vx


def lda_vwn_c(n):
    '''
        Vosko-Wilk-Nusair parametrization of the correlation functional (spin-paired).
        Latex: Eq. 2.12 ff.
    '''
    third = 1 / 3
    pi34 = (3 / (4 * np.pi))**third
    rs = pi34 / n**third

    a = 0.0310907
    b = 3.72744
    c = 12.9352
    x0 = -0.10498

    q = np.sqrt(4 * c - b * b)
    f1 = 2 * b / q
    f2 = b * x0 / (x0 * x0 + b * x0 + c)
    f3 = 2 * (2 * x0 + b) / q
    rs12 = np.sqrt(rs)
    fx = rs + b * rs12 + c
    qx = np.arctan(q / (2 * rs12 + b))

    ec = a * (np.log(rs / fx) + f1 * qx - f2 * (np.log((rs12 - x0)**2 / fx) + f3 * qx))

    tx = 2 * rs12 + b
    tt = tx * tx + q * q
    vc = ec - rs12 * a / 6 * (2 / rs12 - tx / fx - 4 * b / tt - f2 *
                              (2 / (rs12 - x0) - tx / fx - 4 * (2 * x0 + b) / tt))
    return ec, vc
