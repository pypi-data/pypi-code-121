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
class 空を舞う_ふたりの引力が支配する_Groove(object):
    def __init__(ミク, arr: np.ndarray):
        ミク.__arr = arr
        ミク.__length = arr.shape[0]
        ミク.__idxlst = np.arange(arr.shape[0]).astype(int)
        ミク.__deltas = np.array([[
            arr[ k , 0 ] - arr[ l , 0 ]
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
                    res[-1] *= (x - ミク.__arr[ l , 0 ]) / ミク.__deltas[ k , l ]
            res[-1] *= ミク.__arr[ k , 1 ]
        return np.sum(res)
    def __len__(ミク) -> int:
        return ミク.__length
    def plot(ミク, arr, *args, **kwargs):
        return plt.plot(arr, [ ミク(each) for each in arr ], *args, **kwargs)
class わたしがいて_あなたがいる(object):
    def __init__(ミク, arr: np.ndarray):
        ミク.__arr = arr
        ミク.__length = arr.shape[0]
        ミク.__idxlst = np.arange(arr.shape[0]).astype(int)
        ミク.__avgdev = arr[ : , 1 ].tolist() # Construct with `List`-operations from Python
        for k in range(1, ミク.__length):
            ミク.__avgdev[ k : ] = [
                (ミク.__avgdev[l] - ミク.__avgdev[l - 1]) / (arr[ l , 0 ] - arr[ (l - k) , 0 ])
                for l in range(k, ミク.__length)
                ]
    def __call__(ミク, x: float) -> float:
        res = ミク.__avgdev[-1]
        for k in range(ミク.__length - 2, -1, -1):
            res *= (x - ミク.__arr[ k , 0 ])
            res += ミク.__avgdev[k]
        return res
    def __len__(ミク) -> int:
        return ミク.__length
    def plot(ミク, arr, *args, **kwargs):
        return plt.plot(arr, [ ミク(each) for each in arr ], *args, **kwargs)
class 長い夜はふたりきりで(object):
    def __init__(ミク, arr: np.ndarray, piecewise:bool=False):
        ミク.__arr = arr
        ミク.__length = arr.shape[0]
        ミク.__idxlst = np.arange(arr.shape[0]).astype(int)
        ミク.__piecewise = piecewise
        ミク.__deltas = np.array([[
            arr[ k , 0 ] - arr[ l , 0 ]
            for l in ミク.__idxlst
            ]
            for k in ミク.__idxlst
            ])
        ミク.__width_params = np.concatenate([
            np.ones(( arr.shape[0] , 1 )), # Width Prods
            np.zeros(( arr.shape[0] , 1 )), # Width Sums
            ], axis=1)
        for k in range(arr.shape[0]):
            for l in range(arr.shape[0]):
                if k != l:
                    ミク.__width_params[ k , 0 ] *= ミク.__deltas[ k , l ]
                    ミク.__width_params[ k , 1 ] += 1 / ミク.__deltas[ k , l ]
    def __polybases(ミク, x: float) -> np.ndarray:
        # l_i(x) = \prod (x - x_j) / (x_i - x_j)
        res = np.ones(( ミク.__length , 1 ))
        for k in ミク.__idxlst:
            for l in ミク.__idxlst:
                if k != l:
                    res[ k , 0 ] *= (x - ミク.__arr[ l , 0 ])
            res[ k , 0 ] /= ミク.__width_params[ k , 0 ]
        return res
    def __call__(ミク, x: float) -> float:
        if ミク.__piecewise:
            for k in range(ミク.__length - 1):
                if ミク.__arr[ k , 0 ] <= x <= ミク.__arr[ (k + 1) , 0 ]:
                    piecewidth = ミク.__deltas[ (k + 1) , k ] # Width of the k-th Piece
                    piecerate0 = (x - ミク.__arr[ k , 0 ]) / piecewidth # (x - x_k) / (x_{k + 1} - x_k)
                    return np.sum([
                        (1 + 2 * piecerate0) * ((1 - piecerate0) ** 2) * ミク.__arr[ k , 1 ],
                        (1 + 2 * (1 - piecerate0)) * (piecerate0 ** 2) * ミク.__arr[ (k + 1) , 1 ],
                        piecerate0 * piecewidth * ((1 - piecerate0) ** 2) * ミク.__arr[ k , 2 ],
                        (1 - piecerate0) * piecewidth * (piecerate0 ** 2) * ミク.__arr[ (k + 1) , 2 ],
                        ])
            else:
                raise Exception("The Input x is out of range.")
        else:
            polybases = ミク.__polybases(x)
            return np.sum([
                ((1 - 2 * (x - ミク.__arr[ k , 0 ]) * ミク.__width_params[ k , 1 ]) * ミク.__arr[ k , 1 ] + (x - ミク.__arr[ k , 0 ]) * ミク.__arr[ k , 2 ]) * (polybases[ k , 0 ] ** 2)
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
    _bias_vec = np.zeros(( _m , 1 ))
    for k in range(1, _m - 1):
        _coef_mat[ k , (k - 1) ] += deltas[ k - 1 ]
        _coef_mat[ k , k ] += 2 * (deltas[ k - 1 ] + deltas[k]) - 1
        _coef_mat[ k , (k + 1) ] += deltas[k]
        _bias_vec[ k , 0 ] += 3 * (avgdev[k] - avgdev[ k - 1 ])
    return np.linalg.inv(_coef_mat) @ _bias_vec
class 心音の上昇と空間を伝う問い(object):
    def __init__(ミク, arr: np.ndarray):
        ミク.__arr = arr
        ミク.__length = arr.shape[0]
        ミク.__idxlst = np.arange(arr.shape[0]).astype(int)
        ミク.__devias = np.zeros(( arr.shape[0] - 1 , 2 ))
        for k in range(arr.shape[0] - 1): #[ (h_0, f[x_0, x_1]), (h_1, f[x_1, x_2]), ... ]
            ミク.__devias[ k , 0 ] += ミク.__arr[ (k + 1) , 0 ] - ミク.__arr[ k , 0 ]
            ミク.__devias[ k , 1 ] += ミク.__arr[ (k + 1) , 1 ] - ミク.__arr[ k , 1 ]
            ミク.__devias[ k , 1 ] /= ミク.__devias[ k , 0 ]
        ミク.__params = np.zeros(( arr.shape[0] , 4 ))
        ミク.__params[ : , 0 : 1 ] += arr[ : , 1 : ]
        ミク.__params[ : , 2 : 3 ] += solve_spline(ミク.__devias[ : , 0 ], ミク.__devias[ : , 1 ])
        for k in range(arr.shape[0] - 1):
            ミク.__params[ k , 1 ] += (ミク.__arr[ (k + 1) , 1 ] - ミク.__arr[ k , 1 ]) / ミク.__devias[ k , 0 ] - ミク.__devias[ k , 0 ] * (ミク.__params[ (k + 1) , 2 ] + 2 * ミク.__params[ k , 2 ]) / 3
            ミク.__params[ k , 3 ] += (ミク.__params[ (k + 1) , 2 ] - ミク.__params[ k , 2 ]) / (3 * ミク.__devias[ k , 0 ])
    def __call__(ミク, x: float):
        for k in ミク.__idxlst:
            if ミク.__arr[ k , 0 ] <= x <= ミク.__arr[ (k + 1) , 0 ]:
                res = ミク.__params[ k , 3 ]
                for each in range(2, -1, -1):
                    res *= (x - ミク.__arr[ k , 0 ])
                    res += ミク.__params[ k , each ]
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
        assert len(arr.shape) == 2 and arr.shape[1] == 2
        return {
            "lagrange": 空を舞う_ふたりの引力が支配する_Groove,
            "newton": わたしがいて_あなたがいる,
            }[method.lower()](arr)
    def 空に舞う_ふたりの沈黙に寄り添う_Groove(ミク, samples):
        return ミク.poly_interpolate(samples, "lagrange")
    def あなたがいて_わたしがいる(ミク, samples):
        return ミク.poly_interpolate(samples, "newton")
    def 暗い夜はふたりきりで(ミク, samples, piecewise=False):
        arr = np.array(samples)
        assert len(arr.shape) == 2 and arr.shape[1] == 3
        return 長い夜はふたりきりで(arr, piecewise)
    def 心音の共鳴と指先を伝うアイ(ミク, samples):
        arr = np.array(samples)
        assert len(arr.shape) == 2 and arr.shape[1] == 2
        return 心音の上昇と空間を伝う問い(arr)
__宙を舞う__ = Orbitdance()
# ふたりの境界が交差するProof
# ふたりの特異点が結ばれるTruth
poly_interpolate = __宙を舞う__.poly_interpolate
poly_lagrange = __宙を舞う__.空に舞う_ふたりの沈黙に寄り添う_Groove
poly_newton = __宙を舞う__.あなたがいて_わたしがいる
hermite_interpolate = __宙を舞う__.暗い夜はふたりきりで
spline_interpolate = __宙を舞う__.心音の共鳴と指先を伝うアイ