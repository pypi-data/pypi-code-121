import os
from multiprocessing import Pool
import subprocess
from typing import Optional, List, Dict, Any

from . import utils
from .constants import (
    SAY_MAX_SAMPLE_RATE,
    SAY_SAMPLE_SIZES,
    SAY_DATA_TYPES,
    SAY_ENDIANESS,
    SAY_EXECUTABLE,
    SAY_COLORS,
)


def _gen_data_format_arg(
    endianess: str, data_type: str, sample_size: int, sample_rate: int
):
    """
    Generate a string to pass to --data-format
    """
    if endianess not in SAY_ENDIANESS:
        raise ValueError(
            "Invalid `endianess`. Choose from: LE (little endlian) or BE (big endian)"
        )
    if data_type not in SAY_DATA_TYPES:
        raise ValueError(
            "Invalid `data_type`. Choose from: F (float), I (integer), UI (unsigned integer)"
        )
    if sample_size not in SAY_SAMPLE_SIZES:
        raise ValueError(
            f'Invalid `sample_size`. Choose from: {", ".join(SAY_SAMPLE_SIZES)}'
        )

    # allow pass passing sample rate as small number (eg: 24 -> 24000)
    if sample_rate < 1000:
        sample_rate *= 1000

    # don't allow a sample rate greater than the maximum
    if sample_rate > SAY_MAX_SAMPLE_RATE:
        sample_rate = SAY_MAX_SAMPLE_RATE

    return f"{endianess}{data_type}{sample_size}@{int(sample_rate)}"


def _gen_interactive_arg(text_color: str = "white", bg_color: str = "black"):
    """
    Generate a string to pass to --interactive
    """
    if bg_color and not text_color:
        text_color = "white"  # default text color if only background is supplied
    if text_color not in SAY_COLORS:
        raise ValueError(f'Invalid `text_color`, choose from: {", ".join(SAY_COLORS)}')
    if bg_color not in SAY_COLORS:
        raise ValueError(f'Invalid `bg_color`, choose from: {", ".join(SAY_COLORS)}')
    return f"--interactive={text_color}/{bg_color}"


def cmd(
    text: Optional[str] = None,
    voice: Optional[str] = None,
    rate: Optional[int] = None,
    input_file: Optional[str] = None,
    audio_output_file: Optional[str] = None,
    service_name: Optional[str] = None,
    network_send: Optional[str] = None,
    audio_device: Optional[str] = None,
    stereo: bool = False,  # whether or not
    endianness: str = "LE",  # LE/BE
    data_type: str = "F",  # F/I/U
    sample_size: Optional[int] = 32,
    sample_rate: Optional[int] = 22050,
    quality: int = 127,
    progress: bool = False,
    interactive: bool = False,
    text_color: Optional[str] = None,
    bg_color: Optional[str] = None,
    executable: str = SAY_EXECUTABLE,
    **kwargs,
) -> List:
    """
    A python wrapper around the say command.
    OPTIONS
        string
            Specify the text to speak on the command line. This can consist of multiple arguments, which are considered to be separated
            by spaces.

        -f file, --input-file=file
            Specify a file to be spoken. If file is - or neither this parameter nor a message is specified, read from standard input.

        -v voice, --voice=voice
            Specify the voice to be used. Default is the voice selected in System Preferences. To obtain a list of voices installed in
            the system, specify '?' as the voice name.

        -r rate, --rate=rate
            Speech rate to be used, in words per minute.

        -o out.aiff, --output-file=file
            Specify the path for an audio file to be written. AIFF is the default and should be supported for most voices, but some
            voices support many more file formats.

        -n name, --network-send=name
        -n name:port, --network-send=name:port
        -n :port, --network-send=:port
        -n :, --network-send=:
            Specify a service name (default "AUNetSend") and/or IP port to be used for redirecting the speech output through AUNetSend.

        -a ID, --audio-device=ID
        -a name, --audio-device=name
            Specify, by ID or name prefix, an audio device to be used to play the audio. To obtain a list of audio output devices,
            specify '?' as the device name.

        --progress
            Display a progress meter during synthesis.

        -i, --interactive, --interactive=markup
            Print the text line by line during synthesis, highlighting words as they are spoken. Markup can be one of

            o   A terminfo capability as described in terminfo(5), e.g. bold, smul, setaf 1.

            o   A color name, one of black, red, green, yellow, blue, magenta, cyan, or white.

            o   A foreground and background color from the above list, separated by a slash, e.g. green/black. If the foreground color
                is omitted, only the background color is set.

            If markup is not specified, it defaults to smso, i.e. reverse video.

        If the input is a TTY, text is spoken line by line, and the output file, if specified, will only contain audio for the last line
        of the input.  Otherwise, text is spoken all at once.

    AUDIO FORMATS
        Starting in MacOS X 10.6, file formats other than AIFF may be specified, although not all third party synthesizers may initially support them. In simple cases, the
        file format can be inferred from the extension, although generally some of the options below are required for finer grained control:

        --file-format=format
            The format of the file to write (AIFF, caff, m4af, WAVE). Generally, it's easier to specify a suitable file extension for the output file. To obtain a list of
            writable file formats, specify '?' as the format name.

        --data-format=format
            The format of the audio data to be stored. Formats other than linear PCM are specified by giving their format identifiers (aac, alac). Linear PCM formats are
            specified as a sequence of:

            Endianness (optional)
                One of BE (big endian) or LE (little endian). Default is native endianness.

            Data type
                One of F (float), I (integer), or, rarely, UI (unsigned integer).

            Sample size
                One of 8, 16, 24, 32, 64.

            Most available file formats only support a subset of these sample formats.

            To obtain a list of audio data formats for a file format specified explicitly or by file name, specify '?' as the format name.

            The format identifier optionally can be followed by @samplerate and /hexflags for the format.

        --channels=channels
            The number of channels. This will generally be of limited use, as most speech synthesizers produce mono audio only.

        --bit-rate=rate
            The bit rate for formats like AAC. To obtain a list of valid bit rates, specify '?' as the rate. In practice, not all of these bit rates will be available for a
            given format.

        --quality=quality
            The audio converter quality level between 0 (lowest) and 127 (highest).

    """
    if not text and not input_file:
        raise ValueError("Must provide `text` or `input_file`")

    # override text if input file is provided
    elif input_file:
        text = None
        # verify that input file exists
        if not os.path.exists(input_file):
            raise ValueError("`input_file`: {input_file} does not exist!")

    # verify file_format:
    if audio_output_file:
        if not (
            audio_output_file.lower().endswith(".wav")
            or audio_output_file.lower().endswith(".aiff")
        ):
            raise ValueError("`output_file` must be of type .wav or .aiff")

    # verify quality
    if quality < 0 or quality > 127:
        raise ValueError("`quality` must be between 0 and 127")

    # construct base command
    cmd = [executable]
    if text:
        cmd.append(text)
    elif input_file:
        cmd.extend(["-f", input_file])
    if voice:
        cmd.extend(["-v", voice])
    if rate:
        cmd.extend(["-r", rate])

    # output_file specific params
    if audio_output_file:
        cmd.extend(["-o", audio_output_file])
        # # always specify data format
        # cmd.append(
        #     f"--data-format={_gen_data_format_arg(endianness, data_type, sample_size, sample_rate)}"
        # )
        if stereo:
            cmd.append(f"--channels=2")
    else:
        cmd.append(f"--quality={quality}")
        # handle network output if output file is not specified
        if service_name:
            cmd.extend(["-n", service_name])
        if network_send:
            cmd.extend(f"--network-send={network_send}")
        if audio_device:
            cmd.extend(["-a", audio_device])

    # progress bar
    if progress:
        cmd.append("--progress")

    # interactivity
    if interactive:
        cmd.append(_gen_interactive_arg(text_color, bg_color))
    return [str(a) for a in cmd]


def run(args: Optional[List] = None, use_tempfile: bool = True, **kwargs):
    """
    Execute a command given a list of arguments () outputted by `cmd`
    or by supplying the kwargs that `cmd` accepts
    """
    # write text as input file
    tempfile = None
    if kwargs.get("text") and use_tempfile:
        text = kwargs.pop("text")
        tempfile = utils.make_tempfile()
        with open(tempfile, "w") as f:
            f.write(text)
        kwargs["input_file"] = tempfile

    if not args:
        args = cmd(**kwargs)
    try:
        p = subprocess.Popen(args, stdout=subprocess.PIPE)
        p.wait()
    finally:
        if tempfile:
            os.remove(tempfile)


def _run_fx(kwargs: Dict[str, Any]):
    """
    utility for passing kwargs into run fx
    """
    return run(**kwargs)


def spawn(commands: List[Dict[str, Any]]):
    """
    Spawn multiple say processes in parallel
    """
    Pool(len(commands)).map(_run_fx, commands)
