#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2019-02-25 09:53:21
# @Author  : Zhi Liu (zhiliu.mind@gmail.com)
# @Link    : http://iridescent.ink
# @Version : $1.0$

from __future__ import division, absolute_import


import numpy as np
from pyailib.evaluation.error import mse
from pyailib.utils.typevalue import peakvalue


def snr():
    pass


def psnr(P, G, caxis=None, axis=None, vpeak=None, reduction=None):
    r"""Peak Signal-to-Noise Ratio

    The Peak Signal-to-Noise Ratio (PSNR) is expressed as

    .. math::
        {\rm PSNR} = 10 \log10(\frac{V_{\rm peak}^2}{\rm MSE})

    For float data, :math:`V_{\rm peak} = 1`;

    For interges, :math:`V_{\rm peak} = 2^{\rm nbits}`,
    e.g. uint8: 255, uint16: 65535 ...


    Parameters
    -----------
    P : array_like
        The data to be compared. For image, it's the reconstructed image.
    G : array_like
        Reference data array. For image, it's the original image.
    vpeak : float, int or None, optional
        The peak value. If None, computes automaticly.
    reduction : str, optional
        The operation in batch dim, :obj:`None`, ``'mean'`` or ``'sum'`` (the default is :obj:`None`)

    Returns
    -------
    PSNR : float
        Peak Signal to Noise Ratio value.

    Examples
    ---------

    ::

        P = np.array([[0, 200, 210], [220, 5, 6]])
        G = np.array([[251, 200, 210], [220, 5, 6]])
        PSNR = psnr(P, G, vpeak=None)
        print(PSNR)

        P = np.array([[251, 200, 210], [220, 5, 6]]).astype('uint8')
        G = np.array([[0, 200, 210], [220, 5, 6]]).astype('uint8')
        PSNR = psnr(P, G, vpeak=None)
        print(PSNR)

        P = np.array([[251, 200, 210], [220, 5, 6]]).astype('float')
        G = np.array([[0, 200, 210], [220, 5, 6]]).astype('float')
        PSNR = psnr(P, G, vpeak=None)
        print(PSNR)

    """

    if P.dtype != G.dtype:
        print("Warning: P(" + str(P.dtype) + ")and G(" + str(G.dtype) +
              ")have different type! PSNR may not right!")

    if vpeak is None:
        vpeak = peakvalue(G)

    MSE = mse(P, G, caxis=caxis, axis=axis, reduction=reduction)
    PSNR = 10 * np.log10((vpeak ** 2) / MSE)

    return PSNR


if __name__ == '__main__':

    P = np.array([[0, 200, 210], [220, 5, 6]])
    G = np.array([[251, 200, 210], [220, 5, 6]])
    PSNR = psnr(P, G, vpeak=None)
    print(PSNR)

    P = np.array([[251, 200, 210], [220, 5, 6]]).astype('uint8')
    G = np.array([[0, 200, 210], [220, 5, 6]]).astype('uint8')
    PSNR = psnr(P, G, vpeak=None)
    print(PSNR)

    P = np.array([[251, 200, 210], [220, 5, 6]]).astype('float')
    G = np.array([[0, 200, 210], [220, 5, 6]]).astype('float')
    PSNR = psnr(P, G, vpeak=None)
    print(PSNR)
