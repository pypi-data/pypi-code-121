# -*- coding: UTF-8 -*-
import copy
import sys
import wave
sys.path.append('./')
sys.path.append('../')
from ctypes import *
from commFunction import emxArray_real_T,get_data_of_ctypes_,write_ctypes_data_2_file_,get_none_data_of_ctypes_
import  ctypes


# DLL_EXPORT void matchsig_2(const emxArray_real_T *ref, const emxArray_real_T *sig, double
#                 fs, double type,emxArray_real_T *sig_out, double *delay, double *err)


# void matchsig_2(const emxArray_real_T *ref, const emxArray_real_T *sig, double
#                 fs, double type, emxArray_real_T *sig_out, double *delay, double
#                 *err)

# void matchsig_2(const emxArray_real_T *ref, const emxArray_real_T *sig, double
#                 fs, double type, emxArray_real_T *sig_out, double *delay, double
#                 *err)

def match_sig(refFile=None,testFile=None,outFile=None,audioType=0):
    """
    Parameters
    ----------
    refFile
    testFile
    outFile
    audioType  0:speech,1:music

    Returns
    -------

    """

    refstruct, refsamplerate,reflen = get_data_of_ctypes_(refFile)
    teststruct, testsamplerate,testlen = get_data_of_ctypes_(testFile)
    outlen = max(reflen,testlen)

    outStruct = get_none_data_of_ctypes_(outlen)
    if refsamplerate != testsamplerate :
        raise TypeError('Different format of ref and test files!')
    mydll = ctypes.windll.LoadLibrary(sys.prefix + '/matchsig.dll')
    mydll.matchsig_2.argtypes = [POINTER(emxArray_real_T), POINTER(emxArray_real_T), POINTER(emxArray_real_T),c_double,c_double,
                                     POINTER(c_double), POINTER(c_double)]
    delay, err = c_double(0.0), c_double(0.0)
    mydll.matchsig_2(byref(refstruct), byref(teststruct), byref(outStruct),c_double(refsamplerate),c_double(audioType),byref(delay), byref(err))
    if err.value > 0.0:
        return None
    else:
        if outFile is not None:
            write_ctypes_data_2_file_(outFile,outStruct,refsamplerate)
        return delay.value




if __name__ == '__main__':
    ref = r'C:\Users\vcloud_avl\Documents\我的POPO\src.wav'
    test = r'C:\Users\vcloud_avl\Documents\我的POPO\test.wav'
    print(match_sig(refFile=ref, testFile=test, outFile='outfile.wav'))

    pass