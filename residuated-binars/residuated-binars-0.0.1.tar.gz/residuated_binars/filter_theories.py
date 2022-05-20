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
Filter Theories
================

-  reads from ``isabelle.out`` file from the input directory (this
   directory should be an output of ``check_assumption.py`` script)
-  filters only those theory files, for which neither finite model was
   found, nor the proof (depending on the task type)
-  copies filtered theory files from the input directory to another
   given directory

"""
import json
import os
import re
import shutil


def filter_theories(source_path: str, target_path: str) -> None:
    """
    get theory files from an existing folder and copy to another existing
    folder ones those of them, for which neither have a finite counter-example
    nor a proof

    :param source_path: where to look for processed theory files; should
        include an ``isabelle.out`` file with server's output
    :param target_path: where to put theory files without proofs or
        counter-examples
    :returns:
    """
    if not os.path.exists(target_path):
        os.mkdir(target_path)
    with open(
        os.path.join(source_path, "isabelle.out"), "r", encoding="utf-8"
    ) as out_file:
        final_line = [
            re.compile(".*FINISHED (.*)\n?").match(line)
            for line in out_file.readlines()
            if "FINISHED" in line
            and ("Sledgehammering" in line or "Nitpick" in line)
        ][0]
    if final_line is None:
        raise ValueError(f"Unexpected Isabelle server response: {final_line}")
    results = {
        node["theory_name"][6:]: [
            message["message"]
            for message in node["messages"]
            if any(
                nitpick_message in message["message"]
                for nitpick_message in (
                    "Try this: ",
                    "Timed out",
                    "Nitpick found a potentially spurious counterexample",
                    "Nitpick found a counterexample",
                    "Nitpick found no counterexample",
                )
            )
        ][0]
        for node in json.loads(final_line.group(1))["nodes"]
    }
    for result in results:
        if (
            "Nitpick found no counterexample" in results[result]
            or "Timed out" in results[result]
        ):
            shutil.copy(
                os.path.join(source_path, result + ".thy"),
                os.path.join(target_path, result + ".thy"),
            )
