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

"""Template to create a fake version of 'ccs'.
"""

import sys
import shutil
from pathlib import Path, PosixPath  # noqa: F401
import time
import os


datadir = _DATA_DIR_  # noqa: F821

ccsfiles = {
    ('blasr.11mols.bam', 'ccs.blasr.11mols.bam'): (
        datadir/'ccs.blasr.11mols.bam',
        datadir/'ccs.blasr.11mols.bam.pbi',
        datadir/'ccs.blasr.11mols.zmw_metrics.json.gz',
        datadir/'ccs.blasr.11mols.ccs_report.txt',
    ),
    ('baseline.bam', 'ccs.baseline.bam'): (
        datadir/'ccs.baseline.bam',
        datadir/'ccs.baseline.bam.pbi',
        datadir/'ccs.baseline.zmw_metrics.json.gz',
        datadir/'ccs.baseline.ccs_report.txt',
    ),
    ('blasr.8mols.bam', 'ccs.blasr.8mols.bam'): (
        datadir/'ccs.blasr.8mols.bam',
        datadir/'ccs.blasr.8mols.bam.pbi',
        datadir/'ccs_report.txt',
    ),
    ('blasr.12mols.bam', 'ccs.blasr.12mols.bam'): (
        datadir/'ccs.blasr.12mols.bam',
        datadir/'ccs.blasr.12mols.bam.pbi',
        datadir/'ccs.blasr.12mols.zmw_metrics.json.gz',
        datadir/'ccs.blasr.12mols.ccs_report.txt',
    ),
    ('9mols.bam', 'ccs.9mols.bam'): (
        datadir/'ccs.9mols.bam',
        datadir/'ccs.9mols.bam.pbi',
        datadir/'ccs_report.txt',
    ),
}


def heavy_lifting():
    # the sleep time must be >~ 0.2 to allow the process hunter function
    # "count_nprocs" to have a chance to find this process:
    pid = os.getpid()
    markerfile = Path(f".ccs.pid.{pid}")
    markerfile.touch()
    time.sleep(0.3)


if __name__ == "__main__":
    inbam = Path(sys.argv[1])
    assert inbam.is_file()
    outbam = Path(sys.argv[2]).name
    for src in ccsfiles[(inbam.name, outbam)]:
        dst = src.name
        shutil.copyfile(src, dst)

    heavy_lifting()
    print(_STDERR_, file=sys.stderr, end="")  # noqa: F821
    sys.exit(_EXIT_CODE_)  # noqa: F821
