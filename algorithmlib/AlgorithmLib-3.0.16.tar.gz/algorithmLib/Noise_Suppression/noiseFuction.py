# -*- coding: utf-8 -*-
import sys
sys.path.append('./')
sys.path.append('../')

from commFunction import get_rms,make_out_file,get_ave_rms
import numpy as np

from SNR_ESTIMATION.MATCH_SIG import match_sig
from commFunction import get_data_array


speechSection = [12, 15]
noiseSection = [0, 10]
FRAME_LEN = 960



def get_data_pairs(srcFile=None,testFile=None):
    """
    Parameters
    ----------
    srcFile
    testFile
    Returns
    -------
    """

    samples = int(match_sig(refFile=srcFile, testFile=testFile))

    dataSrc, fs, chn = get_data_array(srcFile)
    dataTest, fs2, chn2 = get_data_array(testFile)

    print(dataTest,dataSrc,samples)
    assert fs == fs2
    assert  chn2 == chn
    assert samples > 0

    dataTest = dataTest[samples:]
    M,N = len(dataSrc),len(dataTest)
    targetLen = min(M,N)
    return dataSrc[:targetLen],dataTest[:targetLen],fs,chn


def cal_noise_converge(dataSrc,dataTest,fs,chn):
    """
    Parameters
    ----------
    dataSrc
    dataTest
    Returns
    -------
    """
    srcSpeechLevel = get_rms(dataSrc[fs*speechSection[0]:fs*speechSection[1]])
    curSpeechLevel = get_rms(dataTest[fs*speechSection[0]:fs*speechSection[1]])

    # log（V1 / V2) = X/20

    gain = np.power(10,(srcSpeechLevel - curSpeechLevel)/20)
    newData = dataTest.astype(np.float32) * gain
    make_out_file('source.wav', dataSrc.astype(np.int16), fs, chn)
    make_out_file('target.wav',newData.astype(np.int16),fs,chn)

    n_sengen = len(newData) // FRAME_LEN
    MAX_RMS = -120
    for a in range(n_sengen):
        curLevel = get_rms(newData[a*FRAME_LEN:(a+1)*FRAME_LEN])
        print(MAX_RMS,curLevel)
        if curLevel > MAX_RMS:
            MAX_RMS = curLevel
        if curLevel < MAX_RMS - 20:
            break
    converge = a * FRAME_LEN / fs

    nsLevel = get_ave_rms(dataSrc[int(converge * fs) :noiseSection[1]* fs]) - get_ave_rms(newData[int(converge * fs) :noiseSection[1]* fs])
    return converge, nsLevel
    #TODO 收敛时间
    #TODO 降噪量



def cal_noise_Supp(srcFile,testFile):
    """
    Parameters
    ----------
    data
    Returns
    -------
    """
    srcdata, dstdata, fs, chn = get_data_pairs(srcFile=srcFile, testFile=testFile)
    return  cal_noise_converge(srcdata,dstdata,fs,chn)





if __name__ == '__main__':
    src = 'car_noise_speech.wav'
    dst = 'speech_cn.wav'
    dur = cal_noise_Supp(src,dst)
    print(dur)
    pass