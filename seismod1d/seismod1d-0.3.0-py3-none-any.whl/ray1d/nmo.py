import numpy as np
from scipy.interpolate import interp1d
import matplotlib.pyplot as plt


def get_iso(tv, zv, xv, direction=1, nterm=4, tv_output=[]):

    # get moveout curves for isotropic avo
    # Based on Sun, Wang and Martinez (SEG 2002)
    #
    # ported from Matlab
    #
    # tv : times. 1D array of length n
    # zv: corresponding depth of tv0
    # xv : offsets. 1D array of length m
    # nterm: number of terms to include
    # direction: 1 or -1

    # get some parameters
    c1, c2, c3, c4 = get_par_iso(tv, zv)

    # select number of terms
    if nterm < 4:
        c4 = 0 * c4
    if nterm < 3:
        c3 = 0 * c3

    # change shapes
    xv = xv.reshape((1, len(xv)))
    c1 = c1.reshape((len(c1), 1))
    c2 = c2.reshape((len(c2), 1))
    c3 = c3.reshape((len(c3), 1))
    c4 = c4.reshape((len(c4), 1))

    # calculate output
    tmp = np.tile(c1, len(xv)) + direction * (
        np.matmul(c2, xv ** 2) + np.matmul(c3, xv ** 4) + np.matmul(c4, xv ** 6)
    )
    TX = np.sqrt(np.maximum(0, tmp))

    # calculate moveout curves at specific outptut times
    if len(tv_output) > 0:
        for ix in np.arange(len(xv)):
            TX_new = np.zeros((len(tv_output), len(xv)))
            ff = interp1d(
                tv,
                TX[:, ix],
                kind="linear",
                bounds_error=False,
                fill_value="extrapolate",
            )
            TX_new[:, ix] = ff(tv_output)
        TX = TX_new

    # return movout matrix
    return TX


def get_par_iso(tv, zv):

    # Sun, Wang and Martinez (SEG 2002)
    #
    # This function will calculate a set of coefficients that will be used to
    # get the two-way traveltime after a higher order NMO correction. The
    # coefficients will be used as follows:
    # T = c_1 + c_2*x^2 + c_3*x^4 + c_4*x^6

    # get velocity (m/s)
    dz = np.diff(zv)
    dt = np.diff(tv)
    vv = np.array([2 * (dz / dt)])

    # calculate some parameters
    a1 = 2 * np.cumsum(dz * vv ** -1)
    a2 = 2 * np.cumsum(dz * vv ** 1)
    a3 = 2 * np.cumsum(dz * vv ** 3)
    a4 = 2 * np.cumsum(dz * vv ** 5)

    # calculate output
    c1 = a1 ** 2
    c2 = a1 / a2
    c3 = (a1 ** 2 - a1 * a3) / (4 * a2 ** 4)
    c4 = (2 * a1 * a3 ** 2 - a1 * a2 * a4 - a2 ** 2 * a3) / (8 * a2 ** 7)

    # insert zero at start of each array and ensure 2D output
    c1 = np.insert(c1, 0, 0)
    c2 = np.insert(c2, 0, 0)
    c3 = np.insert(c3, 0, 0)
    c4 = np.insert(c4, 0, 0)

    # return result
    return c1, c2, c3, c4


def get_vti(tv, zv, xv, depth_model, vs_model, delta_model, epsilon_model, direction=1):

    # function [traces TX]=nmo_vti_applyCorr(traces0,xv0,tv0,zv0,t_top0,vs0,delT0,epsT0,opt)
    # % traces0 : input traces. array with n rows and m columns
    # % xv0 : offsets (m). 1D array of length m
    # % tv0 : times (ms). 1D array of length n
    # % zv0 : corresponding depth (m) of tv0 n
    # % opt.dir : 1 - normal NMO, -1 - reverse NMO
    # %
    # % Then a few parameters defining k layers
    # % t_top (ms): length k+1
    # % vs (m/s), delT, epsT, gamT : length k
    # % (vp is derived from tv0 and zv0 - model might have been stretched prior to NMO correction)
    # %
    # % Ursin and Stovas (2006)

    # resample input layers to time vector of traces
    ff = interp1d(zv, tv, kind="linear", bounds_error=False, fill_value="extrapolate")
    time_model = ff(depth_model)
    vs = resample_layer_model(time_model, vs_model, tv)
    delta = resample_layer_model(time_model, delta_model, tv)
    epsilon = resample_layer_model(time_model, epsilon_model, tv)

    # derive vp from time-depth  input
    dt = np.diff(tv, axis=0)
    dz = np.diff(zv, axis=0)
    vp = 2 * dz / dt  # vp=[vp; vp(end)];
    vp = np.insert(vp, 0, vp[0])
    # vp = vp.reshape((1,len(vp)))

    #  get parameters for continued-fraction formula
    vnmo_sq, c1, c2, c3, c4, B = get_par_vti(tv, vp, vs, delta, epsilon)

    # loop through traces and create time table
    TX = np.zeros((len(tv), len(xv)))  # initiate output
    for ix in np.arange(len(xv)):

        # current offset
        xx = xv[ix]

        # get move-out time (squared)
        if 1:  # % Taylor expansion
            temp = 1 + (B * xx ** 2) / (tv ** 2 * vnmo_sq)
            tx_sq = (1 / vnmo_sq) * xx ** 2 + (c2 * xx ** 4) / temp
        else:  # % continued fraction
            tx_sq = c1 * xx ** 2 + c2 * xx ** 4 + c3 * xx ** 6 + c4 * xx ** 8

        tx_sq = tv ** 2 + direction * tx_sq
        tx = np.sqrt(np.maximum(0, tx_sq))

        # assign to output
        TX[:, ix] = tx

    # return output
    return TX


def plot_tx(TX, tv, xv):

    # make figure
    fig = plt.figure("NMO QC2")
    fig.clf()
    nsub = 1
    isub = 1

    plt.subplot(1, nsub, isub)
    isub = isub + 1
    im = plt.imshow(
        TX, aspect="auto"
    )  # ", vmin =, vmax = np.nanmax(self.time[-1,:]), cmap = cmap, aspect='auto', interpolation='none')
    plt.grid()
    # plt.title('time (s)')
    fig.colorbar(im, ax=plt.gca())


def apply(
    traces_in,
    tv,
    zv,
    xv,
    depth_model=[],
    vs_model=[],
    delta_model=[],
    epsilon_model=[],
    nmo_type="isotropic",
    tv_output=[],
    direction=1,
    nterm=4,
):

    # get movout curves
    TX = get(
        tv,
        zv,
        xv,
        depth_model=depth_model,
        vs_model=vs_model,
        delta_model=delta_model,
        epsilon_model=epsilon_model,
        nmo_type=nmo_type,
        tv_output=tv_output,
        direction=direction,
        nterm=nterm,
    )

    # return output traces
    return apply_tx(traces_in, tv, TX)


def resample_tx(TX, tv_out):

    nx = TX.shape[1]
    nt_out = len(tv_out)

    TX_out = np.zeros((nt_out, nx))
    for ix in np.arange(nx):
        ff = interp1d(
            TX[:, 0],
            TX[:, ix],
            kind="linear",
            bounds_error=False,
            fill_value="extrapolate",
        )
        TX_out[:, ix] = ff(tv_out)
    return TX_out


def apply_tx(traces_in, tv, TX):

    # initiate output
    traces_out = 0 * traces_in

    # loop through traces and apply
    for ix in np.arange(traces_in.shape[1]):

        # interpolate
        ff = interp1d(
            tv,
            traces_in[:, ix],
            kind="linear",
            bounds_error=False,
            fill_value="extrapolate",
        )
        traces_out[:, ix] = ff(TX[:, ix])

    # return output
    return traces_out


def get(
    tv,
    zv,
    xv,
    depth_model=[],
    vs_model=[],
    delta_model=[],
    epsilon_model=[],
    nmo_type="isotropic",
    tv_output=[],
    direction=1,
    nterm=4,
):

    # turn off some warnings
    np.seterr(divide="ignore", invalid="ignore", under="ignore")

    # get moveout curves
    if nmo_type == "isotropic":

        TX = get_iso(tv, zv, xv, direction=direction, nterm=nterm)

    elif nmo_type == "vti":

        TX = get_vti(
            tv,
            zv,
            xv,
            depth_model,
            vs_model,
            delta_model,
            epsilon_model,
            direction=direction,
        )

    # calculate moveout curves at specific outptut times
    if len(tv_output) > 0:
        TX_new = np.zeros((len(tv_output), len(xv)))
        for ix in np.arange(len(xv)):
            ff = interp1d(
                tv,
                TX[:, ix],
                kind="linear",
                bounds_error=False,
                fill_value="extrapolate",
            )
            TX_new[:, ix] = ff(tv_output)
        TX = TX_new

    # QC plot
    if 0:
        plot_tx(TX, tv, xv)

    # turn back on warnings
    np.seterr(all="warn")

    # return output
    return TX


def resample_layer_model(time_model, val_model, tv_out):

    ff = interp1d(
        time_model, val_model, kind="next", bounds_error=False, fill_value="extrapolate"
    )
    return ff(tv_out)


def get_par_vti(t0, vp, vs, delT, epsT):

    # define some parameters
    v0 = vp
    gam0 = vp / vs
    sig = gam0 ** 2 * (epsT - delT)

    b1 = gam0 ** 2 - 1
    b2 = 1 + (2 * delT * gam0 ** 2) / b1
    b3 = (4 * sig) / (b1 * gam0 ** 2)

    a0 = 1 + 2 * delT
    a1 = ((2 * sig) / (gam0 ** 2)) * b1
    a2 = -b3 * (delT - sig) * b2
    temp = sig * b2 - 2 * gam0 ** 2 * (delT - sig) ** 2 / b1
    a3 = -(b3 / (gam0 ** 2)) * b2 * temp

    # replace NaN & Inf with zeros (from waterlayer)
    a1[np.isinf(a1)] = 0
    a2[np.isinf(a2)] = 0
    a3[np.isinf(a3)] = 0

    a1[np.isnan(a1)] = 0
    a2[np.isnan(a2)] = 0
    a3[np.isnan(a3)] = 0

    # time step
    dt = t0[1] - t0[0]

    #  mu parameters
    mu0 = np.ones((len(t0), 1))
    mu2 = (dt / t0) * np.cumsum(v0 ** 2 * a0)
    vnmo_sq = mu2
    mu4 = (dt / t0) * np.cumsum(v0 ** 4 * (a0 ** 2 + 4 * a1))
    mu6 = (dt / t0) * np.cumsum(v0 ** 6 * (a0 ** 3 + 4 * a1 * a0 + 8 * a2))
    temp = (
        a0 ** 4
        + (24 / 5) * a1 * a0 ** 2
        + (32 / 5) * a2 * a0
        + (16 / 5) * a1 ** 2
        + (64 / 5) * a3
    )
    mu8 = (dt / t0) * np.cumsum(v0 ** 8 * temp)

    # make S parameters
    S2 = mu4 / mu2 ** 2
    S3 = mu6 / mu4 ** 2
    S4 = mu8 / mu6 ** 2

    # some more parameters
    c2 = (1 - S2) / (4 * t0 ** 2 * vnmo_sq ** 2)
    B = (2 * S2 ** 2 - S2 - S3) / (2 * (S2 - 1))

    c1 = 1 / vnmo_sq
    c3 = (2 * S2 ** 2 - S2 - S3) / (8 * t0 ** 4 * vnmo_sq ** 3)
    temp1 = 24 * (S3 - S2 ** 2) * S2 + 9 * S2 ** 2 - 4 * S3 - 5 * S4
    temp2 = 64 * t0 ** 6 * vnmo_sq ** 4
    c4 = temp1 / temp2

    # return output
    return vnmo_sq, c1, c2, c3, c4, B
