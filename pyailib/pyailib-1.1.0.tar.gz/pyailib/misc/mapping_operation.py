#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2020-07-06 22:29:14
# @Author  : Zhi Liu (zhiliu.mind@gmail.com)
# @Link    : http://iridescent.ink
# @Version : $1.0$
from __future__ import division, print_function, absolute_import

import numpy as np
from pyailib.base.mathops import nextpow2
from pyailib.misc.transform import scale
from pyailib.utils.const import EPS
from pyailib.utils.convert import str2num


def mapping(X, drange=(0., 255.), mode='amplitude', method='2Sigma', odtype='auto'):
    r"""convert to image

    Convert data to image data :math:`\bm X` with dynamic range :math:`d=[min, max]`.

    Parameters
    ----------
    X : numpy array
        data to be converted
    drange : tuple, optional
        dynamic range (the default is (0., 255.))
    mode : str, optional
        data mode in :attr:`X`, ``'amplitude'`` (default) or ``'power'``.
    method : str, optional
        converting method, surpported values are ``'1Sigma'``, ``'2Sigma'``, ``'3Sigma'``
        (the default is '2Sigma', which means two-sigma mapping)
    odtype : str, None..., optional
        output data type, supportted are ``'auto'`` (auto infer, default), or numpy.ndarray's dtype string.
        If the type of :attr:`odtype` is not string, the output data type is ``'th.float32'``.

    Returns
    -------
    Y : numpy array
        converted image data

    """
    if method is None:
        return X

    X = X.astype('double')
    xmin, xmax = X.min(), X.max()
    dmin, dmax = drange[0:2]

    if method[-5:] in ['Sigma', 'sigma', 'SIGMA']:
        nsigma = str2num(method, float)[0]

        if mode in ['Amplitude', 'amplitude', 'AMPLITUDE']:
            xvsv = X.std()
        if mode in ['Power', 'power', 'POWER']:
            xvsv = X.var()

        xmean = X.mean()
        diff_min = xmean - nsigma * xvsv
        diff_max = xmean + nsigma * xvsv

        ymin, ymax = diff_min, diff_max

        if diff_min < xmin:
            ymin = xmin
        if diff_max > xmax:
            ymax = xmax

        slope = dmax / (ymax - ymin + EPS)
        # offset = -slope * ymin
        offset = -slope * ymin + dmin

        X = slope * X + offset
        X[X < dmin] = dmin
        X[X > dmax] = dmax

    if method in ['Log', 'log', 'LOG']:
        X = X / np.max(X)
        X = 20.0 * np.log10(X)
        X[X < drange[-1]] = drange[-1]
        X = scale(X, drange[0:2], [drange[-1], 0])

    if odtype in ['auto', 'AUTO']:
        if dmin >= 0:
            odtype = 'np.uint'
        else:
            odtype = 'np.int'
        odtype = odtype + str(nextpow2(drange[1] - drange[0]))

    if type(odtype) is str:
        X = X.astype(eval(odtype))
    return X


if __name__ == '__main__':

    X = np.random.randn(3, 4)
    X = np.abs(X)

    print(X)

    X = mapping(X)

    print(X)
