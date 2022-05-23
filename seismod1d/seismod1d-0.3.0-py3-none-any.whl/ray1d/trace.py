import numpy as np


def iso(depth, vp, theta_in=np.arange(90)):

    # fast isotropic raytracer

    # convert input angles to radians
    theta_in = np.radians(theta_in)

    # get input size
    nlayers = len(vp)
    nrays = len(theta_in)

    # layer thicknesses
    dz = np.diff(depth)
    dz = np.insert(
        dz, 0, 0
    )  # insert dummy 'top thickness' to make arrays same lengths (not used)

    # get ray angle (phase = group) for all rays and layers
    m = vp.reshape((nlayers, 1)) * np.sin(theta_in) / vp[0]
    m[m > 1] = np.nan  # set post-critical angles to nan
    phase_angle = np.arcsin(m)

    # get offset
    doffset = 2 * dz.reshape((nlayers, 1)) * np.tan(phase_angle)
    offset = np.cumsum(doffset, axis=0)

    # get time
    dt = 2 * dz / vp  # zero offset time step
    dtime = dt.reshape((nlayers, 1)) * (np.cos(phase_angle) ** -1)
    time = np.cumsum(dtime, axis=0)

    # define additional output
    phase_angle = np.degrees(phase_angle)
    phase_velocity = np.tile(vp.reshape((len(vp), 1)), (1, nrays)).astype(float)
    phase_velocity[np.isnan(phase_angle)] = np.nan
    group_angle = np.degrees(phase_angle)
    group_velocity = phase_velocity

    return offset, time, phase_angle, group_angle, phase_velocity, group_velocity


def vti(depth, vp, vs, delta, epsilon, theta_in=np.arange(90)):

    # 1D VTI raytracer based on Tang & Li (2008) and Tsvankin(1996)

    # turn off some warnings
    np.seterr(divide="ignore", invalid="ignore")

    # convert input angles to radians
    theta_in = np.radians(theta_in)

    # get input size
    nlayers = len(vp)
    nrays = len(theta_in)

    # set anisotropy arrays to zero if empty
    if len(delta) == 0:
        delta = 0 * vp
    if len(epsilon) == 0:
        epsilon = 0 * vp

    # initiate output
    dtype = "complex"
    offset = np.zeros((nlayers, nrays)).astype("float")  # m
    time = np.zeros((nlayers, nrays)).astype("float")  # s
    phase_angle = np.zeros((nlayers, nrays)).astype(dtype)  # radians
    group_angle = np.zeros((nlayers, nrays)).astype(dtype)  # radians
    phase_velocity = np.zeros((nlayers, nrays)).astype(dtype)  # m/s
    group_velocity = np.zeros((nlayers, nrays)).astype(dtype)  # m/s

    # layer thicknesses
    dz = np.diff(depth)
    dz = np.insert(
        dz, 0, 0
    )  # insert dummy 'top thickness' to make arrays same lengths (not used)

    # get initial slowness
    pp = np.sin(theta_in) / get_phase_velocity(
        theta_in, vp[1], vs[1], delta[1], epsilon[1]
    )

    # loop through layers
    for ii in np.arange(nlayers):

        # get phase angles (from slowness)new_model
        th_ph = get_phase_angle(pp, vp[ii], vs[ii], delta[ii], epsilon[ii])

        # get phase velocity
        vp_ph = get_phase_velocity(th_ph, vp[ii], vs[ii], delta[ii], epsilon[ii])

        # set post-critical angles to NaN
        if 1:
            kk = np.imag(th_ph) != 0
            th_ph[kk] = np.nan
            pp[kk] = np.nan
            vp_ph[kk] = np.nan

        # get group velocity
        vp_gr = get_group_velocity(th_ph, vp_ph, vp[ii], vs[ii], delta[ii], epsilon[ii])

        # get group angle
        th_gr = get_group_angle(th_ph, vp_ph, vp[ii], vs[ii], delta[ii], epsilon[ii])

        # claculate traveltime and offset increments
        dt = 2 * dz[ii] / (vp_gr * np.cos(th_gr))
        dx = 2 * dz[ii] * np.tan(th_gr)

        # update output
        time[ii, :] = time[ii - 1, :] + np.real(dt)
        offset[ii, :] = offset[ii - 1, :] + np.real(dx)
        phase_angle[ii, :] = th_ph * (180 / np.pi)  # rad --> degree
        group_angle[ii, :] = th_gr * (180 / np.pi)  # rad --> degree
        phase_velocity[ii, :] = vp_ph
        group_velocity[ii, :] = vp_gr

    # turn back on warnings
    np.seterr(all="warn")

    return offset, time, phase_angle, group_angle, phase_velocity, group_velocity


def get_phase_angle(p, vp0, vs0, delT, epsT):

    # initiate output
    theta_phase = np.ones(len(p)).astype("complex") * np.nan

    # calculate phase angle
    f = 1 - (vs0 / vp0) ** 2
    c0 = (1 - f) * vp0 ** 4 * p ** 4
    c1 = (2 * (epsT - f * delT) * vp0 ** 2 * p ** 2 - 2 + f) * vp0 ** 2 * p ** 2
    c2 = 1 - 2 * epsT * vp0 ** 2 * p ** 2 - 2 * f * (epsT - delT) * vp0 ** 4 * p ** 4
    temp = (-c1 + np.sqrt(c1 ** 2 - 4 * c0 * c2)) / (2 * c2)
    temp_sq = np.sqrt(temp)

    # update phase angle
    kk = temp_sq <= 1  # identiy critical angles
    theta_phase[kk] = np.arcsin(temp_sq[kk])

    # theta_phase = np.arcsin(temp_sq)

    return theta_phase


def get_phase_velocity(th, vp0, vs0, delT, epsT):

    f = 1 - (vs0 / vp0) ** 2
    temp = (
        1
        + (4 / f)
        * np.sin(th) ** 2
        * (2 * delT * np.cos(th) ** 2 - epsT * np.cos(2 * th))
        + 4 * (epsT / f) ** 2 * np.sin(th) ** 4
    )
    temp = 1 + epsT * np.sin(th) ** 2 - (f / 2) + (f / 2) * np.sqrt(temp)
    vp_phase = vp0 * np.sqrt(temp)

    return vp_phase


def get_phase_vel_sq_deriv(th, vp0, vs0, delT, epsT):

    # derivate of velocity squared in terms of phase angle
    f = 1 - (vs0 / vp0) ** 2
    d1 = 1 + (2 * epsT * np.sin(th) ** 2) / f
    d2 = 2 * (epsT - delT) * np.sin(2 * th) ** 2 / f
    D = np.sqrt(d1 ** 2 - d2)
    E = epsT * (f + 2 * epsT * np.sin(th) ** 2) * np.sin(2 * th) - f * (
        epsT - delT
    ) * np.sin(4 * th)
    Dvp_ph_sq = vp0 ** 2 * (epsT * np.sin(2 * th) + E / (f * D))

    return Dvp_ph_sq


def get_group_velocity(th, vp_ph, vp0, vs0, delT, epsT):

    # get derivative of square of phase velocity
    Dvp_ph_sq = get_phase_vel_sq_deriv(th, vp0, vs0, delT, epsT)

    # group velocity
    vp_gr = np.sqrt(vp_ph ** 2 + (4 * vp_ph ** 2) ** (-1) * (Dvp_ph_sq ** 2))

    return vp_gr


def get_group_angle(th, vp_ph, vp0, vs0, delT, epsT):

    # get derivative of square of phase velocity
    Dvp_ph_sq = get_phase_vel_sq_deriv(th, vp0, vs0, delT, epsT)

    # group velocity
    dth = np.arctan((2 * vp_ph ** 2) ** (-1) * Dvp_ph_sq)
    th_gr = th + dth

    return th_gr
