'''
File: native_methods.py
Project: pyautd3
Created Date: 05/06/2021
Author: Shun Suzuki
-----
Last Modified: 23/05/2022
Modified By: Shun Suzuki (suzuki@hapis.k.u-tokyo.ac.jp)
-----
Copyright (c) 2022 Hapis Lab. All rights reserved.

'''

import threading
import ctypes
import os
from ctypes import c_uint32, c_void_p, c_bool, c_int, POINTER, c_double, c_char_p, c_ubyte, c_uint, c_ulong, c_ushort, CFUNCTYPE

ErrorHandlerFunc = CFUNCTYPE(None, c_char_p)


class Singleton(type):
    _instances = {}
    _lock = threading.Lock()

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            with cls._lock:
                if cls not in cls._instances:
                    cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class Nativemethods(metaclass=Singleton):
    def init_path(self, bin_location: str, bin_prefix: str, version_triple: str, bin_ext: str):
        self._bin_path = bin_location
        self._prefix = bin_prefix
        self._version = version_triple
        self._ext = bin_ext

    def init_dll(self, legacy: bool):
        self._legacy = legacy

    def init_autd3capi(self):
        if self._legacy:
            self.autd3capi = ctypes.CDLL(os.path.join(self._bin_path,
                                                      f'{self._prefix}autd3capi-{self._version}-legacy{self._ext}'))
        else:
            self.autd3capi = ctypes.CDLL(os.path.join(self._bin_path, f'{self._prefix}autd3capi-{self._version}{self._ext}'))

        self.autd3capi.AUTDGetLastError.argtypes = [c_char_p]
        self.autd3capi.AUTDGetLastError.restype = c_int

        self.autd3capi.AUTDCreateController.argtypes = [POINTER(c_void_p)]
        self.autd3capi.AUTDCreateController.restype = None

        self.autd3capi.AUTDOpenController.argtypes = [c_void_p, c_void_p]
        self.autd3capi.AUTDOpenController.restype = c_bool

        self.autd3capi.AUTDAddDevice.argtypes = [c_void_p, c_double, c_double, c_double, c_double, c_double, c_double]
        self.autd3capi.AUTDAddDevice.restype = c_int

        self.autd3capi.AUTDAddDeviceQuaternion.argtypes = [c_void_p, c_double, c_double, c_double, c_double, c_double, c_double, c_double]
        self.autd3capi.AUTDAddDeviceQuaternion.restype = c_int

        self.autd3capi.AUTDClose.argtypes = [c_void_p]
        self.autd3capi.AUTDClose.restype = c_int

        self.autd3capi.AUTDClear.argtypes = [c_void_p]
        self.autd3capi.AUTDClear.restype = c_int

        self.autd3capi.AUTDSynchronize.argtypes = [c_void_p]
        self.autd3capi.AUTDSynchronize.restype = c_int

        self.autd3capi.AUTDFreeController.argtypes = [c_void_p]
        self.autd3capi.AUTDFreeController.restype = None

        self.autd3capi.AUTDIsOpen.argtypes = [c_void_p]
        self.autd3capi.AUTDIsOpen.restype = c_bool

        self.autd3capi.AUTDGetForceFan.argtypes = [c_void_p]
        self.autd3capi.AUTDGetForceFan.restype = c_bool

        self.autd3capi.AUTDGetReadsFPGAInfo.argtypes = [c_void_p]
        self.autd3capi.AUTDGetReadsFPGAInfo.restype = c_bool

        self.autd3capi.AUTDGetCheckAck.argtypes = [c_void_p]
        self.autd3capi.AUTDGetCheckAck.restype = c_bool

        self.autd3capi.AUTDSetReadsFPGAInfo.argtypes = [c_void_p, c_bool]
        self.autd3capi.AUTDSetReadsFPGAInfo.restype = None

        self.autd3capi.AUTDSetCheckAck.argtypes = [c_void_p, c_bool]
        self.autd3capi.AUTDSetCheckAck.restype = None

        self.autd3capi.AUTDSetForceFan.argtypes = [c_void_p, c_bool]
        self.autd3capi.AUTDSetForceFan.restype = None

        self.autd3capi.AUTDGetSoundSpeed.argtypes = [c_void_p]
        self.autd3capi.AUTDGetSoundSpeed.restype = c_double

        self.autd3capi.AUTDSetSoundSpeed.argtypes = [c_void_p, c_double]
        self.autd3capi.AUTDSetSoundSpeed.restype = None

        self.autd3capi.AUTDGetTransFrequency.argtypes = [c_void_p, c_int, c_int]
        self.autd3capi.AUTDGetTransFrequency.restype = c_double

        self.autd3capi.AUTDSetTransFrequency.argtypes = [c_void_p, c_int, c_int, c_double]
        self.autd3capi.AUTDSetTransFrequency.restype = None

        self.autd3capi.AUTDGetTransCycle.argtypes = [c_void_p, c_int, c_int]
        self.autd3capi.AUTDGetTransCycle.restype = c_ushort

        self.autd3capi.AUTDSetTransCycle.argtypes = [c_void_p, c_int, c_int, c_ushort]
        self.autd3capi.AUTDSetTransCycle.restype = None

        self.autd3capi.AUTDGetWavelength.argtypes = [c_void_p, c_int, c_int, c_double]
        self.autd3capi.AUTDGetWavelength.restype = c_double

        self.autd3capi.AUTDGetAttenuation.argtypes = [c_void_p]
        self.autd3capi.AUTDGetAttenuation.restype = c_double

        self.autd3capi.AUTDSetAttenuation.argtypes = [c_void_p, c_double]
        self.autd3capi.AUTDSetAttenuation.restype = None

        self.autd3capi.AUTDGetFPGAInfo.argtypes = [c_void_p, POINTER(c_ubyte)]
        self.autd3capi.AUTDGetFPGAInfo.restype = c_bool

        self.autd3capi.AUTDUpdateFlags.argtypes = [c_void_p]
        self.autd3capi.AUTDUpdateFlags.restype = c_int

        self.autd3capi.AUTDNumDevices.argtypes = [c_void_p]
        self.autd3capi.AUTDNumDevices.restype = c_int

        self.autd3capi.AUTDTransPosition.argtypes = [c_void_p, c_int, c_int, POINTER(c_double), POINTER(c_double), POINTER(c_double)]
        self.autd3capi.AUTDTransPosition.restype = None

        self.autd3capi.AUTDTransXDirection.argtypes = [c_void_p, c_int, c_int, POINTER(c_double), POINTER(c_double), POINTER(c_double)]
        self.autd3capi.AUTDTransXDirection.restype = None

        self.autd3capi.AUTDTransXDirection.argtypes = [c_void_p, c_int, c_int, POINTER(c_double), POINTER(c_double), POINTER(c_double)]
        self.autd3capi.AUTDTransXDirection.restype = None

        self.autd3capi.AUTDTransZDirection.argtypes = [c_void_p, c_int, c_int, POINTER(c_double), POINTER(c_double), POINTER(c_double)]
        self.autd3capi.AUTDTransZDirection.restype = None

        self.autd3capi.AUTDGetFirmwareInfoListPointer.argtypes = [c_void_p, POINTER(c_void_p)]
        self.autd3capi.AUTDGetFirmwareInfoListPointer.restype = c_int

        self.autd3capi.AUTDGetFirmwareInfo.argtypes = [c_void_p, c_int, c_char_p]
        self.autd3capi.AUTDGetFirmwareInfo.restype = None

        self.autd3capi.AUTDFreeFirmwareInfoListPointer.argtypes = [c_void_p]
        self.autd3capi.AUTDFreeFirmwareInfoListPointer.restype = None

        self.autd3capi.AUTDGainNull.argtypes = [POINTER(c_void_p)]
        self.autd3capi.AUTDGainNull.restype = None

        self.autd3capi.AUTDGainGrouped.argtypes = [POINTER(c_void_p), c_void_p]
        self.autd3capi.AUTDGainGrouped.restype = None

        self.autd3capi.AUTDGainGroupedAdd.argtypes = [c_void_p, c_int, c_void_p]
        self.autd3capi.AUTDGainGroupedAdd.restype = None

        self.autd3capi.AUTDGainFocus.argtypes = [POINTER(c_void_p), c_double, c_double, c_double, c_double]
        self.autd3capi.AUTDGainFocus.restype = None

        self.autd3capi.AUTDGainBesselBeam.argtypes = [
            POINTER(c_void_p),
            c_double,
            c_double,
            c_double,
            c_double,
            c_double,
            c_double,
            c_double,
            c_double]
        self.autd3capi.AUTDGainBesselBeam.restype = None

        self.autd3capi.AUTDGainPlaneWave.argtypes = [POINTER(c_void_p), c_double, c_double, c_double, c_double]
        self.autd3capi.AUTDGainPlaneWave.restype = None

        self.autd3capi.AUTDGainCustom.argtypes = [POINTER(c_void_p), POINTER(c_double), POINTER(c_double), c_ulong]
        self.autd3capi.AUTDGainCustom.restype = None

        self.autd3capi.AUTDDeleteGain.argtypes = [c_void_p]
        self.autd3capi.AUTDDeleteGain.restype = None

        self.autd3capi.AUTDModulationStatic.argtypes = [POINTER(c_void_p), c_double]
        self.autd3capi.AUTDModulationStatic.restype = None

        self.autd3capi.AUTDModulationCustom.argtypes = [POINTER(c_void_p), POINTER(c_ubyte), c_ulong, c_uint]
        self.autd3capi.AUTDModulationCustom.restype = None

        self.autd3capi.AUTDModulationSine.argtypes = [POINTER(c_void_p), c_int, c_double, c_double]
        self.autd3capi.AUTDModulationSine.restype = None

        self.autd3capi.AUTDModulationSineSquared.argtypes = [POINTER(c_void_p), c_int, c_double, c_double]
        self.autd3capi.AUTDModulationSineSquared.restype = None

        self.autd3capi.AUTDModulationSineLegacy.argtypes = [POINTER(c_void_p), c_double, c_double, c_double]
        self.autd3capi.AUTDModulationSineLegacy.restype = None

        self.autd3capi.AUTDModulationSquare.argtypes = [POINTER(c_void_p), c_int, c_double, c_double, c_double]
        self.autd3capi.AUTDModulationSquare.restype = None

        self.autd3capi.AUTDModulationSamplingFrequencyDivision.argtypes = [c_void_p]
        self.autd3capi.AUTDModulationSamplingFrequencyDivision.restype = c_uint

        self.autd3capi.AUTDModulationSetSamplingFrequencyDivision.argtypes = [c_void_p, c_uint]
        self.autd3capi.AUTDModulationSetSamplingFrequencyDivision.restype = None

        self.autd3capi.AUTDModulationSamplingFrequency.argtypes = [c_void_p]
        self.autd3capi.AUTDModulationSamplingFrequency.restype = c_double

        self.autd3capi.AUTDDeleteModulation.argtypes = [c_void_p]
        self.autd3capi.AUTDDeleteModulation.restype = None

        self.autd3capi.AUTDPointSTM.argtypes = [POINTER(c_void_p)]
        self.autd3capi.AUTDPointSTM.restype = None

        self.autd3capi.AUTDGainSTM.argtypes = [POINTER(c_void_p), c_void_p]
        self.autd3capi.AUTDGainSTM.restype = None

        self.autd3capi.AUTDPointSTMAdd.argtypes = [c_void_p, c_double, c_double, c_double, c_ubyte]
        self.autd3capi.AUTDPointSTMAdd.restype = c_bool

        self.autd3capi.AUTDGainSTMAdd.argtypes = [c_void_p, c_void_p]
        self.autd3capi.AUTDGainSTMAdd.restype = c_bool

        self.autd3capi.AUTDSTMSetFrequency.argtypes = [c_void_p, c_double]
        self.autd3capi.AUTDSTMSetFrequency.restype = c_double

        self.autd3capi.AUTDSTMFrequency.argtypes = [c_void_p]
        self.autd3capi.AUTDSTMFrequency.restype = c_double

        self.autd3capi.AUTDSTMSamplingFrequency.argtypes = [c_void_p]
        self.autd3capi.AUTDSTMSamplingFrequency.restype = c_double

        self.autd3capi.AUTDSTMSamplingFrequencyDivision.argtypes = [c_void_p]
        self.autd3capi.AUTDSTMSamplingFrequencyDivision.restype = c_uint32

        self.autd3capi.AUTDSTMSetSamplingFrequencyDivision.argtypes = [c_void_p, c_uint32]
        self.autd3capi.AUTDSTMSetSamplingFrequencyDivision.restype = None

        self.autd3capi.AUTDDeleteSTM.argtypes = [c_void_p]
        self.autd3capi.AUTDDeleteSTM.restype = None

        self.autd3capi.AUTDStop.argtypes = [c_void_p]
        self.autd3capi.AUTDStop.restype = c_int

        self.autd3capi.AUTDCreateSilencer.argtypes = [POINTER(c_void_p), c_ushort, c_ushort]
        self.autd3capi.AUTDCreateSilencer.restype = None

        self.autd3capi.AUTDDeleteSilencer.argtypes = [c_void_p]
        self.autd3capi.AUTDDeleteSilencer.restype = None

        self.autd3capi.AUTDSendHeader.argtypes = [c_void_p, c_void_p]
        self.autd3capi.AUTDSendHeader.restype = c_int

        self.autd3capi.AUTDSendBody.argtypes = [c_void_p, c_void_p]
        self.autd3capi.AUTDSendBody.restype = c_int

        self.autd3capi.AUTDSendHeaderBody.argtypes = [c_void_p, c_void_p, c_void_p]
        self.autd3capi.AUTDSendHeaderBody.restype = c_int

    def init_autd3capi_gain_holo(self):
        if self._legacy:
            self.autd3capi_gain_holo = ctypes.CDLL(os.path.join(self._bin_path,
                                                                f'{self._prefix}autd3capi-{self._version}-gain-holo-legacy{self._ext}'))
        else:
            self.autd3capi_gain_holo = ctypes.CDLL(os.path.join(self._bin_path,
                                                                f'{self._prefix}autd3capi-{self._version}-gain-holo{self._ext}'))

        self.autd3capi_gain_holo.AUTDEigenBackend.argtypes = [POINTER(c_void_p)]
        self.autd3capi_gain_holo.AUTDEigenBackend.restype = None

        self.autd3capi_gain_holo.AUTDDeleteBackend.argtypes = [c_void_p]
        self.autd3capi_gain_holo.AUTDDeleteBackend.restype = None

        self.autd3capi_gain_holo.AUTDAmplitudeConstraintDontCate.argtypes = [POINTER(c_void_p)]
        self.autd3capi_gain_holo.AUTDAmplitudeConstraintDontCate.restype = None

        self.autd3capi_gain_holo.AUTDAmplitudeConstraintNormalize.argtypes = [POINTER(c_void_p)]
        self.autd3capi_gain_holo.AUTDAmplitudeConstraintNormalize.restype = None

        self.autd3capi_gain_holo.AUTDAmplitudeConstraintUniform.argtypes = [POINTER(c_void_p), c_double]
        self.autd3capi_gain_holo.AUTDAmplitudeConstraintUniform.restype = None

        self.autd3capi_gain_holo.AUTDAmplitudeConstraintClamp.argtypes = [POINTER(c_void_p)]
        self.autd3capi_gain_holo.AUTDAmplitudeConstraintClamp.restype = None

        self.autd3capi_gain_holo.AUTDDeleteAmplitudeConstraint.argtypes = [c_void_p]
        self.autd3capi_gain_holo.AUTDDeleteAmplitudeConstraint.restype = None

        self.autd3capi_gain_holo.AUTDGainHoloSDP.argtypes = [POINTER(c_void_p), c_void_p, c_double, c_double, c_ulong, c_void_p]
        self.autd3capi_gain_holo.AUTDGainHoloSDP.restype = None

        self.autd3capi_gain_holo.AUTDGainHoloEVD.argtypes = [POINTER(c_void_p), c_void_p, c_double, c_void_p]
        self.autd3capi_gain_holo.AUTDGainHoloEVD.restype = None

        self.autd3capi_gain_holo.AUTDGainHoloNaive.argtypes = [POINTER(c_void_p), c_void_p, c_void_p]
        self.autd3capi_gain_holo.AUTDGainHoloNaive.restype = None

        self.autd3capi_gain_holo.AUTDGainHoloGS.argtypes = [POINTER(c_void_p), c_void_p, c_ulong, c_void_p]
        self.autd3capi_gain_holo.AUTDGainHoloGS.restype = None

        self.autd3capi_gain_holo.AUTDGainHoloGSPAT.argtypes = [POINTER(c_void_p), c_void_p, c_ulong, c_void_p]
        self.autd3capi_gain_holo.AUTDGainHoloGSPAT.restype = None

        self.autd3capi_gain_holo.AUTDGainHoloLM.argtypes = [
            POINTER(c_void_p),
            c_void_p,
            c_double,
            c_double,
            c_double,
            c_ulong,
            POINTER(c_double),
            c_int,
            c_void_p]
        self.autd3capi_gain_holo.AUTDGainHoloLM.restype = None

        self.autd3capi_gain_holo.AUTDGainHoloGaussNewton.argtypes = [
            POINTER(c_void_p), c_void_p, c_double, c_double, c_ulong, POINTER(c_double), c_int, c_void_p]
        self.autd3capi_gain_holo.AUTDGainHoloGaussNewton.restype = None

        self.autd3capi_gain_holo.AUTDGainHoloGradientDescent.argtypes = [
            POINTER(c_void_p), c_void_p, c_double, c_double, c_ulong, POINTER(c_double), c_int, c_void_p]
        self.autd3capi_gain_holo.AUTDGainHoloGradientDescent.restype = None

        self.autd3capi_gain_holo.AUTDGainHoloGreedy.argtypes = [POINTER(c_void_p), c_void_p, c_int, c_void_p]
        self.autd3capi_gain_holo.AUTDGainHoloGreedy.restype = None

        self.autd3capi_gain_holo.AUTDGainHoloAdd.argtypes = [c_void_p, c_double, c_double, c_double, c_double]
        self.autd3capi_gain_holo.AUTDGainHoloAdd.restype = None

    def init_autd3capi_link_remote_twincat(self):
        self.autd3capi_link_remote_twincat = ctypes.CDLL(os.path.join(self._bin_path,
                                                                      f'{self._prefix}autd3capi-{self._version}-link-remote-twincat{self._ext}'))

        self.autd3capi_link_remote_twincat.AUTDLinkRemoteTwinCAT.argtypes = [POINTER(c_void_p), c_char_p, c_char_p, c_char_p, c_ushort]
        self.autd3capi_link_remote_twincat.AUTDLinkRemoteTwinCAT.restype = None

    def init_autd3capi_link_emulator(self):
        self.autd3capi_link_emulator = ctypes.CDLL(os.path.join(self._bin_path,
                                                                f'{self._prefix}autd3capi-{self._version}-link-emulator{self._ext}'))

        self.autd3capi_link_emulator.AUTDLinkEmulator.argtypes = [POINTER(c_void_p), c_ushort, c_void_p]
        self.autd3capi_link_emulator.AUTDLinkEmulator.restype = None

        self.autd3capi_link_emulator.AUTDLinkEmulatorLegacy.argtypes = [POINTER(c_void_p), c_ushort, c_void_p]
        self.autd3capi_link_emulator.AUTDLinkEmulatorLegacy.restype = None

    def init_autd3capi_modulation_audio_file(self):
        self.autd3capi_modulation_audio_file = ctypes.CDLL(os.path.join(self._bin_path,
                                                                        f'{self._prefix}autd3capi-{self._version}-modulation-audio-file{self._ext}'))

        self.autd3capi_modulation_audio_file.AUTDModulationRawPCM.argtypes = [POINTER(c_void_p), c_char_p, c_double, c_uint]
        self.autd3capi_modulation_audio_file.AUTDModulationRawPCM.restype = None

        self.autd3capi_modulation_audio_file.AUTDModulationWav.argtypes = [POINTER(c_void_p), c_char_p, c_uint]
        self.autd3capi_modulation_audio_file.AUTDModulationWav.restype = None

    def init_autd3capi_link_soem(self):
        if hasattr(self, 'autd3capi_link_soem'):
            return
        self.autd3capi_link_soem = ctypes.CDLL(os.path.join(self._bin_path, f'{self._prefix}autd3capi-{self._version}-link-soem{self._ext}'))

        self.autd3capi_link_soem.AUTDGetAdapterPointer.argtypes = [POINTER(c_void_p)]
        self.autd3capi_link_soem.AUTDGetAdapterPointer.restype = c_int

        self.autd3capi_link_soem.AUTDGetAdapter.argtypes = [c_void_p, c_int, c_char_p, c_char_p]
        self.autd3capi_link_soem.AUTDGetAdapter.restype = None

        self.autd3capi_link_soem.AUTDFreeAdapterPointer.argtypes = [c_void_p]
        self.autd3capi_link_soem.AUTDFreeAdapterPointer.restype = None

        self.autd3capi_link_soem.AUTDLinkSOEM.argtypes = [POINTER(c_void_p), c_char_p, c_int, c_ushort, c_void_p, c_bool]
        self.autd3capi_link_soem.AUTDLinkSOEM.restype = None

    def init_autd3capi_link_twincat(self):
        self.autd3capi_link_twincat = ctypes.CDLL(os.path.join(self._bin_path, f'{self._prefix}autd3capi-{self._version}-link-twincat{self._ext}'))

        self.autd3capi_link_twincat.AUTDLinkTwinCAT.argtypes = [POINTER(c_void_p), c_ushort]
        self.autd3capi_link_twincat.AUTDLinkTwinCAT.restype = None

    def init_autd3capi_backend_cuda(self):

        self.autd3capi_backend_cuda = ctypes.CDLL(os.path.join(self._bin_path, f'{self._prefix}autd3capi-{self._version}-backend-cuda{self._ext}'))

        self.autd3capi_backend_cuda.AUTDCUDABackend.argtypes = [POINTER(c_void_p)]
        self.autd3capi_backend_cuda.AUTDCUDABackend.restype = None
