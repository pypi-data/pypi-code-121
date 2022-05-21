from typing import Union

from .constants import (
    NOTE_TO_MIDI,
    ROOT_TO_MIDI,
    NOTE_EQUIVALENTS,
    MIDI_TO_FREQ,
    MIDI_TO_NOTE,
    NOTE_TO_FREQ,
)


def sharp_to_flat(note_name: str) -> str:
    """
    Translate a sharp note to a flat note, since we only use flats internally
    Args:
        note_name: A valid note name from `midi_utils.constants.NOTE_TO_MIDI`
              or a midi note between 0 and 127.
    """
    if "#" in note_name:
        try:
            sharp_note = NOTE_EQUIVALENTS[note_name[:2]]
        except KeyError:
            raise ValueError(f"Invalid note: {note_name}")
        return sharp_note + note_name[2:]
    return note_name


def note_to_midi(note_name: Union[str, int]) -> int:
    """
    Convert a note name (eg: "C3") into its corresponding midi note value (eg: 60).
    If passed a valid midi note, it will simply return it.
    Args:
        note_name: A valid note name from `midi_utils.constants.NOTE_TO_MIDI`
    """
    if isinstance(note_name, str):
        note_name = note_name.upper()
        note_name = sharp_to_flat(note_name)
        if note_name in NOTE_TO_MIDI:
            return NOTE_TO_MIDI[note_name]
        raise ValueError(f'"{note_name}" is not a valid note.')
    if note_name < 0 or note_name > 127:
        raise ValueError(
            f'"{note_name}" is not a valid midi note. Must be between 0 and 127'
        )
    return note_name


def note_to_freq(note_name: str) -> int:
    """
    Convert a note name (eg: "A4") into its corresponding frequency (eg: 440).
    Args:
        note_name: A valid note name from `midi_utils.constants.NOTE_TO_MIDI`
    """
    try:
        return NOTE_TO_FREQ[note_name]
    except KeyError:
        raise ValueError(f"Invalid note name: {note_name}")


def midi_to_note(midi_note_num: int) -> str:
    """
    Convert a midi note number (eg: 60) into its corresponding note name (eg: "C3").
    If passed a valid midi note, this function will simply return it.

    Args:
        midi_note_num: A midi note number between 0 and 127
    """
    try:
        return MIDI_TO_NOTE[midi_note_num]
    except KeyError:
        raise ValueError(f"Invalid midi note num: {midi_note_num}")


def midi_to_freq(midi_note_num: int) -> float:
    """
    Convert a midi note number (eg: 81) into its corresponding note frequency (eg: 440).
    Args:
        midi_note_num: A midi note number between 0 and 127
    """
    try:
        return MIDI_TO_FREQ[midi_note_num]
    except KeyError:
        raise ValueError(f"Invalid midi note num: {midi_note_num}")


def midi_to_octave(midi_note_num: int, octave: int) -> int:
    """
    Raise a midi note up or down an one or more octaves

    Args:
        midi_note_num: A valid midi note between 0 and 127.
        octave: the number of octaves to adjust the note up (1) or down (-1)
    """
    midi_note_num += octave * 12
    if midi_note_num < 0 or midi_note_num > 127:
        raise ValueError(f"midi note num {midi_note_num} out of valid range.")
    return midi_note_num


def root_to_midi(root: str) -> int:
    """
    Convert a root name (eg: "C") into its corresponding midi note  .
    If passed a valid midi note value, this function will simply return it.

    Args:
        root: A valid root name from `midi_utils.constants.NOTES`
              or a midi note between 0 and 11.
    """
    if isinstance(root, str):
        root = root.upper()
        if root in ROOT_TO_MIDI:
            return ROOT_TO_MIDI[root]
        raise ValueError(
            f'"{root}" is not a valid root name. Choose from: {", ".join(ROOT_TO_MIDI.keys())}'
        )
    if root not in ROOT_TO_MIDI.values():
        raise ValueError(
            f'"{root}" is not a valid midi root. Choose from: {", ".join(ROOT_TO_MIDI.values())}'
        )
    return root


def freq_to_octave(freq: float, octave: int) -> float:
    """
    Adjust a frequency up or down by octaves
    """
    if octave < 0:
        return freq * (1.0 / (abs(octave) * 2.0))
    return freq * (octave * 2.0)
