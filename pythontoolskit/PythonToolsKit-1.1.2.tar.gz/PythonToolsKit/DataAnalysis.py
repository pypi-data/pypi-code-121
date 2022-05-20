#!/usr/bin/env python3
# -*- coding: utf-8 -*-

###################
#    This package implements tools to build python package and tools.
#    Copyright (C) 2022  Maurice Lambert

#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.

#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.

#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <https://www.gnu.org/licenses/>.
###################

"""
This package implements tools to build python package and tools.

>>> from DataAnalysis import DataAnalysis
>>> from pprint import pprint
>>> data = [
...     {
...             "age": 45,
...             "pay": 80000,
...             "level": 12,
...     },
...     {
...             "age": 18,
...             "pay": 25000,
...             "level": 3,
...     },
...     {
...             "age": 45,
...             "pay": 40000,
...             "level": 3,
...     }
... ]
>>> analyse = DataAnalysis(data)
>>> pprint([x for x in analyse.get_medians()])
[statistictype(key='age', value=45),
 statistictype(key='pay', value=40000),
 statistictype(key='level', value=3)]
>>> pprint([x for x in analyse.get_deviations()])
[statistictype(key='age', value=12.727922061357855),
 statistictype(key='pay', value=23213.98046197353),
 statistictype(key='level', value=4.242640687119285)]
>>> pprint([x for x in analyse.get_variances()])
[statistictype(key='age', value=243),
 statistictype(key='pay', value=808333333.3333334),
 statistictype(key='level', value=27)]
>>> pprint([x for x in analyse.get_averages()])
[statistictype(key='age', value=36.0),
 statistictype(key='pay', value=48333.333333333336),
 statistictype(key='level', value=6.0)]
>>> pprint([x for x in analyse.get_maximums()])
[statistictype(key='age', value=valuetype(key='age', value=45, counter=2)),
 statistictype(key='pay', value=valuetype(key='pay', value=80000, counter=1)),
 statistictype(key='level', value=valuetype(key='level', value=12, counter=1))]
>>> pprint([x for x in analyse.get_minimums()])
[statistictype(key='age', value=valuetype(key='age', value=18, counter=1)),
 statistictype(key='pay', value=valuetype(key='pay', value=25000, counter=1)),
 statistictype(key='level', value=valuetype(key='level', value=3, counter=2))]
>>> pprint([x for x in analyse.count_values_by_keys()])
[statistictype(key='age', value=2),
 statistictype(key='pay', value=3),
 statistictype(key='level', value=2)]
>>> analyse.count_values_by_key('level')
statistictype(key='level', value=2)
>>> pprint([x for x in analyse.sort_by_value()])
[valuetype(key='level', value=3, counter=2),
 valuetype(key='level', value=12, counter=1),
 valuetype(key='age', value=18, counter=1),
 valuetype(key='age', value=45, counter=2),
 valuetype(key='pay', value=25000, counter=1),
 valuetype(key='pay', value=40000, counter=1),
 valuetype(key='pay', value=80000, counter=1)]
>>> pprint([x for x in analyse.sort_values_by_sum()])
[valuetype(key='level', value=3, counter=2),
 valuetype(key='level', value=12, counter=1),
 valuetype(key='age', value=18, counter=1),
 valuetype(key='age', value=45, counter=2),
 valuetype(key='pay', value=25000, counter=1),
 valuetype(key='pay', value=40000, counter=1),
 valuetype(key='pay', value=80000, counter=1)]
>>> pprint([x for x in analyse.sort_keys_by_sum()])
[('pay', 145000), ('age', 108), ('level', 18)]
>>> pprint([x for x in analyse.sort_by_counter()])
[valuetype(key='age', value=18, counter=1),
 valuetype(key='pay', value=80000, counter=1),
 valuetype(key='pay', value=25000, counter=1),
 valuetype(key='pay', value=40000, counter=1),
 valuetype(key='level', value=12, counter=1),
 valuetype(key='age', value=45, counter=2),
 valuetype(key='level', value=3, counter=2)]
>>> pprint([x for x in analyse.sort_by_key()])
[valuetype(key='age', value=45, counter=2),
 valuetype(key='age', value=18, counter=1),
 valuetype(key='level', value=12, counter=1),
 valuetype(key='level', value=3, counter=2),
 valuetype(key='pay', value=80000, counter=1),
 valuetype(key='pay', value=25000, counter=1),
 valuetype(key='pay', value=40000, counter=1)]
>>> pprint([x for x in analyse.keys_frequences()])
[statistictype(key='age', value=0.07441809186500006),
 statistictype(key='pay', value=99.91317889282416),
 statistictype(key='level', value=0.012403015310833345)]
>>> pprint([x for x in analyse.keys_values_frequences()])
[statistictype(key=valuetype(key='age', value=45, counter=2), value=0.06201507655416673),
 statistictype(key=valuetype(key='age', value=18, counter=1), value=0.012403015310833345),
 statistictype(key=valuetype(key='pay', value=80000, counter=1), value=55.12451249259265),
 statistictype(key=valuetype(key='pay', value=25000, counter=1), value=17.226410153935202),
 statistictype(key=valuetype(key='pay', value=40000, counter=1), value=27.562256246296325),
 statistictype(key=valuetype(key='level', value=12, counter=1), value=0.008268676873888896),
 statistictype(key=valuetype(key='level', value=3, counter=2), value=0.004134338436944448)]
>>> pprint([x for x in analyse.keys_values_count_frequences()])
[statistictype(key=valuetype(key='age', value=45, counter=2), value=22.22222222222222),
 statistictype(key=valuetype(key='age', value=18, counter=1), value=11.11111111111111),
 statistictype(key=valuetype(key='pay', value=80000, counter=1), value=11.11111111111111),
 statistictype(key=valuetype(key='pay', value=25000, counter=1), value=11.11111111111111),
 statistictype(key=valuetype(key='pay', value=40000, counter=1), value=11.11111111111111),
 statistictype(key=valuetype(key='level', value=12, counter=1), value=11.11111111111111),
 statistictype(key=valuetype(key='level', value=3, counter=2), value=22.22222222222222)]
>>> pprint([x for x in analyse.values_frequences()])
[statistictype(key=45, value=22.22222222222222),
 statistictype(key=18, value=11.11111111111111),
 statistictype(key=80000, value=11.11111111111111),
 statistictype(key=25000, value=11.11111111111111),
 statistictype(key=40000, value=11.11111111111111),
 statistictype(key=12, value=11.11111111111111),
 statistictype(key=3, value=22.22222222222222)]
>>> pprint([x for x in analyse.value_frequence(45)])
[45, 22.22222222222222]
>>> pprint([x for x in analyse.key_value_count_frequence(analyse.valuetype(key='pay', value=80000, counter=1))])
[valuetype(key='pay', value=80000, counter=1), 11.11111111111111]
>>> pprint([x for x in analyse.key_value_frequence(analyse.valuetype(key='pay', value=80000, counter=1))])
[valuetype(key='pay', value=80000, counter=1), 55.12451249259265]
>>> pprint([x for x in analyse.key_frequence('pay')])
['pay', 99.91317889282416]
>>> statistictypes = [DataAnalysis.statistictype(key=45, value=22.22222222222222),
...  DataAnalysis.statistictype(key=18, value=11.11111111111111),
...  DataAnalysis.statistictype(key=80000, value=11.11111111111111),
...  DataAnalysis.statistictype(key=25000, value=11.11111111111111),
...  DataAnalysis.statistictype(key=40000, value=11.11111111111111),
...  DataAnalysis.statistictype(key=12, value=11.11111111111111),
...  DataAnalysis.statistictype(key=3, value=22.22222222222222)]
>>> pprint([x for x in DataAnalysis.sort_statistictype_by_key(statistictypes)])
[statistictype(key=3, value=22.22222222222222),
 statistictype(key=12, value=11.11111111111111),
 statistictype(key=18, value=11.11111111111111),
 statistictype(key=45, value=22.22222222222222),
 statistictype(key=25000, value=11.11111111111111),
 statistictype(key=40000, value=11.11111111111111),
 statistictype(key=80000, value=11.11111111111111)]
>>> pprint([x for x in DataAnalysis.sort_statistictype_by_value(statistictypes)])
[statistictype(key=18, value=11.11111111111111),
 statistictype(key=80000, value=11.11111111111111),
 statistictype(key=25000, value=11.11111111111111),
 statistictype(key=40000, value=11.11111111111111),
 statistictype(key=12, value=11.11111111111111),
 statistictype(key=45, value=22.22222222222222),
 statistictype(key=3, value=22.22222222222222)]
>>> pprint([x for x in DataAnalysis.sort_dict_by_value({"a": 2, "b": 1, "c": 3})])
['b', 'a', 'c']
>>> pprint([x for x in analyse.get_values_by_key('pay')])
[valuetype(key='pay', value=80000, counter=1),
 valuetype(key='pay', value=25000, counter=1),
 valuetype(key='pay', value=40000, counter=1)]
>>> pprint([x for x in analyse.get_gt(DataAnalysis.valuetype(key='level', value=3, counter=2))])
[valuetype(key='age', value=45, counter=2),
 valuetype(key='age', value=18, counter=1),
 valuetype(key='pay', value=80000, counter=1),
 valuetype(key='pay', value=25000, counter=1),
 valuetype(key='pay', value=40000, counter=1),
 valuetype(key='level', value=12, counter=1),
 None]
>>> pprint([x for x in analyse.get_lt(DataAnalysis.valuetype(key='level', value=3, counter=2))])
[None, None, None, None, None, None, None]
>>> pprint([x for x in analyse.get_lt(DataAnalysis.valuetype(key='pay', value=25000, counter=1))])
[valuetype(key='age', value=45, counter=2),
 valuetype(key='age', value=18, counter=1),
 None,
 None,
 None,
 valuetype(key='level', value=12, counter=1),
 valuetype(key='level', value=3, counter=2)]
>>> analyse.count_lt(DataAnalysis.valuetype(key='pay', value=25000, counter=1))
6
>>> analyse.count_gt(DataAnalysis.valuetype(key='pay', value=25000, counter=1))
2
>>> analyse.count_value('level', 3)
valuetype(key='level', value=3, counter=2)
>>> analyse.get_minimum('level')
statistictype(key='level', value=valuetype(key='level', value=3, counter=2))
>>> analyse.get_maximum('level')
statistictype(key='level', value=valuetype(key='level', value=12, counter=1))
>>> analyse.get_sum('level')
statistictype(key='level', value=18)
>>> analyse.get_average('level')
statistictype(key='level', value=6.0)
>>> analyse.get_variance('level')
statistictype(key='level', value=27)
>>> analyse.get_deviation('level')
statistictype(key='level', value=4.242640687119285)
>>> analyse.get_median('level')
statistictype(key='level', value=3)
>>> data = [
...     {
...             "filename": "__init__.py",
...             "size": 255,
...             "lines": 5,
...             "modification": datetime.now(),
...     },
...     {
...             "filename": "WebScripts.py",
...             "size": 256520,
...             "lines": 3214,
...             "modification": datetime(2016, 6, 22, 12, 25, 48),
...     },
...     {
...             "filename": "future_python_file.py",
...     },
... ]
>>> analyse = DataAnalysis(data)
>>> pprint([x for x in analyse.get_sums()])
[statistictype(key='filename', value=None),
 statistictype(key='size', value=256775),
 statistictype(key='lines', value=3219),
 statistictype(key='modification', value=None)]
>>> analyse = DataAnalysis(data, fields=['size', 'lines', 'modification'])
>>> pprint([x for x in analyse.get_sums()])
[statistictype(key='size', value=256775),
 statistictype(key='lines', value=3219),
 statistictype(key='modification', value=None)]
>>> analyse = DataAnalysis(data, filter_=lambda x: x.get("size"))
>>> len(analyse.keys['filename'])
2
>>> analyse = DataAnalysis(data)
>>> len(analyse.keys['filename'])
3
>>> data = (
...     (1,2,3),
...     (500, 412, 561),
...     (721, 216, 683),
...     (10,25,56),
... )
>>> analyse = DataAnalysis(data)
>>> len(analyse.keys[0])
4
>>> analyse = DataAnalysis(data, filters={0: lambda x: x < 100})
>>> len(analyse.keys[0])
2
>>> analyse = DataAnalysis(data, fields=[1,3])
>>> len(analyse.keys[0])
0
>>> pprint([x for x in analyse.get_all_values()])
[valuetype(key=1, value=2, counter=1),
 valuetype(key=1, value=412, counter=1),
 valuetype(key=1, value=216, counter=1),
 valuetype(key=1, value=25, counter=1)]
>>> data = [{"key1": 1, "key2": 2}] * 3 + [{"key1": 2, "key2": 1}] * 2
>>> DataAnalysis.print_data(data, {"key1": "Column name", "key2": 5}, True)
|Column name|key2 |
|-----------|-----|
|1          |2    |
|1          |2    |
|1          |2    |
|1          |2    |
|2          |1    |
|2          |1    |
>>> DataAnalysis.print_data(data, {"key1": "Column name", "key2": 2}, True)
|Column name|ke|
|-----------|--|
|1          |2 |
|1          |2 |
|1          |2 |
|1          |2 |
|2          |1 |
|2          |1 |
>>> DataAnalysis.print_data(data)
|key1|key2|
|----|----|
|1   |2   |
|1   |2   |
|1   |2   |
|1   |2   |
|2   |1   |
|2   |1   |
>>> analysis = DataAnalysis(data)
>>> analysis.statistictypes_printer(analysis.get_deviations())
|key                    |value              |
|-----------------------|-------------------|
|key1                   |0.4898979485566356 |
|key2                   |0.4898979485566356 |
>>> analysis.statistictypes_printer(analysis.get_averages())
|key                    |value              |
|-----------------------|-------------------|
|key1                   |1.4                |
|key2                   |1.6                |
>>> analysis.valuetypes_printer(analysis.get_gt(analysis.valuetype(key="key1", value=0.5, counter=0)))
|key                    |value              |counter     |
|-----------------------|-------------------|------------|
|key1                   |1                  |3           |
|key1                   |2                  |2           |
|key2                   |2                  |3           |
|key2                   |1                  |2           |
>>> from DataAnalysis import PYPLOT
>>> if PYPLOT: analysis.statistictypes_chart(analysis.get_averages())
...
>>> for x in DataAnalysis.get_grouped_DataAnalysis(data, ("key1", "key2")): DataAnalysis.valuetypes_printer(x.get_values()); print()
...
|key                    |value              |counter     |
|-----------------------|-------------------|------------|
|key1                   |1                  |3           |
|key2                   |2                  |3           |
<BLANKLINE>
|key                    |value              |counter     |
|-----------------------|-------------------|------------|
|key1                   |2                  |2           |
|key2                   |1                  |2           |
<BLANKLINE>
>>> if PYPLOT: analysis.valuetypes_values_chart(analysis.get_all_values())
...
>>> if PYPLOT: analysis.valuetypes_counters_chart(analysis.get_values())
...
>>> import sys
>>> sys.modules["matplotlib"] = sys
>>> sys.modules["matplotlib.pyplot"] = sys
>>> from importlib import reload
>>> DataAnalysis = reload(sys.modules["DataAnalysis"]).DataAnalysis
>>> DataAnalysis.show_chart
Traceback (most recent call last):
  ...
AttributeError: type object 'DataAnalysis' has no attribute 'show_chart'
>>>

Run tests:
 ~# python -m doctest DataAnalysis.py
 ~# python DataAnalysis.py            # Verbose mode

1 items passed all tests:
  79 tests in __main__
79 tests in 65 items.
79 passed and 0 failed.
Test passed.

~# coverage run DataAnalysis.py
~# coverage report
Name              Stmts   Miss  Cover
-------------------------------------
DataAnalysis.py     290      0   100%
-------------------------------------
TOTAL               290      0   100%
~#
"""

__version__ = "0.0.1"
__author__ = "Maurice Lambert"
__author_email__ = "mauricelambert434@gmail.com"
__maintainer__ = "Maurice Lambert"
__maintainer_email__ = "mauricelambert434@gmail.com"
__description__ = """
This package implements tools to build python package and tools.
"""
license = "GPL-3.0 License"
__url__ = "https://github.com/mauricelambert/PythonToolsKit"

copyright = """
PythonToolsKit  Copyright (C) 2022  Maurice Lambert
This program comes with ABSOLUTELY NO WARRANTY.
This is free software, and you are welcome to redistribute it
under certain conditions.
"""
__license__ = license
__copyright__ = copyright

__all__ = ["DataAnalysis"]

from typing import Dict, TypeVar, List, Tuple, Union, Any
from collections.abc import Hashable, Iterable, Callable
from collections import defaultdict, namedtuple, Counter
from statistics import fmean, median, pstdev, variance
from functools import partial
from datetime import datetime
from operator import gt, lt

try:
    from matplotlib.pyplot import bar, show, title
except ImportError:
    PYPLOT = False
else:
    PYPLOT = True

Value = TypeVar("Value", str, int, float, complex, datetime, None)
DataAnalysis = TypeVar("DataAnalysis")


class DataAnalysis:

    valuetype = namedtuple("valuetype", ["key", "value", "counter"])
    statistictype = namedtuple("statistictype", ["key", "value"])

    def __init__(
        self,
        data: Iterable[Union[Dict[Hashable, Value]], Iterable[Value]],
        fields: List[Hashable] = None,
        filter_: Callable = None,
        filters: Dict[Hashable, Callable] = {},
    ):
        self.data = data
        self.fields = fields
        self.filter = filter_
        self.filters = filters

        self.keys = defaultdict(lambda: defaultdict(int))
        self.build_keys()

    @staticmethod
    def get_iterator_tuples(
        data: Iterable[Union[Dict[Hashable, Value]], Iterable[Value]]
    ) -> Iterable[Tuple[Hashable, Value]]:

        """
        This function returns an iterator of tuples from dict or Iterable.
        """

        if isinstance(data, dict):
            return data.items()
        else:
            return enumerate(data)

    def build_keys(self) -> None:

        """
        This function build data keys (reqired for all functions).
        """

        keys = self.keys
        fields = self.fields
        filters = self.filters
        fields_is_not_None = fields is not None
        datas = filter(self.filter, self.data) if self.filter else self.data

        get_iterator_tuples = self.get_iterator_tuples
        filters_get = filters.get

        for data in datas:
            elements = get_iterator_tuples(data)
            for key, value in elements:

                filter_ = filters_get(key)
                if (fields_is_not_None and key not in fields) or (
                    filter_ and not filter_(value)
                ):
                    continue

                keys[key][value] += 1

    def get_numbers_by_key(
        self, key: Hashable
    ) -> Union[List[Union[int, float]], None]:

        """
        This function returns a list of numbers by key value.
        """

        all_values = []
        for value, counter in self.keys[key].items():
            if isinstance(value, (int, float)):
                all_values.extend([value] * counter)

        return all_values or None

    def get_median(self, key: Hashable) -> statistictype:

        """
        This function returns median for a specific key.
        """

        return self.get_statistic(key, median)

    def get_medians(self) -> Iterable[statistictype]:

        """
        This function returns medians.
        """

        yield from self.get_statistics(median)

    def get_deviation(self, key: Hashable) -> statistictype:

        """
        This function returns deviation for a specific key.
        """

        return self.get_statistic(key, pstdev)

    def get_deviations(self) -> Iterable[statistictype]:

        """
        This function returns deviations.
        """

        yield from self.get_statistics(pstdev)

    def get_variance(self, key: Hashable) -> statistictype:

        """
        This function returns variance for a specific key.
        """

        return self.get_statistic(key, variance)

    def get_variances(self) -> Iterable[statistictype]:

        """
        This function returns variances.
        """

        yield from self.get_statistics(variance)

    def get_average(self, key: Hashable) -> statistictype:

        """
        This function returns average for a specific key.
        """

        return self.get_statistic(key, fmean)

    def get_averages(self) -> Iterable[statistictype]:

        """
        This function returns averages.
        """

        yield from self.get_statistics(fmean)

    def get_sum(self, key: Hashable) -> statistictype:

        """
        This function returns sum for a specific key.
        """

        return self.get_statistic(key, sum)

    def get_sums(self) -> Iterable[statistictype]:

        """
        This function returns sums.
        """

        yield from self.get_statistics(sum)

    def get_maximum(self, key: Hashable) -> statistictype:

        """
        This function returns maximum for a specific key.
        """

        return self.get_statistic(
            key,
            partial(max, key=lambda x: x.value),
            valuegetter=self.get_values_by_key,
        )

    def get_maximums(self) -> Iterable[statistictype]:

        """
        This function returns maximums.
        """

        yield from self.get_statistics(
            partial(max, key=lambda x: x.value),
            valuegetter=self.get_values_by_key,
        )

    def get_minimum(self, key: Hashable) -> statistictype:

        """
        This function returns minimum for a specific key.
        """

        return self.get_statistic(
            key,
            partial(min, key=lambda x: x.value),
            valuegetter=self.get_values_by_key,
        )

    def get_minimums(self) -> Iterable[statistictype]:

        """
        This function returns minimums.
        """

        yield from self.get_statistics(
            partial(min, key=lambda x: x.value),
            valuegetter=self.get_values_by_key,
        )

    def get_statistic(
        self,
        key: Hashable,
        function: Callable,
        valuegetter: Callable = None,
    ) -> statistictype:

        """
        This function returns specific statistic for a specific key.
        """

        data = (
            valuegetter(key) if valuegetter else self.get_numbers_by_key(key)
        )
        return (
            self.statistictype(key=key, value=function(data))
            if data
            else self.statistictype(key=key, value=data)
        )

    def get_statistics(
        self, function: Callable, valuegetter: Callable = None
    ) -> Iterable[statistictype]:

        """
        This function returns specific statistics.
        """

        get_statistic = self.get_statistic
        yield from (
            get_statistic(key, function, valuegetter)
            for key in self.keys.keys()
        )

    def count_value(self, key: Hashable, value: Value) -> valuetype:

        """
        This function returns valuetype representing
        a key value and counter of this value.
        """

        return self.valuetype(
            key=key, value=value, counter=self.keys[key][value]
        )

    def compare_values(
        self, function: Callable, value1: valuetype, value2: valuetype
    ) -> bool:

        """
        This function compares valuetypes.
        """

        return function(value1.value, value2.value)

    def compare_event_action(
        self,
        ref_value: valuetype,
        event: Callable,
        match_action: Callable,
        not_match_action: Callable = lambda x: None,
    ) -> Any:

        """
        This function calls match_action if event
        return is True else calls not_match_action.

        event signature: event(tested_value: valuetype, ref_value: valuetype) -> bool
        match_action signature: match_action(value: valuetype) -> Any
        not_match_action signature: not_match_action(value: valuetype) -> Any
        """

        yield from (
            match_action(tested_value)
            if event(tested_value, ref_value)
            else not_match_action(tested_value)
            for tested_value in self.get_values()
        )

    def count_gt(self, value: valuetype) -> int:

        """
        This function counts values greater than value.
        """

        return sum(
            self.compare_event_action(
                value,
                partial(self.compare_values, gt),
                lambda x: x.counter,
                lambda x: 0,
            )
        )

    def count_lt(self, value: valuetype) -> int:

        """
        This function counts values lesser than value.
        """

        return sum(
            self.compare_event_action(
                value,
                partial(self.compare_values, lt),
                lambda x: x.counter,
                lambda x: 0,
            )
        )

    def get_gt(self, value: valuetype) -> Iterable[valuetype]:

        """
        This function yields valuetype greater than value.
        """

        yield from (
            self.compare_event_action(
                value, partial(self.compare_values, gt), lambda x: x
            )
        )

    def get_lt(self, value: valuetype) -> Iterable[valuetype]:

        """
        This function yields valuetype lesser than value.
        """

        yield from (
            self.compare_event_action(
                value, partial(self.compare_values, lt), lambda x: x
            )
        )

    def get_values_by_key(self, key: Hashable) -> Iterable[valuetype]:

        """
        This function returns the list of
        keys, values and counters for a key.
        """

        valuetype = self.valuetype
        yield from (
            valuetype(key=key, value=value, counter=counter)
            for value, counter in self.keys[key].items()
        )

    def count_values_by_key(self, key: Hashable) -> statistictype:

        """
        This functions returns a statistictype with
        key and counter of differents values for this key.
        """

        return self.statistictype(key=key, value=len(self.keys[key]))

    def count_values_by_keys(self) -> Iterable[statistictype]:

        """
        This functions returns statistictypes with
        key and counter of differents values for this key.
        """

        yield from (self.count_values_by_key(key) for key in self.keys.keys())

    def get_values(self) -> Iterable[valuetype]:

        """
        This function returns a list of
        each keys, values and counters.
        """

        valuetype = self.valuetype
        yield from (
            valuetype(key=key, value=value, counter=counter)
            for key, values in self.keys.items()
            for value, counter in values.items()
        )

    def get_all_values(self) -> Iterable[valuetype]:

        """
        This function returns a list of
        all keys, values and counters.
        """

        valuetype = self.valuetype
        yield from (
            valuetype(key=key, value=value, counter=counter)
            for key, values in self.keys.items()
            for value, counter in values.items()
            for x in range(counter)
        )

    def sort_by_value(self, *args, **kwargs) -> valuetype:

        """
        This functions returns keys, values
        and counters sorted by values.
        """

        return sorted(
            self.get_values(), *args, key=lambda x: x.value, **kwargs
        )

    def sort_values_by_sum(self, *args, **kwargs) -> Iterable[valuetype]:

        """
        This functions returns keys, values
        and counters sorted by sum of values.
        """

        return sorted(
            self.get_values(),
            *args,
            key=lambda x: x.value * x.counter,
            **kwargs,
        )

    def get_keys_counter(self) -> Counter:

        """
        This function returns a Counter object
        representing key and sum of the values.
        """

        counter = Counter()

        for key, values in self.keys.items():
            for value, number in values.items():
                counter[key] += value * number

        return counter

    def get_values_counter(self) -> Counter:

        """
        This function returns a Counter object
        representing values and values count.
        """

        counter = Counter()

        for key, values in self.keys.items():
            for value, number in values.items():
                counter[value] += number

        return counter

    def get_keys_values_counter(self) -> Counter:

        """
        This function returns a Counter object
        representing valuetypes and sum of the values.
        """

        counter = Counter()
        valuetype = self.valuetype

        for key, values in self.keys.items():
            for value, number in values.items():
                counter[valuetype(key=key, value=value, counter=number)] += (
                    value * number
                )

        return counter

    def get_keys_values_count_counter(self) -> Counter:

        """
        This function returns a Counter object
        representing valuetypes and values count.
        """

        counter = Counter()
        valuetype = self.valuetype

        for key, values in self.keys.items():
            for value, number in values.items():
                counter[
                    valuetype(key=key, value=value, counter=number)
                ] += number

        return counter

    def sort_keys_by_sum(
        self, counter: Counter = None
    ) -> List[Tuple[Hashable, Value]]:

        """
        This functions returns keys and
        values sorted by sum of values.
        """

        counter = counter or self.get_keys_counter()
        return counter.most_common()

    def sort_by_counter(self, *args, **kwargs) -> Iterable[valuetype]:

        """
        This functions returns keys, values
        and counters sorted by counters.
        """

        return sorted(
            self.get_values(), *args, key=lambda x: x.counter, **kwargs
        )

    def sort_by_key(self, *args, **kwargs) -> Iterable[valuetype]:

        """
        This functions returns keys, values and counters sorted by counters.
        """

        return sorted(self.get_values(), *args, key=lambda x: x.key, **kwargs)

    @staticmethod
    def sort_dict_by_value(
        data: Dict[Hashable, Value], *args, **kwargs
    ) -> Dict[Hashable, Value]:

        """
        This functions returns the dict sorted by values.
        """

        return sorted(data, *args, key=lambda x: data[x], **kwargs)

    @staticmethod
    def sort_statistictype_by_value(
        data: Iterable[statistictype], *args, **kwargs
    ) -> Iterable[statistictype]:

        """
        This functions returns statistictypes sorted by values.
        """

        return sorted(data, *args, key=lambda x: x.value, **kwargs)

    @staticmethod
    def sort_statistictype_by_key(
        data: Iterable[statistictype], *args, **kwargs
    ) -> Iterable[statistictype]:

        """
        This functions returns statistictypes sorted by keys.
        """

        return sorted(data, *args, key=lambda x: x.key, **kwargs)

    @staticmethod
    def frequence(
        all_sum: Union[int, float],
        sample_sum: Union[int, float],
        pourcent: bool = True,
    ) -> Union[int, float]:

        """
        This function returns the frequence of sample in all.
        """

        return (
            (sample_sum / all_sum * 100)
            if pourcent
            else (sample_sum / all_sum)
        )

    def key_frequence(
        self,
        key: Hashable,
        pourcent: bool = True,
        counter: Counter = None,
        all_sum: Union[int, float] = None,
    ) -> statistictype:

        """
        This functions returns a statistictype of key frequence.
        """

        counter = counter or self.get_keys_counter()
        return self.statistictype(
            key=key,
            value=self.frequence(
                all_sum or sum(counter.values()), counter[key], pourcent
            ),
        )

    def keys_frequences(
        self, pourcent: bool = True, counter: Counter = None
    ) -> Iterable[statistictype]:

        """
        This generator yields statistictypes of keys frequences.
        """

        counter = counter or self.get_keys_counter()
        all_sum = sum(counter.values())
        yield from (
            self.key_frequence(key, pourcent, counter, all_sum)
            for key in counter.keys()
        )

    def key_value_frequence(
        self,
        value: valuetype,
        pourcent: bool = True,
        counter: Counter = None,
        all_sum: Union[int, float] = None,
    ) -> statistictype:

        """
        This function returns a statistictype of
        the frequency of the sum of the values in
        the key.
        """

        counter = counter or self.get_keys_values_counter()
        return self.statistictype(
            key=value,
            value=self.frequence(
                all_sum or sum(counter.values()), counter[value], pourcent
            ),
        )

    def keys_values_frequences(
        self, pourcent: bool = True, counter: Counter = None
    ) -> Iterable[statistictype]:

        """
        This generator yields statistictypes of
        the frequency of the sum of the values in
        the key.
        """

        counter = counter or self.get_keys_values_counter()
        all_sum = sum(counter.values())
        yield from (
            self.key_value_frequence(value, pourcent, counter, all_sum)
            for value in counter.keys()
        )

    def key_value_count_frequence(
        self,
        value: valuetype,
        pourcent: bool = True,
        counter: Counter = None,
        all_sum: Union[int, float] = None,
    ) -> statistictype:

        """
        This function returns a statistictype of
        the frequency of the sum of the values in
        the key.
        """

        counter = counter or self.get_keys_values_count_counter()
        return self.statistictype(
            key=value,
            value=self.frequence(
                all_sum or sum(counter.values()), counter[value], pourcent
            ),
        )

    def keys_values_count_frequences(
        self, pourcent: bool = True, counter: Counter = None
    ) -> Iterable[statistictype]:

        """
        This generator yields statistictypes of
        the frequency of the sum of the values in
        the key.
        """

        counter = counter or self.get_keys_values_count_counter()
        all_sum = sum(counter.values())
        yield from (
            self.key_value_count_frequence(value, pourcent, counter, all_sum)
            for value in counter.keys()
        )

    def value_frequence(
        self,
        value: Value,
        pourcent: bool = True,
        counter: Counter = None,
        all_sum: Union[int, float] = None,
    ) -> statistictype:

        """
        This functions returns a statistictype of value frequence.
        """

        counter = counter or self.get_values_counter()
        return self.statistictype(
            key=value,
            value=self.frequence(
                all_sum or sum(counter.values()), counter[value], pourcent
            ),
        )

    def values_frequences(
        self, pourcent: bool = True, counter: Counter = None
    ) -> Iterable[statistictype]:

        """
        This generator yields statistictypes of values frequences.
        """

        counter = counter or self.get_values_counter()
        all_sum = sum(counter.values())
        yield from (
            self.value_frequence(value, pourcent, counter, all_sum)
            for value in counter.keys()
        )

    @classmethod
    def get_grouped_DataAnalysis(
        cls: type,
        data: Iterable[Union[Dict[Hashable, Value]], Iterable[Value]],
        columns: Tuple[Hashable],
        *args,
        **kwargs,
    ) -> Iterable[DataAnalysis]:

        """
        This function returns a DataAnalysis instance
        for each group formatted by columns values.
        """

        groups = defaultdict(list)
        for key, element in cls.get_iterator_tuples(data):
            groups[tuple(element[column] for column in columns)].append(
                element
            )

        yield from (cls(x, *args, **kwargs) for x in groups.values())

    @staticmethod
    def statistictypes_printer(data: Iterable[statistictype]) -> None:

        """
        This function prints statistictypes.
        """

        DataAnalysis.print_data(
            data, {0: "key                    ", 1: "value              "}
        )

    @staticmethod
    def valuetypes_printer(data: Iterable[valuetype]) -> None:

        """
        This function prints valuetypes.
        """

        DataAnalysis.print_data(
            data,
            {
                0: "key                    ",
                1: "value              ",
                2: "counter     ",
            },
        )

    @staticmethod
    def print_data(
        data: Iterable[Union[Dict[Hashable, Value]], Iterable[Value]],
        headers: Dict[Hashable, Union[str, int]] = {},
        onetime: bool = False,
    ) -> None:

        """
        This function prints data.

        The headers are printed on the first
        row and set the width of the columns.
        """

        get_iterator_tuples = DataAnalysis.get_iterator_tuples

        def get_row(
            element: Dict[Hashable, Value], is_key: bool = False
        ) -> str:

            """
            This function format an element to be printed.
            """

            values = []
            append = values.append
            get = headers.get

            columns = get_iterator_tuples(element)

            for key, value in columns:
                key_ = get(key, key)
                if isinstance(key_, str):
                    key_length = len(key_)
                    key = key_
                else:
                    key_length = key_

                if is_key:
                    value = str(key)
                else:
                    value = str(value)

                value_length = len(value)
                if value_length > key_length:
                    append(value[:key_length])
                else:
                    append(value.ljust(key_length))

            return "|" + "|".join(values) + "|"

        first = next(iter(data))
        keys = get_row(first, is_key=True)
        line1 = get_row(first)
        separator = "".join(["|" if car == "|" else "-" for car in keys])

        if onetime:
            rows = [keys, separator, line1]
            append = rows.append
            for element in data:
                append(get_row(element))
            print("\n".join(rows))
        else:
            print(keys, separator, line1, sep="\n")
            for element in data:
                print(get_row(element))

    @staticmethod
    def statistictypes_chart(
        data: Iterable[statistictype],
        chart_title: str = "Statistictypes chart",
        *args,
        color=None,
        **kwargs,
    ) -> None:

        """
        This function shows a matplotlib chart of statistictypes.
        """

        keys = []
        values = []
        keys_append = keys.append
        values_append = values.append
        for element in data:
            keys_append(element.key)
            values_append(element.value)

        DataAnalysis.show_chart(
            values, keys, chart_title, *args, color=color, **kwargs
        )

    @staticmethod
    def valuetypes_values_chart(
        data: Iterable[valuetype],
        chart_title: str = "Valuetypes (values) chart",
        *args,
        color=None,
        **kwargs,
    ) -> None:

        """
        This function shows a matplotlib chart of valuetypes.
        """

        DataAnalysis.statistictypes_chart(
            data, chart_title, *args, color=color, **kwargs
        )

    @staticmethod
    def valuetypes_counters_chart(
        data: Iterable[valuetype],
        chart_title: str = "Valuetypes (counters) chart",
        *args,
        color=None,
        **kwargs,
    ) -> None:

        """
        This function shows a matplotlib chart of statistictypes.
        """

        keys = []
        values = []
        keys_append = keys.append
        values_append = values.append
        for element in data:
            keys_append(element.key)
            values_append(element.counter)

        DataAnalysis.show_chart(
            values, keys, chart_title, *args, color=color, **kwargs
        )

    @staticmethod
    def show_chart(
        values: Iterable,
        keys: Iterable,
        chart_title: str = "DataAnalysis chart",
        *args,
        color=None,
        **kwargs,
    ) -> None:

        """
        This function shows a matplotlib chart.
        """

        if not color:
            min_value = min(values)
            max_value = max(values)
            diff = max_value - min_value

            color = tuple(
                ((x - min_value) / diff, 0, 1 - (x - min_value) / diff)
                for x in values
            )

        plot, *_ = bar(
            range(len(values)),
            values,
            *args,
            color=color,
            tick_label=keys,
            **kwargs,
        )
        title(chart_title)
        plot.get_figure().canvas.parent().setWindowTitle("DataAnalysis chart")
        show()


if not PYPLOT:
    del DataAnalysis.statistictypes_chart
    del DataAnalysis.show_chart
    del DataAnalysis.valuetypes_counters_chart
    del DataAnalysis.valuetypes_values_chart

if __name__ == "__main__":
    import doctest

    doctest.testmod(verbose=True)
