'''
File: __init__.py
Project: pyautd3
Created Date: 24/05/2021
Author: Shun Suzuki
-----
Last Modified: 25/05/2022
Modified By: Shun Suzuki (suzuki@hapis.k.u-tokyo.ac.jp)
-----
Copyright (c) 2022 Hapis Lab. All rights reserved.

'''


import shutil
import zipfile
import tarfile
import os
import os.path
import platform
import glob

import requests

from .native_methods.autd3capi import NativeMethods as Base
from .native_methods.autd3capi_gain_holo import NativeMethods as GainHolo
from .native_methods.autd3capi_link_emulator import NativeMethods as LinkEmulator
from .native_methods.autd3capi_link_remote_twincat import NativeMethods as LinkRemoteTwinCAT
from .native_methods.autd3capi_link_twincat import NativeMethods as LinkTwincAT
from .native_methods.autd3capi_modulation_audio_file import NativeMethods as ModulationAudioFile
from .native_methods.autd3capi_backend_cuda import NativeMethods as BackendCUDA
from .native_methods.autd3capi_link_soem import NativeMethods as LinkSOEM


from pyautd3.autd import to_legacy, to_normal
from pyautd3.autd import Focus, BesselBeam, PlaneWave, CustomGain, Null, Grouped
from pyautd3.autd import EigenBackend, CUDABackend
from pyautd3.autd import DontCare, Normalize, Uniform, Clamp
from pyautd3.autd import SDP, EVD, GS, GSPAT, Naive, LM, GaussNewton, GradientDescent, Greedy
from pyautd3.autd import Static, Sine, SineLegacy, SineSquared, Square
from pyautd3.autd import PointSTM, GainSTM
from pyautd3.autd import SilencerConfig
from pyautd3.autd import AUTD
from pyautd3.autd import SOEM, TwinCAT, RemoteTwinCAT, Emulator
from pyautd3.autd import NUM_TRANS_IN_UNIT, NUM_TRANS_X, NUM_TRANS_Y, TRANS_SPACING_MM, DEVICE_HEIGHT, DEVICE_WIDTH

__all__ = [
    'to_legacy',
    'to_normal',
    'Focus',
    'BesselBeam',
    'PlaneWave',
    'CustomGain',
    'Null',
    'Grouped',
    'EigenBackend',
    'CUDABackend',
    'DontCare',
    'Normalize',
    'Uniform',
    'Clamp',
    'SDP',
    'EVD',
    'GS',
    'GSPAT',
    'Naive',
    'LM',
    'GaussNewton',
    'GradientDescent',
    'Greedy',
    'Static',
    'Sine',
    'SineLegacy',
    'SineSquared',
    'Square',
    'PointSTM',
    'GainSTM',
    'SilencerConfig',
    'AUTD',
    'SOEM',
    'TwinCAT',
    'RemoteTwinCAT',
    'Emulator',
    'EmulatorLegacy',
    'NUM_TRANS_IN_UNIT',
    'NUM_TRANS_X',
    'NUM_TRANS_Y',
    'TRANS_SPACING_MM',
    'DEVICE_WIDTH',
    'DEVICE_HEIGHT'
]

__version__ = '2.0.3'

_VERSION_TRIPLE = '.'.join(__version__.split('.')[0:3])
_PLATFORM = platform.system()
_TARGET_OS = ''
_ARCH = ''
_PREFIX = ''
_BIN_EXT = ''
_ARCHIVE_EXT = ''
if _PLATFORM == 'Windows':
    _BIN_EXT = '.dll'
    _ARCHIVE_EXT = '.zip'
    _TARGET_OS = 'win'
    _ARCH = 'x64' if platform.machine().endswith('64') else 'x86'
elif _PLATFORM == 'Darwin':
    _PREFIX = 'lib'
    _BIN_EXT = '.dylib'
    _ARCHIVE_EXT = '.tar.gz'
    _TARGET_OS = 'macos'
    _ARCH = 'universal'
elif _PLATFORM == 'Linux':
    _PREFIX = 'lib'
    _BIN_EXT = '.so'
    _ARCHIVE_EXT = '.tar.gz'
    _TARGET_OS = 'linux'
    if platform.machine().startswith('aarch64'):
        _ARCH = 'arm64'
    elif platform.machine().startswith('arm64'):
        _ARCH = 'arm64'
    elif platform.machine().startswith('arm'):
        _ARCH = 'arm32'
    elif platform.machine().endswith('64'):
        _ARCH = 'x64'
    else:
        raise ImportError('Cannot identify CPU architecture')
else:
    raise ImportError('Not supported OS')

_LIB_NAME_BASE = f'{_PREFIX}autd3capi'
_LIB_PATH = os.path.join(os.path.dirname(__file__), 'bin')


def download_bin():
    asset_base_url = 'https://github.com/shinolab/autd3/releases/download/'
    version = f'v{_VERSION_TRIPLE}'

    url = f'{asset_base_url}{version}/autd3-{version}-{_TARGET_OS}-{_ARCH}{_ARCHIVE_EXT}'

    module_path = os.path.dirname(__file__)
    tmp_archive_path = os.path.join(module_path, 'tmp' + _ARCHIVE_EXT)

    res = requests.get(url, stream=True)
    with open(tmp_archive_path, 'wb') as fp:
        shutil.copyfileobj(res.raw, fp)

    if _ARCHIVE_EXT == '.zip':
        with zipfile.ZipFile(tmp_archive_path) as f:
            for info in f.infolist():
                if info.filename.startswith('bin') and info.filename.endswith(_BIN_EXT):
                    f.extract(info, module_path)
    elif _ARCHIVE_EXT == '.tar.gz':
        with tarfile.open(tmp_archive_path) as f:
            libraries = []
            for i in f.getmembers():
                if i.name.startswith('bin') and i.name.endswith(_BIN_EXT):
                    libraries.append(i)
            f.extractall(path=module_path, members=libraries)

    os.remove(tmp_archive_path)


def load_latest_binary():
    if os.path.exists(os.path.join(_LIB_PATH, f'{_LIB_NAME_BASE}-{_VERSION_TRIPLE}{_BIN_EXT}')):
        return

    print('Cannot find latest binaries. Downloading latest binaries...')

    for file in glob.glob(os.path.join(os.path.dirname(__file__), 'bin', '*')):
        if file.endswith(_BIN_EXT):
            try:
                os.remove(file)
            except Exception:
                print(f'Warning: cannot delete old binary ({file})')

    download_bin()

    for file in glob.glob(os.path.join(os.path.dirname(__file__), 'bin', '*')):
        if file.endswith(_BIN_EXT):
            os.rename(file, file.replace(_BIN_EXT, f'-{_VERSION_TRIPLE}{_BIN_EXT}'))
    print('Done')


load_latest_binary()
Base().init_path(_LIB_PATH, _PREFIX, _VERSION_TRIPLE, _BIN_EXT)
GainHolo().init_path(_LIB_PATH, _PREFIX, _VERSION_TRIPLE, _BIN_EXT)
LinkRemoteTwinCAT().init_path(_LIB_PATH, _PREFIX, _VERSION_TRIPLE, _BIN_EXT)
LinkEmulator().init_path(_LIB_PATH, _PREFIX, _VERSION_TRIPLE, _BIN_EXT)
ModulationAudioFile().init_path(_LIB_PATH, _PREFIX, _VERSION_TRIPLE, _BIN_EXT)
BackendCUDA().init_path(_LIB_PATH, _PREFIX, _VERSION_TRIPLE, _BIN_EXT)
LinkSOEM().init_path(_LIB_PATH, _PREFIX, _VERSION_TRIPLE, _BIN_EXT)
LinkTwincAT().init_path(_LIB_PATH, _PREFIX, _VERSION_TRIPLE, _BIN_EXT)
Base().init_dll()
GainHolo().init_dll()
LinkRemoteTwinCAT().init_dll()
LinkEmulator().init_dll()
ModulationAudioFile().init_dll()
if platform.system() == 'Windows':
    LinkTwincAT().init_dll()
