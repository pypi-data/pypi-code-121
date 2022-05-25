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

import json
import os
from hashlib import md5

import portalocker
from sympy import Matrix

from .function import expression_hash
from .lu_generator import argsort, generate_code, setup_code_generation
from .utils import (
    concat_generator_results,
    create_folder_if_not_exists,
    sympy2c_cache_folder,
)
from .wrapper import WrapperBase

CYTHON_TEMPLATE = "ode_fast_cython_template.pyx"


def known_traces_file(unique_id):
    folder = os.path.join(sympy2c_cache_folder(), "known_traces")
    create_folder_if_not_exists(folder)
    return os.path.join(folder, unique_id + ".json")


def _load_traces(path):
    with portalocker.Lock(path, "r", timeout=1, encoding="utf-8") as fh:
        try:
            traces = json.load(fh)
        except json.decoder.JSONDecodeError:
            # sometimes previos load fails in parallel executions!?
            fh.seek(0)
            content = repr(fh.read())
            traces = json.loads(content)

    return {int(k): v for (k, v) in traces.items()}


def _write_json(path, data):
    with portalocker.Lock(path, "w", timeout=1, encoding="utf-8") as fh:
        json.dump(data, fh, indent=4)


def read_known_traces(unique_id):
    path = known_traces_file(unique_id)
    if not os.path.exists(path):
        return {}
    return _load_traces(path)


def write_known_traces(unique_id, traces):
    path = known_traces_file(unique_id)
    _write_json(path, traces)


def write_new_traces(unique_id, new_traces):
    path = new_traces_file(unique_id)
    _write_json(path, new_traces)


def new_traces_file(unique_id):
    folder = os.path.join(
        os.environ.get("FAKE_CACHE_FOLDER", sympy2c_cache_folder()), "new_traces"
    )
    create_folder_if_not_exists(folder)

    return os.path.join(folder, unique_id + ".json")


def read_new_traces(unique_id):
    path = new_traces_file(unique_id)
    if not os.path.exists(path):
        return {}
    traces = _load_traces(path)
    try:
        os.unlink(path)
    except IOError:
        if os.path.exists(path):
            raise

    return traces


def update_new_traces(unique_id, new_traces):
    if not new_traces:
        return

    num_levels = len(new_traces)

    path = new_traces_file(unique_id)
    if os.path.exists(path):
        existing_traces = _load_traces(path)
    else:
        existing_traces = {}

    if not existing_traces:
        existing_traces = {level: list() for level in range(num_levels)}

    did_update = False
    for level, nti in new_traces.items():
        for trace in nti:
            if trace not in existing_traces[level]:
                existing_traces[level].append(trace)
                did_update = True

    _write_json(path, existing_traces)
    if did_update:
        print("updated new traces at", path)


class OdeFast:
    def __init__(self, name, t, lhs, rhs, splits=None, reorder=False):
        assert len(lhs) == len(rhs)
        self.name = name
        self.t = t
        self.lhs = lhs
        self.rhs = Matrix(rhs)
        if not splits:
            splits = [len(lhs)]

        if max(splits) > len(rhs):
            raise ValueError(
                "split {} is beyond size of the system {}".format(max(splits), len(rhs))
            )
        self.splits = splits
        self.reorder = reorder
        self._unique_id = None
        self._unique_id_equations = None

    def __str__(self):
        return "<OdeFast {} {} {} {}, {}, {}>".format(
            self.name, self.t, self.lhs, self.rhs, self.splits, self.reorder
        )

    @property
    def wrapper(self):
        return OdeFastWrapper

    def get_unique_id(self):
        if self._unique_id is None:
            hasher = md5()
            hasher.update(self.name.encode("utf-8"))
            hasher.update(self.get_unique_id_equations().encode("utf-8"))
            hasher.update(str(self.splits).encode("utf-8"))
            self._unique_id = hasher.hexdigest()
        return self._unique_id

    def get_unique_id_equations(self):
        if self._unique_id_equations is None:
            hasher = md5()
            hasher.update(str(self.t).encode("utf-8"))
            hasher.update(str(self.lhs).encode("utf-8"))
            hasher.update(str(self.reorder).encode("utf-8"))
            for ri in self.rhs:
                hasher.update(expression_hash(ri))
            self._unique_id_equations = hasher.hexdigest()
        return self._unique_id_equations


class OdeFastWrapper(WrapperBase):
    def __init__(self, ode, globals_, visitor, traces=None):
        self.ode = ode
        self.globals_ = globals_
        self.visitor = visitor
        self.t = ode.t
        self.rhs = ode.rhs
        self.lhs = ode.lhs
        self.name = ode.name
        self.reorder = ode.reorder
        if traces is None:
            traces = read_known_traces(ode.get_unique_id())
        self.traces = traces
        self.splits = ode.splits
        self.n = len(ode.lhs)
        self._unique_id = None
        self._c_code = None

    def __str__(self):
        hash_ = md5(str(self.traces).encode("utf-8")).hexdigest()
        return "<OdeFastWrapper {} {} {} {} {}>".format(
            self.name, self.t, self.lhs, self.rhs, hash_
        )

    def compute_permutation(self):
        if self.reorder:
            state_vars = set(self.lhs)
            counts = [-len(rhsi.atoms() & state_vars) for rhsi in self.rhs]
            permutation = argsort(counts)
        else:
            permutation = list(range(self.n))
        return tuple(permutation)

    def setup_code_generation(self):

        self.permutation = self.compute_permutation()

        rhs = Matrix([self.rhs[p] for p in self.permutation])
        lhs = [self.lhs[p] for p in self.permutation]

        cache, J, h, el0, M, rhs = setup_code_generation(
            rhs,
            self.t,
            lhs,
            self.visitor,
            self.ode.get_unique_id_equations(),
            self.permutation,
        )
        self._c_code = list(
            generate_code(
                self.name,
                rhs,
                lhs,
                self.visitor,
                self.traces,
                self.splits,
                cache,
                J,
                h,
                el0,
                M,
                self.permutation,
            )
        )

    def get_unique_id(self):
        if self._unique_id is None:
            hasher = md5()
            hasher.update(self.ode.get_unique_id().encode("utf-8"))
            for level, level_traces in sorted(self.traces.items()):
                hasher.update(str(sorted(level_traces)).encode("utf-8"))
            self._unique_id = hasher.hexdigest()
        return self._unique_id

    def determine_required_extra_wrappers(self):
        for rhs in self.rhs:
            self.visitor.visit(rhs)

    def c_header(self):
        return ""

    @concat_generator_results
    def c_code(self, header_file_path):
        yield from self._c_code

    @concat_generator_results
    def cython_code(self, header_file_path):
        here = os.path.dirname(__file__)
        template = open(os.path.join(here, CYTHON_TEMPLATE)).read()

        liw = 20 + self.n

        lrw = 22 + 16 * self.n + self.n  # extra for lasty storate

        symbols = repr(list(map(repr, self.lhs)))
        permutation = ", ".join(map(str, self.permutation))

        yield template.format(
            N=self.n,
            id_=self.name,
            LRW=lrw,
            LIW=liw,
            symbols=symbols,
            ode_id=self.ode.get_unique_id(),
            permutation=permutation,
            n_splits=len(self.splits),
        )
