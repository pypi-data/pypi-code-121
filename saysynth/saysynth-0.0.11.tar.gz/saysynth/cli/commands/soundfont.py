
import os

import click
from midi_utils import midi_to_note, note_to_midi, midi_scale
from midi_utils import ROOT_TO_MIDI, SCALES

from saysynth import say, phoneme, utils
from saysynth.constants import (
    SAY_TUNE_TAG,
)
from saysynth.cli.options import group_options, VELOCITY_OPTIONS, PHONEME_OPTIONS, voice_opt, rate_opt

@click.command()
@click.option(
    "-s", "--start-at", type=str, default="C3", help="Note name/number to start at"
)
@click.option(
    "-e",
    "--end-at",
    type=str,
    default="G5",
    show_default=True,
    help="Note name/number to end at",
)
@click.option(
    "-c",
    "--scale",
    type=click.Choice([s.lower() for s in SCALES]),
    default="minor",
    show_default=True,
    help="Scale name to use",
)
@click.option(
    "-k", "--key", type=click.Choice(ROOT_TO_MIDI.keys()), default="C", show_default=True, help="Root note of scale"
)
@group_options(voice_opt, rate_opt)
@click.option(
    "-o",
    "--output-dir",
    default="./",
    type=str,
    show_default=True,
    help="Directory to write to",
)
@click.option(
    "-f",
    "--format",
    type=click.Choice(["wav", "aiff"]),
    default="aiff",
    show_default=True,
    help="Format of each note's file.",
)
@group_options(*PHONEME_OPTIONS)
@click.option(
    "-d",
    "--duration",
    default=1_000_000,
    type=int,
    help="The duration each note of the soundfont in milliseconds.",
)
@group_options(*VELOCITY_OPTIONS)
@click.option(
    "-rs",
    "--randomize-segments",
    type=bool,
    default=False,
    help="Randomize every segment of a note. Only applies when --randomize-velocity and --randomize-phoneme are set.",
)
def run(**kwargs):
    """
    Given a scale and other parameters, generate a soundfont of each note as an .aiff or .wav file.
    """
    # add note type to simplify function call
    kwargs["type"] = "note"

    # determine set of notes to generate
    start_at = note_to_midi(kwargs["start_at"])
    end_at = note_to_midi(kwargs["end_at"])
    scale = midi_scale(
        key=kwargs["key"], scale=kwargs["scale"], min_note=start_at, max_note=end_at
    )

    # generate files for each note in the scale
    for midi in scale:

        # add note type/midi not to simplify phoneme_text_from_note function call
        kwargs["type"] = "note"
        kwargs["midi"] = midi
        kwargs["note"] = midi_to_note(midi)

        # generate audio output file name
        audio_output_file = os.path.join(
            kwargs["output_dir"],
            f"{kwargs['voice'].lower()}-{kwargs['rate']}-{midi:02d}.{kwargs['format']}",
        )
        # generate input file of text
        input_file_name = utils.make_tempfile()
        with open(input_file_name, "w") as f:
            f.write(f"{SAY_TUNE_TAG}\n{phoneme.text_from_note(**kwargs)}")
        cmd = say.cmd(
            input_file=input_file_name,
            voice=kwargs["voice"],
            rate=kwargs["rate"],
            audio_output_file=audio_output_file,
        )
        say.run(cmd)
        if not os.path.exists(audio_output_file):
            raise RuntimeError(f"File {audio_output_file} was not successfully created")
        # cleansup tempfile
        os.remove(input_file_name)
