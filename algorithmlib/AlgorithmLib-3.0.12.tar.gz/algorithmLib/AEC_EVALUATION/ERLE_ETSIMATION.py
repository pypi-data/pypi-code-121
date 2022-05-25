# -*- coding: UTF-8 -*-
import sys

sys.path.append('../')
from ctypes import *
from commFunction import emxArray_real_T,get_data_of_ctypes_
import ctypes

#  * -------------------------------------------------------------------------
#  * Arguments    : const emxArray_real_T *sig_mic
#  *                const emxArray_real_T *sig_far
#  *                const emxArray_real_T *sig_ref
#  *                double fs_mic
#  *                double fs_far
#  *                double type
#  *                double *ERLE
#  *                double *output_std
#  *                double *residual_avgdB
#  *                double *err
#  * Return Type  : void
#  */
# void ERLE_estimation(const emxArray_real_T *sig_mic, const emxArray_real_T
#                      *sig_far, const emxArray_real_T *sig_ref, double fs_mic,
#                      double fs_far, double type, double *ERLE, double
#                      *output_std, double *residual_avgdB, double *err)

def cal_erle(micFile = None,testFile =None, refFile =None,targetType=0):

    """
    %         type- input signal type:
    %               0:Chiness
    %               1:English
    %               2:Single Digit
    %               3:Music
    Parameters
    ----------
    inFile
    output
    refFile
    targetType

    Returns
    -------

    """
    instruct,insamplerate,_ = get_data_of_ctypes_(micFile)
    teststruct,outsamplerate,_ = get_data_of_ctypes_(testFile)
    refstruct, refsamplerate, _ = get_data_of_ctypes_(refFile)

    # if refsamplerate != testsamplerate :
    #     raise TypeError('Different format of ref and test files!')
    mydll = ctypes.windll.LoadLibrary(sys.prefix + '/ERLE_estimation.dll')
    mydll.ERLE_estimation.argtypes = [POINTER(emxArray_real_T),POINTER(emxArray_real_T),POINTER(emxArray_real_T),c_double,c_double,c_double,POINTER(c_double),POINTER(c_double),POINTER(c_double),POINTER(c_double)]
    data_format = c_double*11
    gain_table = data_format()
    DR = data_format()
    ERLE,output_std,err,residual_avgdB = c_double(0.0),c_double(0.0),c_double(0.0),c_double(0.0)
    mydll.ERLE_estimation(byref(instruct),byref(teststruct),byref(refstruct),c_double(insamplerate),c_double(outsamplerate),c_double(targetType),byref(ERLE),byref(output_std),byref(residual_avgdB),byref(err))

    if err.value == 0.0:
        return ERLE.value,output_std.value,residual_avgdB.value
    else:
        return None


if __name__ == '__main__':
    file = r'C:\Users\vcloud_avl\Downloads\agc_eva\speech_gaintable.wav'
    test = r'C:\Users\vcloud_avl\Downloads\agc_eva\test.wav'
    ref = ''
    ERLE,output_std,residual_avgdB = cal_erle(micFile=file,testFile=test,refFile=ref,targetType=0)
    print(ERLE,output_std,residual_avgdB)
