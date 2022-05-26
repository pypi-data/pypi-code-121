# -*- coding: UTF-8 -*-
import  sys
import os
from os import path
sys.path.append((os.path.dirname(path.dirname(__file__))))
from ctypes import *
import sys
import  time
from commFunction import global_result,getip

params = [1, 16000, 16, 99, 1, 16000, 16, 99, 1, 1, 0.2, 1, 0, 1, 0, 2, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1,
          -1, -1]  # for WB 16K sample rate
params = [1, 16000, 16, 99, 1, 16000, 16, 99, 1, 1, 0.2, 1, 0, 1, 0, -1, -1, -1, -1, -1, -1, 0, 2, 0, 3, 0, 0, 0, 0, 0]

connect_flag = False
stop_flag = False
stop_flag1 = False
VQTdll = cdll.LoadLibrary(sys.prefix + '/VQTDll.dll')


def VQTLogfunc(msg):
    # print('VQTLogfunc : Start')
    c_s = msg.decode()
    # cs = str(c_s,'utf-8')
    cs = str(c_s)
    print(cs)
    global connect_flag
    global stop_flag1
    if 'Connected' in cs or 'Message sent' in cs:
        connect_flag = True
        stop_flag1 = True


def VQTMSGfunc(msg):
    c_s = string_at(msg)
    cs = str(c_s, 'utf-8')
    print(cs)
    global stop_flag
    if 'VQT PAMS/PSQM Test Failed' in cs:
        mosFailedFlag = True
    else:
        if 'POLQA:' in cs:
            global_result.mosResult['mos'] = cs.split('POLQA:')[1].strip()
        if 'Speech Level Gain:' in cs:
            global_result.mosResult['Speech Level Gain'] = cs.split('Speech Level Gain:')[1].strip()
        if 'Noise Level Gain:' in cs:
            global_result.mosResult['Noise Level Gain'] = cs.split('Noise Level Gain:')[1].strip()


def startvqt(srcFile=None, degFile=None, samplerate=48000):
    params = [1, 0, 16, 99, 1, 0, 16, 99, 1, 1, 0.2, 1, 0, 1, 0, 2]
    params = [1, 16000, 16, 99, 1, 16000, 16, 99, 1, 1, 0.2, 1, 0, 1, 0, 2, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1,
              -1, -1, -1]
    params = [1, 16000, 16, 99, 1, 16000, 16, 99, 1, 1, 0.2, 1, 0, 1, 0, -1, -1, -1, -1, -1, -1, 0, 2, 0, 3, 0, 0, 0, 0,
              0]
    params[1], params[5] = samplerate, samplerate
    params = (c_float * len(params))(*params)
    if connect_flag == False:
        vip = getip()
        try:
            VQTdll.ConnectPort(c_char_p(vip.encode('utf_8')), 6666)
            while connect_flag == False:
                pass
        except Exception as e:
            print(str(e))
    VQTdll.RunVQTPAMSPSQM(0, 0, c_char_p(srcFile.encode('utf_8')), c_char_p(degFile.encode('utf_8')), 1, params)
    time.sleep(5)
    pass


def vqtDisConnect():
    VQTdll.Disconnect()


callback_type = CFUNCTYPE(None, c_char_p)
callback_login = callback_type(VQTLogfunc)
VQTdll.SetVQTLogMessage(callback_login)
# TODO 初始化放到init里
callback_type1 = CFUNCTYPE(None, c_wchar_p)
callback = callback_type1(VQTMSGfunc)
VQTdll.SetVQTRecvDBResponse(callback)


def test_polqa(file_name, count):
    f = file_name
    mode = ['_music', '_speech']
    for m in mode:
        bps = ['20kbps', '28kbps', '32kbps', '40kbps', '48kbps', '64kbps']
        for b in bps:
            for i in range(count):
                input = 'E:\\weiwei\\data_for_opus\\input\\' + f + str(i) + '.wav'
                output = 'E:\\weiwei\\data_for_opus\\output\\' + f + '_comp5_' + b + m + str(i) + '.wav'
                # print(input, output)
                startvqt(srcFile=input, degFile=output, samplerate=48000)
                print(output, mosResult['mos'])


if __name__ == '__main__':
    input = r'E:\01_MOS_AUTO_TESTER\testSrcFiles\Speech_16000\female\femalePolqaWB.pcm'
    output = r'E:\02_POLQA_RESULT\testDstFiles\NERTC_honor8x_iphone11_V4.3.0\L\Speech_16000\NONE\female\femalePolqaWB\femalePolqaWB_20210601201611_O_ManualTest_My Phone2_20210601201611_p_0.0.pcm'
    output2 = r'E:\02_POLQA_RESULT\testDstFiles\NERTC_honor8x_iphone11_V4.3.0\L\Speech_16000\NONE\female\femalePolqaWB\femalePolqaWB_20210601201541_O_ManualTest_My Phone2_20210601201541_p_4.19.pcm'
    output3 = r'E:\02_POLQA_RESULT\testDstFiles\123.pcm'
    startvqt(srcFile=input, degFile=output3,
             samplerate=16000)
    print(global_result.mosResult['mos'])
    VQTdll.Disconnect()
