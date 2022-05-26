import wave
import os
import  numpy as np
from moviepy.editor import AudioFileClip
from commFunction import get_rms,get_ave_rms,get_one_channel_data,get_file_duration,get_data_array
from formatConvert import pcm2wav

def get_wav_from_mp4(mp4file):
    """
    Parameters
    ----------
    mp4file

    Returns
    -------

    """
    suffix = os.path.splitext(mp4file)[-1]
    if suffix != '.mp4':
        raise TypeError('wrong format! not mp4 file!' + str(suffix))
    my_audio_clip = AudioFileClip(mp4file)
    newFileName = mp4file[:-4] + '.wav'
    my_audio_clip.write_audiofile(newFileName)
    return newFileName


def isSlience(Filename =None,section=None,channels=1, bits=16, sample_rate=16000):
    """
    Parameters
    ----------
    Filename 支持 wav 和 pcm 和MP4

    Returns
    -------

    """
    suffix = os.path.splitext(Filename)[-1]

    if suffix == '.mp4':
        Filename = get_wav_from_mp4(Filename)
    if suffix == '.pcm':
        Filename = pcm2wav(Filename,channels,bits,sample_rate)
    if suffix == '.wav':
        pass
    lenth,fs = get_file_duration(Filename)
    data = get_one_channel_data(Filename)
    if section is None:
        startTime = 0
        endTime = lenth
    else:
        startTime = section[0]
        endTime = section[1]
    if startTime > lenth or startTime > endTime:
        raise TypeError('start point is larger than the file lenth :' + str(suffix))
    if endTime > lenth:
        endTime = lenth
    ins = data[int(startTime*fs):int(endTime*fs)]

    dBrmsValue = get_rms(ins)#20*math.log10(get_rms(ins)/32767+ 1.0E-6)
    print(dBrmsValue)
    if dBrmsValue > -70:
        return False
    else:
        for n in range(len(ins)//480):
            curdata = curdata[480*n:480*(n+1)]
            dBrmsValue = get_rms(curdata)#20 * math.log10(get_rms(curdata) / 32767 + 1.0E-6)
            print(dBrmsValue)
            if dBrmsValue > -60:
                return False
        return True
    pass


def audioFormat(wavFileName=None):
    """
    wavFileName：输入文件 wav，mp4
    Returns
    -------
    refChannel:通道数
    refsamWidth：比特位 2代表16bit
    refsamplerate：采样率
    refframeCount：样点数
    """
    suffix = os.path.splitext(wavFileName)[-1]
    if suffix != '.wav' and suffix != '.mp4':
        raise TypeError('wrong format! not wav/mp4 file!' + str(suffix))
    if suffix == '.mp4':
        wavFileName = get_wav_from_mp4(wavFileName)
    wavf = wave.open(wavFileName, 'rb')
    refChannel,refsamWidth,refsamplerate,refframeCount = wavf.getnchannels(),wavf.getsampwidth(),wavf.getframerate(),wavf.getnframes()
    return refChannel,refsamWidth*8,refsamplerate,refframeCount

def get_rms_level(wavFileName=None,rmsMode='total',section=None):
    """
    wavFileName：输入文件 wav，mp4
    Returns
    -------
    refChannel:通道数
    refsamWidth：比特位 2代表16bit
    refsamplerate：采样率
    refframeCount：样点数
    """
    suffix = os.path.splitext(wavFileName)[-1]
    if suffix != '.wav':
        raise TypeError('wrong format! not wav file!' + str(suffix))

    lenth,fs = get_file_duration(wavFileName)
    data = get_one_channel_data(wavFileName)
    if section == None:
        startTime = 0
        endTime = lenth
    else:
        startTime = section[0]
        endTime = section[1]
    if startTime > lenth or startTime > endTime:
        raise TypeError('start point is larger than the file lenth :' + str(suffix))
    if endTime > lenth:
        endTime = lenth
    curdata = data[int(startTime*fs):int(endTime*fs)]
    if rmsMode == 'total':
        return get_rms(curdata)
    if rmsMode == 'average':
        return get_ave_rms(curdata)
    return None



if __name__ == '__main__':
    ref = r'E:\02_ai_vad\5_aecm_1648612346.wav'
    print(isSlience(ref,section=[0,20]),)
    #print(audioFormat(ref))