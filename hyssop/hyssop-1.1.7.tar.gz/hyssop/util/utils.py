# Copyright (C) 2020-Present the hyssop authors and contributors.
#
# This module is part of hyssop and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

'''
File created: August 21st 2020

Modified By: hsky77
Last Updated: August 27th 2020 12:59:54 pm
'''


import os
from typing import List, Dict
from importlib import import_module


def get_class(module: str, *attrs):
    """cls = get_class("module", "class / static function", "class static function")"""
    cls = import_module(module)
    for a in attrs:
        cls = getattr(cls, a)
    return cls


def join_to_abs_path(*paths) -> str:
    """os.path.join() + os.path.abspath() to return only linux path string, that means replace backslash with slash"""
    return os.path.abspath(os.path.join(*paths)).replace('\\', '/')


def join_path(*paths) -> str:
    """os.path.join() to return only linux path string, that means replace backslash with slash"""
    return os.path.join(*paths).replace('\\', '/')


def walk_to_file_paths(file_or_directory: str) -> List[str]:
    """get a list of absolutely path from the input path recursively"""
    file_paths = []
    if os.path.isdir(file_or_directory):
        for root, _, files in os.walk(file_or_directory):
            for i in range(len(files)):
                files[i] = join_path(os.path.abspath(root), files[i])

            if len(files) > 0:
                file_paths.extend(files)
    elif os.path.isfile(file_or_directory):
        file_paths.append(file_or_directory)

    return file_paths
