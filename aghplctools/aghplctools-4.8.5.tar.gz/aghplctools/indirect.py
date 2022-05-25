"""DEPRECATED. Use online module"""
import warnings
import pathlib
from typing import Tuple
from .local_paths import AcquisitionSearch

warnings.warn(  # v4.5.0
    'the indirect module is no longer supported, please leverage the local_paths module and update your imports',
    DeprecationWarning,
    stacklevel=2,
)


def sequence_is_running() -> bool:
    """returns whether a sequence is running"""
    warnings.warn(  # v4.4.0
        'sequence_is_running will be deprecated, access AGDataPath properties instead',
        DeprecationWarning,
        stacklevel=2,
    )
    return AcquisitionSearch.sequence_is_running()


def current_num_and_file() -> Tuple[int, str]:
    """
    Returns the current number in the sequence and the name of the data file being acquired.

    :return: current file number, current file name
    """
    warnings.warn(  # v4.4.0
        'current_num_and_file will be deprecated, access AGDataPath properties instead',
        DeprecationWarning,
        stacklevel=2,
    )
    num, file = AcquisitionSearch.acquiring_instance_num_and_file()
    return num, str(file)


def current_file() -> str:
    """
    Returns the current data file name being acquired (next up in the sequence)

    :return: data file name
    """
    warnings.warn(  # v4.4.0
        'current_file will be deprecated, access AGDataPath properties instead',
        DeprecationWarning,
        stacklevel=2,
    )
    return current_num_and_file()[1]


def current_file_path() -> pathlib.Path:
    """
    Returns the full path for the file name being acquired (next up in the sequence)

    :return: full path to the data file
    """
    warnings.warn(  # v4.4.0
        'current_file_path will be deprecated, access AGDataPath properties instead',
        DeprecationWarning,
        stacklevel=2,
    )
    return AcquisitionSearch.acquiring_instance().current_file
