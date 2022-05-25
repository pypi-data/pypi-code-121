# -*- coding: UTF-8 -*-
import sys
sys.path.append('../')
import ctypes
from ctypes import *
from commFunction import emxArray_real_T,get_data_of_ctypes_

# void SNR_estimation(const emxArray_real_T *ref, const emxArray_real_T *sig,
#                     double fs, double *SNR, double *err)


def cal_snr_music(refFile=None, testFile=None):
    """
    """
    refstruct,refsamplerate,_ = get_data_of_ctypes_(refFile)
    teststruct,testsamplerate,_ = get_data_of_ctypes_(testFile)
    if refsamplerate != testsamplerate:
        raise TypeError('Different format of ref and test files!')
    mydll = ctypes.windll.LoadLibrary(sys.prefix + '/snr_music.dll')
    mydll.SNR_estimation.argtypes = [POINTER(emxArray_real_T),POINTER(emxArray_real_T),c_double, POINTER(c_double),POINTER(c_double)]
    snr,err = c_double(0.0),c_double(0.0)
    mydll.SNR_estimation(byref(refstruct),byref(teststruct),c_double(refsamplerate),byref(snr),byref(err))

    if err.value == 0.0:
        return snr.value
    else:
        return None

if __name__ == '__main__':
    cal_snr_music(refFile='speech.wav',testFile='music_rap.wav')
    pass