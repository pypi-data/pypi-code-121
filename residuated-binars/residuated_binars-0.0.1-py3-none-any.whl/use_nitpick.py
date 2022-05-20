# Copyright 2021-2022 Boris Shminke
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""
Use Nitpick
============

A wrapper ‘do all’ script.

-  runs ``generate_theories.py`` which creates a new ``hyp2`` folder
   with initial hypotheses templates
-  then for each cardinality from 2 to 100 (hard-coded)
-  runs ``add_task.py`` which creates a ``task[n]`` folder for a
   particular cardinality with a respective task for ``Nitpick`` added
   to the templates in ``hyp[n]``
-  runs ``check_assumptions.py`` on a ``task[n]`` folder
-  runs ``filter_theories.py`` which filter theories with no
   counter-examples found to a new folder ``hyp[n+1]``
-  if the ``hyp[n+1]`` folder is empty, the script stops (that means
   counter-examples were found for all original hypotheses)

"""
import os
from typing import List, Optional

from residuated_binars.add_task import TaskType, add_task
from residuated_binars.check_assumptions import check_assumptions
from residuated_binars.filter_theories import filter_theories
from residuated_binars.generate_theories import independence_check


def use_nitpick(
    max_cardinality: int,
    independent_assumptions: List[str],
    additional_assumptions: List[str],
    check_subset_independence: bool,
    server_info: Optional[str] = None,
) -> None:
    """
    incrementally search for finite counter-examples

    :param max_cardinality: maximal cardinality of a model to search for
    :param independent_assumptions: a list of assumption which independence
        we want to check
    :param additional_assumptions: a list of additional assumptions
    :param check_subset_independence: whether to check every assumption from
        the list against all the rest or against any combination of the rest
    :param server_info: an info string of an Isabelle server
    :returns:
    """
    cardinality = 2
    hypotheses = f"hyp{cardinality}"
    independence_check(
        hypotheses,
        independent_assumptions,
        additional_assumptions,
        check_subset_independence,
    )
    while cardinality <= max_cardinality and os.listdir(hypotheses) != []:
        tasks = f"task{cardinality}"
        add_task(hypotheses, tasks, TaskType.NITPICK, cardinality)
        check_assumptions(tasks, server_info)
        cardinality += 1
        hypotheses = f"hyp{cardinality}"
        filter_theories(tasks, hypotheses)
