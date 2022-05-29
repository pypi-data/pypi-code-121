"""Provides an appropriate audio player according to current environment."""
from __future__ import annotations

import sys
import warnings
from abc import ABC, abstractmethod
from types import ModuleType
from typing import Any

import numpy as np
from numpy.typing import NDArray

IPython = sys.modules.get('IPython')
sounddevice: ModuleType | None = None

if IPython is not None and (
    not IPython.get_ipython()
    or IPython.get_ipython().__class__.__name__ == 'TerminalInteractiveShell'
):  # pragma: no cover
    IPython = None

if IPython is None:  # pragma: no cover
    try:
        import sounddevice  # type: ignore[no-redef]
    except OSError as exc:
        with warnings.catch_warnings():
            warnings.simplefilter('always')
            warnings.warn(str(exc), ImportWarning)


class Player(ABC):
    """The abstract class for an audio player."""

    @abstractmethod
    def play(self, data: NDArray[np.float64], rate: float) -> Any:
        """Plays the requested audio waves.

        Arguments:
            data: The sound waves to be played, with a max amplitude of 1.
            rate: The sampling rate.
        """


class IPythonPlayer(Player):
    """An audio player using IPython as backend."""

    def play(self, data: NDArray[np.float64], rate: float) -> Any:
        """Plays the requested audio waves using IPython audio.

        Arguments:
            data: The sound waves to be played, with a max amplitude of 1.
            rate: The sampling rate.

        Returns:
            An instance of IPython.display.Audio.
        """
        assert IPython is not None
        audio = IPython.display.Audio(data, rate=rate, autoplay=True, normalize=False)
        return audio


class PortAudioPlayer(Player):
    """An audio player using PortAudio as backend."""

    def __init__(self) -> None:
        """The PortAudioPlayer constructor."""
        assert sounddevice is not None
        if sounddevice.default.device[1] == -1:
            raise OSError('There is no output device available.')

    def play(self, data: NDArray[np.float64], rate: float) -> None:
        """Plays the requested audio waves using PortAudio.

        Arguments:
            data: The sound waves to be played, with a max amplitude of 1.
            rate: The sampling rate.
        """
        assert sounddevice is not None
        sounddevice.play(data, rate)


def get_player() -> Player:
    """Returns an audio player according to the current environment."""
    if (
        IPython
        and IPython.get_ipython()
        and IPython.get_ipython().__class__.__name__ != 'TerminalInteractiveShell'
    ):
        return IPythonPlayer()
    if sounddevice:
        return PortAudioPlayer()
    raise OSError(
        'Could not find an appropriate player. Nor IPython (Jupyter) nor '
        'sounddevice (PortAudio) are installed.'
    )
