import ctypes
import sys
from ctypes import *


class pesqstruct(Structure):
 _fields_ = [
          ("pesq", c_double),  # c_byte
 ]

def cal_pesq(reffile, testfile,samplerate):
    pesqs = pesqstruct()
    mydll = ctypes.windll.LoadLibrary(sys.prefix + '/PY_PESQ.dll')
    inputFile = c_char_p(bytes(reffile.encode('utf-8')))#create_unicode_buffer(inFile.encode('utf-8'), len(inFile))
    outputFile = c_char_p(bytes(testfile.encode('utf-8')))#create_unicode_buffer(outFile.encode('utf-8'), len(outFile))
    if samplerate == 8000:
        mode = 'nb'
    if samplerate == 16000:
        mode = 'wb'
    cmode  = c_char_p(bytes(mode.encode('utf-8')))
    mydll.cal_pesq(inputFile,outputFile,samplerate,cmode,byref(pesqs))
    return pesqs.pesq


if __name__ == '__main__':
    ref = r'E:\files\out16000_8000.pcm'
    test = r'E:\files\out16000_8000.pcm'


    print(cal_pesq(ref,test,8000))