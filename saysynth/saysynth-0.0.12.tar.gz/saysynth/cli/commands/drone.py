import copy
import sys

import click

from midi_utils import chord
from saysynth import phoneme, say
from saysynth.cli.options import (
    CHORD_OPTIONS,
    PHONEME_OPTIONS,
    SAY_OPTIONS,
    VELOCITY_OPTIONS,
    group_options,
    prepare_options_for_say
)


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
@click.option(
    "-o",
    "--output-file",
    type=str,
    help="A filepath to write the generated text to",
)
@click.option('-x', '--exec', is_flag=True, default=False, help="Run the generated text through the say command. If `--chord` amd `--exec` are provided. ")
@group_options(*SAY_OPTIONS)
def run(**kwargs):
    """
    Given a note name (or midi note number), stream text required to generate a continuous drone for input to say
    """
    # generate the text if a chord isn't passed in
    if not kwargs.get('chord'):
        text = phoneme.drone_from_note(**kwargs)

        # handle writing text to file
        output_file = kwargs.get("output_file")
        if output_file:
            with open(output_file, "w") as f:
                f.write(text)

        # if we're not executing say, write text to stdout
        elif not kwargs.get('exec'):
            sys.stdout.write(text)

        else:
            # execute say
            kwargs = prepare_options_for_say(text, **kwargs)
            say.run(**kwargs)

    # spawn multiple commands, one per note in the chord
    else:
        kwargs['root'] = kwargs.pop('note')
        commands = []
        for note in chord.midi_chord(**kwargs):
            cmd_kwargs = copy.copy(kwargs)
            cmd_kwargs['text'] = phoneme.drone_from_note(note, type="note", **kwargs)
            commands.append(cmd_kwargs)
        say.spawn(commands)
