#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2018-02-05 16:36:03
# @Author  : Zhi Liu (zhiliu.mind@gmail.com)
# @Link    : http://iridescent.ink
# @Version : $1.0$
from __future__ import division, print_function, absolute_import

import numpy as np
import pyailib as pl


def nextpow2(x):
    r"""get the next higher power of 2.

    Given an number :math:`x`, returns the first p such that :math:`2^p >=|x|`. 

    Args:
        x (int or float): an number.

    Returns:
        int: Next higher power of 2.

    Examples:

        ::

            print(prevpow2(-5), nextpow2(-5))
            print(prevpow2(5), nextpow2(5))
            print(prevpow2(0.3), nextpow2(0.3))
            print(prevpow2(7.3), nextpow2(7.3))
            print(prevpow2(-3.5), nextpow2(-3.5))

            # output
            2 3
            2 3
            -2 -1
            2 3
            1 2

    """

    return int(np.ceil(np.log2(np.abs(x) + 1e-32)))


def prevpow2(x):
    r"""get the previous lower power of 2.

    Given an number :math:`x`, returns the first p such that :math:`2^p <=|x|`. 

    Args:
        x (int or float): an number.

    Returns:
        int: Next higher power of 2.

    Examples:

        ::

            print(prevpow2(-5), nextpow2(-5))
            print(prevpow2(5), nextpow2(5))
            print(prevpow2(0.3), nextpow2(0.3))
            print(prevpow2(7.3), nextpow2(7.3))
            print(prevpow2(-3.5), nextpow2(-3.5))

            # output
            2 3
            2 3
            -2 -1
            2 3
            1 2

    """
    
    return int(np.floor(np.log2(np.abs(x) + 1e-32)))


def ebeo(a, b, op='+'):
    r"""element by element operation

    Element by element operation.

    Parameters
    ----------
    a : list, tuple or ndarray
        The first list/tuple/ndarray.
    b : list, tuple or ndarray
        The second list/tuple/ndarray.
    op : str, optional
        Supported operations are:
        - ``'+'`` or ``'add'`` for addition (default)
        - ``'-'`` or ``'sub'`` for substraction
        - ``'*'`` or ``'mul'`` for multiplication
        - ``'/'`` or ``'div'`` for division
        - ``'**'`` or ``pow`` for power
        - ``'<'``, or ``'lt'`` for less than
        - ``'<='``, or ``'le'`` for less than or equal to
        - ``'>'``, or ``'gt'`` for greater than
        - ``'>='``, or ``'ge'`` for greater than or equal to
        - ``'&'`` for bitwise and
        - ``'|'`` for bitwise or
        - ``'^'`` for bitwise xor
        - function for custom operation.

    Raises
    ------
    TypeError
        If the specified operator not in the above list, raise a TypeError.
    """
    if op in ['+', 'add']:
        return [i + j for i, j in zip(a, b)]
    if op in ['-', 'sub']:
        return [i - j for i, j in zip(a, b)]
    if op in ['*', 'mul']:
        return [i * j for i, j in zip(a, b)]
    if op in ['/', 'div']:
        return [i / j for i, j in zip(a, b)]
    if op in ['**', '^', 'pow']:
        return [i ** j for i, j in zip(a, b)]
    if isinstance(op, str):
        raise TypeError("Not supported operation: " + op + "!")
    else:
        return [op(i, j) for i, j in zip(a, b)]


def r2c(X, caxis=-1, keepdims=False):
    r"""convert real-valued array to complex-valued array

    Convert real-valued array (the size of :attr:`axis` -th dimension is 2) to complex-valued array

    Args:
        X (numpy array): real-valued array.
        caxis (int, optional): the complex axis. Defaults to -1.
        keepdims (bool, optional): keepdims? default is False.

    Returns:
        numpy array: complex-valued array

    Examples:

        ::

            import numpy as np

            np.random.seed(2020)

            Xreal = np.random.randint(0, 30, (3, 2, 4))
            Xcplx = r2c(Xreal, caxis=1)
            Yreal = c2r(Xcplx, caxis=0, keepdims=True)

            print(Xreal, Xreal.shape, 'Xreal')
            print(Xcplx, Xcplx.shape, 'Xcplx')
            print(Yreal, Yreal.shape, 'Yreal')
            print(np.sum(Yreal[0] - Xcplx.real), np.sum(Yreal[1] - Xcplx.imag), 'Error')

            # output
            [[[ 0  8  3 22]
            [ 3 27 29  3]]

            [[ 7 24 29 16]
            [ 0 24 10  9]]

            [[19 11 23 18]
            [ 3  6  5 16]]] (3, 2, 4) Xreal

            [[[ 0. +3.j  8.+27.j  3.+29.j 22. +3.j]]

            [[ 7. +0.j 24.+24.j 29.+10.j 16. +9.j]]

            [[19. +3.j 11. +6.j 23. +5.j 18.+16.j]]] (3, 1, 4) Xcplx

            [[[[ 0.  8.  3. 22.]]

            [[ 7. 24. 29. 16.]]

            [[19. 11. 23. 18.]]]


            [[[ 3. 27. 29.  3.]]

            [[ 0. 24. 10.  9.]]

            [[ 3.  6.  5. 16.]]]] (2, 3, 1, 4) Yreal

            0.0 0.0, Error
    """

    if keepdims:
        idxreal = pl.sl(np.ndim(X), axis=caxis, idx=[[0]])
        idximag = pl.sl(np.ndim(X), axis=caxis, idx=[[1]])
    else:
        idxreal = pl.sl(np.ndim(X), axis=caxis, idx=[0])
        idximag = pl.sl(np.ndim(X), axis=caxis, idx=[1])

    return X[idxreal] + 1j * X[idximag]


def c2r(X, caxis=-1):
    r"""convert complex-valued array to real-valued array

    Args:
        X (numpy array): complex-valued array
        caxis (int, optional): complex axis for real-valued array. Defaults to -1.

    Returns:
        numpy array: real-valued array

    Examples:

        ::

            import numpy as np

            np.random.seed(2020)

            Xreal = np.random.randint(0, 30, (3, 2, 4))
            Xcplx = r2c(Xreal, caxis=1)
            Yreal = c2r(Xcplx, caxis=0, keepdims=True)

            print(Xreal, Xreal.shape, 'Xreal')
            print(Xcplx, Xcplx.shape, 'Xcplx')
            print(Yreal, Yreal.shape, 'Yreal')
            print(np.sum(Yreal[0] - Xcplx.real), np.sum(Yreal[1] - Xcplx.imag), 'Error')

            # output
            [[[ 0  8  3 22]
            [ 3 27 29  3]]

            [[ 7 24 29 16]
            [ 0 24 10  9]]

            [[19 11 23 18]
            [ 3  6  5 16]]] (3, 2, 4) Xreal

            [[[ 0. +3.j  8.+27.j  3.+29.j 22. +3.j]]

            [[ 7. +0.j 24.+24.j 29.+10.j 16. +9.j]]

            [[19. +3.j 11. +6.j 23. +5.j 18.+16.j]]] (3, 1, 4) Xcplx

            [[[[ 0.  8.  3. 22.]]

            [[ 7. 24. 29. 16.]]

            [[19. 11. 23. 18.]]]


            [[[ 3. 27. 29.  3.]]

            [[ 0. 24. 10.  9.]]

            [[ 3.  6.  5. 16.]]]] (2, 3, 1, 4) Yreal

            0.0 0.0, Error
    """

    return np.stack((X.real, X.imag), axis=caxis)


def conj(X, caxis=None):
    r"""conjugates a array

    Both complex and real representation are supported.

    Parameters
    ----------
    X : array
        input
    caxis : int or None
        If :attr:`X` is complex-valued, :attr:`cdim` is ignored. If :attr:`X` is real-valued and :attr:`cdim` is integer
        then :attr:`X` will be treated as complex-valued, in this case, :attr:`cdim` specifies the complex axis;
        otherwise (None), :attr:`X` will be treated as real-valued

    Returns
    -------
    array
         the inputs's conjugate matrix.

    Examples
    ---------

    ::

        np.random.seed(2020)
        X = np.random.rand(2, 3, 3)

        print('---conj')
        print(conj(X, caxis=0))
        print(conj(X[0] + 1j * X[1]))

        # ---output
        ---conj
        [[[ 0.98627683  0.87339195  0.50974552]
        [ 0.27183571  0.33691873  0.21695427]
        [ 0.27647714  0.34331559  0.86215894]]

        [[-0.15669967 -0.14088724 -0.75708028]
        [-0.73632492 -0.35566309 -0.34109302]
        [-0.66680305 -0.21710064 -0.56142698]]]
        [[0.98627683-0.15669967j 0.87339195-0.14088724j 0.50974552-0.75708028j]
        [0.27183571-0.73632492j 0.33691873-0.35566309j 0.21695427-0.34109302j]
        [0.27647714-0.66680305j 0.34331559-0.21710064j 0.86215894-0.56142698j]]

    """

    if np.iscomplex(X).any():  # complex in complex
        return np.conj(X)
    else:
        if caxis is None:  # real
            return X
        else:  # complex in real
            d = np.ndim(X)
            return np.concatenate((X[pl.sl(d, axis=caxis, idx=[[0]])], -X[pl.sl(d, axis=caxis, idx=[[1]])]), axis=caxis)


def real(X, caxis=None, keepdims=False):
    r"""obtain real part of a array

    Both complex and real representation are supported.

    Parameters
    ----------
    X : array
        input
    caxis : int or None
        If :attr:`X` is complex-valued, :attr:`cdim` is ignored. If :attr:`X` is real-valued and :attr:`cdim` is integer
        then :attr:`X` will be treated as complex-valued, in this case, :attr:`cdim` specifies the complex axis;
        otherwise (None), :attr:`X` will be treated as real-valued
    keepdims : bool, optional
        keep dimensions?

    Returns
    -------
    array
         the inputs's real part array.

    Examples
    ---------

    ::

        np.random.seed(2020)
        X = np.random.rand(2, 3, 3)

        print('---real')
        print(real(X, caxis=0))
        print(real(X[0] + 1j * X[1]))

        # ---output
        ---real
        [[0.98627683 0.87339195 0.50974552]
        [0.27183571 0.33691873 0.21695427]
        [0.27647714 0.34331559 0.86215894]]
        [[0.98627683 0.87339195 0.50974552]
        [0.27183571 0.33691873 0.21695427]
        [0.27647714 0.34331559 0.86215894]]
    """

    if np.iscomplex(X).any():  # complex in complex
        return X.real
    else:
        if caxis is None:  # real
            return X
        else:  # complex in real
            d = np.ndim(X)
            idx = [[0]] if keepdims else [0]
            return X[pl.sl(d, axis=caxis, idx=idx)]


def imag(X, caxis=None, keepdims=False):
    r"""obtain imaginary part of a array

    Both complex and real representation are supported.

    Parameters
    ----------
    X : array
        input
    caxis : int or None
        If :attr:`X` is complex-valued, :attr:`cdim` is ignored. If :attr:`X` is real-valued and :attr:`cdim` is integer
        then :attr:`X` will be treated as complex-valued, in this case, :attr:`cdim` specifies the complex axis;
        otherwise (None), :attr:`X` will be treated as real-valued
    keepdims : bool, optional
        keep dimensions?

    Returns
    -------
    array
         the inputs's imaginary part array.

    Examples
    ---------

    ::

        np.random.seed(2020)
        X = np.random.rand(2, 3, 3)

        print('---imag')
        print(imag(X, caxis=0))
        print(imag(X[0] + 1j * X[1]))

        # ---output
        ---imag
        [[0.15669967 0.14088724 0.75708028]
        [0.73632492 0.35566309 0.34109302]
        [0.66680305 0.21710064 0.56142698]]
        [[0.15669967 0.14088724 0.75708028]
        [0.73632492 0.35566309 0.34109302]
        [0.66680305 0.21710064 0.56142698]]

    """

    if np.iscomplex(X).any():  # complex in complex
        return np.imag(X)
    else:
        if caxis is None:  # real
            return np.zeros_like(X)
        else:  # complex in real
            d = np.ndim(X)
            idx = [[1]] if keepdims else [1]
            return X[pl.sl(d, axis=caxis, idx=idx)]


def abs(X, caxis=None, keepdims=False):
    r"""obtain amplitude of a array

    Both complex and real representation are supported.

    .. math::
       {\rm abs}({\bf X}) = |{\bf x}| = \sqrt{u^2 + v^2}, x\in {\bf X}

    where, :math:`u, v` are the real and imaginary part of x, respectively.

    Parameters
    ----------
    X : array
        input
    caxis : int or None
        If :attr:`X` is complex-valued, :attr:`cdim` is ignored. If :attr:`X` is real-valued and :attr:`cdim` is integer
        then :attr:`X` will be treated as complex-valued, in this case, :attr:`cdim` specifies the complex axis;
        otherwise (None), :attr:`X` will be treated as real-valued
    keepdims : bool, optional
        keep dimensions?

    Returns
    -------
    array
         the inputs's amplitude.
   
    Examples
    ---------

    ::

        np.random.seed(2020)
        X = np.random.rand(2, 3, 3)

        print('---abs')
        print(abs(X, caxis=0))
        print(abs(X[0] + 1j * X[1]))

        # ---output
        ---abs
        [[0.99864747 0.88468226 0.91269439]
        [0.78490066 0.48990863 0.40424448]
        [0.72184896 0.40619981 1.02884318]]
        [[0.99864747 0.88468226 0.91269439]
        [0.78490066 0.48990863 0.40424448]
        [0.72184896 0.40619981 1.02884318]]

    """

    if np.iscomplex(X).any():  # complex in complex
        return np.abs(X)
    else:
        if caxis is None:  # real
            return np.abs(X)
        else:  # complex in real
            d = np.ndim(X)
            idxreal = [[0]] if keepdims else [0]
            idximag = [[1]] if keepdims else [1]
            return np.sqrt((X[pl.sl(d, axis=caxis, idx=idxreal)]**2 + X[pl.sl(d, axis=caxis, idx=idximag)]**2))


def pow(X, caxis=None, keepdims=False):
    r"""obtain power of a array

    Both complex and real representation are supported.

    .. math::
       {\rm pow}({\bf X}) = |{\bf x}| = u^2 + v^2, x\in {\bf X}

    where, :math:`u, v` are the real and imaginary part of x, respectively.

    Parameters
    ----------
    X : array
        input
    caxis : int or None
        If :attr:`X` is complex-valued, :attr:`cdim` is ignored. If :attr:`X` is real-valued and :attr:`cdim` is integer
        then :attr:`X` will be treated as complex-valued, in this case, :attr:`cdim` specifies the complex axis;
        otherwise (None), :attr:`X` will be treated as real-valued
    keepdims : bool, optional
        keep dimensions?

    Returns
    -------
    array
         the inputs's power.
   
    Examples
    ---------

    ::

        np.random.seed(2020)
        X = np.random.rand(2, 3, 3)

        print('---pow')
        print(pow(X, caxis=0))
        print(pow(X[0] + 1j * X[1]))

        # ---output
        ---pow
        [[0.99729677 0.78266271 0.83301105]
        [0.61606904 0.24001046 0.1634136 ]
        [0.52106592 0.16499828 1.05851829]]
        [[0.99729677 0.78266271 0.83301105]
        [0.61606904 0.24001046 0.1634136 ]
        [0.52106592 0.16499828 1.05851829]]

    """

    if np.iscomplex(X).any():  # complex in complex
        return (X.conj() * X).real
    else:
        if caxis is None:  # real
            return X**2
        else:  # complex in real
            d = np.ndim(X)
            idxreal = [[0]] if keepdims else [0]
            idximag = [[1]] if keepdims else [1]
            return X[pl.sl(d, axis=caxis, idx=idxreal)]**2 + X[pl.sl(d, axis=caxis, idx=idximag)]**2


if __name__ == '__main__':

    import numpy as np

    np.random.seed(2020)

    Xreal = np.random.randint(0, 30, (3, 2, 4))
    Xcplx = r2c(Xreal, caxis=1, keepdims=True)
    Yreal = c2r(Xcplx, caxis=0)

    print(Xreal, Xreal.shape, 'Xreal')
    print(Xcplx, Xcplx.shape, 'Xcplx')
    print(Yreal, Yreal.shape, 'Yreal')
    print(np.sum(Yreal[0] - Xcplx.real), np.sum(Yreal[1] - Xcplx.imag), 'Error')

    print(prevpow2(-5), nextpow2(-5))
    print(prevpow2(5), nextpow2(5))
    print(prevpow2(0.3), nextpow2(0.3))
    print(prevpow2(7.3), nextpow2(7.3))
    print(prevpow2(-3.5), nextpow2(-3.5))

    np.random.seed(2020)
    X = np.random.rand(2, 3, 3)

    print('---conj')
    print(conj(X, caxis=0))
    print(conj(X[0] + 1j * X[1]))

    print('---real')
    print(real(X, caxis=0))
    print(real(X[0] + 1j * X[1]))

    print('---imag')
    print(imag(X, caxis=0))
    print(imag(X[0] + 1j * X[1]))

    print('---abs')
    print(abs(X, caxis=0))
    print(abs(X[0] + 1j * X[1]))

    print('---pow')
    print(pow(X, caxis=0))
    print(pow(X[0] + 1j * X[1]))
