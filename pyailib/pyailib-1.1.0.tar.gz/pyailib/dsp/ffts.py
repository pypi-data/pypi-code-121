#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2017-07-06 10:38:13
# @Author  : Zhi Liu (zhiliu.mind@gmail.com)
# @Link    : http://iridescent.ink
# @Version : $1.0$
from __future__ import division, print_function, absolute_import
import numpy as np
import numpy.fft as npfft


def freq(fs, n, norm=False, shift=False):
    r"""Return the sample frequencies

    Return the sample frequencies.

    Given a window length `n` and a sample rate `fs`, if shift is ``True``::

      f = [-n/2, ..., n/2] / (d*n)

    Given a window length `n` and a sample rate `fs`, if shift is ``False``::

      f = [0, 1, ..., n] / (d*n)

    If :attr:`norm` is ``True``, :math:`d = 1`, else :math:`d = 1/f_s`.

    Parameters
    ----------
    fs : float
        Sampling rate.
    n : int
        Number of samples.
    norm : bool
        Normalize the frequencies.
    shift : bool
        Does shift the zero frequency to center.

    Returns
    -------
    numpy array
        frequency array with size :math:`n×1`.
    """
    d = 1. / fs

    if shift:
        f = np.linspace(-n / 2., n / 2., n, endpoint=True)
    else:
        f = np.linspace(0, n, n, endpoint=True)
    if norm:
        return f / n
    else:
        return f / (d * n)


def fftfreq(fs, n, norm=False, shift=False):
    r"""Return the Discrete Fourier Transform sample frequencies

    Return the Discrete Fourier Transform sample frequencies.

    Given a window length `n` and a sample rate `fs`, if shift is ``True``::

      f = [-n/2, ..., -1,     0, 1, ...,   n/2-1] / (d*n)   if n is even
      f = [-(n-1)/2, ..., -1, 0, 1, ..., (n-1)/2] / (d*n)   if n is odd

    Given a window length `n` and a sample rate `fs`, if shift is ``False``::

      f = [0, 1, ...,   n/2-1,     -n/2, ..., -1] / (d*n)   if n is even
      f = [0, 1, ..., (n-1)/2, -(n-1)/2, ..., -1] / (d*n)   if n is odd

    where :math:`d = 1/f_s`, if :attr:`norm` is ``True``, :math:`d = 1`, else :math:`d = 1/f_s`.

    Parameters
    ----------
    fs : float
        Sampling rate.
    n : int
        Number of samples.
    norm : bool
        Normalize the frequencies.
    shift : bool
        Does shift the zero frequency to center.

    Returns
    -------
    numpy array
        frequency array with size :math:`n×1`.
    """
    d = 1. / fs
    if n % 2 == 0:
        N = n
        N1 = int(n / 2.)
        N2 = int(n / 2.)
        endpoint = False
    else:
        N = n - 1
        N1 = int((n + 1) / 2.)
        N2 = int((n - 1) / 2.)
        endpoint = True

    if shift:
        f = np.linspace(-N / 2., N / 2., n, endpoint=endpoint)
    else:
        f = np.hstack((np.linspace(0, N / 2., N1, endpoint=endpoint),
                       np.linspace(-N / 2., 0, N2, endpoint=False)))
    if norm:
        return f / n
    else:
        return f / (d * n)


def fftshift(x, axis=None):
    r"""Shift the zero-frequency component to the center of the spectrum.

    This function swaps half-spaces for all axes listed (defaults to all).
    Note that ``y[0]`` is the Nyquist component only if ``len(x)`` is even.

    Parameters
    ----------
    x : numpy array
        The input array.
    axis : int, optional
        Axes over which to shift. (Default is None, which shifts all axes.)

    Returns
    -------
    y : numpy array
        The shifted array.

    See Also
    --------
    ifftshift : The inverse of :func:`fftshift`.

    Examples
    --------

    ::

        import numpy as np
        import pyailib.as ps

        x = [1, 2, 3, 4, 5, 6]
        y = np.fft.fftshift(x)
        print(y)
        y = ps.fftshift(x)
        print(y)

        x = [1, 2, 3, 4, 5, 6, 7]
        y = np.fft.fftshift(x)
        print(y)
        y = ps.fftshift(x)
        print(y)

        axis = (0, 1)  # axis = 0, axis = 1
        x = [[1, 2, 3, 4, 5, 6], [0, 2, 3, 4, 5, 6]]
        y = np.fft.fftshift(x, axis)
        print(y)
        y = ps.fftshift(x, axis)
        print(y)


        x = [[1, 2, 3, 4, 5, 6, 7], [0, 2, 3, 4, 5, 6, 7]]
        y = np.fft.fftshift(x, axis)
        print(y)
        y = ps.fftshift(x, axis)
        print(y)

    """

    if axis is None:
        axis = tuple(range(np.ndim(x)))
    elif type(axis) is int:
        axis = tuple([axis])
    for a in axis:
        n = np.size(x, a)
        p = int(n / 2.)
        x = np.roll(x, p, axis=a)
    return x


def ifftshift(x, axis=None):
    r"""Shift the zero-frequency component back.

    The inverse of :func:`fftshift`. Although identical for even-length `x`, the
    functions differ by one sample for odd-length `x`.

    Parameters
    ----------
    x : numpy array
        The input array.
    axis : int, optional
        Axes over which to shift. (Default is None, which shifts all axes.)

    Returns
    -------
    y : numpy array
        The shifted array.

    See Also
    --------
    fftshift : The inverse of `ifftshift`.

    Examples
    --------

    ::

        x = [1, 2, 3, 4, 5, 6]
        y = np.fft.ifftshift(x)
        print(y)
        y = pl.ifftshift(x)
        print(y)

        x = [1, 2, 3, 4, 5, 6, 7]
        y = np.fft.ifftshift(x)
        print(y)
        y = pl.ifftshift(x)
        print(y)

        axis = (0, 1)  # axis = 0, axis = 1
        x = [[1, 2, 3, 4, 5, 6], [0, 2, 3, 4, 5, 6]]
        y = np.fft.ifftshift(x, axis)
        print(y)
        y = pl.ifftshift(x, axis)
        print(y)


        x = [[1, 2, 3, 4, 5, 6, 7], [0, 2, 3, 4, 5, 6, 7]]
        y = np.fft.ifftshift(x, axis)
        print(y)
        y = pl.ifftshift(x, axis)
        print(y)

    """

    if axis is None:
        axis = tuple(range(np.ndim(x)))
    elif type(axis) is int:
        axis = tuple([axis])
    for a in axis:
        n = np.size(x, a)
        p = int((n + 1) / 2.)
        x = np.roll(x, p, axis=a)
    return x


def padfft(X, nfft=None, axis=0, shift=False):
    r"""PADFT Pad array for doing FFT or IFFT

    PADFT Pad array for doing FFT or IFFT

    Parameters
    ----------
    X : ndarray
        Data to be padded.
    nfft : int or None
        the number of fft point.
    axis : int, optional
        Padding dimension. (the default is 0)
    shift : bool, optional
        Whether to shift the frequency (the default is False)
    """

    if axis is None:
        axis = 0

    Nx = np.size(X, axis)

    if nfft < Nx:
        raise ValueError('Output size is smaller than input size!')

    Nd = np.ndim(X)
    Np = int(np.uint(nfft - Nx))
    PS = np.zeros((Nd, 2), dtype='int32')
    PV = [0]
    if shift:
        PS[axis, 0] = int(np.fix((Np + 1) / 2.))
        X = np.pad(X, PS, 'constant', constant_values=PV)
        PS[axis, :] = [0, Np - PS[axis, 0]]
        X = np.pad(X, PS, 'constant', constant_values=PV)
    else:
        PS[axis, 1] = Np
        X = np.pad(X, PS, 'constant', constant_values=PV)

    return X


def fft(a, n=None, axis=-1, norm=None, shift=False):
    N = np.size(a, axis)
    if (n is not None) and (n > N):
        a = padfft(a, n, axis, shift)
    if shift:
        return npfft.fftshift(npfft.fft(npfft.fftshift(a, axes=axis), n=n, axis=axis, norm=norm), axes=axis)
    else:
        return npfft.fft(a, n=n, axis=axis, norm=norm)


def ifft(a, n=None, axis=-1, norm=None, shift=False):
    if shift:
        return npfft.ifftshift(npfft.ifft(npfft.ifftshift(a, axes=axis), n=n, axis=axis, norm=norm), axes=axis)
    else:
        return npfft.ifft(a, n=n, axis=axis, norm=norm)


def fft2(img):
    r"""
    Improved 2D fft
    """
    out = np.zeros(img.shape, dtype=complex)
    for i in range(out.shape[1]):
        # get range fixed column
        out[:, i] = fft(img[:, i])
    for j in range(out.shape[0]):
        out[j, :] = fft(out[j, :])
    return out


def fftx(x, n=None):

    return npfft.fftshift(npfft.fft(npfft.fftshift(x, n)))


def ffty(x, n=None):
    return (npfft.fftshift(npfft.fft(npfft.fftshift(x.transpose(), n)))).transpose()


def ifftx(x, n=None):
    return npfft.fftshift(npfft.ifft(npfft.fftshift(x), n))


def iffty(x, n=None):
    return (npfft.fftshift(npfft.ifft(x.transpose(), n))).transpose()


if __name__ == "__main__":

    import matplotlib.pyplot as plt

    fs = 1000.
    n = 16

    print(np.fft.fftfreq(n, 1. / fs))

    f = fftfreq(fs, n, shift=False, norm=False)
    print(f)
    f = fftfreq(fs, n, shift=False, norm=True)
    print(f)
    f = fftfreq(fs, n, shift=True, norm=True)
    print(f)

    print(np.linspace(-fs / 2., fs / 2., n))

    Ts = 2.
    f0 = 100.
    Fs = 1000.
    Ns = int(Fs * Ts)
    t = np.linspace(0., Ts, Ns)
    # f = np.linspace(-Fs / 2., Fs / 2., Ns)
    f = fftfreq(Fs, Ns, shift=True)
    print(f)

    x = np.sin(2. * np.pi * f0 * t)
    y = fft(x, shift=True)
    y = np.abs(y)

    plt.figure()
    plt.subplot(121)
    plt.grid()
    plt.plot(t, x)
    plt.subplot(122)
    plt.grid()
    plt.plot(f, y)
    plt.show()

    X = np.array([[1, 2, 3], [4, 5, 6]])
    print(X)
    X = padfft(X, nfft=8, axis=0, shift=False)
    print(X)
    X = padfft(X, nfft=8, axis=1, shift=False)
    print(X)
