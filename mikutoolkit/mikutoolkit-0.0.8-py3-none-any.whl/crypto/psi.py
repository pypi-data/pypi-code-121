# (A Simple Function to encode Words to meaningless String)
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
class __Constants(object): # All Keys Here
    KEY_MAT_3 = np.array([ 1,  2,   8, 0,  3,   9, 0, 0, 1 ]).reshape( 3 , 3 ).astype(int)
    KEY_INV_3 = np.array([ 1, 42, 126, 0, 43, 125, 0, 0, 1 ]).reshape( 3 , 3 ).astype(int)
    KEY_MAT_2 = np.array([  7, 0,  1, 1 ]).reshape( 2 , 2 ).astype(int)
    KEY_INV_2 = np.array([ 55, 0, 73, 1 ]).reshape( 2 , 2 ).astype(int)
    RANDOM_STATE = 39
    BIASES = [ 39 , 39 , 39 ]
class __Cryptostr(object):
    def __init__(ミク, x):
        ミク.__list_all = [ "".join([
                x[_] for _ in eachlist
                ]) for eachlist in [ # All Permutations
            [ 0, 1, 2, 3 ], [ 0, 1, 3, 2 ], [ 0, 2, 1, 3 ],
            [ 0, 2, 3, 1 ], [ 0, 3, 1, 2 ], [ 0, 3, 2, 1 ],
            [ 1, 0, 2, 3 ], [ 1, 0, 3, 2 ], [ 1, 2, 0, 3 ],
            [ 1, 2, 3, 0 ], [ 1, 3, 0, 2 ], [ 1, 3, 2, 0 ],
            [ 2, 0, 1, 3 ], [ 2, 0, 3, 1 ], [ 2, 1, 0, 3 ],
            [ 2, 1, 3, 0 ], [ 2, 3, 0, 1 ], [ 2, 3, 1, 0 ],
            [ 3, 0, 1, 2 ], [ 3, 0, 2, 1 ], [ 3, 1, 0, 2 ],
            [ 3, 1, 2, 0 ], [ 3, 2, 0, 1 ], [ 3, 2, 1, 0 ],
            ]]
        ミク.__mapping_cry_num = dict(map(
            lambda x: x[ :: (-1) ],
            enumerate(ミク.__list_all)
            ))
    def __getitem__(ミク, k):
        return ミク.__list_all[k]
    def mapping_cry_num(ミク, x):
        return ミク.__mapping_cry_num[x]
__rs = np.random.RandomState(__Constants.RANDOM_STATE)
__cry = __Cryptostr("miku")
def __num2bin(x, flag=True):
    assert 0 <= x < 256 and isinstance(flag, bool)
    res = bin(x)[ 2 : ]
    return "0" * (7 + int(flag) - len(res)) + res
def __str2num(x):
    res = []
    for _ch in x:
        res += list(_ch.encode("UTF-8"))
    res = "".join( __num2bin(_) for _ in res )
    num_remain = len(res) % 7
    if num_remain:
        res += "".join(__rs.choice([ "0" , "1" ], 7 - num_remain))
    res = np.array([ int(res[ k : (k + 7) ], 2) for k in range(0, len(res), 7) ])
    return res.reshape( 1 , len(res) )
def __num2str(x):
    fstr = "".join( __num2bin(x[ 0 , k ], False) for k in range(x.shape[1]) )
    fres = ""
    k = 0
    while k + 8 <= len(fstr):
        current_num = [ int(fstr[ k : (k + 8) ], 2) ]
        current_stride = 1
        if current_num[0] >= 192:   # 0b110*****
            current_num.append(int(fstr[ (k + 8) : (k + 16) ], 2))
            current_stride += 1
        if current_num[0] >= 224:   # 0b1110****
            current_num.append(int(fstr[ (k + 16) : (k + 24) ], 2))
            current_stride += 1
        if current_num[0] >= 240:   # 0b11110***
            current_num.append(int(fstr[ (k + 24) : (k + 32) ], 2))
            current_stride += 1
        k += 8 * current_stride
        fres += bytes(current_num).decode("UTF-8")
    return fres
def __en2code(x: tuple):
    v, u = x
    fres = [ "" , "" , "" ]
    fres[0] += __cry[v % 24]
    fres[2] += __cry[u % 24]
    v //= 24
    u //= 24
    fres[1] += __cry[ (3 * (v % 3) + (u % 3) + __Constants.BIASES[2]) % 24 ]
    v //= 3
    u //= 3
    return fres[0] + fres[1][ : 2 ] + "39"[u] + fres[1][ 2 : ] + fres[2] + "39"[v]
def __de2code(x):
    t = (__cry.mapping_cry_num(x[ 4 : 6 ] + x[ 7 : 9 ]) - __Constants.BIASES[2]) % 24
    v, u = t // 3, t % 3
    v += { "3": 0, "9": 3 }[x[-1]]
    u += { "3": 0, "9": 3 }[x[ 6]]
    v *= 24
    u *= 24
    v += __cry.mapping_cry_num(x[ : 4 ])
    u += __cry.mapping_cry_num(x[ (-5) : (-1) ])
    return v, u
def __numenco(x):
    res = x.copy()
    num_remain_3 = res.shape[1] % 3
    if num_remain_3:
        res = np.concatenate([ res , __rs.randint(128, size=( 1 , 3 - num_remain_3 )) ], axis=1)
    res += __Constants.BIASES[0]
    res %= 128
    for k in range(0, res.shape[1], 3):
        res[ : , k : (k + 3) ] = res[ : , k : (k + 3) ] @ __Constants.KEY_MAT_3 % 128
    num_remain_2 = res.shape[1] % 2
    if num_remain_2:
        res = np.concatenate([ res , __rs.randint(128, size=( 1 , 1 )) ], axis=1)
    res += __Constants.BIASES[1]
    res %= 128
    for k in range(0, res.shape[1], 2):
        res[ : , k : (k + 2) ] = res[ : , k : (k + 2) ] @ __Constants.KEY_MAT_2 % 128
    return res, num_remain_3
def __numdeco(x):
    assert len(x.shape) == 2 and x.shape[1] % 2 != 1 and x.shape[0] == 1
    res = x.copy()
    for k in range(0, res.shape[1], 2):
        res[ : , k : (k + 2) ] = res[ : , k : (k + 2) ] @ __Constants.KEY_INV_2 % 128
    res -= __Constants.BIASES[1]
    res %= 128
    if res.shape[1] % 3 != 0:
        res = res[ : , : (-1) ]
    for k in range(0, res.shape[1], 3):
        res[ : , k : (k + 3) ] = res[ : , k : (k + 3) ] @ __Constants.KEY_INV_3 % 128
    res -= __Constants.BIASES[0]
    res %= 128
    return res
def __num2cry(x):
    return "".join( __en2code(( x[ 0 , k ] , x[ 0 , (k + 1) ] )) for k in range(0, x.shape[1], 2) )
def __cry2num(x):
    res = []
    for k in range(0, len(x), 14):
        cur_nums = __de2code(x[ k : (k + 14) ])
        res.append(cur_nums[0])
        res.append(cur_nums[1])
    return np.array(res).reshape( 1 , len(res) )
def encode(content: str) -> str:
    """
    UTF-8 Text
    -> Bytes to 7-bit Binaries
    -> Caesar Shift -> Hill(3) Transform
    -> Caesar Shift -> Hill(2) Transform
    -> Encoded
    """
    res    = __str2num(content)
    res, r = __numenco(res)
    res    = __num2cry(res)
    return "39" + res + [ "++" , "!=" , "->" ][r]
def decode(cipher: str) -> str:
    res, r = __cry2num(cipher[ 2 : (-2) ]), { "++": 0 , "!=": 1 , "->": 2 }[cipher[ (-2) : ]]
    res    = __numdeco(res)
    res    = __num2str(res[ : , : res.shape[1] + ((r - 3) if r else 0) ])
    return res
def enfile(filepath: str, outpath:str=None, forcemode:bool=True):
    """
    Encoding a File at the Specified Path.
    Parameters
    ----------
    * filepath: Path of the File to be Encoded;
    * outpath: Path of the Output File, which Loads the Encoded Cipher;
    * forcemode;
    Returns
    -------
    * fout: The Text-IO Wrapper of the Output File.
    See Also
    --------
    `.defile(...)`
    Examples
    --------
    """
    outpath = outpath or (filepath + ".mikucrypto")
    fout = open(outpath, "w" if forcemode else "x")
    with open(filepath, "r") as flin:
        fout.write(encode(flin.read()))
        flin.close()
    return fout
def defile(filepath: str, outpath:str=None, forcemode:bool=True):
    """
    Usages are Similar to `.enfile(...)`.
    """
    outpath = outpath or (filepath + ".txt")
    fout = open(outpath, "w" if forcemode else "x")
    with open(filepath, "r") as flin:
        fout.write(decode(flin.read()))
        flin.close()
    return fout