import sys

import click

from saysynth import phoneme, say
from saysynth.cli.options import (
    PHONEME_OPTIONS, 
    SAY_OPTIONS, 
    group_options, 
    prepare_options_for_say,
    randomize_velocity_opt, 
    velocity_steps_opt, 
    volume_range_opt, 
)

# # # ##
# Midi #
# # # ##


@click.command()
@click.argument("midi_file", required=True)
@click.option(
    "-l",
    "--loops",
    default=1,
    show_default=True,
    type=int,
    help="The number of times to loop the midi file",
)
@click.option(
    "-oct",
    "--octave",
    type=int,
    help="The number of octaves to adjust the pitch up or down (eg: -oct 1 or -oct -1)",
)
@group_options(*PHONEME_OPTIONS)
@group_options(velocity_steps_opt, randomize_velocity_opt, volume_range_opt)
@click.option(
    "-o",
    "--output-file",
    type=str,
    help="A filepath to write the generated text to",
)
@click.option('-x', '--exec', is_flag=True, default=False, help="Run the generated text through the say command")
@group_options(*SAY_OPTIONS)
def run(**kwargs):
    """
    Given a midi file, generate a text-file (or stdout stream) of phonemes with pitch information for input to say
    """

    # generate the text
    text = phoneme.text_from_midi(**kwargs).replace("\n", " ")

    # handle writing text to file
    output_file = kwargs.get("output_file")
    if output_file:
        with open(output_file, "w") as f:
            f.write(text)
        sys.exit(0)

    # if we're not executing say, write text to stdout
    if not kwargs.get('exec'):
        sys.stdout.write(text)
        sys.exit(0)

    # execute say
    kwargs = prepare_options_for_say(text, **kwargs)
    say.run(**kwargs)
