#!/usr/bin/env python

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

"""Template to create a fake version of a faulty 'ccs' that
does not produce a result.
"""

import time
import sys
import os
from pathlib import Path

# the sleep time must be >~ 0.2 to allow the process hunter function
# "count_nprocs" to have a chance to find this process:


def heavy_lifting():
    # the sleep time must be >~ 0.2 to allow the process hunter function
    # "count_nprocs" to have a chance to find this process:
    pid = os.getpid()
    markerfile = Path(f".ccs.pid.{pid}")
    markerfile.touch()
    time.sleep(0.3)


if __name__ == "__main__":
    heavy_lifting()
    print(_STDERR_, file=sys.stderr, end="")  # noqa: F821
    sys.exit(_EXIT_CODE_)  # noqa: F821
