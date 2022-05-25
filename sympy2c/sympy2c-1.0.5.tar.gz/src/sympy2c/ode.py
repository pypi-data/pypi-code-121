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

import sympy as sp

from .function import (
    Alias,
    Function,
    MatrixValuedFunctionWrapper,
    VectorValuedFunctionWrapper,
)
from .utils import Hasher, align, concat_generator_results
from .wrapper import WrapperBase


class Ode:
    def __init__(self, name, t, lhs, rhs_expressions, *, compute_jacobian=True):
        assert len(lhs) == len(rhs_expressions)
        self.name = name
        self.t = t
        self.lhs = lhs
        self.rhs_expressions = rhs_expressions
        self.compute_jacobian = compute_jacobian
        self._unique_id = None

    def __str__(self):
        return (
            "<Ode "
            + " ".join(
                map(
                    str,
                    (
                        self.name,
                        self.t,
                        self.lhs,
                        self.rhs_expressions,
                        self.compute_jacobian,
                    ),
                )
            )
            + ">"
        )

    @property
    def wrapper(self):
        return OdeWrapper

    def get_unique_id(self):
        if self._unique_id is None:
            hasher = Hasher()
            hasher.update("name", self.name)
            hasher.update("t", str(self.t))
            hasher.update("lhs", str(self.lhs))
            hasher.update("compute_jacobian", str(self.compute_jacobian))
            self._unique_id = hasher.hexdigest()
        return self._unique_id


class OdeWrapper(WrapperBase):
    def __init__(self, ode, globals_, visitor):
        self.ode = ode
        self.globals_ = globals_
        self.visitor = visitor

        self.name = ode.name
        self.t = ode.t
        self.rhs_expressions = ode.rhs_expressions
        self.lhs = ode.lhs

        self.n = len(self.lhs)

    def get_unique_id(self):
        return self.ode.get_unique_id()

    def setup_code_generation(self):

        y = Alias("y___", *self.lhs)

        self.ydot = Function(
            "{}_dot".format(self.name), self.rhs_expressions, self.t, y
        )

        if self.ode.compute_jacobian:
            matrix_jacobian = sp.Matrix(self.rhs_expressions).jacobian(self.lhs)
            columnwise_vector_jacobian = matrix_jacobian.T[:]
            self.jacobian = Function(
                "{}_jacobian".format(self.name), columnwise_vector_jacobian, self.t, y
            )
        else:
            self.jacobian = None

        self.wrappers = [
            VectorValuedFunctionWrapper(self.ydot, self.globals_, self.visitor, False)
        ]
        if self.jacobian is not None:
            self.wrappers.append(
                MatrixValuedFunctionWrapper(
                    self.jacobian, self.globals_, self.visitor, False
                )
            )

        for w in self.wrappers:
            w.setup_code_generation()

    @concat_generator_results
    def c_header(self):
        for wrapper in self.wrappers:
            yield wrapper.c_header()

        yield (
            "int _solve_{name}("
            "double *, double *, size_t, double *, double *, int, int, int);"
        ).format(name=self.name)

    @concat_generator_results
    def c_code(self, header_file_path):
        for wrapper in self.wrappers:
            yield wrapper.c_code(header_file_path)
        yield align(
            """
        |void _fex_{name}(double t, double *y, double *ydot, void *data)
        |{{
        |    _{name}_dot(t, y, ydot);
        |}}
        """.format(
                name=self.name
            )
        )

        if self.jacobian:

            yield align(
                """
            |void _fjac_{name}(double t, double *y, double *jac, void *data)
            |{{
            |    _{name}_jacobian(t, y, jac);
            |}}
            """.format(
                    name=self.name
                )
            )

        if self.ode.compute_jacobian:
            jac = "use_jacobian ? _fjac_{name} : NULL".format(name=self.name)
        else:
            jac = "NULL"

        yield align(
            """
        |int _solve_{name}(
        |    double *tgrid, double *y, size_t nt, double * atol, double * rtol,
        |    int max_iter, int max_order, int use_jacobian
        |)
        |{{
        |
        |    int istate = 1;
        |    double t;
        |
        |    int iwork1 = 0;
        |    int iwork2 = 0;
        |    int iwork5 = 1;     // report solver switches
        |    int iwork6 = max_iter;
        |    int iwork7 = 0;
        |    int iwork8 = 0;
        |    int iwork9 = max_order;
        |    int iopt = 1;
        |    int jt = 2;    // lsoda only uses jac in case jac != NULL and else uses
        |                   // approximation.
        |    int itol = 4;  // rtol and atol as vector
        |
        |    // use default values:
        |    double rwork1 = 0.0;  // tcrit
        |    double rwork5 = 0.0;  // h0
        |    double rwork6 = 0.0;  // hmax
        |    double rwork7 = 0.0;  // hmin
        |    void * data = 0;
        |
        |    for (size_t i = 1; i < nt; ++i) {{
        |         t = tgrid[i - 1];
        |         memcpy(y + i * {n}, y + (i - 1) * {n}, {n} * sizeof(double));
        |         /* we subtrace 1 because lsoda uses offset 1 */
        |         lsoda(_fex_{name}, {jac}, {n}, y + i * {n} - 1, &t, tgrid[i], itol,
        |               rtol, atol, 1, &istate, iopt, jt, iwork1, iwork2, iwork5,
        |               iwork6, iwork7, iwork8, iwork9, rwork1, rwork5, rwork6,
        |               rwork7, data);
        |         if (istate <= 0)
        |            break;
        |    }}
        |
        |   n_lsoda_terminate();
        |   return istate;
        |
        |}}
    """
        ).format(name=self.name, n=self.n, jac=jac)

    @concat_generator_results
    def cython_code(self, header_file_path):
        for wrapper in self.wrappers:
            yield wrapper.cython_code(header_file_path)

        yield align(
            """
        |cdef extern from "{header_file_path}":
        |
        |    int _solve_{name}(double *tgrid, double *y, size_t nt, double * atol,
        |                      double * rtol, int max_iter, int max_order,
        |                      int use_jacobian)
        |
        |    void _{name}_dot(double t, double *y, double *ydot)
        """
            + (
                ""
                if not self.ode.compute_jacobian
                else """
        |    void _{name}_jacobian(double t, double *y, double *jac)
        |
        """
            )
            + """
        |import warnings
        |
        |def solve_{name}(
        |    np.ndarray[np.double_t, ndim=1] y0,
        |    np.ndarray[np.double_t, ndim=1] tgrid,
        |    rtol, atol, int max_iter=0, int max_order=5, int use_jacobian=1
        |):
        |    '''solve_{name}(y0, tgrid, atol, rtol, max_iter, max_order, use_jacobian)
        |
        |       default value for max_iter is 0 which indicates "use default value
        |       of lsoda"
        |    '''
        |
        |
        |    cdef size_t nt = tgrid.shape[0]
        |    cdef int state
        |    assert y0.shape[0] == {n}, "y0 has wrong shape"
        |    assert not (use_jacobian > 0) or {compute_jacobian}, (
        |          "you must set 'compute_jacobian' to True when "
        |          "creating the ode wrapper.")
        |    assert isinstance(atol, (float, np.ndarray))
        |    if isinstance(atol, float):
        |         atol = atol * np.ones(({n},))
        |    assert atol.shape == ({n},)
        |
        |    assert isinstance(rtol, (float, np.ndarray))
        |    if isinstance(rtol, float):
        |         rtol = rtol * np.ones(({n},))
        |    assert rtol.shape == ({n},)
        |
        |    assert max_iter >= 0, "max_iter must be 0 or positive"
        |    assert 1 <= max_order <= 5, "max_order must be in 1..5"
        |    cdef double[{n} + 1] _atol
        |    cdef double[{n} + 1] _rtol
        |    cdef size_t i
        |    for i in range(1, {n} + 1):
        |         _atol[i] = atol[i - 1]
        |         _rtol[i] = rtol[i - 1]
        |
        |    cdef np.ndarray[np.double_t, ndim=2, mode='c'] result
        |    result = np.zeros((nt, {n}), dtype=float, order="c")
        |    result[0, :] = y0
        |    cdef long started = microtime()
        |    istate = _solve_{name}(&tgrid[0], &result[0, 0], nt, &_atol[0], &_rtol[0],
        |                           max_iter, max_order, use_jacobian)
        |
        |    result_meta = dict(istate=istate,
        |                       num_steps=None,
        |                       num_feval=None,
        |                       num_lu_solver_calls=None,
        |                       last_switch_at=None,
        |                       seconds_needed = (microtime() - started) / 1e6,
        |                       steps=None,
        |                       step_sizes=None)
        |    return result, result_meta
        |
        |def symbols_{name}():
        |    return {symbols}
        |
        |def rhs_{name}(double t, np.ndarray[np.double_t, ndim=1] y):
        |    cdef np.ndarray result = np.zeros(({n},))
        |    cdef double[:] result_view = result
        |    _{name}_dot(t, &y[0], &result_view[0])
        |    return result
        |"""
            + (
                ""
                if not self.ode.compute_jacobian
                else """

        |def jac_{name}(double t, np.ndarray[np.double_t, ndim=1] y):
        |    cdef np.ndarray result = np.zeros(({n}, {n}))
        |    cdef double[:, :] result_view = result
        |    _{name}_jacobian(t, &y[0], &result_view[0, 0])
        |    return result
        |
        |"""
            )
        ).format(
            header_file_path=header_file_path,
            name=self.name,
            n=self.n,
            symbols=[str(sym) for sym in self.lhs],
            compute_jacobian=self.ode.compute_jacobian,
        )

    def determine_required_extra_wrappers(self):
        pass
