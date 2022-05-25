# -*- coding: UTF-8 -*-
import sys

sys.path.append('../')
from ctypes import *
from commFunction import emxArray_real_T,get_data_of_ctypes_
import ctypes


# void SNR_transient(const emxArray_real_T *ref, const emxArray_real_T *ref_noise,
#                    const emxArray_real_T *sig, double fs, double *SNR, double
#                    *noise_dB, double *err)


# void attackrelease_estimation(const emxArray_real_T *ref, const emxArray_real_T *
#   sig, double fs_ref, double fs_sig, double *time_attack, double *time_release,
#   double *err)
def cal_attack_release(refFile=None, testFile=None):
    """
    """
    refstruct,refsamplerate,_ = get_data_of_ctypes_(refFile)
    teststruct,testsamplerate,_ = get_data_of_ctypes_(testFile)

    if refsamplerate != testsamplerate :
        raise TypeError('Different format of ref and test files!')
    mydll = ctypes.windll.LoadLibrary(sys.prefix + '/attackrelease.dll')
    mydll.attackrelease_estimation.argtypes = [POINTER(emxArray_real_T),POINTER(emxArray_real_T),c_double,c_double, POINTER(c_double),POINTER(c_double),POINTER(c_double)]
    time_attack,time_release,err = c_double(0.0),c_double(0.0),c_double(0.0)
    mydll.attackrelease_estimation(byref(refstruct),byref(teststruct),c_double(refsamplerate),c_double(refsamplerate),byref(time_attack),byref(time_release),byref(err))

    if err.value == 0.0:
        return time_attack.value,time_release.value
    else:
        return None


if __name__ == '__main__':
    file = r'C:\Users\vcloud_avl\Downloads\agc_eva\speech_attackrelease.wav'
    test = r'C:\Users\vcloud_avl\Downloads\agc_eva\test_attackrelease.wav'
    print(cal_attack_release(refFile=file,testFile=test))
    pass