# -*- coding: utf-8 -*-
from glob import glob
from pathlib import Path
from typing import List
from typing import Union


def expand_path(path: Union[str, Path]) -> List[str]:
    paths: List[str] = glob(str(Path(path).expanduser()))
    return paths


def flatten_list(nested_list: Union[list, tuple]) -> list:

    supported_types = (list, tuple)

    results = []
    for item in nested_list:
        if not isinstance(item, supported_types):
            results.append(item)
        else:
            results.extend(flatten_list(item))

    return results
