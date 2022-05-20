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
Script for adding a task
=========================

-  for every theory file in a given folder
-  creates a new file with the same name in another given folder
-  the output file includes the same one lemma as the input
-  but the ‘task’ is changed according to the script’s parameters

Possible task types:

- ``TaskType.NITPICK``, demands a ``cardinality`` to be provided as well
  (finite model search)
- ``TaskType.SLEDGEHAMMER`` (automated proof search)

Both task types have a hard-coded timeout of ``1000000`` seconds.

"""
import os
import re
from enum import Enum


class TaskType(Enum):
    """
    type of tasks to ask ``isabelle`` server to perform
    """

    SLEDGEHAMMER = "sledgehammer[timeout=1000000]"
    NITPICK = "nitpick[timeout=1000000,max_threads=0]"


def add_task(
    source_path: str,
    target_path: str,
    task_type: TaskType,
    cardinality: int = 1,
) -> None:
    """
    take theory files from an existing folder and change tasks in them to given
    ones

    :param source_path: a directory where to get theory files to add tasks to
    :param target_path: where to put new theory files with added tasks
    :param task_type: use Nitpick or Sledgehammer (disprove by finding a finite
        coutner-example or prove)
    :param cardinality: a cardinality of finite model to find (only for Nitpick
        tasks)
    :returns:
    """
    if not os.path.exists(target_path):
        os.mkdir(target_path)
    for theory_name in os.listdir(source_path):
        with open(
            os.path.join(source_path, theory_name), "r", encoding="utf-8"
        ) as theory_file:
            theory_text = theory_file.read()
        theory_text = re.sub(
            "datatype finite_type =.*\n",
            "datatype finite_type = "
            + " | ".join(map(lambda i: "C" + str(i), range(cardinality)))
            + "\n",
            re.sub(
                '"\n.*\n?oops',
                '"\n' + task_type.value + "\noops",
                theory_text,
            ),
        )
        with open(
            os.path.join(target_path, theory_name), "w", encoding="utf-8"
        ) as theory_file:
            theory_file.write(theory_text)
