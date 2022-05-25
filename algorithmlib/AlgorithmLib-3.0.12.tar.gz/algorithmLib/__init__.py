from .formatConvert.wav_pcm import  wav2pcm
from .G160.G160 import cal_g160
from .P563.P563 import cal_563_mos
from .PESQ.PESQ import *
from .POLQA.polqa_client import polqa_client_test
from .SDR.SDR import cal_sdr
from .STI.cal_sti import cal_sti
from .STOI.STOI import *
from .resample.resampler import resample,restruct
from .timeAligment.time_align import cal_delay
from .commFunction import get_data_array
from .SNR_ESTIMATION.MATCH_SIG import match_sig
from .SNR_ESTIMATION.SNR_MUSIC import cal_snr_music
from .SNR_ESTIMATION.SNR_TRANSIENT import cal_snr_transient
from .AGC_EVALUATION.CAL_GAIN_TABLE import cal_gain_table
from .AGC_EVALUATION.CAL_ATTACK_RELEASE import cal_attack_release
from .AGC_EVALUATION.CAL_MUSIC_STABILITY import cal_music_stablility
from .AGC_EVALUATION.CAL_DELAY import cal_DELAY
from .AEC_EVALUATION.MATCH_AEC import MATCH_AEC
from .AEC_EVALUATION.ERLE_ETSIMATION import cal_erle
from .FUNCTION.audioFunction import isSlience,audioFormat
from .AEC_MOS.aecmos import cal_aec_mos
from .MOS_INFER.run_predict import cal_mos_infer
from .Noise_Suppression.noiseFuction import  cal_noise_Supp
from operator import methodcaller
from .computeAudioQuality.mainProcess import computeAudioQuality

from ctypes import  *

def compute_audio_quality(metrics,testFile=None,refFile=None,micFile=None,cleFile=None,aecCaliFile=None,outFile=None,noiseFile=None,samplerate=16000,
                          bitwidth=2,channel=1,refOffset=0,testOffset=0,maxComNLevel =-48.0,speechPauseLevel=-35.0,audioType=0,
                          aecStartPoint=0,aecTargetType=0,aecScenario=0,rmsCalsection=None):
    """
    :param metrics: G160/P563/POLQA/PESQ/STOI/STI/PEAQ/SDR/SII/LOUDNESS/MUSIC/MATCH/
                    TRANSIENT/GAINTABLE/ATTACKRELEASE/MUSICSTA/AGCDELAY/MATCHAEC/
                    ERLE/SLIENCE/FORMAT/AECMOS/AIMOS/TRMS/ARMS/NOISE，必选项
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


