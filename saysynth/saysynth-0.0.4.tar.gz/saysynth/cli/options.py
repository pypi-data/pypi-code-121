import click
from saysynth.constants import (
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
    help="The max duration (in milliseconds) of an individual phoneme",
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
    default="Victoria",
    show_default=True,
    help="Voice to use",
)

SAY_OPTIONS = [rate_opt, voice_opt]
