
from __future__ import annotations

import os
import shutil
from dataclasses import dataclass
from typing import Optional, Literal, Union, NamedTuple

# Types
VadEngine = Literal['smn', 'sm']
PathLike = Union[str, bytes, os.PathLike]
InaLabel = Literal['speech', 'music', 'noise', 'male', 'female']


class ResultFrame(NamedTuple):
    label: str
    start: float
    end: float
    confidence: Optional[float] = None


@dataclass
class InaConfig:
    # ffmpeg command name or path
    ffmpeg: str = os.environ.get('ffmpeg', 'ffmpeg')
    # temporary directory
    tmp_dir: Optional[str] = None
    # Whether to automatically convert input audio files to 16000hz wav
    auto_convert: bool = True


ina_config = InaConfig()


# test ffmpeg installation
if shutil.which(ina_config.ffmpeg) is None:
    print("ffmpeg program not found, please install it or specify ffmpeg command path in environment variable 'ffmpeg'")
