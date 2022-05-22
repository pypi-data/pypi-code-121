import click

from midi_utils.constants import CHORDS
from saysynth.constants import (
    SAY_COLORS,
    SAY_EMPHASIS_VELOCITY_STEPS,
    SAY_ALL_PHONEMES,
    SAY_TUNED_VOICES,
    SAY_PHONEME_CLASSES,
    SAY_PHONEME_MAX_DURATION,
)


def group_options(*options):
    def wrapper(function):
        for option in reversed(options):
            function = option(function)
        return function

    return wrapper


# Phoneme Options

phoneme_opt = click.option(
    "-p",
    "--phoneme",
    default="m",
    help="The phoneme to use.",
    show_default=True,
    type=click.Choice(SAY_ALL_PHONEMES),
)
randomize_phoneme_opt = click.option(
    "-rp",
    "--randomize-phoneme",
    show_default=True,
    help=(
        "Randomize the phoneme for every note. "
        "If `all` is passed, all phonemes will be used. "
        "Alternatively pass a voice and style, eg: Fred:drone. "
        f"Valid voices include: {', '.join(SAY_TUNED_VOICES)}. "
        f"Valid styles include: {', '.join(SAY_PHONEME_CLASSES)}."
    ),
)

phoneme_duration_opt = click.option(
    "-pd",
    "--phoneme-duration",
    default=SAY_PHONEME_MAX_DURATION,
    show_default=True,
    type=int,
    help="The max duration in ms of an individual phoneme",
)

PHONEME_OPTIONS = [phoneme_opt, randomize_phoneme_opt, phoneme_duration_opt]

# Velocity Options

velocity_opt = click.option(
    "-vl",
    "--velocity",
    type=int,
    show_default=True,
    default=100,
    help="The midi velocity value to use for each note.",
)
velocity_steps_opt = click.option(
    "-vs",
    "--velocity-steps",
    type=int,
    nargs=2,
    show_default=True,
    default=SAY_EMPHASIS_VELOCITY_STEPS,
    help="The midi velocity values at which to add emphasis to a note",
)
randomize_velocity_opt = click.option(
    "-rv",
    "--randomize-velocity",
    type=int,
    nargs=2,
    help="Randomize a note's emphasis by supplying a min and max midi velocity (eg: -rv 40 120)",
)

VELOCITY_OPTIONS = [velocity_opt, velocity_steps_opt, randomize_velocity_opt]

# Say Options
rate_opt = click.option(
    "-r", "--rate", type=int, default=70, show_default=True, help="Rate to speak at"
)
voice_opt = click.option(
    "-v",
    "--voice",
    type=click.Choice(SAY_TUNED_VOICES),
    default="Fred",
    show_default=True,
    help="Voice to use",
)
# input_file_opt = click.option(
#     '-i',
#     "--input-file",
#     type=click.File(mode = "w"),
#     help="File to read text input from"
# )
output_file_opt = click.option(
    "-ao",
    "--audio-output-file",
    type=str,
    help="File to write audio output to",
)
audio_device_opt = click.option(
    "-ad",
    "--audio-device",
    type=str,
    help="Name of the audio device to send the signal to",
)
networks_send_opt = click.option(
    "-ns", "--network-send", type=str, help="Network address to send the signal to"
)
stereo_opt = click.option(
    "-st",
    "--stereo",
    is_flag=True,
    default=False,
    help="Whether or not to generate a stereo signal",
)
sample_size_opt = click.option(
    "-ss",
    "--sample-size",
    type=int,
    default=32,
    help="Sample size of the signal (1:32)",
)
sample_rate_opt = click.option(
    "-sr",
    "--sample-rate",
    type=int,
    default=22050,
    help="Sample rate of the signal (0:22050)",
)
quality_opt = click.option(
    "-q", "--quality", type=int, default=127, help="Quality of the signal (1:127)"
)
progress_bar_opt = click.option(
    "-pg",
    "--progress",
    is_flag=True,
    default=False,
    help="Whether or not to display an interactive progress bar",
)
interactive_opt = click.option(
    "-in",
    "--interactive",
    is_flag=True,
    default=False,
    help="Whether or not to display highlighted text",
)
text_color_opt = click.option(
    "-tc",
    "--text-color",
    type=click.Choice(SAY_COLORS),
    help="The text color to use when displaying highlighted text",
)
bg_color_opt = click.option(
    "-bc",
    "--bg-color",
    type=click.Choice(SAY_COLORS),
    help="The background color to use when displaying highlighted text",
)


SAY_OPTIONS = [
    rate_opt,
    voice_opt,
    output_file_opt,
    audio_device_opt,
    networks_send_opt,
    stereo_opt,
    sample_size_opt,
    sample_rate_opt,
    quality_opt,
    progress_bar_opt,
    interactive_opt,
    text_color_opt,
    bg_color_opt,
]

# Chord Options

chord_opt = click.option(
    "-c",
    "--chord",
    required=False,
    type=click.Choice([c.lower() for c in CHORDS.keys()]),
    help="An optional name of a chord to build using the note as root.",
)
inversion_opt = click.option(
    "-nv",
    "--inversion",
    default=[],
    required=False,
    type=lambda x: [int(i.strip()) for i in x.split(",")],
    help="A list of integers (eg: '0,1,-1') specifying the direction and amplitude to invert each note. The length of this list much match the number of notes in the chord.",
)
stack_opt = click.option(
    "-k",
    "--stack",
    default=0,
    required=False,
    type=int,
    help="Stack a chord up (eg: '1' or '2') or down(eg: '-1' or '-2').",
)

CHORD_OPTIONS = [chord_opt, inversion_opt, stack_opt]
