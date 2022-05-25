# Copyright (C) 2021- 2022 Cosmo Tech
# This document and all information contained herein is the exclusive property -
# including all intellectual property rights pertaining thereto - of Cosmo Tech.
# Any use, reproduction, translation, broadcasting, transmission, distribution,
# etc., to any person is prohibited unless it has been previously and
# specifically authorized by written means by Cosmo Tech.

import inspect

import numpy
import pandas

from . import descriptivestats
from ...core.parameterset import ParameterSet
from ...utilities import get_logger
from ...utilities.registry import Registry

StatisticsRegistry = Registry()

all_stats = dict(inspect.getmembers(descriptivestats, inspect.isfunction))

for func in all_stats.keys():
    if func in ["covariance", "correlation", "mode"]:
        params = {"Results key": func}
    else:
        params = {"Results key": "statistics"}
    StatisticsRegistry.register(all_stats[func], name=func, info=params)


class StatAnalyzer:
    """
    Statistical data analyzer
    """

    def __init__(self, list_of_statistics):
        self._list_of_statistics = []
        for key in list_of_statistics:
            if key in StatisticsRegistry.keys():
                self._list_of_statistics.append(key)
            else:
                logger = get_logger(__name__)
                logger = get_logger(__name__)
                logger.warning(
                    "Key {} is not in the StatisticsRegistry and will be ignored".format(
                        key
                    )
                )

    def run(self, data):
        df = ParameterSet.to_dataframe(data)
        # Filter to keep only columns having a numeric type
        df = df.select_dtypes(include=numpy.number)
        output_dfs = {}
        output_scalars = {}
        for func in self._list_of_statistics:
            if StatisticsRegistry.information[func]["Results key"] == func:
                # If the output estimator format is a DataFrame, add the DataFrame to the results
                output_dfs.update(StatisticsRegistry[func](df))
            else:
                # If the output estimator format is a Series, add the Series to the general DataFrame
                output_scalars.update(StatisticsRegistry[func](df))

        results = {"statistics": pandas.DataFrame(output_scalars)}
        results.update(output_dfs)
        return results
