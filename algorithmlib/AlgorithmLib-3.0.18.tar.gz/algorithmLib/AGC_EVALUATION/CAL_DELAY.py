# -*- coding: UTF-8 -*-
import sys

sys.path.append('../')
from ctypes import *
from commFunction import emxArray_real_T,get_data_of_ctypes_
import ctypes

#  * -------------------------------------------------------------------------
#  * Arguments    : const emxArray_real_T *ref_in
#  *                const emxArray_real_T *sig_in
#  *                double fs
#  *                double *delay
#  *                double *err
#  * Return Type  : void
#  */
# void delay_estimation_15s(const emxArray_real_T *ref_in, const emxArray_real_T
#   *sig_in, double fs, double *delay, double *err)

def cal_DELAY(refFile=None, testFile=None):
    """
    """
    refstruct,refsamplerate,_ = get_data_of_ctypes_(refFile)
    teststruct,testsamplerate,_ = get_data_of_ctypes_(testFile)

    if refsamplerate != testsamplerate :
        raise TypeError('Different format of ref and test files!')
    mydll = ctypes.windll.LoadLibrary(sys.prefix + '/agcDelay.dll')
    mydll.delay_estimation_15s.argtypes = [POINTER(emxArray_real_T),POINTER(emxArray_real_T),c_double,POINTER(c_double),POINTER(c_double)]
    delay,err = c_double(0.0),c_double(0.0)
    mydll.delay_estimation_15s(byref(refstruct),byref(teststruct),c_double(refsamplerate),byref(delay),byref(err))

    if err.value == 0.0:
        return delay.value
    else:
        return None


if __name__ == '__main__':
    file = r'C:\Users\vcloud_avl\Downloads\agc_eva\speech_gaintable.wav'
    test = r'C:\Users\vcloud_avl\Downloads\agc_eva\test.wav'
    delay = cal_DELAY(refFile=file,testFile=test)
    print(delay)
    pass