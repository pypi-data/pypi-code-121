import os
import sys
from pathlib import Path
from typing import Union

try:
    import flywheel
except (ModuleNotFoundError, ImportError) as e:
    raise ValueError("Please install `sdk` extra to use this module.") from e


# Typing shortcut
Container = Union[
    flywheel.Project,
    flywheel.Subject,
    flywheel.Session,
    flywheel.Acquisition,
    flywheel.FileEntry,
    flywheel.AnalysisOutput,
]

PathLike = Union[str, os.PathLike, Path]
