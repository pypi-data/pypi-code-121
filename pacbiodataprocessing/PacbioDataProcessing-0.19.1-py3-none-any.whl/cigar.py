#######################################################################
#
# Copyright (C) 2021 David Palao
#
# This file is part of PacBio data processing.
#
#  PacBioDataProcessing is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  PacBio data processing is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with PacBioDataProcessing. If not, see <http://www.gnu.org/licenses/>.
#
#######################################################################

"""This module provides basic '*re-invented*' functionality to handle
Cigars.
A Cigar describes the differences between two sequences by providing a
series of operations that one has to apply to one sequence to obtain the
other one. For instance, given these two sequences:

sequence 1 (e.g. from the refenrece)::

  AAGTTCCGCAAATT

and

sequence 2 (e.g. from the aligner)::

  AAGCTCCCGCAATT

The Cigar that brings us from sequence 1 to sequence 2 is::

  3=1X3=1I4=1D2=

where the numbers refer to the amount of letters and the symbols'
meaning can be found in the table below. Therefore the Cigar in the
example is a shorthand for:

*3 equal bases followed by 1 replacement followed by 3 equal bases*
*followed by 1 insertion followed by 4 equal bases*
*followed by 1 deletion followed by 2 equal bases*

+--------+-------------+
| symbol |   meaning   |
+========+=============+
|   =    |  equal      |
+--------+-------------+
|   I    | insertion   |
+--------+-------------+
|   D    | deletion    |
+--------+-------------+
|   X    | replacement |
+--------+-------------+
|   S    | soft clip   |
+--------+-------------+
|   H    | hard clip   |
+--------+-------------+

"""

import re


_SYMBOLS = "=IDSXH"


class Cigar:
    def __init__(self, incigar):
        self._incigar = str(incigar)

    def __len__(self):
        return len(list(self.__iter__()))

    def __iter__(self):
        return (
            _.group() for _ in re.finditer(rf"\d+[{_SYMBOLS}]", self._incigar))

    def __repr__(self):
        return "Cigar({})".format(repr(self._incigar))

    def __eq__(self, other):
        return self._incigar == other._incigar

    @property
    def number_pb_diffs(self):
        diffs = 0
        for item in self:
            howmany = int(item[:-1])
            sym = item[-1]
            if sym != "=":
                diffs += howmany
        return diffs

    @property
    def number_diff_items(self):
        num = 0
        for item in self:
            sym = item[-1]
            if sym != "=":
                num += 1
        return num

    @property
    def number_diff_types(self):
        return len({_[-1] for _ in self if _[-1] != "="})

    @property
    def number_pbs(self):
        num = 0
        for item in self:
            sym = item[-1]
            howmany = int(item[:-1])
            if sym in "=XISH":
                num += howmany
        return num

    @property
    def diff_ratio(self):
        """difference ratio: ``1`` means that *each* base is different;
        ``0`` means that all the bases are equal.
        """
        return self.number_pb_diffs/self.number_pbs

    @property
    def sim_ratio(self):
        """similarity ratio: ``1`` means that all the bases are equal;
        ``0`` means that *each* base is different.

        This is computed from :py:meth:`diff_ratio`.
        """
        return 1-self.diff_ratio
