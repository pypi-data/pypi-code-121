import audioop
import numpy as np
import soundfile
import subprocess
from pathlib import Path

from .constants import SAMPLING_RATE, FRAME_SIZE, BYTE_ENCODING
from .log import logger
from .utils import my_assert

# Initialize path to faad
FAAD_PATH1 = Path('/usr/local/bin/faad')
FAAD_PATH2 = Path('/usr/bin/faad')
if FAAD_PATH1.exists():
    FAAD_PATH = FAAD_PATH1
elif FAAD_PATH2.exists():
    FAAD_PATH = FAAD_PATH2
else:
    FAAD_PATH = None


def load_audio_file(file_name) -> np.ndarray:
    with soundfile.SoundFile(file_name) as f:
        if f.samplerate != SAMPLING_RATE:
            raise ValueError("Wrong sampling rate")
        logger.debug(f"File has {f.frames} samples and {f.channels} channels")
        my_assert(f.channels <= 2, "Too many channels")
        n_chunks = ((f.frames - 1) // FRAME_SIZE) + 1
        res = np.zeros((n_chunks * FRAME_SIZE, f.channels), dtype='float64', order='C')
        assert res.shape[0] >= f.frames
        to_read = f.frames
        read = f.read(to_read, out=res)
        # Workaround
        while len(read) == 0:  # failed to read
            logger.debug("failed read, chopping a bit of the file")
            to_read -= 4096
            if to_read <= 0:
                raise RuntimeError("Failed to read file with soundfile")
            read = f.read(to_read, out=res)
    if res.shape[1] == 1:
        res = np.outer(res, np.ones((2,)))
    assert res.shape == (n_chunks * FRAME_SIZE, 2)
    logger.info(f"Loaded {n_chunks} chunks")
    return res


def is_m4a_supported() -> bool:
    return FAAD_PATH is not None


def load_m4a_file(file_name: str) -> np.ndarray:
    if FAAD_PATH is None:
        raise RuntimeError("FAAD missing")
    res = subprocess.run([FAAD_PATH, "-b", "1", "-f", "2", "-w", file_name], capture_output=True)
    if res.returncode != 0:
        raise ValueError("Failed to decode file")

    # parse file info
    rate = None
    channels = 0
    for line in res.stderr.decode('UTF8').splitlines():
        if line.startswith('Samplerate:'):
            rate = int(line.split('\t')[-1])
        elif line.startswith('Total channels:'):
            channels = int(line.split('\t')[-1])
    if rate != SAMPLING_RATE:
        raise ValueError("Wrong sampling rate")
    if not 1 <= channels <= 2:
        raise ValueError("Wrong number of channels")

    # reformat audio output
    data = res.stdout
    if channels == 2:
        left = np.frombuffer(audioop.tomono(data, 2, 1, 0), dtype='i2')
        right = np.frombuffer(audioop.tomono(data, 2, 0, 1), dtype='i2')
    else:
        left = np.frombuffer(data, dtype='i2')
        right = left
    assert len(left) == len(right)
    n_frames = len(left)
    n_chunks = ((n_frames - 1) // FRAME_SIZE) + 1
    sig = np.zeros((n_chunks * FRAME_SIZE, 2))
    sig[:n_frames, 0] = left / 32768
    sig[:n_frames, 1] = right / 32768
    return sig


def save_audio_file(file_name, data: bytes):
    sig = np.frombuffer(data, dtype=BYTE_ENCODING)
    soundfile.write(file_name, sig, SAMPLING_RATE, 'PCM_16')
