from pynextflow.entities import Tuple, Channel, Path, Val, Bash, Python
from pynextflow.entities.channel import ChannelFromPath, ChannelFromList
from pynextflow.executors.nextflow import Nextflow
from pynextflow.executors.tower import Tower
from pynextflow.executors.local import Local
from pynextflow.process import _process_decorator
from pynextflow.workflow import _workflow_decorator
from pynextflow.utils import pickle, unpickle

process = _process_decorator
workflow = _workflow_decorator


path = Path
val = Val
tuple = Tuple
bash = Bash
python = Python


def from_file_pairs(pattern: str, check_if_exists: bool = False) -> Channel:
    return Channel(
        f"Channel.fromFilePairs(\"{pattern}\", checkIfExists: {'true' if check_if_exists else 'false'})"
    )


def from_path(pattern: str) -> Channel:
    return ChannelFromPath(pattern)


def from_list(values: list) -> Channel:
    return ChannelFromList(values)
