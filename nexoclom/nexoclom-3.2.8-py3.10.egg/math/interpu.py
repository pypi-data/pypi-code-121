"""``interpu()``: 1D linear interpolation using astropy quantities.

This is a wrapper for numpy.interp for use when using astropy quantities. If
x and xp have different units, xp is converted to the units of x before
interpolation. An exception is raised if the units are not compatible
(i.e., the units of xp cannot be converted to the units of x).

:Author: Matthew Burger
"""
import numpy as np
import astropy.units as u


def interpu(x, xp, fp, **kwargs):
    """Return one dimensional interpolated astropy quantities.
    :param x: The x-coordinates at which to evaluate the interpolated values
    :param xp: The x-coordinates of the data points.
    :param fp: The y-coordinates of the data points
    :param kwargs:
    :return:
    
    **Notes**
    x and xp must have compatible units. See `numpy.interp
    <https://docs.scipy.org/doc/numpy/reference/generated/numpy.interp.html>`_
    for details on interpolation.
    """
    quantity = type(1 * u.km)
    
    if isinstance(x, quantity):
        x_ = x.value
    else:
        raise TypeError('x must be an astropy quantity')
    
    if isinstance(xp, quantity):
        if x.unit == xp.unit:
            xp_ = xp.value
        else:
            xp_ = xp.to(x.unit).value
    else:
        raise TypeError('xp must be an astropy quantity')

    if isinstance(fp, quantity):
        fp_ = fp.value
    else:
        raise TypeError('fp must be an astropy quantity')
    
    result = np.interp(x_, xp_, fp_, **kwargs)
    return result * fp.unit
