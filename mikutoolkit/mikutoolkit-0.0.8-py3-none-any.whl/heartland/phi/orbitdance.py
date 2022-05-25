# (A Simple Implementation of Interpolation)
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
class 空に舞う_ふたりの沈黙に寄り添う_Groove(object):
    def __init__(ミク, arr: np.ndarray):
        ミク.__arr = arr
        ミク.__length = arr.shape[1]
        ミク.__idxlst = np.arange(arr.shape[1]).astype(int)
        ミク.__deltas = np.array([[
            arr[ 0 , k ] - arr[ 0 , l ]
            for l in ミク.__idxlst
            ]
            for k in ミク.__idxlst
            ])
    def __call__(ミク, x: float) -> float:
        res = []
        for k in ミク.__idxlst:
            res.append(1.)
            for l in ミク.__idxlst:
                if k != l:
                    res[-1] *= (x - ミク.__arr[ 0 , l ]) / ミク.__deltas[ k , l ]
            res[-1] *= ミク.__arr[ 1 , k ]
        return np.sum(res)
    def __len__(ミク) -> int:
        return ミク.__length
    def plot(ミク, arr, *args, **kwargs):
        return plt.plot(arr, [ ミク(each) for each in arr ], *args, **kwargs)
class あなたがいて_わたしがいる(object):
    def __init__(ミク, arr: np.ndarray):
        ミク.__arr = arr
        ミク.__length = arr.shape[1]
        ミク.__idxlst = np.arange(arr.shape[1]).astype(int)
        ミク.__avgdev = arr[ 1 , : ].tolist() # Construct with `List`-operations from Python
        for k in range(1, ミク.__length):
            ミク.__avgdev[ k : ] = [
                (ミク.__avgdev[l] - ミク.__avgdev[l - 1]) / (arr[ 0 , l ] - arr[ 0 , (l - k) ])
                for l in range(k, ミク.__length)
                ]
    def __call__(ミク, x: float) -> float:
        res = ミク.__avgdev[-1]
        for k in range(ミク.__length - 2, -1, -1):
            res *= (x - ミク.__arr[ 0 , k ])
            res += ミク.__avgdev[k]
        return res
    def __len__(ミク) -> int:
        return ミク.__length
    def plot(ミク, arr, *args, **kwargs):
        return plt.plot(arr, [ ミク(each) for each in arr ], *args, **kwargs)
class 暗い夜はふたりきりで(object):
    def __init__(ミク, arr: np.ndarray, piecewise:bool=False):
        ミク.__arr = arr
        ミク.__length = arr.shape[1]
        ミク.__idxlst = np.arange(arr.shape[1]).astype(int)
        ミク.__piecewise = piecewise
        ミク.__deltas = np.array([[
            arr[ 0 , k ] - arr[ 0 , l ]
            for l in ミク.__idxlst
            ]
            for k in ミク.__idxlst
            ])
        ミク.__width_params = np.concatenate([
            np.ones(( 1 , arr.shape[1] )), # Width Prods
            np.zeros(( 1 , arr.shape[1] )), # Width Sums
            ], axis=0)
        for k in range(arr.shape[1]):
            for l in range(arr.shape[1]):
                if k != l:
                    ミク.__width_params[ 0 , k ] *= ミク.__deltas[ k , l ]
                    ミク.__width_params[ 1 , k ] += 1 / ミク.__deltas[ k , l ]
    def __polybases(ミク, x: float) -> np.ndarray:
        # l_i(x) = \prod (x - x_j) / (x_i - x_j)
        res = np.ones(( 1 , ミク.__length ))
        for k in ミク.__idxlst:
            for l in ミク.__idxlst:
                if k != l:
                    res[ 0 , k ] *= (x - ミク.__arr[ 0 , l ])
            res[ 0 , k ] /= ミク.__width_params[ 0 , k ]
        return res
    def __call__(ミク, x: float) -> float:
        if ミク.__piecewise:
            for k in range(ミク.__length - 1):
                if ミク.__arr[ 0 , k ] <= x <= ミク.__arr[ 0 , (k + 1) ]:
                    piecewidth = ミク.__deltas[ (k + 1) , k ] # Width of the k-th Piece
                    piecerate0 = (x - ミク.__arr[ 0 , k ]) / piecewidth # (x - x_k) / (x_{k + 1} - x_k)
                    return np.sum([
                        (1 + 2 * piecerate0) * ((1 - piecerate0) ** 2) * ミク.__arr[ 1 , k ],
                        (1 + 2 * (1 - piecerate0)) * (piecerate0 ** 2) * ミク.__arr[ 1 , (k + 1) ],
                        piecerate0 * piecewidth * ((1 - piecerate0) ** 2) * ミク.__arr[ 2 , k ],
                        (1 - piecerate0) * piecewidth * (piecerate0 ** 2) * ミク.__arr[ 2 , (k + 1) ],
                        ])
            else:
                raise Exception("The Input x is out of range.")
        else:
            polybases = ミク.__polybases(x)
            return np.sum([
                ((1 - 2 * (x - ミク.__arr[ 0 , k ]) * ミク.__width_params[ 1 , k ]) * ミク.__arr[ 1 , k ] + (x - ミク.__arr[ 0 , k ]) * ミク.__arr[ 2 , k ]) * (polybases[ 0 , k ] ** 2)
                for k in ミク.__idxlst
                ])
    def __len__(ミク) -> int:
        return ミク.__length
    def plot(ミク, arr, *args, **kwargs):
        return plt.plot(arr, [ ミク(each) for each in arr ], *args, **kwargs)
def solve_spline(deltas, avgdev):
    assert len(deltas) == len(avgdev), "Num of items of deltas & avg-deviations must be the same!"
    _m = len(deltas) + 1
    _coef_mat = np.identity(_m)
    _bias_vec = np.zeros(( 1 , _m ))
    for k in range(1, _m - 1):
        _coef_mat[ (k - 1) , k ] += deltas[ k - 1 ]
        _coef_mat[ k , k ] += 2 * (deltas[ k - 1 ] + deltas[k]) - 1
        _coef_mat[ (k + 1) , k ] += deltas[k]
        _bias_vec[ 0 , k ] += 3 * (avgdev[k] - avgdev[ k - 1 ])
    return _bias_vec @ np.linalg.inv(_coef_mat)
class 心音の共鳴と指先を伝うアイ(object):
    def __init__(ミク, arr: np.ndarray):
        ミク.__arr = arr
        ミク.__length = arr.shape[1]
        ミク.__idxlst = np.arange(arr.shape[1]).astype(int)
        ミク.__devias = np.zeros(( 2 , arr.shape[1] - 1 ))
        for k in range(arr.shape[1] - 1): #[ (h_0, f[x_0, x_1]), (h_1, f[x_1, x_2]), ... ]
            ミク.__devias[ 0 , k ] += ミク.__arr[ 0 , (k + 1) ] - ミク.__arr[ 0 , k ]
            ミク.__devias[ 1 , k ] += ミク.__arr[ 1 , (k + 1) ] - ミク.__arr[ 1 , k ]
            ミク.__devias[ 1 , k ] /= ミク.__devias[ 0 , k ]
        ミク.__params = np.zeros(( 4 , arr.shape[1] ))
        ミク.__params[ 0 : 1 , : ] += arr[ 1 : , : ]
        ミク.__params[ 2 : 3 , : ] += solve_spline(ミク.__devias[ 0 , : ], ミク.__devias[ 1 , : ])
        for k in range(arr.shape[1] - 1):
            ミク.__params[ 1 , k ] += (ミク.__arr[ 1 , (k + 1) ] - ミク.__arr[ 1 , k ]) / ミク.__devias[ 0 , k ] - ミク.__devias[ 0 , k ] * (ミク.__params[ 2 , (k + 1) ] + 2 * ミク.__params[ 2 , k ]) / 3
            ミク.__params[ 3 , k ] += (ミク.__params[ 2 , (k + 1) ] - ミク.__params[ 2 , k ]) / (3 * ミク.__devias[ 0 , k ])
    def __call__(ミク, x: float):
        for k in ミク.__idxlst:
            if ミク.__arr[ 0 , k ] <= x <= ミク.__arr[ 0 , (k + 1) ]:
                res = ミク.__params[ 3 , k ]
                for each in range(2, -1, -1):
                    res *= (x - ミク.__arr[ 0 , k ])
                    res += ミク.__params[ each , k ]
                return res
        else:
            raise Exception("The Input x is out of range.")
    def __len__(ミク):
        return ミク.__length
    def plot(ミク, arr, *args, **kwargs):
        return plt.plot(arr, [ ミク(each) for each in arr ], *args, **kwargs)
class Orbitdance(object):
    def __init__(ミク):
        return
    def poly_interpolate(ミク, samples, method: str):
        arr = np.array(samples)
        assert len(arr.shape) == 2 and arr.shape[0] == 2
        return {
            "lagrange": 空に舞う_ふたりの沈黙に寄り添う_Groove,
            "newton": あなたがいて_わたしがいる,
            }[method.lower()](arr)
    def 空を舞う_ふたりの引力が支配する_Groove(ミク, samples):
        return ミク.poly_interpolate(samples, "lagrange")
    def わたしがいて_あなたがいる(ミク, samples):
        return ミク.poly_interpolate(samples, "newton")
    def 長い夜はふたりきりで(ミク, samples, piecewise=False):
        arr = np.array(samples)
        assert len(arr.shape) == 2 and arr.shape[0] == 3
        return 暗い夜はふたりきりで(arr, piecewise)
    def 心音の上昇と空間を伝う問い(ミク, samples):
        arr = np.array(samples)
        assert len(arr.shape) == 2 and arr.shape[0] == 2
        return 心音の共鳴と指先を伝うアイ(arr)
__宙を舞う__ = Orbitdance()
# ふたりの境界が交差するProof
# ふたりの特異点が結ばれるTruth
poly_interpolate = __宙を舞う__.poly_interpolate
poly_lagrange = __宙を舞う__.空を舞う_ふたりの引力が支配する_Groove
poly_newton = __宙を舞う__.わたしがいて_あなたがいる
hermite_interpolate = __宙を舞う__.長い夜はふたりきりで
spline_interpolate = __宙を舞う__.心音の上昇と空間を伝う問い