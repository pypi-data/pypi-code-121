from __future__ import annotations

import pathlib
import re
from typing import Any, Dict, List, Optional
import pandas as pd
from reil.datatypes.feature import FeatureSet
from reil.datatypes.feature_array_dumper import FeatureSetDumper


class TrajectoryDumper(FeatureSetDumper):
    @staticmethod
    def _dump(
            component: FeatureSet,
            additional_info: Optional[Dict[str, Any]],
            filename: str, path: pathlib.PurePath) -> bool:
        '''Write stats to file.'''

        component_dict = component.value
        measure_names = re.findall(
            'daily_((?!dose).+?)_history', ' '.join(component_dict))

        temp = pd.DataFrame({m: component_dict[f'daily_{m}_history']
                             for m in measure_names})
        temp.drop(temp.tail(1).index, inplace=True)  # type: ignore
        temp['dose'] = component_dict['daily_dose_history']
        interval_history: List[int] = \
            component_dict['interval_history']  # type: ignore
        temp['decision_points'] = [
            a for t in interval_history
            for a in ([1] + [0] * (t-1))]

        temp['day'] = temp.index + 1  # type: ignore

        for k, v in component_dict.items():
            if k not in ['daily_dose_history',
                         'interval_history',
                         'day'] + [f'daily_{m}_history'
                                   for m in measure_names]:
                temp[k] = v

        for k, v in (additional_info or {}).items():
            temp[k] = v

        try:
            fname = pathlib.Path(path / filename)
            header = not fname.exists()
            with open(fname, 'a+', newline='') as f:
                temp.to_csv(f, mode='a+', header=header)
        except PermissionError:
            return False

        return True
