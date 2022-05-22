from pathlib import Path
from typing import Tuple, Union

import numpy as np
from pydub import AudioSegment


def read_audio(path: Union[str, Path]) -> Tuple[np.ndarray, int, int, int]:
    audio_segment = AudioSegment.from_file(path)

    return (
        np.array(audio_segment.get_array_of_samples()),
        audio_segment.frame_rate,
        audio_segment.sample_width,
        audio_segment.channels,
    )
