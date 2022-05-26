# void music_stability(const emxArray_real_T *ref, const emxArray_real_T *sig,
#                      double fs_ref, double fs_sig, double music_stability_ratio
#                      [1294], double *err)

# -*- coding: UTF-8 -*-
import sys

sys.path.append('../')
from ctypes import *
from commFunction import emxArray_real_T,get_data_of_ctypes_
import ctypes

def cal_music_stablility(refFile=None, testFile=None):
    """
    """
    refstruct,refsamplerate,_ = get_data_of_ctypes_(refFile)
    teststruct,testsamplerate,_ = get_data_of_ctypes_(testFile)

    if refsamplerate != testsamplerate :
        raise TypeError('Different format of ref and test files!')
    mydll = ctypes.windll.LoadLibrary(sys.prefix + '/musicStability.dll')
    mydll.music_stability.argtypes = [POINTER(emxArray_real_T),POINTER(emxArray_real_T),c_double,c_double,POINTER(c_double),POINTER(c_double)]
    data_format = c_double*1294
    msr = data_format()
    err = c_double(0.0)
    mydll.music_stability(byref(refstruct),byref(teststruct),c_double(refsamplerate),c_double(refsamplerate),msr,byref(err))

    if err.value == 0.0:
        return msr
    else:
        return None


if __name__ == '__main__':
    file = r'C:\Users\vcloud_avl\Downloads\agc_eva\music_stability_.wav'
    test = r'C:\Users\vcloud_avl\Downloads\agc_eva\test_music_stability.wav'
    res = cal_music_stablility(refFile=file,testFile=test)
    for a in res:
        print(a)
    pass