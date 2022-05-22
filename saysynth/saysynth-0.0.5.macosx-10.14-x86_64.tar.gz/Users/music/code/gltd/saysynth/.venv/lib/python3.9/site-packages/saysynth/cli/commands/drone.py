
import sys

import click

from saysynth import phoneme
from saysynth.cli.options import CHORD_OPTIONS, PHONEME_OPTIONS, SAY_OPTIONS, VELOCITY_OPTIONS, group_options


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
@group_options(*CHORD_OPTIONS)
@group_options(*PHONEME_OPTIONS)
@click.option(
    "-pl",
    "--phoneme-loops",
    default=None,
    type=int,
    help="The number of times to loop an individual phoneme. If not provided, the drone will continue indefinitely.",
)
@group_options(*VELOCITY_OPTIONS)
@click.option('-x', '--exec', is_flag=True, default=False, help="Run the generated text through the say command. If `--chord` amd `--exec` are provided. ")
@group_options(*SAY_OPTIONS)
def run(**kwargs):
    """
    Given a note name (or midi note number), stream text required to generate a continuous drone for input to say
    """
    
    # if stdout
    sys.stdout.write(phoneme.drone_from_note(**kwargs))