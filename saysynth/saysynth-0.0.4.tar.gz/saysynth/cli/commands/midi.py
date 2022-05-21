
import sys

import click

from saysynth import phoneme
from saysynth.cli.options import PHONEME_OPTIONS, group_options, randomize_velocity_opt, velocity_steps_opt

# # # ##
# Midi #
# # # ##


@click.command()
@click.argument("midi_file", required=True)
@click.argument(
    "output_file",
    required=False,
)
@group_options(*PHONEME_OPTIONS)
@click.option(
    "-l",
    "--loops",
    default=1,
    show_default=True,
    type=int,
    help="The number of times to loop the midi file",
)
@click.option(
    "-o",
    "--octave",
    type=int,
    help="The number of octaves to adjust the pitch up or down (eg: -o 1 or -o -1)",
)
@group_options(velocity_steps_opt, randomize_velocity_opt)
def run(**kwargs):
    """
    Given a midi file, generate a text-file (or stdout stream) of phonemes with pitch information for input to say
    """
    text = phoneme.text_from_midi(**kwargs)
    output_file = kwargs.get("output_file")
    if output_file:
        with open(output_file, "w") as f:
            f.write(text)
    else:
        sys.stdout.write(text)

