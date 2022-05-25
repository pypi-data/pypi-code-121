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

import multiprocessing

from sympy import Matrix


def _jacobian(args):
    expressions, variables = args
    return expressions.jacobian(variables)


def jacobian(expressions, variables, N=4):
    if expressions.rows < 4 * N:
        return expressions.jacobian(variables)
    blocks = [Matrix(expressions[i::N]) for i in range(N)]
    args = [(b, variables) for b in blocks]
    with multiprocessing.Pool(N) as pool:
        partial_results = pool.map(_jacobian, args)

    result = [partial_results[i % N][i // N, :] for i in range(expressions.rows)]
    return Matrix(result)
