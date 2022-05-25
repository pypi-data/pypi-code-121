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

import itertools
import os
import pickle
from collections import defaultdict
from textwrap import dedent
from time import time

import sympy as sp
from sympy import Identity, Matrix, cse

from .rec_inv import rec_inv
from .speedup import jacobian
from .symbol import Symbol, symbols
from .utils import create_folder_if_not_exists, sympy2c_cache_folder, timeit
from .vector import VectorElement

"""

FROM https://math.boisestate.edu/~wright/courses/m566/luexample2print.pdf


M = LUP  (P is row permutations)

# lu
for k = 1:n-1
    for i = k+1:n  % Loop over the rows in column k+1
        A(i,k) = A(i,k)/A(k,k);
        for j = k+1:n  % Loop over the columns in row i
            A(i,j) = A(i,j) - A(i,k)*A(k,j);

# forward sub

x(1) = b(1);
for j = 2:n
    x(j) = b(j) - L(j,1:j-1)*x(1:j-1);
end

# back sub

x(n) = x(n)/U(n,n);
for j = n-1:-1:1
    x(j) = ( x(j) - U(j,j+1:n)*x(j+1:n) )/U(j,j);
    end
"""


g = itertools.count(0)
xi_symbols_generator = (Symbol(f"_x_{i:03d}") for i in g)  # in itertools.count())


def partial_cse(e):
    ignore = e.atoms(sp.Symbol) - e.free_symbols
    return cse(e, xi_symbols_generator, ignore=ignore)


class Cache:
    def __init__(self, unique_id_ode):
        folder = os.path.join(sympy2c_cache_folder(), "lu_generator")
        create_folder_if_not_exists(folder)
        self._path = os.path.join(folder, unique_id_ode)
        if os.path.exists(self._path):
            self._cache = pickle.load(open(self._path, "rb"))
        else:
            self._cache = {}

    def __contains__(self, key):
        return key in self._cache

    def lookup(self, key):
        return self._cache[key]

    def store(self, key, value):
        self._cache[key] = value
        with open(self._path, "wb") as fh:
            pickle.dump(self._cache, fh)


def setup_code_generation(
    rhs, time_var, state_vars, visitor, unique_id_ode, permutation
):

    variable_names = set(str(s) for s in rhs.atoms()) | set((str(time_var),))
    assert (
        "h" not in variable_names
    ), "you must not use the symbol h in your expressions"
    assert (
        "el0" not in variable_names
    ), "you must not use the symbol el0 in your expressions"

    for term in rhs:
        visitor.visit(term)

    t = Symbol("_t")
    rhs = rhs.subs({time_var: t})

    cache = Cache(unique_id_ode)
    N = len(rhs)

    # TODO: more caching!
    with timeit("compute jacobian and M"):
        if ("jacobian", permutation) in cache:
            print("... cache hit")
            J, h, el0, M = cache.lookup(("jacobian", permutation))
        else:
            J = jacobian(rhs, state_vars)
            h, el0 = symbols("ls0001_.h ls0001_.el0")
            M = (Identity(N) - h * el0 * J).as_mutable()
            cache.store(("jacobian", permutation), (J, h, el0, M))

    return cache, J, h, el0, M, rhs


def generate_code(
    id_, rhs, state_vars, visitor, traces, splits, cache, J, h, el0, M, permutation
):

    N = len(rhs)
    if splits is None:
        splits = [N]
    splits = sorted(splits)

    with timeit("run cse"):
        key = ("M_reduced", permutation)
        if key in cache:
            print("... cache hit")
            sub_assignments, M_reduced = cache.lookup(key)
        else:
            sub_assignments, (M_reduced,) = partial_cse(M)
            cache.store(key, (sub_assignments, M_reduced))

    sizes = [
        s
        for s in [splits[0]]
        + [s1 - s0 for (s0, s1) in zip(splits, splits[1:])]
        + [N - splits[-1]]
        if s > 0
    ]
    if not traces:
        traces = {i: [list(range(s))] for i, s in enumerate(sizes)}
    assert isinstance(traces, dict)

    print("create header")
    yield from generate_header(id_, rhs, N, traces, splits)

    print("create fnorm_")
    yield from generate_fnorm_(id_, J, state_vars, visitor.visit)

    yield from create_split_lu(
        id_,
        sub_assignments,
        M_reduced,
        traces,
        state_vars,
        visitor.visit,
        splits,
        cache,
        permutation,
    )

    print("create rhs")
    yield from generate_code_rhs(id_, rhs, state_vars, visitor.visit)


def _split(M, n):
    A = M[:n, :n]
    B = M[:n, n:]
    C = M[n:, :n]
    D = M[n:, n:]

    s = time()
    if D.shape[0]:  # messages for corner cases might be confusing
        fill = (
            sum(1 for i in range(D.shape[0]) for j in range(D.shape[1]) if D[i, j] != 0)
            / D.shape[0]
            / D.shape[1]
        )
        print(f"start inverting D of shape {D.shape}, fill_degree={fill*100:.0f}%")
    xii, Dinv = rec_inv(D)  # D.inv()
    needed = time() - s
    if D.shape[0]:  # messages for corner cases might be confusing
        print(f"inverting D of shape {D.shape} needed {needed:.1f}[s]")
    U = B * Dinv
    R = A - U * C
    return xii, R, U, C, D


def compute_splits(M, splits):
    R = M
    Di_Ci = []
    split_sub_assignments = []
    for split in reversed(splits):
        xii, R, U, C, D = _split(R, split)
        split_sub_assignments.extend(xii)
        if D:
            Di_Ci.append((D, C, split))
    return split_sub_assignments, R, U, Di_Ci


def create_split_lu(
    id_,
    sub_assignments,
    M_reduced,
    all_traces,
    state_vars,
    expression_to_c,
    splits,
    cache,
    permutation,
):

    yield from _create_decl_lu(id_, 0)
    for trace_idx, trace in enumerate(all_traces[0]):
        yield from _create_decl_split_lu_0(id_, trace_idx)

    for level, traces in all_traces.items():
        if level == 0:
            yield from _create_decl_split_lu_0(id_, trace_idx)
        else:
            yield from _create_decl_lu(id_, level)
            for trace_idx in range(len(traces)):
                yield from _create_decl_split_lu_i(id_, level, trace_idx)

    splits = tuple(splits)
    with timeit("compute schur complement matrices"):
        key = (splits, permutation)
        if key in cache:
            print("... cache hit")
            R, U, Di_Ci, sub_assignments, split_sub_assignments = cache.lookup(key)

        else:
            split_sub_assignments, R, U, Di_Ci = compute_splits(M_reduced, splits)
            cache.store(
                key,
                (R, U, Di_Ci, sub_assignments, split_sub_assignments),
            )

    traces = all_traces[0]

    yield from create_lu(
        id_,
        0,
        sub_assignments + split_sub_assignments,
        R,
        traces,
        state_vars,
        expression_to_c,
    )
    yield from create_lu_fallback_0(
        id_,
        sub_assignments + split_sub_assignments,
        U,
        traces,
        state_vars,
        expression_to_c,
    )

    for trace_idx in range(len(traces)):
        yield from _create_split_lu_0(
            id_,
            R,
            U,
            traces,
            trace_idx,
            sub_assignments + split_sub_assignments,
            state_vars,
            expression_to_c,
        )

    for level, (Di, Ci, split) in enumerate(reversed(Di_Ci), 1):

        traces = all_traces[level]

        yield from create_lu(
            id_,
            level,
            sub_assignments + split_sub_assignments,
            Di,
            traces,
            state_vars,
            expression_to_c,
        )
        yield from create_lu_fallback_i(
            id_,
            level,
            sub_assignments + split_sub_assignments,
            Ci,
            traces,
            split,
            state_vars,
            expression_to_c,
        )
        for trace_idx in range(len(traces)):

            yield from _create_split_lu_i(
                id_,
                level,
                Di,
                Ci,
                traces,
                trace_idx,
                split,
                sub_assignments + split_sub_assignments,
                state_vars,
                expression_to_c,
            )

    yield from generate_solve_split(id_, all_traces, splits, M_reduced.shape[0])


def generate_solve_split(id_, all_traces, splits, N):

    n_traces = len(all_traces[0])

    tlens = ", ".join(
        str(len(all_traces[level]) + 1) for level in range(len(all_traces))
    )

    yield dedent(
        rf"""

    std::vector<std::vector<unsigned int> > _call_counts_{id_};
    static unsigned int  _next_solver_{id_}[{len(splits) + 1}] = {{0}};

    extern "C" void _reset_next_solver_{id_}() {{
        for (int i=0; i <= {len(splits)}; i++)
            _next_solver_{id_}[i] = 0;  // solve_lu
    }}
    extern "C" void _solve_fast_{id_}(double * _t, double *_x, double *_y, int *ier) {{

        // lsoda assumes that we have _b and _x in the same memory location
        // but for our solvers this results in conflicts, thus we need to
        // separate _b and _x:

        std::vector<unsigned int> _cc;
        unsigned int _n[] = {{ {tlens} }};
        if (_call_counts_{id_}.size() == 0) {{
            for (int _ii=0; _ii < {len(all_traces)}; ++_ii) {{
                    _cc.clear();
                    _cc.insert(_cc.begin(), _n[_ii], 0);
                    _call_counts_{id_}.push_back(_cc);
                }}
        }}
        double _b[{N}];
        double _dummy[{N}];
        for (unsigned int _i = 0; _i < {N}; _i++) _b[_i] = _x[_i];

    """
    )

    for level, traces in all_traces.items():
        yield f"    int solver_{level} = _next_solver_{id_}[{level}];"
        yield f"    _call_counts_{id_}.at({level}).at(solver_{level})++;"

    yield ""
    yield f"    int _tried_0[{n_traces}] = {{ 0 }};"
    yield f"    if (__enable_fast_solver_{id_} == 0) solver_0 = {n_traces};"

    for j in range(len(all_traces[0])):
        yield f"    if (solver_0 == {j})"
        yield (
            f"        _next_solver_{id_}[0] = solve_{id_}__0_{j}(*_t, _b, _x, _x, _y,"
            f"_tried_0, __enable_sparse_lu_solver_{id_});"
        )

    yield f"    if (solver_0 == {j + 1})"
    yield (
        f"        _next_solver_{id_}[0] = solve_lu_{id_}__0_f(*_t, _b, _x, _x, _y,"
        f"_tried_0, __enable_sparse_lu_solver_{id_});"
    )
    yield ""
    offset = len(all_traces[0]) + 1

    for level, split in enumerate(splits, 1):
        if split == N:
            continue
        n_traces = len(all_traces[level])
        yield f"    int _tried_{level}[{n_traces}] = {{ 0 }};"
        yield f"    if (__enable_fast_solver_{id_} == 0)"
        yield f"        solver_{level} = {len(all_traces[level])};"
        for j in range(len(all_traces[level])):
            yield f"    if (solver_{level} == {j})"
            yield (
                f"        _next_solver_{id_}[{level}] ="
                f" solve_{id_}__{level}_{j}(*_t, _b, _x, _x + {split}, _y,"
                f" _tried_{level}, __enable_sparse_lu_solver_{id_});"
            )

        yield f"    if (solver_{level} == {j + 1})"
        yield (
            f"        _next_solver_{id_}[{level}] ="
            f" solve_lu_{id_}__{level}_f(*_t, _b, _x, _x + {split}, _y,"
            f" _tried_{level}, __enable_sparse_lu_solver_{id_});"
        )
        offset *= n_traces + 1

    yield "}"


def _create_decl_split_lu_0(id_, trace_idx):

    yield (
        f'extern "C" int solve_{id_}__0_{trace_idx}(double _t,'
        f" double *__restrict__ __b, double * _x0, "
        f" double *__restrict__ _x, double *__restrict__ _y, int * _tried,"
        " int _consider_sparsity);"
    )


def _create_decl_split_lu_i(id_, level, trace_idx):

    yield (
        f'extern "C" int solve_{id_}__{level}_{trace_idx}(double _t, '
        f"double *__restrict__ __b, double *_x0, "
        f"double *__restrict__ _x, double *__restrict__ _y, int * _tried,"
        " int _consider_sparsity);"
    )


def _create_split_lu_0(
    id_, R, U, traces, trace_idx, sub_assignments, state_vars, expression_to_c
):

    n0, n1 = U.shape
    trace = traces[trace_idx]

    yield (
        f'extern "C" int solve_{id_}__0_{trace_idx}(double _t,'
        f" double *__restrict__ __b, double * _x0, "
        f" double *__restrict__ _x, double *__restrict__ _y, int * _tried, "
        " int _consider_sparsity) {"
    )

    yield f"    // {R}"
    yield ""
    yield from init_state_vars_from_y(state_vars, indent="    ")
    yield from create_xi_varables(sub_assignments, expression_to_c)

    yield ""
    yield f"    double _b[{n0}];"

    for i in range(n0):
        yield f"    _b[{i}] = __b[{i}];"
        for j in range(n1):
            xij = U[i, j]
            if xij != 0:
                xij_expr = expression_to_c(xij)
                yield f"    _b[{i}] -= __b[{n0} + {j}] * ({xij_expr});"

    yield ""
    yield "    double _v_max, _temp;"
    yield "    int _j_max;"
    yield f"    _tried[{trace_idx}] = 1;"
    yield ""

    yield from create_sparse_lu(id_, 0, R, expression_to_c, trace, traces)

    yield f"    return {trace_idx};"
    yield "}"


def _create_split_lu_i(
    id_,
    level,
    D,
    C,
    traces,
    trace_idx,
    b_offset,
    sub_assignments,
    state_vars,
    expression_to_c,
):

    n1 = D.shape[0]
    n0 = C.shape[1]

    trace = traces[trace_idx]

    yield (
        f'extern "C" int solve_{id_}__{level}_{trace_idx}(double _t, '
        f"double *__restrict__ __b, double *_x0, "
        f"double *__restrict__ _x, double *__restrict__ _y, int * _tried,"
        " int _consider_sparsity) {"
    )
    yield f"    // {traces[trace_idx]}"
    yield ""
    yield from init_state_vars_from_y(state_vars, indent="    ")
    yield from create_xi_varables(sub_assignments, expression_to_c)

    yield ""
    yield f"    double _b[{n1}];"

    yield ""
    yield "    double _v_max, _temp;"
    yield "    int _j_max;"
    yield f"    _tried[{trace_idx}] = 1;"
    yield ""

    for i in range(n1):
        yield f"    _b[{i}] = __b[{i} + {b_offset}];"
        for j in range(n0):
            if C[i, j] != 0:
                cij_expr = expression_to_c(C[i, j])
                yield f"    _b[{i}] -= _x0[{j}] * ({cij_expr});"

    yield from create_sparse_lu(id_, level, D, expression_to_c, trace, traces)
    yield f"    return {trace_idx};"
    yield "}"


def _create_decl_lu(id_, level):
    yield (
        'extern "C" '
        f"int solve_lu_{id_}__{level}(double _t, double* _b, double *_x0, double* _x,"
        " double* _y, int* _tried, int _consider_sparsity);"
    )


def create_lu_fallback_0(id_, sub_assignments, U, traces, state_vars, expression_to_c):
    n0, n1 = U.shape

    yield dedent(
        f"""
    extern "C"
    int solve_lu_{id_}__0_f(double _t, double* __b, double *_x0, double* _x, double* _y,
                            int* _tried, int _consider_sparsity)
    {{
    """
    )
    yield from init_state_vars_from_y(state_vars, indent="    ")
    yield from create_xi_varables(sub_assignments, expression_to_c)
    yield ""
    yield f"    double _b[{n0}];"

    for i in range(n0):
        yield f"    _b[{i}] = __b[{i}];"
        for j in range(n1):
            xij = U[i, j]
            if xij != 0:
                xij_expr = expression_to_c(xij)
                yield f"    _b[{i}] -= __b[{n0} + {j}] * ({xij_expr});"

    yield (
        f"    return solve_lu_{id_}__0(_t, _b, _x0, _x, _y, _tried,"
        " _consider_sparsity);"
    )
    yield "}"


def create_lu_fallback_i(
    id_, level, sub_assignments, C, traces, b_offset, state_vars, expression_to_c
):
    n0, n1 = C.shape

    yield dedent(
        f"""
    extern "C"
    int solve_lu_{id_}__{level}_f(double _t, double* __b, double * _x0, double* _x,
                                  double* _y, int* _tried, int _consider_sparsity)
    {{
    """
    )
    yield from init_state_vars_from_y(state_vars, indent="    ")
    yield from create_xi_varables(sub_assignments, expression_to_c)
    yield ""
    yield f"    double _b[{n0}];"

    for i in range(n0):
        yield f"    _b[{i}] = __b[{i} + {b_offset}];"
        for j in range(n1):
            if C[i, j] != 0:
                cij_expr = expression_to_c(C[i, j])
                yield f"    _b[{i}] -= _x0[{j}] * ({cij_expr});"

    yield (
        f"    return solve_lu_{id_}__{level}(_t, _b, _x0, _x, _y, _tried, "
        "_consider_sparsity);"
    )
    yield "}"


def create_lu(
    id_,
    level,
    sub_assignments,
    M_reduced,
    traces,
    state_vars,
    expression_to_c,
):

    N = M_reduced.rows
    n = len(traces)

    lines = [
        f"double {xi} = {expression_to_c(expr)};" for (xi, expr) in sub_assignments
    ]
    sub_assignment_code = "\n        ".join(lines)

    M_init_code = "\n        ".join(
        f"_M({i}, {j}) = {expression_to_c(M_reduced[i, j])};"
        for i in range(N)
        for j in range(N)
        if M_reduced[i, j] != 0
    )

    col_end = [max(i for i in range(N) if M_reduced[i, j] != 0) for j in range(N)]
    row_end = [max(j for j in range(N) if M_reduced[i, j] != 0) for i in range(N)]

    # col_end = row_end = [N - 1] * N

    row_end_str = ", ".join(map(str, row_end))
    col_end_str = ", ".join(map(str, col_end))

    init_state_vars_code = "\n        ".join(init_state_vars_from_y(state_vars))

    code = f"""
    // FROM https://math.boisestate.edu/~wright/courses/m566/luexample2print.pdf

    #undef _M
    #define _M(i, j) __M[i + j * {N}]

    #define PRINT_TRACES 0

    extern "C"
    int solve_lu_{id_}__{level}(double _t, double* _b, double *_x0, double* _x,
                                double* _y, int* _tried, int  _consider_sparsity)
    {{
        // printf("enter solve_lu_{id_}\\n");

        reset_timer();

        int    _i, _j, _k, _i_max, _count, _pi, _pk;
        double _v_max, _temp;
        double __M[{N} * {N}] = {{0}};

        int _perm[{N}];
        int _trace[{N}];

        int _row_ends[{N}] = {{ {row_end_str} }};
        int _col_ends[{N}] = {{ {col_end_str} }};

        for (_i = 0; _i < {N}; _i++) _perm[_i] = _trace[_i] = _i;

        {init_state_vars_code}
        {sub_assignment_code}
        {M_init_code}

        if (0)
            for (int _i=0; _i < {N}; _i++) {{
                for (int _j=0; _j < {N}; _j++)
                    printf("%+.1e  ", _M(_i, _j));
                printf("\\n");
            }}


        double _v;

        int _col_end_k, _row_end_k, _row_end_i;

        _col_end_k = _row_end_k = _row_end_i = {N - 1};

        for (_k = 0; _k < {N-1}; _k++) {{

            _v_max = fabs(_M(_perm[_k], _k));

            _i_max = _k;

             if (_consider_sparsity)
                _col_end_k = _col_ends[_k];

            for (_j = _k + 1; _j <= _col_end_k; _j++) {{
                if ((_temp = fabs(_M(_perm[_j], _k))) > _v_max * SEC_FACTOR)
                {{
                    _v_max = _temp;
                    _i_max = _j;
                }}
            }}
            if (_v_max == 0.0) return -2;
            _j = _perm[_k];
            _perm[_k] = _perm[_i_max];
            _perm[_i_max] = _j;
            // printf("SWAP %d %d\\n", _k, _i_max);

            _trace[_k] = _i_max;

            _pk = _perm[_k];
            if (_consider_sparsity)
                _row_end_k = _row_ends[_pk];

            for (_i = _k + 1; _i <= _col_end_k; _i++) {{

                _pi = _perm[_i];

                _M(_pi, _k) /= _M(_pk, _k);


                if (_consider_sparsity) {{
                    _row_end_k = _row_ends[_pk];
                    _row_end_i = _row_ends[_pi];

                    for (_j = _k + 1; _j <= _row_end_k; _j++) {{
                        _M(_pi, _j) -= _M(_pi, _k) * _M(_pk, _j);
                        if (_M(_pi, _j) != 0) {{
                            if (_j > _row_end_i) {{
                                if (0) printf("extend row_ends %d from %d to %d\\n",
                                              _pi, _row_end_i, _j);
                                _row_end_i = _row_ends[_pi] = _j;
                            }}
                            if (_pi > _col_ends[_j]) {{
                                if (0) printf("extend col_ends %d from %d to %d\\n",
                                              _j, _col_ends[_j], _pi);
                                _col_ends[_j] = _pi;
                            }}
                        }} else {{
                            if (_j == _row_end_i)
                            _row_end_i = _row_ends[_pi] = _k - 1;
                            if (_pi == _col_ends[_j]) {{
                                if (0) printf("shrink col_ends %d from %d to %d\\n",
                                              _j, _col_ends[_j], _pi - 1);
                                _col_ends[_j]--;
                                }}
                        }}
                    }}
                }}
                else
                    for (_j = _k + 1; _j <= _row_end_k; _j++)
                        _M(_pi, _j) -= _M(_pi, _k) * _M(_pk, _j);
            }}

        }}
        if (0)
            for (int _i=0; _i < {N}; _i++) {{
                for (int _j=0; _j < {N}; _j++)
                    printf("%+.1e  ", _M(_i, _j));
                printf("\\n");
            }}

        if (0)
            for (int _j=0; _j < {N}; _j++) {{
                int _ce = 0;
                for (int _i=0; _i < {N}; _i++) {{
                    if(_M(_i, _j) !=0)
                        _ce = _i;
                }}
                printf("col_end %d: %d %d\\n", _j, _col_ends[_j], _ce);

            }}
        if (0)
            for (int _i=0; _i < {N}; _i++) {{
                int _re = 0;
                for (int _j=0; _j < {N}; _j++)
                    if(_M(_i, _j) !=0)
                        _re = _j;
                printf("row_end %d: %d %d\\n", _i, _row_ends[_i], _re);
            }}

        _v_max = fabs(_M(_perm[_k], _k));
        if (_v_max == 0.0) return -2;

        // forward substitution

        _x[0] = _b[_perm[0]];
        for (_j = 1; _j < {N}; _j++) {{
            _x[_j] = _b[_perm[_j]];
            for (_k = 0; _k < _j; _k++)
                _x[_j] -= _M(_perm[_j], _k) * _x[_k];
        }}

        // backward hubstitution

        _x[{N-1}] = _x[{N-1}] / _M(_perm[{N - 1}], {N - 1});
        for (_j = {N-2}; _j >=0; _j--) {{
            for (_k = _j + 1; _k < {N}; _k++)
                _x[_j] -= _M(_perm[_j], _k) * _x[_k];
            _x[_j] /= _M(_perm[_j], _j);
        }}

        _total_time_{id_}_lup_solver += time_delta();

        for (_j = 0; _j < {n}; _j++) {{
            _count = 0;
            for (_i = 0;  _i < {N}; _i++) {{
                if (_trace[_i] != _traces_{id_}__{level}[_j][_i])
                    break;
                _count += 1;
            }}
            if (_count == {N}) {{
                // printf("leave solve_lu_{id_} with trace %d\\n", _j);
                return _j;
                }}
        }}

        // register new trace

        std::vector<int> _new_trace;
        _new_trace.reserve({N});
        for (_i = 0;  _i < {N}; _i++)
            _new_trace.push_back(_trace[_i]);

        int _before = _new_traces["{id_}"][{level}].size();

        _new_traces["{id_}"][{level}].insert(_new_trace);

        int _after = _new_traces["{id_}"][{level}].size();

        if (PRINT_TRACES)
            if (_before != _after) {{
                printf("new trace %d\\n", _after);
                for (_j = 0; _j < {N}; _j++) {{
                    for (_i = 0; _i < {N}; _i++)
                        printf("  %+e,", _M(_i, _j));
                    printf("\\n");
                }}
                printf("rhs: ");
                for (_i = 0; _i < {N}; _i++) printf(" %e, ", _b[_i]);
                printf("\\nsolution: ");
                for (_i = 0; _i < {N}; _i++) printf(" %e, ", _x[_i]);
                printf("\\n");
            }}

        // printf("leave solve_lu_{id_} with new trace\\n");
        return {len(traces)};
    }}
    """
    yield dedent(code)


def init_state_vars_from_y(state_vars, indent=""):
    vector_elements = defaultdict(list)
    for i, state_var in enumerate(state_vars):
        if isinstance(state_var, VectorElement):
            vector_elements[state_var.vector_name].append((state_var.index, i))
        else:
            yield f"{indent}double {state_var} = _y[{i}];"

    for vector_name, used_elements in vector_elements.items():
        array_size = max(used_elements)[0] + 1
        yield f"{indent}double {vector_name}[{array_size}];"
        for vec_index, y_index in used_elements:
            yield f"{indent}{vector_name}[{vec_index}] = _y[{y_index}];"


def generate_fnorm_(id_, J, state_vars, expression_to_c):
    N = J.rows

    # c function name ends with "_" because of fortran linking. The modified
    # lsoda calls fnorm from Fortran wich is the same as fnorm_ in C.

    code = f"""
    extern "C" double _fnorm_{id_}(double *__t, double *_ewt, double *_y) {{
        // c function name ends with "_" because of fortran linking. The modified
        // lsoda calls fnorm from Fortran wich is the same as fnorm_ in C.
        double _fnorm = 0.0, _row_norm;
        """
    yield dedent(code)

    yield from init_state_vars_from_y(state_vars, indent="    ")

    yield ""
    yield "    double _t = *__t;"
    yield ""

    sub_assignments, (new_expressions,) = partial_cse(J)

    for (xi, expr) in sub_assignments:
        c_expr = expression_to_c(expr)
        yield f"    double {xi} = {c_expr};"

    for i in range(N):
        yield "    _row_norm = 0.0f;"
        for j in range(N):
            if J[i, j] != 0:
                expression = expression_to_c(new_expressions[i, j])
                yield f"    _row_norm += fabs({expression} / _ewt[{j}]);"
        yield f"    _row_norm *= _ewt[{i}];"
        yield "    if (_row_norm > _fnorm) _fnorm = _row_norm;"
    # yield r'   printf("fnorm = %e\n", _fnorm);'
    yield "    return _fnorm;"
    yield "}"


def generate_header(id_, rhs, N, traces, splits):

    yield ""
    yield f"#define N_{id_} {N}"
    yield ""
    yield f"static double _total_time_{id_}_fast_solver;"
    yield f"static double _total_time_{id_}_lup_solver;"
    yield f"static int __enable_fast_solver_{id_} = 1;"
    yield f"static int __enable_sparse_lu_solver_{id_} = 1;"
    yield ""
    yield f'extern "C" void _reset_timers_{id_}() {{'
    yield f"        _total_time_{id_}_fast_solver = 0.0;"
    yield f"        _total_time_{id_}_lup_solver = 0.0;"
    yield "}"
    yield ""
    yield f'extern "C" void _enable_fast_solver_{id_}(int enable) {{'
    yield f"        __enable_fast_solver_{id_} = enable;"
    yield "}"
    yield f'extern "C" void _enable_sparse_lu_solver_{id_}(int enable) {{'
    yield f"        __enable_sparse_lu_solver_{id_} = enable;"
    yield "}"
    yield ""
    yield f'extern "C" double _get_timer_{id_}_fast() {{'
    yield f"        return _total_time_{id_}_fast_solver;"
    yield "}"
    yield ""
    yield f'extern "C" double _get_timer_{id_}_lup() {{'
    yield f"        return _total_time_{id_}_lup_solver;"
    yield "}"

    for level, level_traces in traces.items():
        # tri = [ (t0, ...tl), (t0, .. tl), ...]
        yield f"std::vector<std::vector<int>> _traces_{id_}__{level} = {{"
        for trace in level_traces:
            yield "        {{ {} }},".format(", ".join(map(str, trace)))
        yield "};"

    yield (
        f'extern "C" int solve_lu_{id_}(double, double*, double *, double*, double*,'
        " int*, int);"
    )
    yield ""


def create_check(id_, M, expression_to_c, state_vars):
    n = M.shape[0]
    yield f"void _check_{id_}(double _t, double *_x, double *_b, double *_y) {{"

    yield from init_state_vars_from_y(state_vars, indent="    ")
    yield "     double _sum;"

    for i in range(n):
        yield "    _sum = 0.0;"
        for j in range(n):
            if M[i, j] != 0:
                mij_expr = expression_to_c(M[i, j])
                yield f"    _sum += _x[{j}] * {mij_expr};"
        yield rf"""    printf("r{i}= %e ", (_b[{i}] - _sum) / _b[{i}]);"""
    yield r"""    printf("\n");"""
    yield "}"


def create_sparse_lu(id_, level, M, expression_to_c, trace, traces):

    N = M.rows
    Me = [[expression_to_c(M[i, j]) for j in range(N)] for i in range(N)]

    perm = list(range(N))

    declared = set()

    yield "    reset_timer();"

    for i in range(N):
        for j in range(N):
            if M[i, j]:
                yield f"    double _m_{i}_{j} = {Me[i][j]};"
                declared.add((i, j))

    for k in range(N - 1):

        pk = perm[k]
        if (pk, k) not in declared:
            yield f"    double _m_{pk}_{k} = {Me[pk][k]};"
            declared.add((pk, k))
        yield f"    _v_max = fabs(_m_{pk}_{k});"

        yield f"    _j_max = {k};"
        # yield f"""printf("k={k}, _v_max=%f\\n", _v_max);"""

        for j in range(k + 1, N):
            pj = perm[j]
            if (pj, k) in declared:
                yield f"    if ((_temp = fabs(_m_{pj}_{k})) > _v_max * SEC_FACTOR)"
                yield f"       {{ _j_max = {j}; _v_max = _temp; }}"

        yield f"    if (_j_max != {trace[k]}) {{"
        yield f'        // printf("try trace switch for k={k} j_max=%d\\n", _j_max);'

        for nt, t in enumerate(traces):
            if any(t[i] != trace[i] for i in range(k)):
                continue

            if t[k] == trace[k]:
                continue

            yield f"        if (_j_max == {t[k]} && !_tried[{nt}]) {{"
            yield (
                f"            return solve_{id_}__{level}_{nt}(_t, __b, _x, _x, _y,"
                " _tried, _consider_sparsity);"
            )
            yield "        }"
        yield (
            f"        return solve_lu_{id_}__{level}(_t, _b, _x, _x, _y, _tried,"
            " _consider_sparsity);"
        )

        yield "    }"
        yield ""

        perm[k], perm[trace[k]] = perm[trace[k]], perm[k]

        pk = perm[k]

        for i in range(k + 1, N):
            pi = perm[i]

            if (pi, k) in declared:
                if (pi, k) not in declared:
                    yield f"    double _m_{pi}_{k} = {Me[pi][k]};"
                    declared.add((pi, k))

                if (pk, k) not in declared:
                    yield f"    double _m_{pk}_{k} = {Me[pk][k]};"
                    declared.add((pk, k))
                yield f"    _m_{pi}_{k} /= _m_{pk}_{k};"

            for j in range(k + 1, N):
                if (pi, k) in declared and (
                    pk,
                    j,
                ) in declared:  # M[pi, k] and M[pk, j]:
                    if (pi, j) not in declared:
                        yield f"    double _m_{pi}_{j} = {Me[pi][j]};"
                        declared.add((pi, j))
                    if (pi, k) not in declared:
                        yield f"    double _m_{pi}_{k} = {Me[pi][k]};"
                        declared.add((pi, k))
                    if (pk, j) not in declared:
                        yield f"    double _m_{pk}_{j} = {Me[pk][j]};"
                        declared.add((pk, j))
                    yield f"    _m_{pi}_{j} -= _m_{pi}_{k} * _m_{pk}_{j};"

        yield ""

    # forward substitution
    yield "    // forward substution"
    yield ""
    yield f"    _x[0] = _b[{perm[0]}];"
    for j in range(1, N):
        pj = perm[j]
        yield f"    _x[{j}] = _b[{pj}];"
        for k in range(j):
            if (pj, k) in declared:
                yield f"    _x[{j}] -= _m_{pj}_{k} * _x[{k}];"

    # backwards substitution
    yield "    // backwards substution"
    yield ""

    if (perm[N - 1], N - 1) in declared:
        yield f"    _x[{N - 1}] /= _m_{perm[N - 1]}_{N-1};"

    for j in range(N - 2, -1, -1):
        pj = perm[j]
        for k in range(j + 1, N):
            if (pj, k) in declared:
                yield f"    _x[{j}] -= _m_{pj}_{k} * _x[{k}];"

        if (pj, j) in declared:
            yield f"    _x[{j}] /= _m_{pj}_{j};"

    yield ""
    yield f"    _total_time_{id_}_fast_solver += time_delta();"
    yield ""


def create_xi_varables(xi, expression_to_c):

    for (v, t) in xi:
        t = expression_to_c(t)
        yield f"    double {v} = {t};"


def generate_code_rhs(id_, rhs, state_vars, expression_to_c):

    sub_assignments, (expressions,) = partial_cse(rhs)

    init_xi = "\n        ".join(
        f"double {xii} = {expression_to_c(e)};" for (xii, e) in sub_assignments
    )

    set_ydot = "\n        ".join(
        f"_ydot[{i}] = {expression_to_c(e)};" for (i, e) in enumerate(expressions)
    )

    init_state_vars_code = "\n        ".join(init_state_vars_from_y(state_vars))

    code = f"""
    extern "C" void _rhs_{id_}(long int *_n, double *__t, double *__restrict__ _y,
                               double *__restrict__ _ydot) {{

        double _t = *__t;

        // printf("%.15e   %.15e %.15e %.15e\\n", _t, _y[0], _y[1], _y[2]);

        {init_state_vars_code}
        {init_xi}
        {set_ydot}

        // printf("rhs:  t=%.15e ydot= %.15e %.15e %.15e\\n\\n",
        //        _t, _ydot[0], _ydot[1], _ydot[2]);
    }}
    """

    yield dedent(code)


def argsort(items):
    s = sorted(zip(items, itertools.count()))
    return list(zip(*s))[1]


def main():
    a, b, c, d, e, f = symbols("a b c d e f")

    M = Matrix(
        [
            [a, b, 0, 0, 0, 1],
            [b, a, c, 0, 0, 0],
            [0, c, a, d, 0, 0],
            [0, 0, d, a, e, 0],
            [0, 0, 0, e, a, f],
            [0, 0, 0, 0, f, a],
        ]
    )

    g, h, i = symbols("g H i")

    M = Matrix([[a, 0, 0], [b, c, 0], [d, e, f]])

    M = Matrix([[a, 0, 0], [b, c, 0], [d, e, f]])
    M = Matrix([[a, b, c], [0, d, e], [0, 0, f]])

    M = Matrix([[a, b, c, d], [b, c, d, e], [c, d, e, f], [d, e, f, g]])

    M = Matrix([[a, b, c], [0, d, e], [0, 0, f]])

    M = Matrix(
        [
            [a, b, 0, 0, 0, 0, 0],
            [b, a, c, 0, 0, 0, 0],
            [0, c, a, d, 0, 0, 0],
            [0, 0, d, a, e, 0, 0],
            [0, 0, 0, e, a, f, 0],
            [h, 0, 0, 0, f, a, f],
            [0, 0, 0, 0, i, 1, g],
        ]
    )
    M = Matrix([[a, 0, 0], [b, c, 0], [d, e, f]])
    M = Matrix([[a, b, c], [d, e, f], [g, h, i]])

    N = 3
    M = 20 * Identity(N).as_mutable()

    syms = symbols("a b c d e f g i j")

    for i in range(N - 1):
        M[i, i + 1] = syms[i % len(syms)]
        M[i + 1, i] = syms[i % len(syms)]

    M[0, N - 1] = a
    for i in range(N):
        M[N - 1, i] = b

    y0, y1, y2 = symbols("_y[0] _y[1] _y[2]")
    rhs = Matrix(
        [
            -0.04 * y0 + 1e4 * y1 * y2,
            0.04 * y0 - 1e4 * y1 * y2 - 3e7 * y1**2,
            3e7 * y1**2,
        ]
    )

    state_vars = [y0, y1, y2]

    traces = [[0, 1, 2]]

    generate_code(rhs, Symbol("t"), state_vars, traces)
