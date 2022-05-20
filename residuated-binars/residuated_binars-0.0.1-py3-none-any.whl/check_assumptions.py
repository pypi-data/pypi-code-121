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
Check Assumptions
==================

-  gets all theory files from a given directory
-  constructs a command for Isabelle server to process these files
-  saves the log of Isabelle server replies to the file named
   ``isabelle.out`` in the directory where the theory files are

This script depends on `Python client for Isabelle
server <https://pypi.org/project/isabelle-client>`__.

"""
import logging
import os
import sys
from typing import Optional

import nest_asyncio
from isabelle_client import get_isabelle_client
from isabelle_client.utils import start_isabelle_server


def get_customised_logger(task_folder: str) -> logging.Logger:
    """
    get a nice logger

    :param rask_folder: a base folder (and a task name)
    """
    logfile_name = os.path.join(task_folder, "isabelle.out")
    if os.path.exists(logfile_name):
        os.remove(logfile_name)
    logger = logging.getLogger(os.path.basename(task_folder))
    handler = logging.FileHandler(logfile_name)
    handler.setFormatter(logging.Formatter("%(asctime)s: %(message)s"))
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    return logger


def check_assumptions(path: str, server_info: Optional[str] = None) -> None:
    """
    ask Isabelle server to process all theory files in a given path

    :param path: a folder with theory files
    :param server_info: an info string of an Isabelle server
    :returns:
    """
    nest_asyncio.apply()
    theories = [
        theory_name[0]
        for theory_name in [
            os.path.splitext(theory_file) for theory_file in os.listdir(path)
        ]
        if theory_name[1] == ".thy"
    ]
    new_server_info = _start_server_if_needed(path, server_info)
    isabelle_client = get_isabelle_client(new_server_info)
    isabelle_client.logger = get_customised_logger(path)
    isabelle_client.use_theories(
        theories=theories, master_dir=get_abs_path(path), watchdog_timeout=0
    )
    if server_info is None:
        isabelle_client.shutdown()


def get_abs_path(path: str) -> str:
    """
    :param path: a path
    :returns: an absolute path, corrected to CygWin path for Windows
    """
    abs_path = os.path.abspath(path)
    if sys.platform == "win32":
        abs_path = abs_path.replace("C:\\", "/cygdrive/c/").replace("\\", "/")
    return abs_path


def _start_server_if_needed(path: str, server_info: Optional[str]) -> str:
    if server_info is None:
        new_server_info, _ = start_isabelle_server(
            log_file=os.path.join(path, "server.log"),
            name=os.path.basename(path),
        )
    else:
        new_server_info = server_info
    return new_server_info
