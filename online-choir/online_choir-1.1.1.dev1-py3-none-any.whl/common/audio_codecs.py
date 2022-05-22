import audioop
import numpy as np
import struct
from typing import Tuple

from ..common.constants import FRAME_SIZE, BYTE_ENCODING
from ..common.log import logger
from ..common.utils import my_assert

_PRIME_IDX_MULTIPLIER = 199


class AudioEncoder:
    def __init__(self):
        self.next_index = 0

    def __call__(self, sig: np.array) -> bytes:
        return self.create_frame(self._encode_signal(sig))

    def create_frame(self, payload) -> bytes:
        prefix = self._prefix(self.next_index)
        self.next_index += 1
        return prefix + payload

    def _encode_signal(self, sig: np.array) -> bytes:
        my_assert(sig.shape == (FRAME_SIZE,), "wrong signal shape")
        digitalized = sig * 32768
        if digitalized.max() > 32767 or digitalized.min() < -32768:
            logger.warning("Saturation!")
            np.clip(digitalized, -32768, 32767, out=digitalized)
        np.rint(digitalized, out=digitalized)
        return digitalized.astype(BYTE_ENCODING).tobytes()

    @staticmethod
    def _prefix(idx: int):
        return struct.pack("!i", _PRIME_IDX_MULTIPLIER * idx)

    @staticmethod
    def silence_frame(idx: int) -> bytes:
        return AudioEncoder._prefix(idx) + b'\x00' * 1024


class AdpcmEncoder(AudioEncoder):
    def __init__(self):
        super().__init__()
        self._state = None

    def _encode_signal(self, sig: np.array) -> bytes:
        lin = super(AdpcmEncoder, self)._encode_signal(sig)
        comp, self._state = audioop.lin2adpcm(lin, 2, self._state)
        return comp

    @staticmethod
    def silence_frame(idx: int) -> bytes:
        return AudioEncoder._prefix(idx) + b'\x00' * 256


class StereoEncoder(AudioEncoder):
    def __init__(self):
        super().__init__()
        self._state_left = None
        self._state_right = None

    def _encode_signal(self, sig: np.array) -> bytes:
        my_assert(sig.shape == (FRAME_SIZE, 2), "Wrong signal shape")
        left = super(StereoEncoder, self)._encode_signal(sig[:, 0])
        right = super(StereoEncoder, self)._encode_signal(sig[:, 1])
        comp_left, self._state_left = audioop.lin2adpcm(left, 2, self._state_left)
        comp_right, self._state_right = audioop.lin2adpcm(right, 2, self._state_right)
        return comp_left + comp_right

    @staticmethod
    def silence_frame(idx: int) -> bytes:
        return AudioEncoder._prefix(idx) + b'\x00' * 512


class AudioDecoder:
    PACKET_SIZE = 1028

    def __init__(self, next_index: int = 0):
        self.next_index = next_index

    def __call__(self, data: bytes, array: np.ndarray):
        self._check_input(data)
        self._to_array(data, array, 4)

    def _check_input(self, data: bytes):
        my_assert(len(data) == self.PACKET_SIZE, "wrong data length")
        idx = self.peek_frame_index(data)
        my_assert(idx == self.next_index, f"Expected frame {self.next_index} got {idx}")
        self.next_index = idx + 1

    @staticmethod
    def _to_array(data: bytes, array: np.ndarray, offset: int):
        my_assert(array.shape == (FRAME_SIZE,), "wrong signal shape")
        array[:] = np.frombuffer(data, offset=offset, dtype=BYTE_ENCODING) / 32768

    @staticmethod
    def peek_frame_index(data: bytes) -> int:
        n, = struct.unpack("!i", data[:4])
        my_assert(n % _PRIME_IDX_MULTIPLIER == 0, "Invalid data chunk")
        return n // _PRIME_IDX_MULTIPLIER


class AdpcmDecoder(AudioDecoder):
    PACKET_SIZE = 260

    def __init__(self, next_index: int = 0):
        super().__init__(next_index)
        self._state = None

    def __call__(self, data: bytes, array: np.ndarray):
        lin = self.decompress(data, 2)
        self._to_array(lin, array, 0)

    def decompress(self, data: bytes, depth=2) -> bytes:
        self._check_input(data)
        lin, self._state = audioop.adpcm2lin(data[4:], depth, self._state)
        return lin


class StereoDecoder(AudioDecoder):
    PACKET_SIZE = 516

    def __init__(self, next_index: int = 0):
        super().__init__(next_index)
        self._state_left = None
        self._state_right = None

    def __call__(self, data: bytes, array: np.ndarray):
        my_assert(array.shape == (FRAME_SIZE, 2), "wrong signal shape")
        left, right = self.decode_left_right(data)
        array[:, 0] = np.frombuffer(left, dtype=BYTE_ENCODING) / 32768
        array[:, 1] = np.frombuffer(right, dtype=BYTE_ENCODING) / 32768

    def decode_left_right(self, data: bytes, depth=2) -> Tuple[bytes, bytes]:
        self._check_input(data)
        left, self._state_left = audioop.adpcm2lin(data[4:260], depth, self._state_left)
        right, self._state_right = audioop.adpcm2lin(data[260:], depth, self._state_right)
        return left, right
