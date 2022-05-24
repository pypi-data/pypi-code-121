#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2019-07-24 18:29:48
# @Author  : Zhi Liu (zhiliu.mind@gmail.com)
# @Link    : http://iridescent.ink
# @Version : $1.0$

import numpy as np
from pyailib.utils.const import EPS


def contrast(X, caxis=None, axis=None, mode='way1', reduction='mean'):
    r"""Compute contrast of an complex image

    ``'way1'`` is defined as follows, see [1]:

    .. math::
       C = \frac{\sqrt{{\rm E}\left(|I|^2 - {\rm E}(|I|^2)\right)^2}}{{\rm E}(|I|^2)}


    ``'way2'`` is defined as follows, see [2]:

    .. math::
        C = \frac{{\rm E}(|I|^2)}{\left({\rm E}(|I|)\right)^2}

    [1] Efficient Nonparametric ISAR Autofocus Algorithm Based on Contrast Maximization and Newton
    [2] section 13.4.1 in "Ian G. Cumming's SAR book"

    Parameters
    ----------
    X : numpy ndarray
        The image array.
    caxis : int or None
        If :attr:`X` is complex-valued, :attr:`caxis` is ignored. If :attr:`X` is real-valued and :attr:`caxis` is integer
        then :attr:`X` will be treated as complex-valued, in this case, :attr:`caxis` specifies the complex axis;
        otherwise (None), :attr:`X` will be treated as real-valued
    axis : int or None
        The dimension axis (:attr:`caxis` is not included) for computing contrast. The default is :obj:`None`, which means all. 
    mode : str, optional
        ``'way1'`` or ``'way2'``
    reduction : str, optional
        The operation in batch dim, :obj:`None`, ``'mean'`` or ``'sum'`` (the default is ``'mean'``)

    Returns
    -------
    C : scalar or numpy array
        The contrast value of input.

    Examples
    ---------

    ::

        np.random.seed(2020)
        X = np.random.randn(5, 2, 3, 4)

        # real
        C1 = contrast(X, caxis=None, axis=(-2, -1), mode='way1', reduction=None)
        C2 = contrast(X, caxis=None, axis=(-2, -1), mode='way1', reduction='sum')
        C3 = contrast(X, caxis=None, axis=(-2, -1), mode='way1', reduction='mean')
        print(C1, C2, C3)

        # complex in real format
        C1 = contrast(X, caxis=1, axis=(-2, -1), mode='way1', reduction=None)
        C2 = contrast(X, caxis=1, axis=(-2, -1), mode='way1', reduction='sum')
        C3 = contrast(X, caxis=1, axis=(-2, -1), mode='way1', reduction='mean')
        print(C1, C2, C3)

        # complex in complex format
        X = X[:, 0, ...] + 1j * X[:, 1, ...]
        C1 = contrast(X, caxis=None, axis=(-2, -1), mode='way1', reduction=None)
        C2 = contrast(X, caxis=None, axis=(-2, -1), mode='way1', reduction='sum')
        C3 = contrast(X, caxis=None, axis=(-2, -1), mode='way1', reduction='mean')
        print(C1, C2, C3)

        # ---output
        [[1.07323512 1.39704055]
        [0.96033633 1.35878254]
        [1.57174342 1.42973702]
        [1.37236497 1.2351262 ]
        [1.06519696 1.4606771 ]] 12.924240207170865 1.2924240207170865
        [0.86507341 1.03834259 1.00448054 0.89381925 1.20616657] 5.007882367336851 1.0015764734673702
        [0.86507341 1.03834259 1.00448054 0.89381925 1.20616657] 5.007882367336851 1.0015764734673702
    """

    if np.iscomplex(X).any():  # complex in complex
        X = (X * X.conj()).real
    else:
        if caxis is None:  # real
            X = X**2
        else:  # complex in real
            X = np.sum(X**2, axis=caxis)

    if mode in ['way1', 'WAY1']:
        Xmean = X.mean(axis=axis, keepdims=True)
        C = np.sqrt(np.power(X - Xmean, 2).mean(axis=axis, keepdims=True)) / (Xmean + EPS)
        C = C.squeeze(axis)
    if mode in ['way2', 'WAY2']:
        C = X.mean(axis=axis) / (np.power((np.sqrt(X).mean(axis=axis, keepdims=True)), 2) + EPS)
        C = C.squeeze(axis)

    if reduction in ['mean', 'MEAN']:
        C = np.mean(C)
    if reduction in ['sum', 'SUM']:
        C = np.sum(C)
    return C


if __name__ == '__main__':

    np.random.seed(2020)
    X = np.random.randn(5, 2, 3, 4)

    # real
    C1 = contrast(X, caxis=None, axis=(-2, -1), mode='way1', reduction=None)
    C2 = contrast(X, caxis=None, axis=(-2, -1), mode='way1', reduction='sum')
    C3 = contrast(X, caxis=None, axis=(-2, -1), mode='way1', reduction='mean')
    print(C1, C2, C3)

    # complex in real format
    C1 = contrast(X, caxis=1, axis=(-2, -1), mode='way1', reduction=None)
    C2 = contrast(X, caxis=1, axis=(-2, -1), mode='way1', reduction='sum')
    C3 = contrast(X, caxis=1, axis=(-2, -1), mode='way1', reduction='mean')
    print(C1, C2, C3)

    # complex in complex format
    X = X[:, 0, ...] + 1j * X[:, 1, ...]
    C1 = contrast(X, caxis=None, axis=(-2, -1), mode='way1', reduction=None)
    C2 = contrast(X, caxis=None, axis=(-2, -1), mode='way1', reduction='sum')
    C3 = contrast(X, caxis=None, axis=(-2, -1), mode='way1', reduction='mean')
    print(C1, C2, C3)
