# -*- coding: UTF-8 -*-
import sys

sys.path.append('../')
from ctypes import *
from commFunction import emxArray_real_T,get_data_of_ctypes_
import ctypes


# void SNR_transient(const emxArray_real_T *ref, const emxArray_real_T *ref_noise,
#                    const emxArray_real_T *sig, double fs, double *SNR, double
#                    *noise_dB, double *err)

def cal_snr_transient(refFile=None, noisetFile=None, testFile=None):
    """
    """
    refstruct,refsamplerate,_ = get_data_of_ctypes_(refFile)
    teststruct,testsamplerate,_ = get_data_of_ctypes_(testFile)
    noiseStruct,noisesamplerate,_ = get_data_of_ctypes_(noisetFile)
    if refsamplerate != testsamplerate or refsamplerate!= noisesamplerate:
        raise TypeError('Different format of ref and test files!')
    mydll = ctypes.windll.LoadLibrary(sys.prefix + '/snr_transient.dll')
    mydll.SNR_transient.argtypes = [POINTER(emxArray_real_T),POINTER(emxArray_real_T),POINTER(emxArray_real_T),c_double, POINTER(c_double),POINTER(c_double),POINTER(c_double)]
    snr_1,snr_2,err = c_double(0.0),c_double(0.0),c_double(0.0)
    mydll.SNR_transient(byref(refstruct),byref(noiseStruct),byref(teststruct),c_double(refsamplerate),byref(snr_1),byref(snr_2),byref(err))

    if err.value == 0.0:
        return snr_1.value,snr_2.value
    else:
        return None


if __name__ == '__main__':

    cal_snr_transient(refFile='speech.wav',noisetFile='transientNoise.wav',testFile='test.wav')
    pass