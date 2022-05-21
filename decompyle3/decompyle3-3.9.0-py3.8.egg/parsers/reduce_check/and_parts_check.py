#  Copyright (c) 2020, 2022 Rocky Bernstein
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.


def and_parts_check(
    self, lhs: str, n: int, rule, ast, tokens: list, first: int, last: int
) -> bool:

    for t in range(first, last):
        print(tokens[t])
    print("=" * 40)
    from trepan.api import debug

    debug()
    return ast[-1][-1].attr != ast[0][-1].attr
