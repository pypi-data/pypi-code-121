#!/usr/bin/env python
# encoding: utf-8

# The MIT License

# Copyright (c) 2018 Ina (David Doukhan - http://www.ina.fr/)

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

from __future__ import annotations

import tempfile
import warnings
from pathlib import Path
from subprocess import Popen, PIPE
from typing import Optional, Callable, Any

import numpy as np

from .constants import ina_config, PathLike
from .sidekit_mfcc import read_wav
from .tf_mfcc import mel_spect


def _wav2feats(wav_path: PathLike):
    """
    Extract features for wav 16k mono
    """
    sig, read_framerate, sample_width = read_wav(wav_path)
    shp = sig.shape
    # wav should contain a single channel
    assert len(shp) == 1 or (len(shp) == 2 and shp[1] == 1)
    # wav sample rate should be 16000 Hz
    assert read_framerate == 16000
    # current version of readwav is supposed to return 4
    # whatever encoding is detected within the wav file
    assert sample_width == 4
    # sig *= (2**(15-sampwidth))

    np.seterr(divide='ignore')
    np.seterr(invalid='ignore')
    # _, loge, _, mspec = mfcc(sig.astype(np.float32), get_mspec=True)
    loge, mspec = mel_spect(sig)

    # Management of short duration segments
    difflen = 0
    if len(loge) < 68:
        difflen = 68 - len(loge)
        warnings.warn(
            "media %s duration is short. Robust results require length of at least 720 milliseconds" % wav_path)
        mspec = np.concatenate((mspec, np.ones((difflen, 24)) * np.min(mspec)))
        # loge = np.concatenate((loge, np.ones(difflen) * np.min(mspec)))

    return mspec, loge, difflen


def media2feats(path: PathLike, start_sec: int = 0, stop_sec: Optional[int] = None):
    """
    Convert media to temp wav 16k file and return features
    """
    if ina_config.auto_convert:
        return to_wav(path, True, start_sec, stop_sec, _wav2feats)

    return _wav2feats(path)


def to_wav(path: PathLike, tmp_dir: bool = False, start_sec: int = 0, stop_sec: Optional[int] = None,
           tmp_callback: Optional[Callable[[Path], Any]] = None, sr: Optional[int] = 16000):
    """
    Convert an audio file to wav and resample it using FFmpeg

    :param path: Path of original audio file
    :param tmp_dir: Whether to use temporary directory
    :param start_sec: Start second (Default: 0)
    :param stop_sec: Stop second (Default: None - full song)
    :param tmp_callback: Callback if you're using temporary directory, because it's cleared after the call
    :param sr: Sample rate (Default: resample to 16000) - Set to None to disable resampling
    :return: Wave file path, or return value of the callback
    """
    path = Path(path)
    tmp = None
    dir = path.parent
    if tmp_dir:
        tmp = tempfile.TemporaryDirectory(dir=ina_config.tmp_dir)
        dir = Path(tmp.name)

    # build ffmpeg command line
    wav_path = dir / path.with_suffix('.converted.wav').name
    args = [ina_config.ffmpeg, '-y', '-i', str(path.absolute()), '-ac', '1']
    if sr:
        args += ['-ar', str(sr)]
    if start_sec > 0:
        args += ['-ss', '%f' % start_sec]
    if stop_sec is not None:
        args += ['-to', '%f' % stop_sec]
    args.append(str(wav_path.absolute()))

    # launch ffmpeg
    p = Popen(args, stdout=PIPE, stderr=PIPE)
    output, error = p.communicate()
    assert p.returncode == 0, error

    # Call temp callback
    if tmp_callback:
        result = tmp_callback(wav_path)
    else:
        result = wav_path

    if tmp:
        tmp.cleanup()

    return result
