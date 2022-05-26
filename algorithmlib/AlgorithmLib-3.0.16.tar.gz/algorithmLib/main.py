from operator import methodcaller
from computeAudioQuality.mainProcess import computeAudioQuality
from ctypes import  *


def compute_audio_quality(metrics, testFile=None, refFile=None,micFile=None,cleFile=None, aecCaliFile=None,outFile=None, noiseFile=None,
                              samplerate=16000, bitwidth=2, channel=1, refOffset=0, testOffset=0, maxComNLevel=-48.0,
                              speechPauseLevel=-35.0,audioType=0,aecStartPoint=0,aecTargetType=0,aecScenario=0,rmsCalsection=None):
    """
    :param metrics: G160/P563/POLQA/PESQ/STOI/STI/PEAQ/SDR/SII/LOUDNESS/MUSIC/MATCH/
                    TRANSIENT/GAINTABLE/ATTACKRELEASE/MUSICSTA/AGCDELAY/MATCHAEC/
                    ELRE/SLIENCE/FORMAT/AECMOS/AIMOS/TRMS/ARMS/NOISE，必选项
    # G160 无采样率限制；  WAV/PCM输入 ；三端输入: clean、ref、test；无时间长度要求；
    # P563 8000hz(其他采样率会强制转换到8khz)；  WAV/PCM输入 ；单端输入: test；时长 < 20s；
    # POLQA 窄带模式  8k  超宽带模式 48k ；WAV/PCM输入 ；双端输入：ref、test；时长 < 20s；
    # PESQ 窄带模式  8k   宽带模式 16k ；WAV/PCM输入 ；双端输入：ref、test；时长 < 20s；
    # STOI 无采样率限制; 双端输入：ref、test；无时间长度要求；
    # STI >8k(实际会计算8khz的频谱)； WAV/PCM输入 ；双端输入：ref、test；时长 > 20s
    # PEAQ 无采样率限制；WAV/PCM输入 ；双端输入：ref、test；无时间长度要求；
    # SDR 无采样率限制; WAV/PCM输入 ; 双端输入：ref、test；无时间长度要求；
    # MATCH 无采样率限制; WAV/PCM输入;三端输入：ref、test、out； 无时间长度要求；
    # MUSIC 无采样率限制;WAV/PCM输入;双端输入：ref、test；无时间长度要求；
    # TRANSIENT 无采样率限制,WAV/PCM输入;三端输入：cle、noise、test； 无时间长度要求；
    # GAINTABLE 无采样率限制,WAV/PCM输入;双端输入：ref、test；固定信号输入；
    # ATTACKRELEASE 无采样率限制,WAV/PCM输入;双端输入：ref、test；固定信号输入；
    # MUSICSTA 无采样率限制,WAV/PCM输入;双端输入：ref、test；无时间长度要求；
    # AGCDELAY 无采样率限制,WAV/PCM输入;双端输入：ref、test；无时间长度要求；
    # MATCHAEC 无采样率限制 WAV/PCM输入;三端输入：ref、mic,test，；无时间长度要求；
    # ELRE 无采样率限制 WAV/PCM输入;三端输入：mic,ref、test；无时间长度要求；
    # SLIENCE 无采样率限制 WAV/PCM/MP4输入;单端输入：test；无时间长度要求；
    # FORMAT 无采样率限制 WAV/MP4输入;单端输入：test；无时间长度要求；
    # AECMOS 无采样率限制 WAV/PCM输入 ；三端输入：mic,ref、test；无时间长度要求；
    # AIMOS 无采样率限制 WAV/PCM输入 ；单端输入：test；无时间长度要求；
    # TRMS 无采样率限制 WAV/PCM输入 ；单端输入：test；无时间长度要求；
    # ARMS 无采样率限制 WAV/PCM输入 ；单端输入：test；无时间长度要求；
    # NOISE 无采样率限制 WAV/PCM输入 ；双端输入：ref、test；无时间长度要求；
    不同指标输入有不同的采样率要求，如果传入的文件不符合该指标的要求，会自动变采样到合法的区间
    :param testFile: 被测文件，必选项
    :param refFile:  参考文件，可选项，全参考指标必选，比如POLQA/PESQ/PEAQ
    :param micFile:  micIN，可选项，回声指标必选，MATCHAEC/ELRE/AECMOS
    :param cleFile:  干净语音文件，可选项，G160,TRANSIENT需要
    :param noiseFile 噪声文件，可选项，突发噪声信噪比计算需要
    :param aecCaliFile 用于做AEC对齐的校准文件  MATCHAEC专用
    :param outFile 输出文件，可选项，对齐文件可选
    :param samplerate: 采样率，可选项，pcm文件需要 default = 16000
    :param bitwidth: 比特位宽度，可选项，pcm文件需要 default = 2
    :param channel: 通道数，可选项，pcm文件需要 default = 1
    :param refOffset: ref文件的样点偏移，可选项，指标G160需要
    :param testOffset: test文件的样点偏移，可选项，指标G160需要
    :param maxComNLevel: 测试G160文件的最大舒适噪声
    :param speechPauseLevel 测试G160文件的语音间歇段的噪声
    :param audioType  输入音频的模式 0：语音 1：音乐 MATCH/GAINTABLE需要
    :param aecStartPoint  计算AECMOS，选择从第几秒开始计算
    :param aecTargetType  0:Chiness 1:English 2:Single Digit 3:Music  计算MATCHAEC/ELRE
    :param aecScenario 计算aec mos专用     0:'doubletalk_with_movement', 1:'doubletalk', 2:'farend_singletalk_with_movement', 3:'farend_singletalk', 4:'nearend_singletalk'
    :param rmsCalsection 计算rms的区间 TRMS和ARMS需要，时间单位s，比如：[1,20]
    :return:
    """
    paraDicts = {
        'metrics':metrics,
        'testFile':testFile,
        'refFile':refFile,
        'micFile':micFile,
        'cleFile':cleFile,
        'noiseFile':noiseFile,
        'aecCaliFile':aecCaliFile,
        'outFile':outFile,
        'samplerate':samplerate,
        'bitwidth':bitwidth,
        'channel':channel,
        'refOffset':refOffset,
        'testOffset':testOffset,
        'maxComNLevel':maxComNLevel,
        "speechPauseLevel":speechPauseLevel,
        "audioType":audioType,
        "aecStartPoint":aecStartPoint,
        "aecTargetType":aecTargetType,
        'aecScenario':aecScenario,
        'rmsCalsection':rmsCalsection
    }
    comAuQUA = computeAudioQuality(**paraDicts)
    return methodcaller(metrics)(comAuQUA)

if __name__ == '__main__':

    # speech = r'D:\AutoWork\audiotestalgorithm\algorithmLib\SNR_ESTIMATION\speech.wav'
    # music = r'D:\AutoWork\audiotestalgorithm\algorithmLib\SNR_ESTIMATION\music_rap.wav'
    # transi = r'D:\AutoWork\audiotestalgorithm\algorithmLib\SNR_ESTIMATION\transientNoise.wav'
    # test = r'D:\AutoWork\audiotestalgorithm\algorithmLib\SNR_ESTIMATION\test.wav'
    # res = compute_audio_quality('MUSIC',refFile=speech,testFile=music)
    #
    # print(res)
    #
    # res = compute_audio_quality('TRANSIENT',cleFile=speech,noiseFile=transi,testFile=test)
    # print(res)
    #
    # res = compute_audio_quality('MATCH',refFile=speech,testFile=test,outFile='123.wav')
    # print(res)
    #print(compute_audio_quality('G160', testFile=src,refFile=src,samplerate=16000))

    #print(match_sig(refFile='speech.wav', targetFile='test.wav', outFile='outfile.wav'))
    import time
    for a in range(200):
        time.sleep(1)
        src = r'E:\audioalgorithm\audiotestalgorithm\demos\02_p563_demo\cleDstFile.wav'
        print(compute_audio_quality('P563',testFile=src))
    exit(0)
    file = r'C:\Users\vcloud_avl\Downloads\agc_eva\speech_attackrelease.wav'
    test = r'C:\Users\vcloud_avl\Downloads\agc_eva\test_attackrelease.wav'
    print(compute_audio_quality('ATTACKRELEASE',refFile=file,testFile=test))

    file = r'C:\Users\vcloud_avl\Downloads\agc_eva\speech_gaintable.wav'
    test = r'C:\Users\vcloud_avl\Downloads\agc_eva\test.wav'
    lim,gain_table,DR = compute_audio_quality('GAINTABLE',refFile=file,testFile=test,audioType=1)
    print(lim,gain_table[0],DR[2])
    for a in gain_table:
        print(a)
    for a in DR:
        print(a)

    file = r'C:\Users\vcloud_avl\Downloads\agc_eva\music_stability_.wav'
    test = r'C:\Users\vcloud_avl\Downloads\agc_eva\test_music_stability.wav'
    res = compute_audio_quality('MUSICSTA',refFile=file, testFile=test)
    for a in res:
        print(a)

    file = r'C:\Users\vcloud_avl\Downloads\agc_eva\speech_gaintable.wav'
    test = r'C:\Users\vcloud_avl\Downloads\agc_eva\test.wav'
    delay = compute_audio_quality('AGCDELAY',refFile=file,testFile=test)
    print(delay)

    compute_audio_quality('MATCH',refFile=file,testFile=test,outFile='out.wav',audioType=1)