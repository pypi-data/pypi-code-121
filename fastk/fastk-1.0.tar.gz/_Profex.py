from ctypes import CDLL, POINTER, Structure, cast, c_int, c_ushort, c_char_p, c_longlong
from typing import Union, Optional, List, Tuple
from os.path import dirname, join, isfile


class Profile(Structure):
    _fields_ = [("profile", POINTER(c_ushort)),
                ("length", c_int),
                ("K", c_int)]


lib = CDLL(join(dirname(__file__), "Profex.so"))
lib.load_profile.restype = POINTER(Profile)


def profex(fastk_prefix: str,
           read_id: int,
           zero_padding: bool = False,
           return_k: bool = False) -> Union[List[int], Tuple[List[int], int]]:
    """Run Profex and return the k-mer count profile of a single read.

    positional arguments:
      @ fastk_prefix : Prefix of the output files of FastK.
      @ read_id      : Read ID (1, 2, ...)
      @ zero_padding : If True, add (K - 1) zero counts to the prefix.
      @ return_k     : If True, return the value of K as well.
    """
    assert isfile(f"{fastk_prefix}.prof"), "No .prof file"
    ret = lib.load_profile(c_char_p(fastk_prefix.encode('utf-8')),
                           c_longlong(read_id))
    x = cast(ret.contents.profile,
             POINTER(c_ushort * ret.contents.length))[0]
    counts = [x[i] for i in range(len(x))]
    K = ret.contents.K
    lib.free_profile(ret)
    if zero_padding:
        counts = [0] * (K - 1) + counts
    return counts if not return_k else (counts, K)
