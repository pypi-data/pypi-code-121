import random
from typing import Optional, List, Union, Tuple

from midi_utils import midi_to_freq, note_to_midi, freq_to_octave

from . import midi
from .utils import frange
from .constants import (
    SAY_PHONEME_SILENCE,
    SAY_PHONEME_MAX_DURATION,
    SAY_EMPHASIS_VELOCITY_STEPS,
    SAY_PHONEME_CLASSES,
    SAY_ALL_PHONEMES,
    SAY_TUNED_VOICES,
    SAY_TUNE_TAG,
    SAY_PHONEME_VOICE_CLASSES,
)


def get_emphasis(
    velocity: Optional[int],
    velocity_steps: Tuple[int, int] = SAY_EMPHASIS_VELOCITY_STEPS,
) -> str:
    """
    Translate a midi velocity value (0-127) into a phoneme emphasis value ("", "1", or "2")
    when provided with a tuple of steps (step_1, step_2) eg: (75, 100)
    """
    if not velocity:
        return ""
    if velocity > velocity_steps[1]:
        return "2"
    if velocity > velocity_steps[0]:
        return "1"
    return ""


def format_text(
    phoneme: str,
    duration: float,
    frequency: float,
    emphasis: int,
    is_silence: bool,
):
    """
    Format note text.
    TODO: Handle intra-note modulation? Use volm tag for velocity?
    """
    if is_silence:
        return f"{SAY_PHONEME_SILENCE} {{D {duration}}}\n"
    return f"{emphasis}{phoneme} {{D {duration}; P {frequency}:0 {frequency}:100}}\n"


def _get_phoneme_params(
    phoneme: str,
    randomize_phoneme: bool,
    velocity: int,
    randomize_velocity: bool,
    velocity_steps: Tuple[int, int],
) -> Tuple[str, int, int]:

    # handle phoneme randomization
    if randomize_phoneme:
        if randomize_phoneme == "all":
            phoneme = get_random()
        else:
            voice, style = randomize_phoneme.split(":")
            phoneme = get_random(voice, style)

    # handle velocity randomization
    if randomize_velocity:
        velocity = midi.random_velocity(*randomize_velocity)

    # generate emphasis
    emphasis = get_emphasis(velocity, velocity_steps)
    return phoneme, velocity, emphasis


def text_from_note(
    note: Union[int, str],  # accept a midi note or note name
    type: str,
    duration: float,
    velocity: int,
    phoneme: str,
    randomize_phoneme: Optional[str] = None,
    velocity_steps: Tuple[int, int] = SAY_EMPHASIS_VELOCITY_STEPS,
    randomize_velocity: Optional[Tuple[int, int]] = None,
    phoneme_duration: int = SAY_PHONEME_MAX_DURATION,
    octave: Optional[int] = None,
    sig_digits_duration: int = 2,
    randomize_segments: bool = False,
    **kwargs,
) -> str:
    """
    Generate say text for an individual note
    """
    is_silence = type == "silence"

    # lookup frequency
    if not is_silence:
        # allow note names
        frequency = midi_to_freq(note_to_midi(note))
        # octave adjustment
        if octave:
            frequency = freq_to_octave(frequency, octave)
    else:
        frequency = None

    phoneme, velocity, emphasis = _get_phoneme_params(
        phoneme, randomize_phoneme, velocity, randomize_velocity, velocity_steps
    )

    # return one note if the duration is short enough
    if duration <= phoneme_duration:
        return format_text(phoneme, duration, frequency, emphasis, is_silence)

    # otherwise create multiple phonemes which add up to the phoneme_duration
    texts = []
    for dur_step in frange(
        phoneme_duration, duration, phoneme_duration, sig_digits_duration
    ):

        # optionally randomize every segment.
        if randomize_segments:
            phoneme, velocity, emphasis = _get_phoneme_params(
                phoneme, randomize_phoneme, velocity, randomize_velocity, velocity_steps
            )

        text = format_text(phoneme, phoneme_duration, frequency, emphasis, is_silence)
        texts.append(text)

    # add final step and return
    text = format_text(phoneme, (duration - dur_step), frequency, emphasis, is_silence)
    texts.append(text)
    return "".join(texts)


def text_from_midi(
    midi_file: str,
    phoneme: Optional[str] = None,
    randomize_phoneme: Optional[str] = None,
    phoneme_duration: int = SAY_PHONEME_MAX_DURATION,
    loops: int = 1,
    octave: Optional[int] = None,
    velocity_steps: Tuple[int, int] = SAY_EMPHASIS_VELOCITY_STEPS,
    randomize_velocity: Optional[Tuple[int, int]] = None,
    randomize_segments: bool = False,
    sig_digits_duration: int = 5,
    **kwargs,
) -> str:
    """
    Generate a text blob for input to say from a midi file, optionally looping it.
    TODO: vary phonemes
    """
    text = f"{SAY_TUNE_TAG}\n"
    for _ in range(0, loops, 1):
        for note in midi.process(midi_file):
            text += text_from_note(
                phoneme=phoneme,
                phoneme_duration=phoneme_duration,
                octave=octave,
                velocity_steps=velocity_steps,
                randomize_velocity=randomize_velocity,
                randomize_phoneme=randomize_phoneme,
                sig_digits_duration=sig_digits_duration,
                randomize_segments=randomize_segments**note,
            )
    return text


def get_random(
    voice: Optional[str] = None,
    style: Optional[str] = None,
    choices: Optional[List[str]] = None,
) -> str:
    """
    Generate a random phoneme.
    Args:
        voice: Either Fred, Alex, or Veronica
        style: Either drone, noise, or note
        choices: A list of phonemes to choose from
    """
    if choices:
        return random.choice(choices)
    if (style and not voice) or (voice and not style):
        raise ValueError(
            "To use `style`/`voice` randomization, both parameters must be supplied."
        )
    if style and voice:
        voice = voice.title()  # allow for lowercase
        try:
            return random.choice(SAY_PHONEME_VOICE_CLASSES[voice][style])
        except KeyError:
            raise ValueError(
                f"Invalid `voice` '{voice}' or `style` '{style}'. "
                f"`voice` must be one of: {', '.join(SAY_TUNED_VOICES)}. "
                f"`style` must be one of: {', '.join(SAY_PHONEME_CLASSES)}"
            )
    return random.choice(SAY_ALL_PHONEMES)
