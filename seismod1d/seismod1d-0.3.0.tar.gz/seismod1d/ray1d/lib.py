import numpy as np
from scipy.interpolate import interp1d


def resample_to_uniform_offset(offset_in, value_in, offset_out):

    # size of input
    nrow, ncol = offset_in.shape

    # initiate output
    value_out = np.ones((nrow, len(offset_out))) * 0

    # check input type
    if np.iscomplex(value_in).any():
        value_out = value_out.astype(complex)

    # loop across rows
    for ii in np.arange(nrow):

        # interpolate value
        xx = offset_in[ii, :]
        yy = value_in[ii, :]

        # ignore nan
        kk = ~np.isnan(xx * yy)
        xx = xx[kk]
        yy = yy[kk]

        # ensure strictly input offset
        kk = np.where(np.diff(xx) > 0)[0]
        if len(kk) >= 2:

            # strictly increasing part
            xx = xx[kk]
            yy = yy[kk]

            # interpolate
            ff = interp1d(xx, yy, kind="cubic", bounds_error=False, fill_value=np.nan)
            val = ff(offset_out)
            value_out[ii, :] = val

    return value_out
