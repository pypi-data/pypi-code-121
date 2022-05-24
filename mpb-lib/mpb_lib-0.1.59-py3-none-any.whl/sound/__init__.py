# rpgパッケージ用の初期化スクリプト
# 
# Copyright (c) 2021 Atsush Shibata(shivata@m-info.co.jp)
#
# Released under the MIT license.

import os
from io import BytesIO
import io
import numpy as np
from imageio import imread
import scipy
from scipy.io import wavfile
import IPython


def load(tone):
    """
    wavファイルを読み込む関数。toneにはc,e,gを指定。
    """
    if tone not in ["c", "d", "e", "f", "g", "a", "b"]:
        print("引数は，c，d，eのどれかの文字列にしてください。")
        return
    base = os.path.dirname(__file__)
    wavpath = os.path.join(base, f"./wavs/{tone}.wav")
    with open(wavpath, 'rb') as wav:
        freq, snd_arr = wavfile.read(wav)
        return snd_arr.astype(dtype="int").tolist()
    return 


def play(the_list):
    return IPython.display.Audio(np.array(the_list), rate=22050)

