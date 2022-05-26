# -*- coding: UTF-8 -*-
import sys

sys.path.append('../')
import librosa
import requests

import numpy as np
import datetime

SCORING_URL = 'https://dnsmos.azurewebsites.net/score-dec'
AUTH = ('netease',
        'decmos')


SCENARIOS = [
    'doubletalk_with_movement',
    'doubletalk',
    'farend_singletalk_with_movement',
    'farend_singletalk',
    'nearend_singletalk'
]


def read_and_process_audio_files(lpb_path, mic_path, enh_path,startPoint,SAMPLE_RATE):
    lpb_sig, _ = librosa.load(lpb_path, sr=SAMPLE_RATE)
    mic_sig, _ = librosa.load(mic_path, sr=SAMPLE_RATE)
    enh_sig, _ = librosa.load(enh_path, sr=SAMPLE_RATE)

    # Make the clips the same length
    min_len = np.min([len(lpb_sig), len(mic_sig), len(enh_sig)])
    lpb_sig = lpb_sig[:min_len]
    mic_sig = mic_sig[:min_len]
    enh_sig = enh_sig[:min_len]


    lpb_sig, mic_sig, enh_sig = process_audio(
        lpb_sig, mic_sig, enh_sig,startPoint,SAMPLE_RATE)

    return lpb_sig, mic_sig, enh_sig



def process_audio(lpb_sig, mic_sig, enh_sig,startPoint,SAMPLE_RATE):
    silence_duration = startPoint * SAMPLE_RATE
    lpb_sig = lpb_sig[silence_duration:]
    mic_sig = mic_sig[silence_duration:]
    enh_sig = enh_sig[silence_duration:]
    return lpb_sig, mic_sig, enh_sig


def get_score(lpb_sig, mic_sig, enh_sig, scenario):
    audio_data = {
        'lpb': lpb_sig.tolist(),
        'mic': mic_sig.tolist(),
        'enh': enh_sig.tolist(),
        'scenario': scenario
    }

    response = requests.post(SCORING_URL, json=audio_data, auth=AUTH)
    json_body = response.json()

    if 'error' in json_body:
        raise Exception(json_body['error'])

    return json_body


def cal_aec_mos(refFile=None,micFile=None,testFile=None,scenario=1,startPoint=0,SAMPLE_RATE=48000):
    """
    Parameters
    ----------
    refFile
    micFile
    testFile
    scenario  0: doubletalk_with_movement 1:doubletalk 2:farend_singletalk_with_movement 3:farend_singletalk 4:nearend_singletalk
    startPoint： determine from which audio sample (startPoint(in second) * SAMPLE_RATE) to calculte
    SAMPLE_RATE：
    Returns
    -------

    """
    start = datetime.datetime.now()
    lpb_sig, mic_sig, enh_sig = read_and_process_audio_files(
        refFile, micFile, testFile,startPoint,SAMPLE_RATE)
    sjson = get_score(lpb_sig,mic_sig,enh_sig,SCENARIOS[scenario])
    end = datetime.datetime.now()
    print('time duration:',end-start)
    return sjson

if __name__ == '__main__':
    path = r'D:\AudioPublicWork\3a_auto_test_porject\3a_auto_test_porject\08_TestDstFiles\sdk_zego_vivo_y3hf_music_V_shengbo_compare\aec\Speech\TestCase_01_None_None\near_cn'
    ref = path + '\\' + 'far_cn_minus_30db.wav'
    mic =  path + '\\' + 'stdRefFile.wav'
    test =  path + '\\' + 'mixDstFile.wav'
    cal_aec_mos(testFile=test,refFile=ref,micFile=mic,startPoint=0,SAMPLE_RATE=16000,scenario=0)
