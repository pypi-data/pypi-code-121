from typing import List, Union, Optional

from .utils import bpm_to_time


def apply_style(notes: List[int], name: str = "down"):
    return {
        "down": lambda x: reversed(sorted(x)),
        "up": lambda x: sorted(x),
        "downup": lambda x: list(reversed(sorted(x))) + list(sorted(x))[1:-1],
        "updown": lambda x: list(sorted(x)) + list(reversed(sorted(x)))[1:-1],
    }.get(name)(notes)


def midi_arp(
    chord_notes: List[int],  # list of notes to arpeggiate
    bpm: float = 120.0,  # bpm
    count: Union[float, int, str] = "1/16",
    time_sig: str = "4/4",  # time signature
    octaves: List[int] = [0],  # a list of octaves to add to the chord (eg: [-1, 2])
    loops: int = 4,  # The number of times to loop the pattern
    style: str = "down",  # TODO: implement different styles
    retrigger: Optional[int] = None  # number of notes after which to restart pattern.
    # if None, the pattern will loop over and over again
):
    """
    Given a list of chord notes, a style name (eg: up, down)
    """
    # create list of notes
    chord_notes = list(
        set(chord_notes + [o * 12 + n for o in octaves for n in chord_notes])
    )
    note_duration = bpm_to_time(bpm, count, time_sig)

    n_loops = 0
    while True:
        n_steps = 0
        # apply the style /  order
        for note in apply_style(chord_notes, style):
            yield {
                "note": note,
                "duration": note_duration,
            }

        n_loops += 1
        if n_loops >= loops:
            break
