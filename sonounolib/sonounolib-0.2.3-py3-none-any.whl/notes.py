"""This package provide tools to handle the scientific pitch notation."""
from __future__ import annotations

from typing import Mapping

__all__ = ['NOTE_FREQUENCIES', 'asfrequency']


def get_note_frequencies() -> Mapping[str, float]:
    """Returns note frequencies according to the scientific pitch notation.

    The covered octaves are 0 to 10, so that notes from C0 to B10 are defined.
    Sharp notes are denoted with a '#' character and flat notes with a 'b' letter.

    Examples:
        >>> frequencies = get_note_frequencies()
        >>> print(frequencies['A4'], frequencies['C#4'], frequencies['Db4'])

    """
    octaves = range(0, 11)
    notes = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    keys = [f'{n}{o}' for o in octaves for n in notes]
    base_freq = 440  # Frequency of reference note A4
    ibase = keys.index('A4')

    freqs = [2 ** ((n - ibase) / 12) * base_freq for n in range(len(keys))]
    frequencies = dict(zip(keys, freqs))

    flats = {
        'Db': 'C#',
        'Eb': 'D#',
        'Gb': 'F#',
        'Ab': 'G#',
        'Bb': 'A#',
    }
    for octave in octaves:
        for flat, sharp in flats.items():
            frequencies[f'{flat}{octave}'] = frequencies[f'{sharp}{octave}']

    return frequencies


NOTE_FREQUENCIES = get_note_frequencies()


def asfrequency(value: float | str) -> float:
    """Returns the frequency associated to a note or the input frequency otherwise.

    Arguments:
        value: The note in scientific pitch notation, or the frequency.

    Raises:
        ValueError: When the input is a string and is not a note in the range C0 - B10.

    Returns:
        If the input is a string, it is assummed to be a note, and its associated
        frequency is returned. Otherwise, this input is assumed to be a frequency and
        is returned as-is.

    Example:
        >>> from sonounolib.notes import asfrequency
        >>> assert asfrequency('A4') == 440
        >>> assert asfrequency(440) == 440
    """
    if isinstance(value, str):
        try:
            return NOTE_FREQUENCIES[value]
        except KeyError:
            raise ValueError(f'Unknown note: {value!r}.') from None
    return value
