from typing import Any, Callable, Dict, Iterable, List, Set, Tuple, Type, Union

import pytest  # type:ignore


def _abstracts():
    # TODO: implemement plugin
    pass


@pytest.fixture
def abstracts() -> Callable:
    return _abstracts
