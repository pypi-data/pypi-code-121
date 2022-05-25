# -*- coding: UTF-8 -*-
import struct
import ctypes
import sys
import time
from ctypes import *


class p563Struct(Structure):
 _fields_ = [
          ("fSpeechLevel", c_double),  # c_byte
          ("fPitchAverage", c_double),  # c_byte
          ("fNoiseLevel", c_double),  #  c_byte
          ("fSnr", c_double),  # c_byte
          ("fRobotisation", c_double),  #  c_byte
          ("fPredictedMos", c_double)  # c_byte
     ]


def cal_563_mos(degFile):
    """
    仅支持窄带信号 （8k、16bit、mono）
    :param degFile: 输入文件
    :return: 无参考的MOS,语音电平，信噪比，噪声电平
    """
    p563 = p563Struct()
    mydll = ctypes.windll.LoadLibrary(sys.prefix + '/p563.dll')
    #buf = create_string_buffer(degFile.encode('gbk'), len(degFile))
    buf = c_char_p(bytes(degFile.encode('utf-8')))
    mydll.NR_MOS(buf,byref(p563))
    return p563.fPredictedMos,p563.fSpeechLevel,p563.fSnr,p563.fNoiseLevel

if __name__ == '__main__':
    for a in range(100):
        time.sleep(20)
        src = r'E:\audioalgorithm\audiotestalgorithm\demos\02_p563_demo\cleDstFile.wav'
        print(cal_563_mos(src))