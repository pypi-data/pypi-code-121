import fastvarints as fvi
import numpy as np

def test_version():
    assert fvi.__version__ == "0.0.1"


def test_comp_decomp():
    arr = np.random.poisson(30, 5000000) + 1 # elias does not work on 0s # .frame.decompress
    arr= arr.astype(np.uint32)
    comp = fvi.compress(arr)
    arr_dec = fvi.decompress(comp)
    assert len(arr) == len(arr_dec)
    assert (arr == arr_dec).all()

