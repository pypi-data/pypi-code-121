# This file is part of sympy2c.
#
# Copyright (C) 2013-2022 ETH Zurich, Institute for Particle and Astrophysics and SIS
# ID.
#
# This program is free software: you can redistribute it and/or modify it under the
# terms of the GNU General Public License as published by the Free Software Foundation,
# either version 3 of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
# PARTICULAR PURPOSE.  See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with this
# program.  If not, see <http://www.gnu.org/licenses/>.

import distutils.util
import functools
import hashlib
import os
import subprocess
import sys
import time
from contextlib import contextmanager

from sympy import Symbol

from .version import __version__


def get_platform():
    platform = distutils.util.get_platform()
    os, *version, machine = platform.split("-")
    if os != "macosx":
        return platform
    python_exe_path = subprocess.check_output(["which", "python"], text=True).strip()
    file_type = subprocess.check_output(["file", python_exe_path], text=True).strip()
    machine = file_type.split(" ")[-1]
    return "-".join([os, *version, machine])


def create_folder_if_not_exists(folder):
    if not os.path.exists(folder):
        try:
            os.makedirs(folder)
        except IOError:
            # might be triggered due to race conditin
            assert os.path.exists(folder)


def align(text):
    """removes | markers and everyting left to them"""
    lines = text.split("\n") + ["", ""]
    return "\n".join(line.partition("|")[2] for line in lines)


def concat_generator_results(function):
    """code generator methods here *yield* code blocks.
    This decorator then *returns* the concatendated blocks
    as a single string
    """

    @functools.wraps(function)
    def inner(*a, **kw):
        concat = "\n".join(function(*a, **kw))
        stripped = [line.rstrip() for line in concat.split("\n")]
        return "\n".join(stripped)

    return inner


def bound_symbols(*expressions):
    def union(generator):
        return set.union(*list(generator))

    all_symbols = union(expression.atoms(Symbol) for expression in expressions)
    free_symbols = union(expression.free_symbols for expression in expressions)

    return all_symbols - free_symbols


@contextmanager
def run_in_folder(folder):
    create_folder_if_not_exists(folder)
    current_folder = os.getcwd()
    try:
        os.chdir(folder)
        yield
    finally:
        os.chdir(current_folder)


@contextmanager
def timeit(task):
    print("start", task)
    started = time.time()
    yield
    print("time needed for {}: {:.2f} seconds".format(task, time.time() - started))


PRINT_INFO = os.environ.get("PRINTHASHES") is not None


class Hasher:
    def __init__(self):
        self._hasher = hashlib.md5()

    def update(self, name, what):
        self._hasher.update(what.encode("utf-8"))
        if PRINT_INFO:
            print("HASH", name, self._hasher.hexdigest(), what)

    def hexdigest(self):
        return self._hasher.hexdigest()[:8]


def base_cache_folder():
    home = os.path.expanduser("~")
    if sys.platform.startswith("darwin"):
        base_folder = os.path.join(home, "Library", "Cache")
    else:
        base_folder = os.path.join(home, "_cache")
    return base_folder


def sympy2c_cache_folder():
    fake_folder = os.environ.get("FAKE_CACHE_FOLDER")
    if fake_folder is not None:
        return fake_folder
    import numpy

    numpy_version = "_".join(numpy.__version__.split("."))
    sympy_version = "_".join(map(str, __version__))
    return os.path.join(
        base_cache_folder(),
        "sympy2c",
        sympy_version + "__np_" + numpy_version + "__" + get_platform(),
    )
