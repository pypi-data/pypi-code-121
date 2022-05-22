#!/usr/bin/env python
# encoding: utf-8

# The MIT License

# Copyright (c) 2018 Ina (David Doukhan - http://www.ina.fr/)

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
import numpy as np
from numba import *


@njit(cache=True)
def pred_to_logemission(pred: boolean[:]) -> float32[:, :]:
    eps = float32(1e-10)
    ret = np.ones((len(pred), 2), dtype=np.float32) * eps
    ret[pred == 0, 0] = 1 - eps
    ret[pred == 1, 1] = 1 - eps
    return np.log(ret)


@njit(cache=True)
def log_trans_exp(exp: int32, cost0: float32 = 0, cost1: float32 = 0) -> float32[:, :]:
    # transition cost is assumed to be 10**-exp
    cost = float32(-exp * np.log(10))
    ret = np.ones((2, 2), dtype=np.float32) * cost
    ret[0, 0] = cost0
    ret[1, 1] = cost1
    return ret


@njit(cache=True)
def diag_trans_exp(exp: int32, dim: int32) -> float32[:, :]:
    cost = float32(-exp * np.log(10))
    ret = np.ones((dim, dim), dtype=np.float32) * cost
    for i in range(dim):
        ret[i, i] = 0
    return ret
