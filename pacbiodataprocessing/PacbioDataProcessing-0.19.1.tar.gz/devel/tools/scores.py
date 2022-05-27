#######################################################################
#
# Copyright (C) 2021 David Palao
#
# This file is part of PacBioDataProcessing.
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

import sys
from math import log10
from statistics import mean


def combined_score(*qs):
    pok = 1
    for q in qs:
        poki = 1-10**(-q/10)
        pok *= poki
    try:
        Q = -10*log10(1-pok)
    except ValueError:
        Q = min(qs)
    return Q


if __name__ == "__main__":
    scores = [float(i) for i in sys.argv[1:]]
    cscore = combined_score(*scores)
    aver = mean(scores)
    mini = min(scores)
    print(f"Scores: {scores}")
    print(f" - combined : {cscore}")
    print(f" - mean     : {aver}")
    print(f" - min      : {mini}")
