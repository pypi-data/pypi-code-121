from __future__ import annotations

import pathlib
import time
from typing import Any, Dict, Optional, Tuple, Union

import pandas as pd
from reil.datatypes.feature import FeatureSet


class FeatureSetDumper:
    def __init__(
            self, filename: str,
            path: Union[str, pathlib.PurePath] = '.',
            columns: Optional[Tuple[str]] = None) -> None:
        self._path = pathlib.PurePath(path)
        self._filename = filename if filename.endswith(
            '.csv') else f'{filename}.csv'
        pathlib.Path(self._path).mkdir(parents=True, exist_ok=True)
        if columns:
            with open(self._path / self._filename, 'a+', newline='') as f:
                pd.DataFrame([], columns=columns).to_csv(
                    f, header=True)

    def dump(
            self, component: FeatureSet,
            additional_info: Optional[Dict[str, Any]] = None,
    ) -> None:
        '''Write stats to file.'''
        attempts = 0
        while attempts < 5 and not self._dump(
                component, additional_info, self._filename, self._path):
            time.sleep(1)
            attempts += 1

        if attempts == 5:
            self._dump(
                component, additional_info,
                f'{self._filename}_temp', self._path)

    @staticmethod
    def _dump(
            component: FeatureSet,
            additional_info: Optional[Dict[str, Any]],
            filename: str, path: pathlib.PurePath) -> bool:
        '''Write stats to file.'''
        raise NotImplementedError
