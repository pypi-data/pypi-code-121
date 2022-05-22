# This file is part of the litprog project
# https://github.com/litprog/litprog
#
# Copyright (c) 2018-2021 Manuel Barkhau (mbarkhau@gmail.com) - MIT License
# SPDX-License-Identifier: MIT
from __future__ import annotations
import re
import typing as typ
try:
    import importlib.resources as importlib_resources
except ImportError:
    import importlib_resources
SELECTED_STATIC_DEPS = {'static/fonts_screen\\.css',
    'static/fonts_print\\.css', 'static/katex\\.css',
    'static/codehilite\\.css', 'static/general_v2\\.css',
    'static/screen_v3\\.css', 'static/popper.js', 'static/app.js',
    'static/print\\.css', 'static/print_a4\\.css', 'static/print_a5\\.css',
    'static/print_letter\\.css', 'static/print_ereader\\.css',
    'static/print_halfletter\\.css', 'static/print_tallcol\\.css',
    'static/print_tallcol_a4\\.css', 'static/print_tallcol_letter\\.css',
    'static/.+\\.css', 'static/.+\\.svg', 'static/fonts/.+\\.woff2',
    'static/fonts/.+\\.woff', 'static/fonts/.+\\.ttf'}
Package = typ.NewType('Package', str)


def iter_paths() ->typ.Iterator[tuple[Package, str, typ.ContextManager]]:
    available_filepaths = {package: list(importlib_resources.contents(
        package)) for package in ['litprog.static', 'litprog.static.fonts']}
    for static_fpath in SELECTED_STATIC_DEPS:
        dirpath, fname = static_fpath.rsplit('/', 1)
        package = Package('litprog.' + dirpath.replace('/', '.'))
        pkg_fname_re = re.compile(fname)
        for pkg_fname in available_filepaths[package]:
            if pkg_fname_re.match(pkg_fname):
                pkg_path_ctx = importlib_resources.path(package, pkg_fname)
                yield package, pkg_fname, pkg_path_ctx
