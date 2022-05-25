import click

from midi_utils.constants import CHORDS
from saysynth.constants import (
    SAY_COLORS,
    SAY_EMPHASIS_VELOCITY_STEPS,
    SAY_ALL_PHONEMES,
    SAY_TUNED_VOICES,
    SAY_PHONEME_CLASSES,
    SAY_PHONEME_MAX_DURATION,
    SAY_VOLUME_RANGE,
)


def group_options(*options):
    def wrapper(function):
        for option in reversed(options):
            function = option(function)
        return function

    return wrapper


def prepare_options_for_say(text: str, **kwargs):
    # handle some param edge cases
    rp = kwargs.get("randomize_phoneme")
    if rp and ":" in rp:
        kwargs["voice"] = rp.split(":")[0].strip().title()
    kwargs["text"] = text
    kwargs["use_tempfile"] = True
    return kwargs


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
        "Alternatively pass a list of phonemes (eg 'm,l,n') or a voice and style, eg: Fred:drone. "
        f"Valid voices include: {', '.join(SAY_TUNED_VOICES)}. "
        f"Valid styles include: {', '.join(SAY_PHONEME_CLASSES)}."
    ),
)
randomize_segments_opt = click.option(
    "-rs",
    "--randomize-segments",
    is_flag=True,
    help="Randomize every segment of a phoneme",
)

phoneme_duration_opt = click.option(
    "-pd",
    "--phoneme-duration",
    default=SAY_PHONEME_MAX_DURATION,
    show_default=True,
    type=float,
    help="The max duration in ms of an individual phoneme",
)
phoneme_bpm_opt = click.option(
    "-pb",
    "--phoneme-bpm",
    default=None,
    type=float,
    help="The bpm to use when calculating phoneme duration",
)
phoneme_count_opt = click.option(
    "-pc",
    "--phoneme-count",
    default=4,
    type=str,
    show_default=True,
    help="The note length to use when calculating phoneme duration (eg: 1/8 or 0.123 or 3)",
)
phoneme_time_sig_opt = click.option(
    "-pts",
    "--phoneme-time-sig",
    default="4/4",
    type=str,
    show_default=True,
    help="The time signature to use when calculating phoneme duration",
)

PHONEME_OPTIONS = [
    phoneme_opt,
    randomize_phoneme_opt,
    randomize_segments_opt,
    phoneme_duration_opt,
    phoneme_bpm_opt,
    phoneme_count_opt,
    phoneme_time_sig_opt,
]

# Velocity Options

velocity_opt = click.option(
    "-vl",
    "--velocity",
    type=int,
    show_default=True,
    default=110,
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
volume_range_opt = click.option(
    "-vr",
    "--volume-range",
    type=float,
    nargs=2,
    show_default=True,
    default=SAY_VOLUME_RANGE,
    help="The mix and maximum volumes (range 0.0:1.0) to use when mapping from midi velocities",
)
randomize_velocity_opt = click.option(
    "-rv",
    "--randomize-velocity",
    type=int,
    nargs=2,
    help="Randomize a note's emphasis by supplying a min and max midi velocity (eg: -rv 40 120)",
)

VELOCITY_OPTIONS = [
    velocity_opt,
    velocity_steps_opt,
    volume_range_opt,
    randomize_velocity_opt,
]

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
    default="white",
    help="The text color to use when displaying highlighted text",
)
bg_color_opt = click.option(
    "-bc",
    "--bg-color",
    type=click.Choice(SAY_COLORS),
    default="black",
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
chord_velocities_opt = click.option(
    "-cv",
    "--chord-velocities",
    required=False,
    type=lambda x: [int(i.strip()) for i in x.split(",")] if x else [],
    help="A list of integers (eg: '50,100,127') specifying the midi velocity each note i the chord. The length of this list much match the number of notes in the chord. --volume-range anyd --velocity-steps also modify this parameter",
)
chord_inversions_opt = click.option(
    "-ci",
    "--chord-inversions",
    "inversions",
    default=[],
    required=False,
    type=lambda x: [int(i.strip()) for i in x.split(",")] if x else [],
    help="A list of integers (eg: '0,1,-1') specifying the direction and amplitude to invert each note. The length of this list much match the number of notes in the chord (post-stack).",
)
chord_stack_opt = click.option(
    "-cs",
    "--chord-stack",
    "stack",
    default=0,
    required=False,
    type=int,
    help="Stack a chord up (eg: '1' or '2') or down(eg: '-1' or '-2').",
)

CHORD_OPTIONS = [chord_opt, chord_inversions_opt, chord_stack_opt, ]
