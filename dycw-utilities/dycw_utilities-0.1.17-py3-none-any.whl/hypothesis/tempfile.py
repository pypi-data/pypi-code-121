from hypothesis.strategies import SearchStrategy
from hypothesis.strategies import just

from dycw_utilities.tempfile import TemporaryDirectory


def temp_dirs() -> SearchStrategy[TemporaryDirectory]:
    return just(TemporaryDirectory())
