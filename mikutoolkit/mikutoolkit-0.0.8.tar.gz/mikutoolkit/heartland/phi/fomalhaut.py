# (A Simple Implementation of (Regressingly) Fitting)
# GNU General Public License v3.0,
#             Copyright (C) 2022 凪坤 (GitHub ID: sandyzikun)
# -*-
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# -*-
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
# -*-
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.
# -*-
import numpy as np
from matplotlib import pyplot as plt
def solve_polyls(arr, order):
    _coef_mat = np.zeros((order + 1, order + 1))
    _bias_vec = np.zeros(( 1 , order + 1 ))
    _xarr = np.ones(arr.shape[1])
    _coef_mat[ 0 , 0 ] += arr.shape[1]
    _bias_vec[ 0 , 0 ] += np.sum(arr[ 1 , : ])
    for k in range(order):
        _xarr *= arr[ 0 , : ]
        _bias_vec[ 0 , (k + 1) ] += np.sum(arr[ 1 , : ] * _xarr)
        _xsum = np.sum(_xarr)
        for l in range(k + 2):
            _coef_mat[ (k + 1 - l) , l ] += _xsum
    for k in range(order):
        _xarr *= arr[ 0 , : ]
        _xsum = np.sum(_xarr)
        for l in range(order - k):
            _coef_mat[ (-l - 1) , (k + l + 1) ] += _xsum
    return _bias_vec @ np.linalg.inv(_coef_mat)
class 積層都市の底で_本当の愛を知らないの(object):
    # 軌道都市の底で_本当の空を知らないの
    def __init__(ミク, arr: np.ndarray, order: int):
        ミク.__arr = arr
        ミク.__length = arr.shape[1]
        ミク.__idxlst = np.arange(arr.shape[1]).astype(int)
        ミク.__order = order
        ミク.__params = solve_polyls(arr, order)
    def __call__(ミク, x: float) -> float:
        res = ミク.__params[ 0 , (-1) ]
        for each in ミク.__params[ 0 , :: (-1) ]:
            res *= x
            res += each
        return res
    def plot(ミク, arr, *args, **kwargs):
        return plt.plot(arr, [ ミク(each) for each in arr ], *args, **kwargs)
class Fomalhaut(object):
    def __init__(ミク):
        return
    def 気高く輝くあの星よ(ミク, xrange: tuple[2], ylist: list[float], method:str="trapezoid") -> float:
        method = method.lower()
        stride = xrange[1] - xrange[0]
        if method == "trapezoid":
            stride /= len(ylist) - 1
            return (sum(ylist) - (ylist[0] + ylist[-1]) * .5) * stride
        elif method == "simpson":
            assert len(ylist) % 2
            stride /= (len(ylist) - 1) // 2
            return (sum(ylist) + sum(ylist[ 1 :: 2 ]) - (ylist[0] + ylist[-1]) * .5) * stride / 3
        else:
            raise Exception
    def 眩しく輝くあの星よ(ミク, samples, order:int=2):
        arr = np.array(samples)
        assert len(arr.shape) == 2 and arr.shape[0] == 2
        return 積層都市の底で_本当の愛を知らないの(arr, order)
# ゼロに変えて
__魔法をかけて__ = Fomalhaut()
composite_integrate = __魔法をかけて__.気高く輝くあの星よ
leastsquare_regress = __魔法をかけて__.眩しく輝くあの星よ