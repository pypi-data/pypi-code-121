# Copyright 2022 Boris Shminke
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
Short scripts useful for other submodules
=========================================

"""
import os
import shutil
from glob import glob
from typing import Sequence


def remove_dirs(dir_list: Sequence[str]) -> None:
    """
    >>> os.path.exists("remove-test1")
    False
    >>> os.path.exists("remove-test2")
    False
    >>> os.mkdir("remove-test1")
    >>> os.mkdir(os.path.join("remove-test1", "some"))
    >>> os.mkdir("remove-test2")
    >>> os.path.exists(os.path.join("remove-test1", "some"))
    True
    >>> os.path.exists("remove-test2")
    True
    >>> remove_dirs(("remove-test*",))
    >>> os.path.exists("remove-test1")
    False
    >>> os.path.exists("remove-test2")
    False

    :param dir_list: subfolders of the current folder to remove completely
        (no questions asked!)
    :returns:
    """
    for some_dir in dir_list:
        for path in glob(os.path.join(".", some_dir)):
            shutil.rmtree(path)
