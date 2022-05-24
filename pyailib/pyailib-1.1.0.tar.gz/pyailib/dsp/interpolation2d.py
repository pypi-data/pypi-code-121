#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2018-02-05 16:36:03
# @Author  : Zhi Liu (zhiliu.mind@gmail.com)
# @Link    : http://iridescent.ink
# @Version : $1.0$

import numpy as np
from scipy import interpolate
from pyailib.utils.const import *


def interp2d(X, ratio=(2, 2), axis=(0, 1), method='cubic'):

    Hin, Win = X.shape[axis[0]], X.shape[axis[1]]
    Hout, Wout = int(Hin * ratio[0]), int(Win * ratio[1])
    yin, xin = np.mgrid[0:Hin:1, 0:Win:1]
    yout, xout = np.linspace(0, Hout, Hout), np.linspace(0, Wout, Wout)

    print(xin.shape, yin.shape)
    interpfunc = interpolate.interp2d(xin, yin, X, kind=method)

    return interpfunc(xout, yout)


if __name__ == '__main__':

    import pyailib as pl
    import matplotlib.pyplot as plt

    X = pl.imread('../../data/fig/Lena.png')
    print(X.shape, X.min(), X.max())

    X = pl.dnsampling(X, ratio=(0.125, 0.125), axis=(0, 1), mod='uniform', method='throwaway')
    print(X.shape, X.min(), X.max())

    # X = pl.upsampling(X, (512, 512), axis=(0, 1), method='Lanczos')
    X = pl.interp2d(X, ratio=(2, 2), axis=(0, 1))
    plt.figure()
    plt.imshow(X)
    plt.show()
