import os
import random
from typing import Generator, Dict, List, Any

import mido
from midi_utils import midi_to_note


def load(midi_file: str) -> List[mido.Message]:
    """
    Load and validate a midi file, returning a list of messages
    """
    if not os.path.exists(midi_file):
        raise ValueError(f"{midi_file} does not exist")

    mid = mido.MidiFile(midi_file)

    # TODO: handle multitrack midi files
    if len(mid.tracks) > 1:
        raise NotImplementedError(
            "There is not currently support for multi-track midifiles."
        )

    # filter valid messages
    messages = [msg for msg in mid if msg.type in ["note_on", "note_off"]]

    # validate first message
    if messages[0].type != "note_on":
        raise ValueError(
            "This midi file does not start with a note_on message. "
            "Reformat and try again"
        )

    # validate final message
    if messages[-1].type != "note_off":
        raise ValueError(
            "This midi file does not end with a note_off message. "
            "Reformat and try again"
        )
    return messages


def process(midi_file: str) -> Generator[Dict[str, Any], None, None]:
    """
    Load a midi file and yield say-friendly parameters
    """
    messages = load(midi_file)
    total_time = 0
    for i, curr_msg in enumerate(messages):
        total_time += curr_msg.time
        prev_msg = messages[i - 1]

        # ignore first note_on message and only yield when
        # we get a note off message
        if i > 0 and curr_msg.type == "note_off":
            if prev_msg.type != "note_on":
                raise ValueError(
                    f"Overlapping note {midi_to_note(prev_msg.note)} found at message #{i} @ {total_time:.2f}s. "
                    "Only fully monophonic tracks are supported. "
                    "Reformat and try again."
                )
            # if previous note on message has a delta time, yield silence
            if prev_msg.time > 0:
                yield {
                    "type": "silence",
                    "note": None,
                    "duration": prev_msg.time * 1000.0,
                    "velocity": None,
                }
            # yield the note with computed duration
            yield {
                "type": "note",
                "note": prev_msg.note,
                "duration": curr_msg.time * 1000.0,
                "velocity": prev_msg.velocity,
            }


def random_velocity(min: int = 0, max: int = 127) -> int:
    """
    Generate a random velocity value given a min and max
    """
    return random.choice(list(range(min, max + 1)))
