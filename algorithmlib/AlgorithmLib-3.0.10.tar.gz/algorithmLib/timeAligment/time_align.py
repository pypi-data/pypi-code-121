import ctypes
import sys
from ctypes import *
from formatConvert import wav2pcm


class delaystruct(Structure):
 _fields_ = [

        ("Crude_DelayEst", c_long),  # c_byte

 ]

def cal_delay(reffile, testfile, samplerate):
        delays = delaystruct()
        mydll = ctypes.windll.LoadLibrary(sys.prefix + '/time_align.dll')
        inputFile = c_char_p(
               bytes(reffile.encode('utf-8')))  # create_unicode_buffer(inFile.encode('utf-8'), len(inFile))
        outputFile = c_char_p(
               bytes(testfile.encode('utf-8')))  # create_unicode_buffer(outFile.encode('utf-8'), len(outFile))
        if samplerate == 8000:
               mode = 'nb'
        if samplerate == 16000:
               mode = 'wb'
        cmode = c_char_p(bytes(mode.encode('utf-8')))
        mydll.cal_delay(inputFile, outputFile, samplerate, cmode, byref(delays))
        print(delays.Crude_DelayEst)
        return delays.Crude_DelayEst

if __name__ == '__main__':
       ref = r'D:\AutoWork\audiotestalgorithm\algorithmLib\SNR_ESTIMATION\speech.wav'
       test = r'D:\AutoWork\audiotestalgorithm\algorithmLib\SNR_ESTIMATION\test.wav'
       cal_delay(wav2pcm(ref),wav2pcm(test),16000)
       pass