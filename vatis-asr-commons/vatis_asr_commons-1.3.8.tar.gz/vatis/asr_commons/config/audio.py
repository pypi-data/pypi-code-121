from enum import Enum
from typing import Optional, Dict, Union

from vatis.asr_commons.domain import AudioFormatError


class Language(Enum):
    ro_RO = 'ro_RO'
    en_GB = 'en_GB'


class SampleRate(Enum):
    RATE_16000 = 16000


class Channel(Enum):
    ONE = 1


class BitDepth(Enum):
    BIT_16 = 16


class AudioFormat(Enum):
    WAV = 'wav'
    WEBM = 'webm'


class AudioAttributes:
    def __init__(self, sample_rate: Optional[Union[int, SampleRate]] = None,
                 bit_rate: Optional[int] = None,
                 bit_depth: Optional[Union[int, BitDepth]] = None,
                 audio_format: Optional[Union[str, AudioFormat]] = None,
                 sending_headers: bool = False,
                 channels: Optional[Union[int, Channel]] = None,
                 codec: Optional[str] = None, **kwargs):
        self.sample_rate: Optional[int] = sample_rate.value if isinstance(sample_rate, SampleRate) else sample_rate
        self.bit_rate: Optional[int] = bit_rate
        self.bit_depth: Optional[int] = bit_depth.value if isinstance(bit_depth, BitDepth) else bit_depth
        self.audio_format: Optional[AudioFormat] = None
        self.sending_headers: bool = sending_headers
        self.channels: Optional[int] = channels.value if isinstance(channels, Channel) else channels
        self.codec: Optional[str] = codec

        if audio_format is None:
            # b/w compatibility
            self.__dict__ = DEFAULT_WAV_PCM.__dict__
        else:
            self.audio_format = audio_format if isinstance(audio_format, AudioFormat) else AudioFormat(audio_format)

        if not self.sending_headers:
            self._compute_sampling_attributes()
            assert self.sample_rate is not None, 'Sample rate is mandatory if audio headers won\'t be sent'
            assert self.bit_depth is not None, 'Bit depth is mandatory if audio headers won\'t be sent'
            assert self.bit_rate is not None, 'Bit rate is mandatory if audio headers won\'t be sent'
            assert self.channels is not None, 'Channels number is mandatory if audio headers won\'t be sent'

        if not self.sending_headers:
            if (self.sample_rate is None or self.bit_rate is None or self.bit_depth is None or self.channels is None) and self.audio_format in _default_audio_attributes:
                default_attributes: AudioAttributes = get_default_attributes(self.audio_format)

                self.sample_rate = default_attributes.sample_rate
                self.bit_depth = default_attributes.bit_depth
                self.bit_rate = default_attributes.bit_rate
                self.channels = default_attributes.channels
            elif self.sample_rate is None or self.bit_rate is None or self.bit_depth is None or self.channels is None:
                raise AudioFormatError(audio_error_code=AudioFormatError.ErrorCode.BAD_AUDIO_FORMAT,
                                       actual=f'sample_rate{str(self.sample_rate)}, bit_depth={str(self.bit_depth)}, bit_rate={str(self.bit_rate)}, channels={self.channels}',
                                       expected='Valid configuration')

    def _compute_sampling_attributes(self):
        if self.bit_depth is not None:
            if self.bit_depth % 8 != 0:  # this means we're provided with sample width in bytes instead of bits
                self.bit_depth *= 8

        if self.bit_depth is not None and self.bit_rate is not None:
            expected_sample_rate: int = self.bit_rate // self.bit_depth

            if self.sample_rate is not None:
                if self.sample_rate != expected_sample_rate:
                    raise AudioFormatError(audio_error_code=AudioFormatError.ErrorCode.BAD_SAMPLE_RATE,
                                           actual=str(self.sample_rate),
                                           expected=str(expected_sample_rate))
            else:
                self.sample_rate = expected_sample_rate
        elif self.bit_depth is not None and self.sample_rate is not None:
            self.bit_rate = self.sample_rate * self.bit_depth
        elif self.bit_rate is not None and self.sample_rate is not None:
            self.bit_depth = self.bit_rate // self.sample_rate

    def init_attributes(self, sample_rate: int, bit_depth: int, bit_rate: int, channels: int):
        assert self.sending_headers, 'Initializing attributes when sending headers was set to False'

        self.sample_rate = sample_rate
        self.bit_rate = bit_rate
        self.bit_depth = bit_depth
        self.channels = channels

        self._compute_sampling_attributes()

    def copy(self):
        return AudioAttributes(**self.__dict__)

    def __str__(self):
        return f'AudioAttributes(sample_rate={self.sample_rate}, bit_rate={self.bit_rate}, bit_depth={self.bit_depth}, ' \
               f'audio_format={self.audio_format.value}, channels={self.channels}, codec={self.codec})'

    def __repr__(self):
        return self.__str__()


DEFAULT_WAV_PCM: AudioAttributes = AudioAttributes(audio_format=AudioFormat.WAV,
                                                   sample_rate=16000,
                                                   codec='pcm_s16le',
                                                   bit_depth=16,
                                                   channels=1,
                                                   sending_headers=False)

DEFAULT_WEBM_OPUS: AudioAttributes = AudioAttributes(audio_format=AudioFormat.WEBM,
                                                     sample_rate=48000,
                                                     codec='libopus',
                                                     bit_depth=32,
                                                     channels=1,
                                                     sending_headers=False)

_default_audio_attributes: Dict[AudioFormat, AudioAttributes] = {
    AudioFormat.WAV: DEFAULT_WAV_PCM,
    AudioFormat.WEBM: DEFAULT_WEBM_OPUS
}


def get_default_attributes(audio_format: AudioFormat) -> Optional[AudioAttributes]:
    return _default_audio_attributes[audio_format].copy()
