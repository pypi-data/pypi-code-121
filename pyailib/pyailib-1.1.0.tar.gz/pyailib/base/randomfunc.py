#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2015-10-15 10:34:16
# @Author  : Zhi Liu (zhiliu.mind@gmail.com)
# @Link    : http://iridescent.ink
# @Version : $1.1$

import random
import numpy as np
from pyailib.base.arrayops import arraycomb


def setseed(seed=None, target='numpy'):
    r"""set seed

    Set numpy / random seed.

    Parameters
    ----------
    seed : int or None, optional
        seed for random number generator (the default is None)
    target : str, optional
        - ``'numpy'``: ``np.random.seed(seed)`` (the default)
        - ``'random'``: ``random(seed)``

    """

    if target in ['numpy', 'np']:
        np.random.seed(seed)
    if target in ['random']:
        random.seed(seed)


def randperm(start, stop, n):
    r"""randperm function like matlab

    genarates diffrent random interges in range [start, stop)

    Parameters
    ----------
    start : int or list
        start sampling point

    stop : int or list
        stop sampling point

    n : int, list or None
        the number of samples (default None, (stop - start))

    Returns
    -------
    P : list
        the randomly permuted intergers. 

    see :func:`randgrid`, :func:`randperm2d`.

    """

    if (n is not None) and (type(n) is not int):
        raise TypeError('The number of samples should be an integer or None!')
    elif n is None:
        n = int(stop - start)

    Ps = []
    starts = [start] if type(start) is int else start
    stops = [stop] if type(stop) is int else stop
    for start, stop in zip(starts, stops):
        P = np.random.permutation(range(start, stop, 1))[0:n]
        Ps.append(list(P))
    if len(Ps) == 1 and type(Ps[0]) is list:
        Ps = Ps[0]
    return Ps


def randperm2d(H, W, number, population=None, mask=None):
    r"""randperm 2d function

    genarates diffrent random interges in range [start, end)

    Parameters
    ----------
    H : int
        height

    W : int
        width
    number : int
        random numbers
    population : {list or numpy array(1d or 2d)}
        part of population in range(0, H*W)


    Returns
    -------
        Ph : list
            the randomly permuted intergers in height direction. 
        Pw : list
            the randomly permuted intergers in width direction. 

    see :func:`randgrid`, :func:`randperm`.
    
    """

    if population is None:
        population = np.array(range(0, H * W)).reshape(H, W)
    population = np.array(population)
    if mask is not None and np.sum(mask) != 0:
        population = population[mask > 0]

    population = population.flatten()
    population = np.random.permutation(population)

    Ph = np.floor(population / W).astype('int')
    Pw = np.floor(population - Ph * W).astype('int')

    # print(Pw + Ph * W)
    return list(Ph[0:number]), list(Pw[0:number])


def randgrid(start, stop, step, shake=0, n=None):
    r"""generates non-repeated uniform stepped random integers

    Generates :attr:`n` non-repeated random integers from :attr:`start` to :attr:`stop`
    with step size :attr:`step`.

    When step is 1 and shake is 0, it works similar to randperm,

    Parameters
    ----------
    start : int or list
        start sampling point
    stop : int or list
        stop sampling point
    step : int or list
        sampling stepsize
    shake : float
        the shake rate, if :attr:`shake` is 0, no shake, (default),
        if positive, add a positive shake, if negative, add a negative.
    n : int or None
        the number of samples (default None, int((stop0 - start0) / step0) * int((stop1 - start1) / step1)...).

    Returns
    -------
        for multi-dimension, return a list of lists, for 1-dimension, return a list of numbers.

    see :func:`randperm`.

    Example
    -------

    Plot sampled randperm and randgrid point.

    .. image:: ./_static/demo_randgrid.png
       :scale: 100 %
       :align: center

    The results shown in the above figure can be obtained by the following codes.

    ::

        import matplotlib.pyplot as plt

        setseed(2021)
        print(randperm(2, 40, 8), ", randperm(2, 40, 8)")
        print(randgrid(2, 40, 1, -1., 8), ", randgrid(2, 40, 1, 8, -1.)")
        print(randgrid(2, 40, 6, -1, 8), ", randgrid(2, 40, 6, 8)")
        print(randgrid(2, 40, 6, 0.5, 8), ", randgrid(2, 40, 6, 8, 0.5)")
        print(randgrid(2, 40, 6, -1, 12), ", randgrid(2, 40, 6, 12)")
        print(randgrid(2, 40, 6, 0.5, 12), ", randgrid(2, 40, 6, 12, 0.5)")

        mask = np.zeros((5, 6))
        mask[3, 4] = 0
        mask[2, 5] = 0

        Rh, Rw = randperm2d(5, 6, 4, mask=mask)

        print(Rh)
        print(Rw)

        N, H, W = 32, 512, 512

        y1 = pl.randperm(0, H, N)
        x1 = pl.randperm(0, W, N)
        print(len(y1), len(x1))

        y2 = pl.randgrid(0, H, 32, 0., N)
        x2 = pl.randgrid(0, W, 32, 0., N)
        print(len(y2), len(x2))
        print(y2, x2)

        y3, x3 = pl.randperm([0, 0], [H, W], N)
        print(len(y3), len(x3))

        y4, x4 = pl.randgrid([0, 0], [H, W], [32, 32], [0.25, 0.25], N)
        print(len(y4), len(x4))

        plt.figure()
        plt.subplot(221)
        plt.grid()
        plt.plot(x1, y1, '*')
        plt.subplot(222)
        plt.grid()
        plt.plot(x2, y2, '*')
        plt.subplot(223)
        plt.grid()
        plt.plot(x3, y3, '*')
        plt.subplot(224)
        plt.grid()
        plt.plot(x4, y4, '*')
        plt.show()

    """

    starts = [start] if type(start) is int else start
    stops = [stop] if type(stop) is int else stop
    steps = [step] if type(step) is int else step
    shakes = [shake] if type(shake) is int or type(shake) is float else shake
    if (n is not None) and (type(n) is not int):
        raise TypeError('The number of samples should be an integer or None!')
    elif n is None:
        n = float('inf')
    index = []
    for start, stop, step, shake in zip(starts, stops, steps, shakes):
        shakep = shake if abs(shake) >= 1 and type(shake) is int else int(shake * step)
        x = np.array(range(start, stop, step))
        if shakep != 0:
            s = np.random.randint(0, abs(shakep), len(x))
            x = x - s if shakep < 0 else x + s
            x[x >= (stop - step)] = stop - step
            x[x < start] = start
        index.append(x)
    P = arraycomb(index)
    n = min(P.shape[0], n)
    idx = np.random.permutation(range(0, P.shape[0], 1))
    P = P[idx[:n], ...]

    if len(starts) == 1:
        P = P.squeeze(1)
        return P
    else:
        return P.transpose()


if __name__ == '__main__':

    import matplotlib.pyplot as plt

    setseed(2021)
    print(randperm(2, 40, 8), ", randperm(2, 40, 8)")
    print(randgrid(2, 40, 1, -1., 8), ", randgrid(2, 40, 1, 8, -1.)")
    print(randgrid(2, 40, 6, -1, 8), ", randgrid(2, 40, 6, 8)")
    print(randgrid(2, 40, 6, 0.5, 8), ", randgrid(2, 40, 6, 8, 0.5)")
    print(randgrid(2, 40, 6, -1, 12), ", randgrid(2, 40, 6, 12)")
    print(randgrid(2, 40, 6, 0.5, 12), ", randgrid(2, 40, 6, 12, 0.5)")

    mask = np.zeros((5, 6))
    mask[3, 4] = 0
    mask[2, 5] = 0

    Rh, Rw = randperm2d(5, 6, 4, mask=mask)

    print(Rh)
    print(Rw)

    y = randperm(0, 8192, 800)
    x = randperm(0, 8192, 800)

    y, x = randgrid([0, 0], [512, 512], [64, 64], [0.0, 0.], 32)
    print(len(y), len(x))

    plt.figure()
    plt.plot(x, y, 'o')
    plt.show()

    y, x = randgrid([0, 0], [8192, 8192], [256, 256], [0., 0.], 400)
    print(len(y), len(x))

    plt.figure()
    plt.plot(x, y, '*')
    plt.show()

