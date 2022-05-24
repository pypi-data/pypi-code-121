"""This module defines the Track class.

The Track class is the main building block to process audio sounds
using the sonoUno library.
"""
from __future__ import annotations

import warnings
from pathlib import Path
from typing import BinaryIO, Literal

import numpy as np
import soundfile as sf
from numpy.typing import ArrayLike, NDArray

from .notes import asfrequency
from .utils import asmax_amplitude, pad_along_axis

try:
    import sounddevice as sd
except OSError as exc:  # pragma: no cover
    with warnings.catch_warnings():
        warnings.simplefilter('always')
        warnings.warn(str(exc), ImportWarning)
    sd = None

__all__ = ['Track']


class Track:
    """Class representing an audio track.

    Attributes:
        rate: The sampling rate, i.e. the number of samples per second used to encode
            the audio.
        max_amplitude: The maximum value for the sound wave amplitude
        sample_duration: The inverse of the sample rate.
        duration: The track duration, in seconds.
        cue_write: The time at which new writings on the track will be started.

    """

    DEFAULT_TRACK_RATE = 44100
    DEFAULT_TRACK_MAX_AMPLITUDE = 1

    VALID_FORMATS = 'int16', 'int32', 'float32', 'float64'

    max_amplitude: float
    _data: NDArray[np.float64]
    _index_write: int
    _size: int

    def __init__(
        self,
        rate: int = DEFAULT_TRACK_RATE,
        max_amplitude: float | str = DEFAULT_TRACK_MAX_AMPLITUDE,
    ):
        """The Track constructor.

        Arguments:
            rate: The sampling rate, in Hertz.
            max_amplitude: The maximum encodable amplitude of the signal.
        """
        self.rate = rate
        self.sample_duration = 1 / rate
        self.max_amplitude = asmax_amplitude(max_amplitude)
        self._data = np.array([], dtype=float)
        self._index_write = 0
        self._size = 0

    @property
    def shape(self) -> tuple[int, ...]:
        """The shape of the track data array.

        Note:
            This shape can be greater (in case of trailing blank) or lesser (in case
            of over-allocation) than that of the track data buffer.
        """
        return self._data.shape[:-1] + (self._size,)

    @property
    def duration(self) -> float:
        """The track duration, in seconds."""
        return self._size * self.sample_duration

    @property
    def cue_write(self) -> float:
        """The starting time, in seconds, of the next write."""
        return self._index_write * self.sample_duration

    def set_cue_write(self, value: float) -> Track:
        """Sets the cue time for next write.

        Arguments:
           value: The start time of the next write in the track.

        Returns:
           The current track.

        Example:
            To play two sine waves concurrently, at different frequencies:
            >>> from sonounolib import Track
            >>> track = Track()
            >>> track.add_sine_wave(440, duration=1) \
                     .set_cue_write(0) \
                     .add_sine_wave(880, duration=1)
            >>> track.play()
        """
        if value < 0:
            raise ValueError(f'Negative cue write value: {value}')
        self._index_write = round(value * self.rate)
        return self

    def play(self, cue_read: float = 0, duration: float | None = None) -> None:
        """Plays the audio track.

        Arguments:
            cue_read: The starting time for playing the data.
            duration: The number of seconds to be played.

        Raises:
            OSError: When the PortAudio library is not installed or when there is no
                output device available.
        Example:
            To play the track sound waves:
            >>> from sonounolib import Track
            >>> track = Track().add_sine_wave(440, duration=1)
            >>> track.play()
        """
        if sd is None:
            raise OSError(
                'The sounddevice package could not be imported. Check if the PortAudio '
                'library is installed.'
            )
        if sd.default.device[1] == -1:
            raise OSError('There is no output device available.')

        data = self.get_data(cue_read=cue_read, duration=duration)
        data /= self.max_amplitude
        sd.play(data, self.rate)

    @classmethod
    def from_wav(
        cls,
        file: str | Path | BinaryIO,
        max_amplitude: float = 1,
    ) -> Track:
        """Reads a wave sound file into a Track.

        Arguments:
           file: The file to read from.
           max_amplitude: The max amplitude of the returned sound waves.
        """
        data, rate = sf.read(file)
        max_amplitude_in = asmax_amplitude(data.dtype.name)
        data = data.T.astype(float) * (max_amplitude / max_amplitude_in)
        track = Track(rate=rate, max_amplitude=max_amplitude)
        track.add_raw_data(data)
        return track

    def to_wav(
        self,
        file: str | Path | BinaryIO,
        format: Literal['int16', 'int32', 'float32', 'float64'] = 'int16',
    ) -> None:
        """Writes the track to a file-like output.

        Arguments:
            file: The file to write to.
            format: The data type to use when encoding the track sound waves.
        """
        if format not in self.VALID_FORMATS:
            raise ValueError(f'Cannot infer a wave format for data type: {format!r}.')
        required_max_amplitude = asmax_amplitude(format)
        data = self.get_data() * (required_max_amplitude / self.max_amplitude)
        data = data.T.astype(format, copy=False)
        sf.write(file, data, self.rate, format='wav')

    def get_data(
        self, cue_read: float = 0, duration: float | None = None
    ) -> NDArray[np.float64]:
        """Returns the samples of the tracks.

        Arguments:
            cue_read: The starting time for reading the data.
            duration: The number of seconds to be read.

        Returns:
            The track data after the specified read cue.

        Example:
            To display the sound waves:
            >>> import matplotlib.pyplot as mp
            >>> from sonounolib import Track
            >>> track = Track()
            >>> track.add_sine_wave(440, duration=1)
            >>> mp.plot(track.get_data())
        """
        if cue_read < 0:
            raise ValueError(f'Negative cue read value: {cue_read}')
        if duration is not None:
            raise NotImplementedError
        start_index = int(cue_read * self.sample_duration)
        data = self._data[..., start_index : self._size]
        overflow = self._size - data.shape[-1]
        if overflow > 0:
            data = pad_along_axis(data, overflow)
        return data

    def repeat(self, n: int) -> Track:
        """Repeats the sound waves by the specified number of times.

        Arguments:
            n: The number of repeats. The value of 1 means no repetitions, i.e.
                the track is not affected.

        Raises:
            ValueError: When the number of repeats is less than one.

        Returns:
            The current track, with its data repeated `n` times.
        """
        if n < 1:
            raise ValueError(f'The number of repeats is less than one: {n!r}.')
        if n == 1:
            return self
        data = np.tile(self.get_data(), n - 1)
        self.set_cue_write(self.duration)
        return self.add_raw_data(data)

    def add_blank(self, duration: float) -> Track:
        """Adds a blank to the track.

        Arguments:
            duration: Duration of the sound in seconds.

        Returns:
            The current track, with the specified blank.

        Example:
            To play two sine waves concurrently, at different frequencies:
            >>> from sonounolib import Track
            >>> track = Track()
            >>> track.add_blank(1)
            >>> assert track.duration == 1
        """
        nsample = int(duration * self.rate)
        self._index_write += nsample
        self._size = max(self._index_write, self._size)
        return self

    def add_track(self, track: Track, cue_read: float = 0) -> Track:
        """Adds another track to the track.

        Arguments:
            track: The track to be added.
            cue_read: The starting time for reading the data of the track to be added.

        Returns:
            The current track, whose data has been updated with the input track.

        Example:
            To combine two tracks:
            >>> from sonounolib import Track
            >>> track1 = Track().add_sine_wave(440, duration=1)
            >>> track2 = Track().add_sine_wave(880, duration=1)
            >>> track1.set_cue_write(0.5).add_track(track2)
            >>> track1.play()
        """
        if self.rate != track.rate:
            raise ValueError('Cannot mix tracks with different sampling rates.')
        data = track.get_data(cue_read)
        if self.max_amplitude != track.max_amplitude:
            data = (self.max_amplitude / track.max_amplitude) * data
        return self.add_raw_data(data)

    def add_sine_wave(
        self,
        frequency: float | str,
        duration: float,
        amplitude: float = 1 / 4,
    ) -> Track:
        """Adds a sine wave to the track.

        Arguments:
            frequency: Frequency of the sine wave.
            duration: Duration of the sound in seconds.
            amplitude: The default is 1/4 of the maximum amplitude.

        Returns:
            The current track, whose data has been updated with the specified sine
            waves.

        Example:
            To play two sine waves concurrently, at different frequencies:
            >>> from sonounolib import Track
            >>> track = Track()
            >>> track.add_sine_wave(440, duration=1)
            >>> track.play()
        """
        frequency = asfrequency(frequency)
        amplitude *= self.max_amplitude
        nsample = int(self.rate * duration)
        times = np.linspace(0, nsample * self.sample_duration, nsample, endpoint=False)
        data = amplitude * np.sin(2 * np.pi * frequency * times)
        return self.add_raw_data(data)

    def add_raw_data(self, data: ArrayLike) -> Track:
        """Adds the value of an ndarray to the track.

        Arguments:
            data: The sound waves to be added to the track.

        Returns:
            The current track, whose data has been updated with the input sound waves.
        """
        data = np.asanyarray(data).astype(float, copy=False)
        self._extend_data_if_needed(data.shape[-1])
        new_index_write = self._index_write + data.shape[-1]
        self._data[..., self._index_write : new_index_write] += data
        self._index_write = new_index_write
        self._size = max(self._size, self._index_write)
        return self

    def _extend_data_if_needed(self, required_nsample: int) -> None:
        current_shape = self._data.shape
        current_size = current_shape[-1]
        overflow = self._index_write + required_nsample - current_size
        if overflow > 0:
            increment = overflow + self._size
            self._data = pad_along_axis(self._data, increment)
