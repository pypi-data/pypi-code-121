# -*- coding: UTF-8 -*-
import sys

sys.path.append('./')
sys.path.append('../')
from ctypes import *
from commFunction import emxArray_real_T,get_data_of_ctypes_,write_ctypes_data_2_file_,get_none_data_of_ctypes_
import ctypes


def MATCH_AEC(refFile=None, testFile=None, caliFile=None,outFile=None,targetType=0):
    """
    %         type- input signal type:
    %               0:Chiness
    %               1:English
    %               2:Single Digit
    %               3:Music
    """
    refstruct,refsamplerate,reflen = get_data_of_ctypes_(refFile)
    teststruct,testsamplerate,testlen = get_data_of_ctypes_(testFile)
    calistruct,calisamplerate,_ = get_data_of_ctypes_(caliFile)
    outlen = max(reflen, testlen)
    outStruct = get_none_data_of_ctypes_(outlen)

    if refsamplerate != testsamplerate or testsamplerate!= calisamplerate:
        raise TypeError('Different format of ref and test files!')
    mydll = ctypes.windll.LoadLibrary(sys.prefix + '/matchsig_aec.dll')
    mydll.matchsig_aec.argtypes = [POINTER(emxArray_real_T),POINTER(emxArray_real_T),POINTER(emxArray_real_T),c_double,c_double,POINTER(emxArray_real_T),POINTER(c_double)]
    err,fs_out,type = c_double(0.0),c_double(refsamplerate),c_double(targetType)
    mydll.matchsig_aec(byref(teststruct),byref(refstruct),byref(calistruct),refsamplerate,type,byref(outStruct),byref(err))

    if err.value == 0.0:
        if outFile is not None:
            write_ctypes_data_2_file_(outFile, outStruct,refsamplerate)
        return delay.value
    else:
        return None


if __name__ == '__main__':
    path = r'D:\AudioPublicWork\3a_auto_test_porject\3a_auto_test_porject\08_TestDstFiles\sdk_zego_vivo_y3hf_music_V_shengbo_compare\aec\Speech\TestCase_01_None_None\near_cn'
    ref = path +'\\' +'far_cn.wav'
    test = path +'\\' + 'mixDstFile.wav'
    cali = path +'\\' + 'mixDstFile.wav'
    outFile = r'C:\Users\vcloud_avl\Downloads\Speech\TestCase_01_None_None\near_cn\target.wav'
    delay = MATCH_AEC(refFile=ref,testFile=test,caliFile=cali,outFile=outFile,targetType=0)
    print(delay)
    pass