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

from sympy import BlockMatrix, Matrix, Number, Symbol, cse

from .symbol import symbols


def quick_inv(M):
    M = M.copy()
    n = M.shape[0]
    si = symbols(" ".join(f"_a{i}" for i in range(n * n)))
    cache = {}
    for i in range(n):
        for j in range(n):
            if not isinstance(M[i, j], (Symbol, Number)):
                symbol = si[i + n * j]
                cache[symbol] = M[i, j]
                M[i, j] = symbol

    return M.inv().subs(cache)


class RecursiveInverse:
    def __init__(self):
        self.xii = []
        self.next_symbol = self._symbol_generator()

    def _symbol_generator(self):
        i = 0
        while True:
            yield Symbol(f"__x{i}")
            i += 1

    def __call__(self, M):
        xii = []
        Minv = self._inv(xii, M)
        return xii, Minv

    def _inv(self, xii, M):
        n = M.shape[0]
        if n > 2:
            A = M[: n // 2, : n // 2]
            B = M[: n // 2, n // 2 :]
            C = M[n // 2 :, : n // 2]
            D = M[n // 2 :, n // 2 :]

            Ai = self._inv(xii, A)
            xi, (Ai,) = cse(Ai, self.next_symbol)
            xii.extend(xi)

            R = D - C * Ai * B

            Ri = self._inv(xii, R)
            xi, (Ri,) = cse(Ri, self.next_symbol)
            xii.extend(xi)

            M1 = Ai + Ai * B * Ri * C * Ai
            M2 = -Ai * B * Ri
            M3 = -Ri * C * Ai
            M4 = Ri

            Mi = Matrix(BlockMatrix([[M1, M2], [M3, M4]]))
        elif n == 1:
            Mi = M**-1
        else:
            Mi = quick_inv(M)
        return Mi


rec_inv = RecursiveInverse()
