
import sys

import click

from saysynth import phoneme
from saysynth.cli.options import PHONEME_OPTIONS, VELOCITY_OPTIONS, group_options
from saysynth.constants import SAY_TUNE_TAG


# # # # #
# Drone #
# # # # #


@click.command()
@click.argument("note", required=True)
@click.option(
    "-d",
    "--max-duration",
    default=1_000_000,
    type=int,
    help="The duration of the drone in milliseconds.",
)
@group_options(*PHONEME_OPTIONS)
@click.option(
    "-pl",
    "--phoneme-loops",
    default=None,
    type=int,
    help="The number of times to loop an individual phoneme. If not provided, the drone will continue indefinitely.",
)
@group_options(*VELOCITY_OPTIONS)
def run(**kwargs):
    """
    Given a note name (or midi note number), stream text required to generate a continuous drone for input to say
    """
    phoneme_loops = kwargs.pop("phoneme_loops", None)
    max_duration = kwargs.pop("max_duration", None)

    # set the phonemes duration to the max phoneme duration
    kwargs["duration"] = kwargs["max_phoneme_duration"]
    # add note type to simplify function call
    kwargs["type"] = "note"

    loops = 0
    duration = 0
    sys.stdout.write(f"{SAY_TUNE_TAG}\n")
    while True:
        text = phoneme.text_from_note(**kwargs)
        sys.stdout.write(f"{text}\n")

        # check for max loops
        if phoneme_loops:
            loops += 1
            if loops >= phoneme_loops:
                break

        # check for max duration
        if max_duration:
            duration += kwargs["duration"]
            if duration >= max_duration:
                break

