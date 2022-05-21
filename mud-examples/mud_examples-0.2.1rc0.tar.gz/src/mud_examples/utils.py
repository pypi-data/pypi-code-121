#!/usr/bin/env python
# -*- coding: utf-8 -*-

import numpy as np
import os
import types
import importlib


def check_dir(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)


def make_2d_normal_mesh(N=50, window=1):
    """
    Constructs mesh based on normal distribution to
    discretize each axis.
    >>> from mud_examples.utils import make_2d_normal_mesh
    >>> x, y, XX = make_2d_normal_mesh(3)
    >>> print(XX)
    [[-1. -1.]
     [ 0. -1.]
     [ 1. -1.]
     [-1.  0.]
     [ 0.  0.]
     [ 1.  0.]
     [-1.  1.]
     [ 0.  1.]
     [ 1.  1.]]
    """
    X = np.linspace(-window, window, N)
    Y = np.linspace(-window, window, N)
    X, Y = np.meshgrid(X, Y)
    XX = np.vstack([X.ravel(), Y.ravel()]).T
    return (X, Y, XX)


def make_2d_unit_mesh(N=50, window=1):
    """
    Constructs mesh based on uniform distribution to
    discretize each axis.
    >>> from mud_examples.utils import make_2d_unit_mesh
    >>> x, y, XX = make_2d_unit_mesh(3)
    >>> print(XX)
    [[0.  0. ]
     [0.5 0. ]
     [1.  0. ]
     [0.  0.5]
     [0.5 0.5]
     [1.  0.5]
     [0.  1. ]
     [0.5 1. ]
     [1.  1. ]]
    """
    X = np.linspace(0, window, N)
    Y = np.linspace(0, window, N)
    X, Y = np.meshgrid(X, Y)
    XX = np.vstack([X.ravel(), Y.ravel()]).T
    return (X, Y, XX)


class LazyLoader(types.ModuleType):
    def __init__(self, module_name="utensor_cgen", submod_name=None):
        self._module_name = "{}{}".format(
            module_name, submod_name and ".{}".format(submod_name) or ""
        )
        self._mod = None
        super(LazyLoader, self).__init__(self._module_name)

    def _load(self):
        if self._mod is None:
            self._mod = importlib.import_module(self._module_name)
        return self._mod

    def __getattr__(self, attrb):
        try:
            return getattr(self._load(), attrb)
        except ModuleNotFoundError:
            pass

    def __dir__(self):
        return dir(self._load())
