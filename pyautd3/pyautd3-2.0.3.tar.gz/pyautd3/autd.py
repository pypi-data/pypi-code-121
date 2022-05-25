'''
File: autd.py
Project: pyautd3
Created Date: 24/05/2021
Author: Shun Suzuki
-----
Last Modified: 25/05/2022
Modified By: Shun Suzuki (suzuki@hapis.k.u-tokyo.ac.jp)
-----
Copyright (c) 2022 Hapis Lab. All rights reserved.

'''


import ctypes
from ctypes import c_void_p, byref, c_double
import numpy as np

from .native_methods.autd3capi import NativeMethods as Base
from .native_methods.autd3capi_gain_holo import NativeMethods as GainHolo
from .native_methods.autd3capi_link_emulator import NativeMethods as LinkEmulator
from .native_methods.autd3capi_link_remote_twincat import NativeMethods as LinkRemoteTwinCAT
from .native_methods.autd3capi_link_twincat import NativeMethods as LinkTwincAT
from .native_methods.autd3capi_modulation_audio_file import NativeMethods as ModulationAudioFile
from .native_methods.autd3capi_link_soem import NativeMethods as LinkSOEM
from .native_methods.autd3capi_backend_cuda import NativeMethods as BackendCUDA

ErrorHandlerFunc = ctypes.CFUNCTYPE(None, ctypes.c_char_p)

NUM_TRANS_IN_UNIT = 249
NUM_TRANS_X = 18
NUM_TRANS_Y = 14
TRANS_SPACING_MM = 10.16
DEVICE_WIDTH = 192.0
DEVICE_HEIGHT = 151.4


def to_legacy():
    Base().dll.AUTDSetMode(0)
    GainHolo().dll.AUTDSetModeHolo(0)


def to_normal():
    Base().dll.AUTDSetMode(1)
    GainHolo().dll.AUTDSetModeHolo(1)


class Body:
    def __init__(self):
        self.ptr = c_void_p()


class Header:
    def __init__(self):
        self.ptr = c_void_p()


class Gain(Body):
    def __init__(self):
        super().__init__()

    def __del__(self):
        Base().dll.AUTDDeleteGain(self.ptr)


class Focus(Gain):
    def __init__(self, pos, amp: float = 1.0):
        super().__init__()
        Base().dll.AUTDGainFocus(byref(self.ptr), pos[0], pos[1], pos[2], amp)

    def __del__(self):
        super().__del__()


class BesselBeam(Gain):
    def __init__(self, pos, dir, theta_z, amp: float = 1.0):
        super().__init__()
        Base().dll.AUTDGainBesselBeam(byref(self.ptr), pos[0], pos[1], pos[2], dir[0], dir[1], dir[2], theta_z, amp)

    def __del__(self):
        super().__del__()


class PlaneWave(Gain):
    def __init__(self, pos, dir, amp: float = 1.0):
        super().__init__()
        Base().dll.AUTDGainPlaneWave(byref(self.ptr), pos[0], pos[1], pos[2], dir[0], dir[1], dir[2], amp)

    def __del__(self):
        super().__del__()


class CustomGain(Gain):
    def __init__(self, amp, phase):
        super().__init__()
        p_size = len(phase)
        phase = np.ctypeslib.as_ctypes(np.array(phase).astype(np.double))
        amp = np.ctypeslib.as_ctypes(np.array(amp).astype(np.double))
        Base().dll.AUTDGainCustom(byref(self.ptr), amp, phase, p_size)

    def __del__(self):
        super().__del__()


class Null(Gain):
    def __init__(self):
        super().__init__()
        Base().dll.AUTDGainNull(byref(self.ptr))

    def __del__(self):
        super().__del__()


class Backend():
    def __init__(self):
        self.ptr = c_void_p()

    def __del__(self):
        GainHolo().dll.AUTDDeleteBackend(self.ptr)


class EigenBackend(Backend):
    def __init__(self):
        super().__init__()
        GainHolo().dll.AUTDEigenBackend(byref(self.ptr))

    def __del__(self):
        super().__del__()


class CUDABackend(Backend):
    def __init__(self):
        super().__init__()
        BackendCUDA().init_dll()
        BackendCUDA().dll.AUTDCUDABackend(byref(self.ptr))

    def __del__(self):
        super().__del__()


class AmplitudeConstraint():
    def __init__(self, id, value):
        self._id = id
        self.value = None if value is None else c_double(value)

    def id(self):
        return self._id

    def ptr(self):
        return None if self.value is None else byref(self.value)


class DontCare(AmplitudeConstraint):
    def __init__(self):
        super().__init__(0, None)


class Normalize(AmplitudeConstraint):
    def __init__(self):
        super().__init__(1, None)


class Uniform(AmplitudeConstraint):
    def __init__(self, value: float):
        super().__init__(2, value)


class Clamp(AmplitudeConstraint):
    def __init__(self):
        super().__init__(3, None)


class Holo(Gain):
    def __init__(self):
        super().__init__()
        self._constraint = Normalize()

    def __del__(self):
        super().__del__()

    def add(self, focus, amp):
        GainHolo().dll.AUTDGainHoloAdd(self.ptr, focus[0], focus[1], focus[2], amp)

    def amplitude_constraint(self, constraint: AmplitudeConstraint):
        GainHolo().dll.AUTDSetConstraint(self.ptr, constraint.id(), constraint.ptr())


class SDP(Holo):
    def __init__(self, backend: Backend, alpha: float = 1e-3, lambda_: float = 0.9, repeat: int = 100):
        super().__init__()
        GainHolo().dll.AUTDGainHoloSDP(byref(self.ptr), backend.ptr, alpha, lambda_, repeat)

    def __del__(self):
        super().__del__()


class EVD(Holo):
    def __init__(self, backend: Backend, gamma: float = 1.0):
        super().__init__()
        GainHolo().dll.AUTDGainHoloEVD(byref(self.ptr), backend.ptr, gamma)

    def __del__(self):
        super().__del__()


class GS(Holo):
    def __init__(self, backend: Backend, repeat: int = 100):
        super().__init__()
        GainHolo().dll.AUTDGainHoloGS(byref(self.ptr), backend.ptr, repeat)

    def __del__(self):
        super().__del__()


class GSPAT(Holo):
    def __init__(self, backend: Backend, repeat: int = 100):
        super().__init__()
        GainHolo().dll.AUTDGainHoloGSPAT(byref(self.ptr), backend.ptr, repeat)

    def __del__(self):
        super().__del__()


class Naive(Holo):
    def __init__(self, backend: Backend):
        super().__init__()
        GainHolo().dll.AUTDGainHoloNaive(byref(self.ptr), backend.ptr)

    def __del__(self):
        super().__del__()


class LM(Holo):
    def __init__(self, backend: Backend, eps1: float = 1e-8, eps2: float = 1e-8, tau: float = 1e-3,
                 k_max: int = 5, initial=None):
        super().__init__()
        GainHolo().dll.AUTDGainHoloLM(
            byref(self.ptr),
            backend.ptr,
            eps1,
            eps2,
            tau,
            k_max,
            initial,
            0 if initial is None else len(initial))

    def __del__(self):
        super().__del__()


class GaussNewton(Holo):
    def __init__(self, backend: Backend, eps1: float = 1e-6, eps2: float = 1e-6,
                 k_max: int = 500, initial=None):
        super().__init__()
        GainHolo().dll.AUTDGainHoloGaussNewton(
            byref(self.ptr),
            backend.ptr,
            eps1,
            eps2,
            k_max,
            initial,
            0 if initial is None else len(initial))

    def __del__(self):
        super().__del__()


class GradientDescent(Holo):
    def __init__(self, backend: Backend, eps: float = 1e-6, step: float = 0.5,
                 k_max: int = 2000, initial=None):
        super().__init__()
        GainHolo().dll.AUTDGainHoloGradientDescent(
            byref(self.ptr),
            backend.ptr,
            eps,
            step,
            k_max,
            initial,
            0 if initial is None else len(initial))

    def __del__(self):
        super().__del__()


class Greedy(Holo):
    def __init__(self, backend: Backend, phase_div: int = 16):
        super().__init__()
        GainHolo().dll.AUTDGainHoloGreedy(
            byref(self.ptr),
            backend.ptr,
            phase_div)

    def __del__(self):
        super().__del__()


class Modulation(Header):
    def __init__(self):
        super().__init__()

    def __del__(self):
        Base().dll.AUTDDeleteModulation(self.ptr)

    @ property
    def sampling_frequency_division(self):
        return Base().dll.AUTDModulationSamplingFrequencyDivision(self.ptr)

    @ sampling_frequency_division.setter
    def sampling_frequency_division(self, value: int):
        return Base().dll.AUTDModulationSetSamplingFrequencyDivision(self.ptr, value)

    @ property
    def sampling_frequency(self):
        return Base().dll.AUTDModulationSamplingFrequency(self.ptr)


class Static(Modulation):
    def __init__(self, amp: float = 1.0):
        super().__init__()
        Base().dll.AUTDModulationStatic(byref(self.ptr), amp)

    def __del__(self):
        super().__del__()


class CustomModulation(Modulation):
    def __init__(self, data, sampling_freq_div: int):
        super().__init__()
        size = len(data)
        data = np.array(data).astype(np.uint8)
        data = np.ctypeslib.as_ctypes(data)

        Base().dll.AUTDModulationCustom(byref(self.ptr), data, size, sampling_freq_div)

    def __del__(self):
        super().__del__()


class Sine(Modulation):
    def __init__(self, freq: int, amp: float = 1.0, offset: float = 0.5):
        super().__init__()
        Base().dll.AUTDModulationSine(byref(self.ptr), freq, amp, offset)

    def __del__(self):
        super().__del__()


class SineSquared(Modulation):
    def __init__(self, freq: int, amp: float = 1.0, offset: float = 0.5):
        super().__init__()
        Base().dll.AUTDModulationSineSquared(byref(self.ptr), freq, amp, offset)

    def __del__(self):
        super().__del__()


class SineLegacy(Modulation):
    def __init__(self, freq: float, amp: float = 1.0, offset: float = 0.5):
        super().__init__()
        Base().dll.AUTDModulationSineLegacy(byref(self.ptr), freq, amp, offset)

    def __del__(self):
        super().__del__()


class Square(Modulation):
    def __init__(self, freq: int, low: float = 0.0, high: float = 1.0, duty: float = 0.5):
        super().__init__()
        Base().dll.AUTDModulationSquare(byref(self.ptr), freq, low, high, duty)

    def __del__(self):
        super().__del__()


class STM(Body):
    def __init__(self):
        super().__init__()

    def __del__(self):
        Base().dll.AUTDDeleteSTM(self.ptr)

    @ property
    def frequency(self):
        return Base().dll.AUTDSTMFrequency(self.ptr)

    @ frequency.setter
    def frequency(self, freq: float):
        return Base().dll.AUTDSTMSetFrequency(self.ptr, freq)

    @ property
    def sampling_frequency(self):
        return Base().dll.AUTDSTMSamplingFrequency(self.ptr)

    @ property
    def sampling_frequency_division(self):
        return Base().dll.AUTDSTMSamplingFrequencyDivision(self.ptr)

    @ sampling_frequency_division.setter
    def sampling_frequency_division(self, value: int):
        return Base().dll.AUTDSTMSetSamplingFrequencyDivision(self.ptr, value)


class PointSTM(STM):
    def __init__(self):
        super().__init__()
        Base().dll.AUTDPointSTM(byref(self.ptr))

    def __del__(self):
        super().__del__()

    def add(self, point, duty_shift: int = 0):
        return Base().dll.AUTDPointSTMAdd(self.ptr, point[0], point[1], point[2], duty_shift)


class Link:
    def __init__(self):
        self.link_ptr = c_void_p()


class SOEM(Link):
    def __init__(self, ifname: str, dev_num: int, cycle_ticks: int = 2, error_handler=None, high_presicion: bool = True):
        super().__init__()
        error_handler = ErrorHandlerFunc(error_handler) if error_handler is not None else None
        LinkSOEM().init_dll()
        LinkSOEM().dll.AUTDLinkSOEM(byref(self.link_ptr), ifname.encode('mbcs'),
                                    dev_num, cycle_ticks, error_handler, high_presicion)

    @ staticmethod
    def enumerate_adapters():
        LinkSOEM().init_dll()
        res = []
        handle = c_void_p()
        size = LinkSOEM().dll.AUTDGetAdapterPointer(byref(handle))

        for i in range(size):
            sb_desc = ctypes.create_string_buffer(128)
            sb_name = ctypes.create_string_buffer(128)
            LinkSOEM().dll.AUTDGetAdapter(handle, i, sb_desc, sb_name)
            res.append([sb_name.value.decode('mbcs'), sb_desc.value.decode('mbcs')])

        LinkSOEM().dll.AUTDFreeAdapterPointer(handle)

        return res


class TwinCAT(Link):
    def __init__(self, cycle_ticks):
        super().__init__()
        LinkTwincAT().dll.AUTDLinkTwinCAT(byref(self.link_ptr), cycle_ticks)


class RemoteTwinCAT(Link):
    def __init__(self, remote_ip_addr, remote_ams_net_id, local_ams_net_id, cycle_ticks):
        super().__init__()
        LinkRemoteTwinCAT().dll.AUTDLinkRemoteTwinCAT(byref(self.link_ptr), remote_ip_addr.encode('mbcs'),
                                                      remote_ams_net_id.encode('mbcs'),
                                                      local_ams_net_id.encode('mbcs'), cycle_ticks)


class SilencerConfig(Header):
    def __init__(self, step: int = 10, cycle: int = 4096):
        super().__init__()
        Base().dll.AUTDCreateSilencer(byref(self.ptr), step, cycle)

    def __del__(self):
        Base().dll.AUTDDeleteSilencer(self.ptr)

    @staticmethod
    def none():
        return SilencerConfig(0xFFFF, 4096)


class AUTD:
    def __init__(self):
        self.p_cnt = c_void_p()
        Base().dll.AUTDCreateController(byref(self.p_cnt))
        self.__disposed = False

    def __del__(self):
        self.dispose()

    def last_error():
        size = Base().dll.AUTDGetLastError(None)
        err = ctypes.create_string_buffer(size)
        Base().dll.AUTDGetLastError(err)
        return err.value.decode('mbcs')

    def open(self, link: Link):
        return Base().dll.AUTDOpenController(self.p_cnt, link.link_ptr)

    def firmware_info_list(self):
        res = []
        handle = c_void_p()
        size = Base().dll.AUTDGetFirmwareInfoListPointer(self.p_cnt, byref(handle))

        for i in range(size):
            sb = ctypes.create_string_buffer(256)
            Base().dll.AUTDGetFirmwareInfo(handle, i, sb)
            res.append(sb.value.decode('mbcs'))

        Base().dll.AUTDFreeFirmwareInfoListPointer(handle)

        return res

    def dispose(self):
        if not self.__disposed:
            self.close()
            self._free()
            self.__disposed = True

    def add_device(self, pos, rot):
        return Base().dll.AUTDAddDevice(self.p_cnt, pos[0], pos[1], pos[2], rot[0], rot[1], rot[2])

    def add_device_quaternion(self, pos, q):
        return Base().dll.AUTDAddDeviceQuaternion(self.p_cnt, pos[0], pos[1], pos[2], q[0], q[1], q[2], q[3])

    def stop(self):
        return Base().dll.AUTDStop(self.p_cnt)

    def synchronize(self):
        return Base().dll.AUTDSynchronize(self.p_cnt)

    def close(self):
        return Base().dll.AUTDClose(self.p_cnt)

    def clear(self):
        return Base().dll.AUTDClear(self.p_cnt)

    def update_flags(self):
        return Base().dll.AUTDUpdateFlags(self.p_cnt)

    def _free(self):
        Base().dll.AUTDFreeController(self.p_cnt)

    @ property
    def is_open(self):
        return Base().dll.AUTDIsOpen(self.p_cnt)

    @ property
    def force_fan(self):
        return Base().dll.AUTDGetForceFan(self.p_cnt)

    @ force_fan.setter
    def force_fan(self, value: bool):
        return Base().dll.AUTDSetForceFan(self.p_cnt, value)

    @ property
    def check_ack(self):
        return Base().dll.AUTDGetCheckAck(self.p_cnt)

    @ check_ack.setter
    def check_ack(self, value: bool):
        return Base().dll.AUTDSetCheckAck(self.p_cnt, value)

    @ property
    def sound_speed(self):
        return Base().dll.AUTDGetSoundSpeed(self.p_cnt)

    @ sound_speed.setter
    def sound_speed(self, sound_speed: float):
        Base().dll.AUTDSetSoundSpeed(self.p_cnt, sound_speed)

    @ property
    def attenuation(self):
        return Base().dll.AUTDGetAttenuation(self.p_cnt)

    @ attenuation.setter
    def attenuation(self, attenuation: float):
        Base().dll.AUTDSetAttenuation(self.p_cnt, attenuation)

    @ property
    def reads_fpga_info(self):
        Base().dll.AUTDGetReadsFPGAInfo(self.p_cnt)

    @ reads_fpga_info.setter
    def reads_fpga_info(self, value: bool):
        Base().dll.AUTDSetReadsFPGAInfo(self.p_cnt, value)

    @ property
    def fpga_info(self):
        infos = np.zeros([self.num_devices()]).astype(np.ubyte)
        pinfos = np.ctypeslib.as_ctypes(infos)
        Base().dll.AUTDGetFPGAInfo(self.p_cnt, pinfos)
        return infos

    def num_devices(self):
        return Base().dll.AUTDNumDevices(self.p_cnt)

    def send(self, a, b=None):
        if b is None and isinstance(a, Header):
            return Base().dll.AUTDSendHeader(self.p_cnt, a.ptr)
        if b is None and isinstance(a, Body):
            return Base().dll.AUTDSendBody(self.p_cnt, a.ptr)
        if isinstance(a, Header) and isinstance(b, Body):
            return Base().dll.AUTDSendHeaderBody(self.p_cnt, a.ptr, b.ptr)
        raise NotImplementedError()

    def trans_pos(self, dev_idx: int, trans_idx_local: int):
        x = c_double(0.0)
        y = c_double(0.0)
        z = c_double(0.0)
        Base().dll.AUTDTransPosition(self.p_cnt, dev_idx, trans_idx_local, byref(x), byref(y), byref(z))
        return np.array([x.value, y.value, z.value])

    def trans_frequency(self, dev_idx: int, trans_idx_local: int):
        return Base().dll.AUTDGetTransFrequency(self.p_cnt, dev_idx, trans_idx_local)

    def set_trans_frequency(self, dev_idx: int, trans_idx_local: int, freq: float):
        return Base().dll.AUTDSetTransFrequency(self.p_cnt, dev_idx, trans_idx_local, freq)

    def trans_cycle(self, dev_idx: int, trans_idx_local: int):
        return Base().dll.AUTDGetTransCycle(self.p_cnt, dev_idx, trans_idx_local)

    def set_trans_cycle(self, dev_idx: int, trans_idx_local: int, cycle: int):
        return Base().dll.AUTDSetTransCycle(self.p_cnt, dev_idx, trans_idx_local, cycle)

    def wavelength(self, dev_idx: int, trans_idx_local: int, sound_speed: float):
        return Base().dll.AUTDGetWavelength(self.p_cnt, dev_idx, trans_idx_local, sound_speed)

    def trans_direction_x(self, dev_idx: int, trans_idx_local: int):
        x = c_double(0.0)
        y = c_double(0.0)
        z = c_double(0.0)
        Base().dll.AUTDTransXDirection(self.p_cnt, dev_idx, trans_idx_local, byref(x), byref(y), byref(z))
        return np.array([x.value, y.value, z.value])

    def trans_direction_y(self, dev_idx: int, trans_idx_local: int):
        x = c_double(0.0)
        y = c_double(0.0)
        z = c_double(0.0)
        Base().dll.AUTDTransYDirection(self.p_cnt, dev_idx, trans_idx_local, byref(x), byref(y), byref(z))
        return np.array([x.value, y.value, z.value])

    def trans_direction_z(self, dev_idx: int, trans_idx_local: int):
        x = c_double(0.0)
        y = c_double(0.0)
        z = c_double(0.0)
        Base().dll.AUTDTransZDirection(self.p_cnt, dev_idx, trans_idx_local, byref(x), byref(y), byref(z))
        return np.array([x.value, y.value, z.value])


class Grouped(Gain):
    def __init__(self, autd: AUTD):
        super().__init__()
        Base().dll.AUTDGainGrouped(byref(self.ptr), autd.p_cnt)

    def __del__(self):
        super().__del__()

    def add(self, dev_idx: int, gain: Gain):
        Base().dll.AUTDGainGroupedAdd(self.ptr, dev_idx, gain.ptr)


class GainSTM(STM):
    def __init__(self, autd: AUTD):
        super().__init__()
        Base().dll.AUTDGainSTM(byref(self.ptr), autd.p_cnt)

    def __del__(self):
        super().__del__()

    def add(self, gain: Gain):
        return Base().dll.AUTDGainSTMAdd(self.ptr, gain.ptr)


class Emulator(Link):
    def __init__(self, port: int, autd: AUTD):
        super().__init__()
        LinkEmulator().dll.AUTDLinkEmulator(byref(self.link_ptr), port, autd.p_cnt)


class RawPCM(Modulation):
    def __init__(self, path: str, sampling_freq: float, mod_freq_div: int):
        super().__init__()
        ModulationAudioFile().dll.AUTDModulationRawPCM(byref(self.ptr), path.encode('mbcs'), sampling_freq, mod_freq_div)

    def __del__(self):
        super().__del__()


class Wav(Modulation):
    def __init__(self, path: str, mod_freq_div: int):
        super().__init__()
        ModulationAudioFile().dll.AUTDModulationWav(byref(self.ptr), path.encode('mbcs'), mod_freq_div)

    def __del__(self):
        super().__del__()
