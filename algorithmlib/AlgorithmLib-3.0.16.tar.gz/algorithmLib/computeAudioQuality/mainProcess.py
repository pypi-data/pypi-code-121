
import sys
import  os
import time
from os import  path
sys.path.append(os.path.dirname(path.dirname(__file__)))
from formatConvert.wav_pcm import wav2pcm,pcm2wav
from G160.G160 import cal_g160
from P563.P563 import cal_563_mos
from PESQ.PESQ import cal_pesq
from POLQA.polqa_client import  polqa_client_test
from SDR.SDR import cal_sdr
from STI.cal_sti import cal_sti
from STOI.STOI import cal_stoi
from PEAQ.PEAQ import cal_peaq
from resample.resampler import resample,restruct
from timeAligment.time_align import cal_delay
import os
import wave
import numpy as np
from ctypes import  *
from SNR_ESTIMATION.MATCH_SIG import match_sig
from SNR_ESTIMATION.SNR_MUSIC import cal_snr_music
from SNR_ESTIMATION.SNR_TRANSIENT import cal_snr_transient
from AGC_EVALUATION.CAL_GAIN_TABLE import cal_gain_table
from AGC_EVALUATION.CAL_ATTACK_RELEASE import cal_attack_release
from AGC_EVALUATION.CAL_MUSIC_STABILITY import cal_music_stablility
from AGC_EVALUATION.CAL_DELAY import cal_DELAY
from AEC_EVALUATION.MATCH_AEC import MATCH_AEC
from AEC_EVALUATION.ERLE_ETSIMATION import cal_erle
from AEC_MOS.aecmos import cal_aec_mos
from MOS_INFER.run_predict import cal_mos_infer
from FUNCTION.audioFunction import isSlience,audioFormat,get_rms_level
from Noise_Suppression.noiseFuction import  cal_noise_Supp

allMetrics = ['G160','P563','POLQA','PESQ','STOI','STI','PEAQ','SDR',
              'SII','LOUDNESS','MUSIC','TRANSIENT','MATCH','GAINTABLE',
              'ATTACKRELEASE','MUSICSTA','AGCDELAY','SLIENCE','FORMAT',
              'MATCHAEC','ERLE','AECMOS','AIMOS','TRMS','ARMS','NOISE']


class computeAudioQuality():
    def __init__(self,**kwargs):
        """
        :param kwargs:
        """
        #print(**kwargs)
        self.__parse_para(**kwargs)
        self.__chcek_valid()
        pass

    def __parse_para(self,**kwargs):
        """
        :param kwargs:
        :return:
        """
        self.mertic = kwargs['metrics']
        self.testFile = kwargs['testFile']
        self.refFile = kwargs['refFile']
        self.micFile = kwargs['micFile']
        self.cleFile = kwargs['cleFile']
        self.noiseFile = kwargs['noiseFile']
        self.caliFile = kwargs['aecCaliFile']
        self.outFile = kwargs['outFile']
        self.samplerate = kwargs['samplerate']
        self.bitwidth = kwargs['bitwidth']
        self.channel = kwargs['channel']
        self.refOffset = kwargs['refOffset']
        self.testOffset = kwargs['refOffset']
        self.maxComNLevel = kwargs['maxComNLevel']
        self.speechPauseLevel = kwargs['speechPauseLevel']
        self.audioType = kwargs["audioType"]
        self.aecStartPoint = kwargs['aecStartPoint']
        self.aecScenario = kwargs['aecScenario']
        self.aecTargetType = kwargs["aecTargetType"]
        self.rmsCalsection = kwargs["rmsCalsection"]
        #maxComNLevel=c_double(-48.0),speechPauseLevel=c_double(-35.0)

    def __chcek_valid(self):
        """
        :return:
        """
        if self.mertic not in allMetrics:
            raise ValueError('matrix must betwin ' + str(allMetrics))

    def __check_format(self,curWav):
        """
        :param curWav:
        :return:
        """
        curType = os.path.splitext(curWav)[-1]
        if curType !='.wav':
            return self.channel,self.bitwidth,self.samplerate
        wavf = wave.open(curWav,'rb')
        curChannel = wavf.getnchannels()
        cursamWidth = wavf.getsampwidth()
        cursamplerate = wavf.getframerate()
        wavf.close()
        if curChannel != 1:
            raise ValueError('wrong type of channel' + curWav)
        if cursamWidth != 2:
            raise ValueError('wrong type of samWidth' + curWav)
        return curChannel,cursamWidth,cursamplerate

    def __double_end_check(self):
        """
        :return:
        """
        if  self.refFile is None or self.testFile is None:
            raise EOFError('lack of inputfiles!')
        if self.__check_format(self.testFile) != self.__check_format(self.refFile):
            raise TypeError('there are different parametre in inputfiles!')

    def __data_convert(self,ref,test):
        """
        :return:
        """
        with open(wav2pcm(ref), 'rb') as ref:
            pcmdata = ref.read()
        with open(wav2pcm(test), 'rb') as ref:
            indata = ref.read()
        ref = np.frombuffer(pcmdata, dtype=np.int16)
        ins = np.frombuffer(indata, dtype=np.int16)
        lenth = min(len(ref),len(ins))
        return ref[:lenth],ins[:lenth]

    def G160(self):
        """
        :return:
        # g160 无采样率限制
        # WAV/PCM 输入
        """
        if self.cleFile is None or self.refFile is None or self.testFile is None:
            raise EOFError('lack of inputfiles!')
        if self.__check_format(self.testFile) != self.__check_format(self.refFile) or \
            self.__check_format(self.testFile) != self.__check_format(self.cleFile):
            raise TypeError('there are different parametre in inputfiles!')
        return cal_g160(pcm2wav(self.cleFile,sample_rate=self.samplerate),pcm2wav(self.refFile,sample_rate=self.samplerate),pcm2wav(self.testFile,sample_rate=self.samplerate),self.refOffset,self.testOffset,maxComNLevel=self.maxComNLevel,speechPauseLevel=self.speechPauseLevel)

    def P563(self):
        """
        # P 563 PCM输入 、 8Khz
        # • Sampling frequency: 8000 Hz
        #  If higher frequencies are used for recording, a separate down-sampling by using a high
        # quality flat low pass filter has to be applied. Lower sampling frequencies are not allowed.
        # • Amplitude resolution: 16 bit linear PCM
        # • Minimum active speech in file: 3.0 s
        # • Maximum signal length: 20.0 s
        # • Minimum speech activity ratio: 25%
        # • Maximum speech activity ratio: 75%
        :return:
        """
        if self.testFile is None:
            raise EOFError('lack of inputfiles!')
        curCH,curBwidth,curSR = self.__check_format(self.testFile)
        #TODO 将采样率
        if curSR != 8000:
            print('file will be resampled to 8k!')
        finalName = wav2pcm(resample(pcm2wav(self.testFile,sample_rate=self.samplerate),8000))
        return cal_563_mos(finalName)

    def POLQA(self):
        """
        #POLQA  窄带模式  8k   超宽带模式 48k
        # pcm输入
        :return:
        """

        self.__double_end_check()
        curCH,curBwidth,curSR = self.__check_format(self.testFile)

        result =  polqa_client_test(wav2pcm(self.refFile),wav2pcm(self.testFile),curSR)
        time.sleep(2)
        return  result


    def PESQ(self):
        """
        # PESQ 窄带模式8K  宽带模式 16k
        # 数据块输入
        :return:
        """
        self.__double_end_check()
        curCH,curBwidth,curSR = self.__check_format(self.testFile)
        if curSR < 16000:
            print('file will be resampled to 8k!')
            finalrefName = wav2pcm(resample(pcm2wav(self.refFile, curSR), 8000))
            finaltestName = wav2pcm(resample(pcm2wav(self.testFile, curSR), 8000))
            return cal_pesq(finalrefName, finaltestName, 8000)
        else:
            print('file will be resampled to 16k!')
            finalrefName = wav2pcm(resample(pcm2wav(self.refFile, sample_rate=curSR), 16000))
            finaltestName = wav2pcm(resample(pcm2wav(self.testFile, sample_rate=curSR), 16000))
            return cal_pesq(finalrefName,finaltestName,16000)


    def STOI(self):
        """
        #STOI
        #数据块输入
        #采样率 16000
        :return:
        """
        self.__double_end_check()
        ref, ins = self.__data_convert(wav2pcm(resample(pcm2wav(self.refFile),16000)),wav2pcm(resample(pcm2wav(self.testFile),16000)))
        result = cal_stoi(ref,ins,sr=16000)
        return result
        pass

    def STI(self):
        """
        #sti
        #wav输入 采样率无关
        :return:
        """
        self.__double_end_check()
        return cal_sti(pcm2wav(self.refFile,sample_rate=self.samplerate),pcm2wav(self.testFile,sample_rate=self.samplerate))
        pass

    def SII(self):
        """
        Returns
        -------

        """
        pass

    def PEAQ(self):
        """
        # wav输入
        :return:
        """
        self.__double_end_check()
        curCH,curBwidth,curSR = self.__check_format(self.testFile)
        if curSR not in [8000,16000]:
            #TODO 采样率
            pass
        #TODO 计算peaq
        return cal_peaq(pcm2wav(self.refFile,sample_rate=self.samplerate),pcm2wav(self.testFile,sample_rate=self.samplerate))
        pass

    def SDR(self):
        """
        #SDR
        #数据块输入  采样率无关
        :return:
        """
        self.__double_end_check()
        ref, ins = self.__data_convert(wav2pcm(resample(pcm2wav(self.refFile),16000)),wav2pcm(resample(pcm2wav(self.testFile),16000)))
        result = cal_sdr(ref,ins,sr=16000)
        return result
        pass

    def MUSIC(self):
        """
        # MUSIC SNR
        # 无采样率限制
        # WAV/PCM 输入
        :return:
        """
        self.__double_end_check()
        return cal_snr_music(refFile=pcm2wav(self.refFile,sample_rate=self.samplerate),testFile=pcm2wav(self.testFile,sample_rate=self.samplerate))

    def TRANSIENT(self):
        """
        # Transient noise SNR
        # 无采样率限制
        # WAV/PCM 输入
        :return:
        """
        if self.cleFile is None or self.testFile is None or self.noiseFile is None:
            raise EOFError('lack of inputfiles!')
        if self.__check_format(self.cleFile) != self.__check_format(self.testFile) or \
            self.__check_format(self.testFile) != self.__check_format(self.noiseFile):
            raise TypeError('there are different parametre in inputfiles!')
        return cal_snr_transient(pcm2wav(self.cleFile,sample_rate=self.samplerate),pcm2wav(self.noiseFile,sample_rate=self.samplerate),pcm2wav(self.testFile,sample_rate=self.samplerate))

    def MATCH(self):
        """
        # MATCH SIG
        # 无采样率限制
        # 可选择是否输出文件
        # WAV/PCM 输入
        :return:
        """
        self.__double_end_check()
        return match_sig(pcm2wav(self.refFile,sample_rate=self.samplerate), pcm2wav(self.testFile,sample_rate=self.samplerate), self.outFile,self.audioType)

    def LOUDNESS(self):
        """
        Returns
        -------

        """
        pass

    def __cal_sii__(self):
        '''
        Returns
        -------

        '''
        #return cal_sii()
        pass

    def GAINTABLE(self):
        """
        AGC PARA 1
        计算agc的gain table
        :return:
        """
        self.__double_end_check()
        return cal_gain_table(refFile=pcm2wav(self.refFile, sample_rate=self.samplerate),
                             testFile=pcm2wav(self.testFile, sample_rate=self.samplerate),targetType=self.audioType)

    def ATTACKRELEASE(self):
        """
        AGC PARA 2
        计算agc的attack release
        :return:
        """
        self.__double_end_check()
        return cal_attack_release(refFile=pcm2wav(self.refFile, sample_rate=self.samplerate),
                             testFile=pcm2wav(self.testFile, sample_rate=self.samplerate))
    def MUSICSTA(self):
        """
        AGC PARA 3
        计算music 信号稳定性
        :return:
        """
        self.__double_end_check()
        return cal_music_stablility(refFile=pcm2wav(self.refFile, sample_rate=self.samplerate),
                             testFile=pcm2wav(self.testFile, sample_rate=self.samplerate))

    def AGCDELAY(self):
        """
        AGC PARA 3
        计算文件延时
        :return:
        """
        self.__double_end_check()
        return cal_DELAY(refFile=pcm2wav(self.refFile, sample_rate=self.samplerate),
                             testFile=pcm2wav(self.testFile, sample_rate=self.samplerate))

    def AECMOS(self):
        """
        Returns
        -------

        """
        if self.refFile is None or self.micFile is None or self.testFile is None:
            raise EOFError('lack of inputfiles!')
        if self.__check_format(self.refFile) != self.__check_format(self.micFile) or \
            self.__check_format(self.micFile) != self.__check_format(self.testFile):
            raise TypeError('there are different parametre in inputfiles!')
        return cal_aec_mos(pcm2wav(self.refFile,sample_rate=self.samplerate),pcm2wav(self.micFile,sample_rate=self.samplerate),pcm2wav(self.testFile,sample_rate=self.samplerate),scenario=self.aecScenario,startPoint=self.aecStartPoint,SAMPLE_RATE=self.samplerate)

    def AIMOS(self):
        """
        Returns
        -------

        """
        if self.testFile is None:
            raise EOFError('lack of inputfiles!')
        finalName = pcm2wav(self.testFile,sample_rate=self.samplerate)
        return cal_mos_infer(finalName)

    def ERLE(self):
        """
        Returns
        -------

        """
        if self.refFile is None or self.micFile is None or self.testFile is None:
            raise EOFError('lack of inputfiles!')
        if self.__check_format(self.refFile) != self.__check_format(self.micFile) or \
            self.__check_format(self.micFile) != self.__check_format(self.testFile):
            raise TypeError('there are different parametre in inputfiles!')
        return cal_erle(refFile=pcm2wav(self.refFile,sample_rate=self.samplerate),micFile=pcm2wav(self.micFile,sample_rate=self.samplerate),testFile=pcm2wav(self.testFile,sample_rate=self.samplerate),targetType=self.aecTargetType)

    def MATCHAEC(self):
        """
        Returns
        -------

        """
        if self.caliFile is None or self.refFile is None or self.testFile is None:
            raise EOFError('lack of inputfiles!')
        if self.__check_format(self.caliFile) != self.__check_format(self.refFile) or \
            self.__check_format(self.caliFile) != self.__check_format(self.testFile):
            raise TypeError('there are different parametre in inputfiles!')
        return MATCH_AEC(pcm2wav(self.refFile,sample_rate=self.samplerate),pcm2wav(self.testFile,sample_rate=self.samplerate),pcm2wav(self.caliFile,sample_rate=self.samplerate),self.outFile,targetType=self.aecTargetType)

    def SLIENCE(self):
        """
        Returns
        -------

        """
        if self.testFile is None:
            raise EOFError('lack of inputfiles!')
        return isSlience(self.testFile,sample_rate=self.samplerate,bits=self.bitwidth,channels=self.channel,section=self.rmsCalsection)

    def FORMAT(self):
        """
        Returns
        -------

        """
        if self.testFile is None:
            raise EOFError('lack of inputfiles!')
        return audioFormat(self.testFile)


    def TRMS(self):
        """
        Returns
        -------
        # (wavFileName=None,rmsMode='total',startTime=0,endTime=1):
        """
        if self.testFile is None:
            raise EOFError('lack of inputfiles!')
        return get_rms_level(wavFileName=pcm2wav(self.testFile,sample_rate=self.samplerate),rmsMode='total',section=self.rmsCalsection)
    def ARMS(self):
        """
        Returns
        -------

        """
        if self.testFile is None:
            raise EOFError('lack of inputfiles!')
        return get_rms_level(wavFileName=pcm2wav(self.testFile,sample_rate=self.samplerate),rmsMode='average',section=self.rmsCalsection)

    def NOISE(self):
        """
        Returns
        -------

        """
        self.__double_end_check()
        return cal_noise_Supp(pcm2wav(self.refFile, sample_rate=self.samplerate),
                             pcm2wav(self.testFile, sample_rate=self.samplerate))