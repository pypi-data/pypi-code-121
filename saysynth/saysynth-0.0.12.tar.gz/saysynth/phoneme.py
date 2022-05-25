import random
from typing import Optional, List, Union, Tuple

from midi_utils import midi_to_freq, note_to_midi, freq_to_octave

from . import midi
from .utils import bpm_to_time, frange, rescale
from .constants import (
    SAY_PHONEME_SILENCE,
    SAY_PHONEME_MAX_DURATION,
    SAY_EMPHASIS_VELOCITY_STEPS,
    SAY_PHONEME_CLASSES,
    SAY_ALL_PHONEMES,
    SAY_TUNED_VOICES,
    SAY_TUNE_TAG,
    SAY_PHONEME_VOICE_CLASSES,
    SAY_VOLUME_RANGE,
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


def get_volume_tag(
    velocity: Optional[int] = None,
    volume_range: Tuple[float, float] = SAY_VOLUME_RANGE,
) -> str:
    """
    Translate a midi velocity value (0-127) into a pair of say volume tags, eg: "[[ volm +0.1 ]]"
    """
    if not velocity:
        return ""
    volume = rescale(velocity, [0, 127], volume_range)
    return f"[[ volm {volume} ]]"


def format_text(
    phoneme: str,
    duration: float,
    frequency: float,
    emphasis: int,
    volume_tag: str,
    is_silence: bool,
):
    """
    Format note text.
    TODO: Handle intra-note modulation? Use volm tag for velocity?
    """
    if is_silence:
        return f"{SAY_PHONEME_SILENCE} {{D {duration}}}"
    return f"{volume_tag} {emphasis}{phoneme} {{D {duration}; P {frequency}:0 {frequency}:100}}"


def _get_phoneme_params(
    phoneme: str,
    randomize_phoneme: bool,
    velocity: int,
    randomize_velocity: bool,
    velocity_steps: Tuple[int, int],
    volume_range: Tuple[float, float],
) -> Tuple[str, int, int]:

    # handle phoneme randomization
    if randomize_phoneme:
        if randomize_phoneme == "all":
            phoneme = get_random()
        elif "," in randomize_phoneme:
            choices = [c.strip() for c in randomize_phoneme.split(",")]
            phoneme = get_random(choices=choices)
        else:
            voice, style = randomize_phoneme.split(":")
            phoneme = get_random(voice, style)

    # handle velocity randomization
    if randomize_velocity:
        velocity = midi.random_velocity(*randomize_velocity)

    # generate emphasis
    emphasis = get_emphasis(velocity, velocity_steps)
    # generate volume tags
    volume_tag = get_volume_tag(velocity, volume_range)
    return phoneme, velocity, emphasis, volume_tag


def _get_phoneme_duration(
    phoneme_duration, phoneme_bpm=None, phoneme_count=1, phoneme_time_sig="4/4", **kwargs
):
    """
    calculate phoneme duration or pass it through
    """
    if phoneme_bpm:
        return int(bpm_to_time(phoneme_bpm, phoneme_count, phoneme_time_sig))
    return phoneme_duration


def text_from_note(
    note: Union[int, str],
    duration: float,
    velocity: int,
    phoneme: str,
    type: str = "note",
    randomize_phoneme: Optional[str] = None,
    velocity_steps: Tuple[int, int] = SAY_EMPHASIS_VELOCITY_STEPS,
    volume_range: Tuple[float, float] = SAY_VOLUME_RANGE,
    randomize_velocity: Optional[Tuple[int, int]] = None,
    phoneme_duration: int = SAY_PHONEME_MAX_DURATION,
    phoneme_bpm: float = None,
    phoneme_count: Optional[Union[str, float, int]] = None,
    phoneme_time_sig: Optional[str] = None,
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

    # compute phoneme duration
    phoneme_duration = _get_phoneme_duration(
        phoneme_duration, phoneme_bpm, phoneme_count, phoneme_time_sig
    )

    phoneme, velocity, emphasis, volume_tag = _get_phoneme_params(
        phoneme,
        randomize_phoneme,
        velocity,
        randomize_velocity,
        velocity_steps,
        volume_range,
    )

    # return one note if the duration is short enough

    if duration <= phoneme_duration:
        return format_text(
            phoneme,
            duration,
            frequency,
            emphasis,
            volume_tag,
            is_silence
        )

    # otherwise create multiple phonemes which add up to the phoneme_duration
    texts = []
    for dur_step in frange(
        phoneme_duration,
        duration,
        phoneme_duration,
        sig_digits_duration
    ):

        # optionally randomize every segment.
        if randomize_segments:
            phoneme, velocity, emphasis, volume_tag = _get_phoneme_params(
                phoneme,
                randomize_phoneme,
                velocity,
                randomize_velocity,
                velocity_steps,
                volume_range,
            )

        text = format_text(
            phoneme,
            phoneme_duration,
            frequency,
            emphasis,
            volume_tag,
            is_silence
        )
        texts.append(text)

    # add final step and return
    text = format_text(
        phoneme,
        (duration - dur_step),
        frequency,
        emphasis,
        volume_tag,
        is_silence
    )
    texts.append(text)
    return f" ".join(texts) + " "


def drone_from_note(
    note: Union[int, str], velocity: int = 100, phoneme: str = "m", **kwargs
) -> str:
    """
    Generate drone text from `text_from_note` options
    """
    max_duration = kwargs.pop("max_duration")

    # set each phonemes duration to the max phoneme duration
    phoneme_duration = _get_phoneme_duration(**kwargs)
    # override phoneme duration
    if max_duration < phoneme_duration:
        phoneme_duration = float(max_duration)
    phoneme_loops = kwargs.get("phoneme_loops")

    loops = 0
    total_duration = 0
    drone_text = f"{SAY_TUNE_TAG} "
    while True:
        drone_text += f"{text_from_note(note, phoneme_duration, velocity, phoneme, **kwargs)} "

        # check for max loops
        if phoneme_loops:
            loops += 1
            if loops >= phoneme_loops:
                break

        # check for max duration
        if max_duration:
            total_duration += phoneme_duration
            if total_duration >= max_duration:
                break
    return drone_text


def text_from_midi(
    midi_file: str,
    phoneme: Optional[str] = None,
    randomize_phoneme: Optional[str] = None,
    phoneme_duration: int = SAY_PHONEME_MAX_DURATION,
    phoneme_bpm: float = None,
    phoneme_count: Optional[Union[str, float, int]] = None,
    phoneme_time_sig: Optional[str] = None,
    loops: int = 1,
    octave: Optional[int] = None,
    velocity_steps: Tuple[int, int] = SAY_EMPHASIS_VELOCITY_STEPS,
    volume_range: Tuple[float, float] = SAY_VOLUME_RANGE,
    randomize_velocity: Optional[Tuple[int, int]] = None,
    randomize_segments: bool = False,
    sig_digits_duration: int = 5,
    **kwargs,
) -> str:
    """
    Generate a text blob for input to say from a midi file, optionally looping it.
    TODO: vary phonemes
    """
    text = f"{SAY_TUNE_TAG} "
    for _ in range(0, loops, 1):
        for note in midi.process(midi_file):
            text += (
                text_from_note(
                    phoneme=phoneme,
                    phoneme_duration=phoneme_duration,
                    phoneme_bpm=phoneme_bpm,
                    phoneme_count=phoneme_count,
                    phoneme_time_sig=phoneme_time_sig,
                    octave=octave,
                    velocity_steps=velocity_steps,
                    volume_range=volume_range,
                    randomize_velocity=randomize_velocity,
                    randomize_phoneme=randomize_phoneme,
                    sig_digits_duration=sig_digits_duration,
                    randomize_segments=randomize_segments,
                    **note,
                )
                + " "
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
