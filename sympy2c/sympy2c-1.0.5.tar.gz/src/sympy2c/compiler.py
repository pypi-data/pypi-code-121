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

import glob
import hashlib
import importlib
import os
import shutil
import subprocess
import sys
import tempfile
import threading
import time
import warnings
from contextlib import contextmanager
from functools import partial

from .build_gsl import install_gsl_if_needed
from .build_lsoda import install_lsoda_if_needed
from .build_lsoda_fast import install_lsoda_fast_if_needed
from .integral import IntegralFunctionWrapper
from .ode_fast import read_new_traces
from .utils import (
    align,
    base_cache_folder,
    create_folder_if_not_exists,
    get_platform,
    sympy2c_cache_folder,
)

HERE = os.path.dirname(os.path.abspath(__file__))


if os.environ.get("TOX_PACKAGE") is not None:
    print()
    print("*" * 80)
    print("*" * 80)
    print()
    print("HERE", HERE)
    print()
    print("*" * 80)
    print("*" * 80)
    print()


def compile_if_needed_and_load(
    module_wrapper, root_folder, lsoda_root_folder, gsl_root, compilation_flags
):
    cache_folder = base_cache_folder()

    if gsl_root is None:
        gsl_root = os.path.join(cache_folder, "gsl", get_platform())
    if not os.path.exists(gsl_root) or not os.listdir(gsl_root):
        download_folder = tempfile.mkdtemp()
        install_gsl_if_needed(download_folder, gsl_root)

    lsoda_object_file = install_lsoda_if_needed(lsoda_root_folder)
    lsoda_fast_static_lib = install_lsoda_fast_if_needed(lsoda_root_folder)

    libf2c_path = compile_libf2c()

    bf = build_folder(module_wrapper, compilation_flags, root_folder)

    generate_files_and_compile_if_needed(
        wrapper_id(module_wrapper, compilation_flags),
        bf,
        module_wrapper,
        gsl_root,
        lsoda_object_file,
        lsoda_fast_static_lib,
        libf2c_path,
        compilation_flags,
    )
    module = LoadedModule(bf)
    return module


def compile_libf2c():
    folder = os.path.join(base_cache_folder(), "libf2c", get_platform())
    lib_path = os.path.join(folder, "libf2c.a")
    if os.path.exists(lib_path):
        return lib_path

    create_folder_if_not_exists(folder)
    for path in glob.glob(os.path.join(HERE, "f2c_files", "*")):
        shutil.copy(path, folder)

    current_folder = os.getcwd()
    try:
        os.chdir(folder)
        run_command("gcc -O3 -fPIC -c -DINTEGER_STAR_8=1 -w -Wfatal-errors *.c")
        run_command("ar rcs libf2c.a *.o")
    finally:
        os.chdir(current_folder)
    return lib_path


def generate_files_and_compile_if_needed(
    wrapper_id,
    build_folder,
    module_wrapper,
    gsl_root,
    lsoda_object_file,
    lsoda_fast_static_lib,
    libf2c_path,
    compilation_flags,
):

    IntegralFunctionWrapper.reset()

    if glob.glob(os.path.join(build_folder, "_wrapper_{}.so".format(wrapper_id))):
        print("wrapper already exists at", build_folder)
        return build_folder

    print()
    print("write files to")
    print(build_folder)
    print()

    create_folder_if_not_exists(build_folder)

    if not glob.glob(os.path.join(build_folder, "_wrapper_{}.pyx".format(wrapper_id))):
        print("create source files at", build_folder)
        create_source_files(
            build_folder,
            module_wrapper,
            gsl_root,
            lsoda_object_file,
            lsoda_fast_static_lib,
            libf2c_path,
            wrapper_id,
            compilation_flags,
        )
    else:
        print("source files already exist at", build_folder)
    compile_files(build_folder)


class LoadedModule:
    """wraps compiled module to support pickling"""

    def __init__(self, folder):
        self._folder = os.path.abspath(folder)
        self._wrapper_id = os.path.basename(folder)
        self._module_name = "_wrapper_" + self._wrapper_id
        self._init()

    def _init(self):
        if self._module_name in sys.modules:
            del sys.modules[self._module_name]
        try:
            before = os.getcwd()
            os.chdir(self._folder)
            sys.path.insert(0, self._folder)
            self._module = importlib.import_module(self._module_name)
        except FileNotFoundError:
            raise ImportError()
        finally:
            sys.path.pop(0)
            os.chdir(before)
        for name, unique_id in self._module.get_fast_ode_unique_ids().items():
            if read_new_traces(unique_id):
                warnings.warn(
                    "there are new permuations pending, you might want to recompile"
                )
                break

    def reload(self):
        self._init()

    def __getattr__(self, name):
        return getattr(self._module, name)

    def __getstate__(self):
        return self._folder, self._module_name

    def __setstate__(self, data):
        try:
            self._folder, self._module_name = data
            self._init()
        except Exception:
            import traceback

            traceback.print_exc()

    def __dir__(self):
        return self._module.__dir__()


# for backwards compatibility:
load_module = LoadedModule


def create_source_files(
    build_folder,
    module_wrapper,
    gsl_root,
    lsoda_object_file,
    lsoda_fast_static_lib,
    libf2c_path,
    wrapper_id,
    compilation_flags,
):

    j = partial(os.path.join, build_folder)

    print("setup code generation")
    module_wrapper.setup_code_generation()

    with open(j("functions.cpp"), "w") as fh:
        print(module_wrapper.c_code("functions.hpp"), file=fh)

    with open(j("functions.hpp"), "w") as fh:
        print(module_wrapper.c_header(), file=fh)

    with open(
        j("_wrapper_{wrapper_id}.pyx".format(wrapper_id=wrapper_id)),
        "w",
    ) as fh:
        print(module_wrapper.cython_code("functions.hpp"), file=fh)

    if not compilation_flags:
        compilation_flags = ["-O3"]

    setup_py_content = align(
        """
    |from distutils.core import setup
    |from distutils.extension import Extension
    |from distutils.sysconfig import get_config_vars
    |
    |from Cython.Build import cythonize
    |import numpy as np
    |import glob
    |import os
    |import sys
    |
    |sourcefiles = ['_wrapper_{wrapper_id}.pyx', 'functions.cpp']
    |
    |if (os.environ.get("CC") == "clang" or get_config_vars()['CC'] == 'clang'
    |    or sys.platform == "darwin"):
    |        libf2c = ['{libf2c}']
    |        link_flags = []
    |else:
    |        libf2c = ['-Wl,--whole-archive', '{libf2c}', '-Wl,--no-whole-archive']
    |        link_flags = ["-Wl,--allow-multiple-definition"]
    |
    |extensions = [Extension("_wrapper_{wrapper_id}",
    |                sourcefiles,
    |                define_macros = [('HAVE_INLINE', '1')],
    |                include_dirs=['{gsl_root}/include', np.get_include(),],
    |                library_dirs=['{gsl_root}/lib'],
    |                extra_compile_args = {compilation_flags} +
    |                          ["-std=c++11",
    |                           "-fPIC",
    |                           "-DINTEGER_STAR_8=1",
    |                           "-pipe",
    |                           "-Wno-unused-variable",
    |                           "-fno-var-tracking",
    |                           "-Wno-unused-but-set-variable",
    |                           ],
    |                extra_link_args = ["-fPIC",
    |                                   "-u s_stop",
    |                                   ] + link_flags,
    |                extra_objects = (['{gsl_root}/lib/libgsl.a', '{lsoda_object_file}',
    |                                  '{lsoda_fast_static_lib}']
    |                                 + libf2c
    |                                 )
    |                )
    |              ]
    |
    |setup(
    |   ext_modules=cythonize(extensions, language="c++")
    |)
    """
    ).format(
        gsl_root=gsl_root,
        lsoda_object_file=lsoda_object_file,
        lsoda_fast_static_lib=lsoda_fast_static_lib,
        libf2c=libf2c_path,
        wrapper_id=wrapper_id,
        compilation_flags=compilation_flags,
    )

    with open(j("setup.py"), "w") as fh:
        print(setup_py_content, file=fh)


def compile_files(folder):
    try:
        LoadedModule(folder)
        return
    except ImportError:
        pass
    current_folder = os.getcwd()
    try:
        os.chdir(folder)
        print()
        print("compile python extension module")
        s = time.time()
        run_command("python setup.py build_ext --inplace")
        print(
            "compiling the module needed {:.1f} minutes".format((time.time() - s) / 60)
        )
    finally:
        os.chdir(current_folder)


def run_command(cmd):
    print("$", cmd)
    with monitor():
        proc = subprocess.run(
            cmd,
            stderr=subprocess.STDOUT,
            stdout=subprocess.PIPE,
            shell=True,
            universal_newlines=True,
        )
    if proc.returncode:
        print(proc.stdout)
        raise OSError("compilation failed")


@contextmanager
def monitor():
    t = PrintAliveThread()
    t.start()
    try:
        yield
    finally:
        t.running = False
        time.sleep(0.05)
        print()
        t.join()


class PrintAliveThread(threading.Thread):
    def __init__(self):
        super().__init__()
        self.running = True

    def run(self):
        started = time.time()
        while self.running:
            while time.time() < started + 1.0:
                if not self.running:
                    return
                time.sleep(0.05)
            started = time.time()
            print(".", end="")
            sys.stdout.flush()


def build_folder(module_wrapper, compilation_flags, root_folder=None):
    if root_folder is None:
        root_folder = sympy2c_cache_folder()
    return os.path.join(root_folder, wrapper_id(module_wrapper, compilation_flags))


def wrapper_id(module_wrapper, compilation_flags):
    return "{}_{}".format(
        module_wrapper.get_unique_id(),
        hashlib.md5(str(compilation_flags).encode("ascii")).hexdigest()[:5],
    )
