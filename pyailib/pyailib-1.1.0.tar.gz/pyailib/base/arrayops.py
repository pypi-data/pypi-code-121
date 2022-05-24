#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2020-03-23 19:28:33
# @Author  : Zhi Liu (zhiliu.mind@gmail.com)
# @Link    : http://iridescent.ink
# @Version : $1.0$
from __future__ import division, print_function, absolute_import
import numpy as np


def sl(dims, axis, idx=None):
    r"""slice any axis

    generates slice of specified axis.

    Parameters
    ----------
    dims : int
        total dimensions
    axis : int or list
        select axis list.
    idx : list or None, optional
        slice lists of the specified :attr:`axis`, if None, does nothing (the default)

    Returns
    -------
    tuple of slice
        slice for specified axis elements.

    Examples
    --------

    ::

        import numpy as np

        np.random.seed(2020)
        X = np.random.randint(0, 100, (9, 10))
        print(X, 'X)
        print(X[sl(2, -1, [0, 1])], 'Xsl')

        # output:

        [[96  8 67 67 91  3 71 56 29 48]
        [32 24 74  9 51 11 55 62 67 69]
        [48 28 20  8 38 84 65  1 79 69]
        [74 73 62 21 29 90  6 38 22 63]
        [21 68  6 98  3 20 55  1 52  9]
        [83 82 65 42 66 55 33 80 82 72]
        [94 91 14 14 75  5 38 83 99 10]
        [80 64 79 30 84 22 46 26 60 13]
        [24 63 25 89  9 69 47 89 55 75]] X
        [[96  8]
        [32 24]
        [48 28]
        [74 73]
        [21 68]
        [83 82]
        [94 91]
        [80 64]
        [24 63]] Xsl

    """

    idxall = [slice(None)] * dims

    axis = [axis] if type(axis) is int else axis
    idx = [idx] if type(idx) not in [list, tuple] else idx
    if len(axis) != len(idx):
        raise ValueError('The index for each axis should be given!')

    naxis = len(axis)
    for n in range(naxis):
        idxall[axis[n]] = idx[n]

    return tuple(idxall)


def cut(x, pos, axis=None):
    r"""Cut array at given position.

    Cut array at given position.

    Parameters
    ----------
    x : numpy array
        an array to be cutted.
    pos : tulpe or list
        cut positions: ((cpstart, cpend), (cpstart, cpend), ...)
    axis : int, tulpe or list, optional
        cut axis (the default is None, which means nothing)
    """

    if axis is None:
        return x
    if type(axis) == int:
        axis = tuple([axis])
    nDims = np.ndim(x)
    idx = [None] * nDims

    if len(axis) > 1 and len(pos) != len(axis):
        raise ValueError('You should specify cut axis for each cut axis!')
    elif len(axis) == 1:
        axis = tuple(list(axis) * len(pos))

    uqaixs = np.unique(axis)
    for a in uqaixs:
        idx[a] = []

    for i in range(len(axis)):
        idx[axis[i]] += range(pos[i][0], pos[i][1])

    for a in uqaixs:
        idxall = [slice(None)] * nDims
        idxall[a] = idx[a]
        x = x[tuple(idxall)]
    return x


def cat(arrays, axis=None, out=None):

    arrays = list(arrays)
    for n in range(len(arrays)):
        try:
            arrays.remove([])
            arrays.remove(None)
        except:
            pass
    return np.concatenate(arrays, axis=axis, out=out)


def arraycomb(arrays, out=None):
    r"""compute the elemnts combination of several lists.

    Args:
        arrays (list or numpy array): The lists or arrays.
        out (numpy array, optional): The combination results (defaults is :obj:`None`).

    Returns:
        numpy array: The combination results.

    Examples:

    Compute the combination of three lists: :math:`[1,2,3]`, :math:`[4, 5]`, :math:`[6,7]`,
    this will produce a :math:`12\times 3` array.

    ::

        x = arraycomb(([1, 2, 3], [4, 5], [6, 7]))
        print(x, x.shape)

        # output:
        [[1 4 6]
        [1 4 7]
        [1 5 6]
        [1 5 7]
        [2 4 6]
        [2 4 7]
        [2 5 6]
        [2 5 7]
        [3 4 6]
        [3 4 7]
        [3 5 6]
        [3 5 7]] (12, 3)

    """
    arrays = [np.asarray(x) for x in arrays]
    dtype = arrays[0].dtype
    n = np.prod([x.size for x in arrays])
    if out is None:
        out = np.zeros([n, len(arrays)], dtype=dtype)
    m = int(n / arrays[0].size)
    out[:, 0] = np.repeat(arrays[0], m)

    if arrays[1:]:
        arraycomb(arrays[1:], out=out[0:m, 1:])

    for j in range(1, arrays[0].size):
        out[j * m:(j + 1) * m, 1:] = out[0:m, 1:]

    return out


if __name__ == '__main__':

    np.random.seed(2020)
    X = np.random.randint(0, 100, (9, 10))
    print('X')
    print(X)
    Y = cut(X, ((1, 4), (5, 8)), axis=0)
    print('Y = cut(X, ((1, 4), (5, 8)), axis=0)')
    print(Y)
    Y = cut(X, ((1, 4), (7, 9)), axis=(0, 1))
    print('Y = cut(X, ((1, 4), (7, 9)), axis=(0, 1))')
    print(Y)
    Y = cut(X, ((1, 4), (1, 4), (5, 8), (7, 9)), axis=(0, 1, 0, 1))
    print('cut(X, ((1, 4), (1, 4), (5, 8), (7, 9)), axis=(0, 1, 0, 1))')
    print(Y)

    print('--------------------sl')
    print(X, 'X')
    print(X[sl(2, -1, [[0, 1]])], 'Xsl')
    print(X[:, 0:2])
    print('--------------------cat')
    print(cat(([], [], np.array([[1, 2], [3, 4]])), axis=0))

    print('--------------------arraycomb')
    x = arraycomb(([1, 2, 3], [4, 5], [6, 7]))
    print(x, x.shape)

    x = arraycomb(([1, 2, 3, 4], [4, 5], [6, 7]))
    print(x, x.shape)

    x = arraycomb(([1, 2, 3, 4]))
    print(x, x.shape)

    x = arraycomb([[0, 64, 128, 192, 256, 320, 384, 448], [0,  64, 128, 192, 256, 320, 384, 448]])
    print(x, x.shape)

