import numpy as np
from scipy.interpolate import interp1d


def get_time(zz, vp, start_time=0):

    # returns time by integrating velocity with depth
    # assumes constant velocity between depth points, i.e. vp[i] valid between zz[i-1] and zz[i]

    # calculate time
    dz = np.diff(zz)  # depth step (m)
    dt = 2 * dz / vp[1:]  # time step (s)
    tt = np.cumsum(dt)

    # insert zero time at top
    tt = np.insert(tt, 0, 0)

    # add start time
    tt = tt + start_time

    return tt


def get_time_linear(zz, vp):

    # returns time by integrating velocity with depth
    # assumes linear velocity between depth points

    # derive time
    dvp = np.diff(vp)
    dzz = np.diff(zz)
    ln_vp = np.log(vp)
    dln_vp = np.diff(ln_vp)
    aa = dvp / dzz

    # compute time step different if constant velocity across interval (avoid 0/0)
    dtt = 2 * dzz / vp[1:]
    ii = dvp != 0
    dtt[dvp != 0] = 2 * (aa[ii] ** -1) * dln_vp[ii]

    # sum time steps
    tt = np.cumsum(dtt)
    tt = np.insert(tt, 0, 0)

    # return time
    return tt


def get_time_from_td(z_td, t_td, z_in, kind="interp", int_method="linear"):

    # get time from td-realtion sampled at input depth
    if kind == "interp":

        ff = interp1d(
            z_td, t_td, kind=int_method, bounds_error=False, fill_value=np.nan
        )
        return ff(z_in)

    elif kind == "constant_vel":  # assumes constant velocity between input samples

        return 0


def get_depth_from_td(z_td, t_td, t_in, kind="interp", int_method="linear"):

    # get time from td-realtion sampled at input depth
    if kind == "interp":
        ff = interp1d(
            t_td, z_td, kind=int_method, bounds_error=False, fill_value="extrapolate"
        )
        return ff(t_in)


def apply_td_stretch(ref_time, model_depth, model_time, td_depth, td_time, direction=1):

    # zero-offset time
    ref_time0 = ref_time[:, 0]

    # get depth at reflection times from model time-depth

    ff = interp1d(
        model_time,
        model_depth,
        kind="linear",
        bounds_error=False,
        fill_value="extrapolate",
    )
    ref_depth0 = ff(ref_time0)

    # get time at reflection depths based on input td-relationship
    ff = interp1d(
        td_depth, td_time, kind="linear", bounds_error=False, fill_value="extrapolate"
    )
    ref_time_new0 = ff(ref_depth0)

    # get difference from current zero-offset time
    dt = ref_time_new0 - ref_time0

    # create 2D matrix of size ref_time based on dt
    nt = len(dt)
    ntr = ref_time.shape[1]  # number of output traces
    DT = np.tile(dt.reshape(nt, 1), (1, ntr))

    # return new time-table
    return ref_time + direction * DT
