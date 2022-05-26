from enum import Enum


class AudioFormatError(ValueError):
    class ErrorCode(str, Enum):
        BAD_SAMPLE_RATE = '1'
        BAD_BIT_DEPTH = '2'
        BAD_CHANNELS_NUMBER = '3'
        BAD_AUDIO_FORMAT = '4'
        MAXIMUM_LENGTH_EXCEEDED = '5'

    def __init__(self, audio_error_code: ErrorCode, actual: str, expected: str):
        super(AudioFormatError, self).__init__()
        self._audio_error_code = audio_error_code
        self._actual = actual
        self._expected = expected

    @property
    def audio_error_code(self):
        return self._audio_error_code

    @property
    def actual(self):
        return self._actual

    @property
    def expected(self):
        return self._expected
