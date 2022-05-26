# -*- coding: UTF-8 -*-
import os
import time
import wave
import numpy as np

def wav2pcm(wavfile, data_type=np.int16):
    """
    :param wavfile:
    :param data_type:
    :return:
    """
    suffix = os.path.splitext(wavfile)[-1]
    if suffix == '.pcm':
        return wavfile
    if suffix != '.wav':
        raise TypeError('wrong format! not wav file!' + str(suffix))
    newFileName = wavfile[:-4] + '.pcm'
    f = open(wavfile, "rb")
    f.seek(0)
    f.read(44)
    data = np.fromfile(f, dtype= data_type)
    data.tofile(newFileName)
    f.close()
    return newFileName
    #os.remove(wavfile)


def pcm2wav(pcm_file, channels=1, bits=16, sample_rate=16000):
    """
    :param pcm_file:
    :param channels:
    :param bits:
    :param sample_rate:
    :return:
    """
    suffix = os.path.splitext(pcm_file)[-1]
    if suffix == '.wav':
        return pcm_file
    if suffix != '.pcm':
        raise TypeError('wrong format! not pcm file!' + str(suffix))
    newFileName = pcm_file[:-4] + '.wav'
    pcmf = open(pcm_file, 'rb')
    pcmdata = pcmf.read()
    pcmf.close()
    if bits % 8 != 0:
        raise ValueError("bits % 8 must == 0. now bits:" + str(bits))
    wavfile = wave.open(newFileName, 'wb')
    wavfile.setnchannels(channels)
    wavfile.setsampwidth(bits // 8)
    wavfile.setframerate(sample_rate)
    wavfile.writeframes(pcmdata)
    wavfile.close()
    time.sleep(1)
    #os.remove(pcm_file)
    return newFileName





if __name__ == '__main__':
    cle = r'E:\files\cle_malePolqaWB.wav'
    wav2pcm(cle)