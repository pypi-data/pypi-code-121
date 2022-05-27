import shutil
from typing import List, Tuple, Union, Text, Any

FilePath = str
Words = Union[Text, List[Text], List[List[Text]]]
__all__ = ["cmd_exists", "FilePath", "Words"]


def __dir__() -> List[Text]:
    return __all__


def __getattr__(name: str) -> Any:
    if name not in __all__:
        raise AttributeError(name)
    return globals()[name]


def cmd_exists(cmd: FilePath) -> bool:
    """
    Checks whether or not a desired command exists.

    Parameters
    ----------
    cmd : FilePath
        a desired command

    Return
    ------
    bool
        whether or not the desired command exists.
    """
    return shutil.which(cmd) is not None
