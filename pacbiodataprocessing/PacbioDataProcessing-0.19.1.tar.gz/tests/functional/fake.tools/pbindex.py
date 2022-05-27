#!/usr/bin/env python

#######################################################################
#
# Copyright (C) 2021, 2022 David Palao
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

"""Template to create a fake version of 'pbindex'.
"""

import sys
import shutil
from pathlib import Path, PosixPath  # noqa: F401

datadir = _DATA_DIR_  # noqa: F821

bam2pbi = {
    'blasr.11mols.19399571.bam': datadir/'blasr.11mols.19399571.bam.pbi',
    'blasr.11mols.23658875.bam': datadir/'blasr.11mols.23658875.bam.pbi',
    'blasr.11mols.28836053.bam': datadir/'blasr.11mols.28836053.bam.pbi',
    'blasr.11mols.29229724.bam': datadir/'blasr.11mols.29229724.bam.pbi',
    'blasr.11mols.45744686.bam': datadir/'blasr.11mols.45744686.bam.pbi',
    'blasr.11mols.52167204.bam': datadir/'blasr.11mols.52167204.bam.pbi',
    'blasr.11mols.55116046.bam': datadir/'blasr.11mols.55116046.bam.pbi',
    'blasr.11mols.59179888.bam': datadir/'blasr.11mols.59179888.bam.pbi',
    'blasr.11mols.60359568.bam': datadir/'blasr.11mols.60359568.bam.pbi',
    'blasr.11mols.72352689.bam': datadir/'blasr.11mols.72352689.bam.pbi',
    'blasr.11mols.74515099.bam': datadir/'blasr.11mols.74515099.bam.pbi',
    'blasr.12mols.19399571.bam': datadir/'blasr.12mols.19399571.bam.pbi',
    'blasr.12mols.23658875.bam': datadir/'blasr.12mols.23658875.bam.pbi',
    'blasr.12mols.28836053.bam': datadir/'blasr.12mols.28836053.bam.pbi',
    'blasr.12mols.29229724.bam': datadir/'blasr.12mols.29229724.bam.pbi',
    'blasr.12mols.45744686.bam': datadir/'blasr.12mols.45744686.bam.pbi',
    'blasr.12mols.52167204.bam': datadir/'blasr.12mols.52167204.bam.pbi',
    'blasr.12mols.55116046.bam': datadir/'blasr.12mols.55116046.bam.pbi',
    'blasr.12mols.59179888.bam': datadir/'blasr.12mols.59179888.bam.pbi',
    'blasr.12mols.60359568.bam': datadir/'blasr.12mols.60359568.bam.pbi',
    'blasr.12mols.72352689.bam': datadir/'blasr.12mols.72352689.bam.pbi',
    'blasr.12mols.74515099.bam': datadir/'blasr.12mols.74515099.bam.pbi',
    'blasr.12mols.9900000.bam': datadir/'blasr.12mols.9900000.bam.pbi',
    'blasr.8mols.25294.bam': datadir/'blasr.8mols.25294.bam.pbi',
    'blasr.8mols.150700.bam': datadir/'blasr.8mols.150700.bam.pbi',
    'blasr.8mols.14728.bam': datadir/'blasr.8mols.14728.bam.pbi',
    'blasr.8mols.107947.bam': datadir/'blasr.8mols.107947.bam.pbi',
    'blasr.8mols.67334.bam': datadir/'blasr.8mols.67334.bam.pbi',
    'blasr.8mols.49610.bam': datadir/'blasr.8mols.49610.bam.pbi',
    'blasr.8mols.89194.bam': datadir/'blasr.8mols.89194.bam.pbi',
    'blasr.8mols.86474.bam': datadir/'blasr.8mols.86474.bam.pbi',
    'blasr.baseline.19399571.bam': datadir/'blasr.baseline.19399571.bam.pbi',
    'blasr.baseline.23658875.bam': datadir/'blasr.baseline.23658875.bam.pbi',
    'blasr.baseline.28836053.bam': datadir/'blasr.baseline.28836053.bam.pbi',
    'blasr.baseline.29229724.bam': datadir/'blasr.baseline.29229724.bam.pbi',
    'blasr.baseline.45744686.bam': datadir/'blasr.baseline.45744686.bam.pbi',
    'blasr.baseline.52167204.bam': datadir/'blasr.baseline.52167204.bam.pbi',
    'blasr.baseline.55116046.bam': datadir/'blasr.baseline.55116046.bam.pbi',
    'blasr.baseline.59179888.bam': datadir/'blasr.baseline.59179888.bam.pbi',
    'blasr.baseline.60359568.bam': datadir/'blasr.baseline.60359568.bam.pbi',
    'blasr.baseline.72352689.bam': datadir/'blasr.baseline.72352689.bam.pbi',
    'blasr.baseline.74515099.bam': datadir/'blasr.baseline.74515099.bam.pbi',
    'blasr.9mols.67334.bam': datadir/'blasr.9mols.67334.bam.pbi',
    'blasr.9mols.150700.bam': datadir/'blasr.9mols.150700.bam.pbi',
    'blasr.9mols.107947.bam': datadir/'blasr.9mols.107947.bam.pbi',
    'pi-shifted.blasr.9mols.155993.bam':
    datadir/'pi-shifted.blasr.9mols.155993.bam.pbi',
}

if __name__ == "__main__":
    if _EXIT_CODE_ == 0:  # noqa: F821
        bam = Path(sys.argv[1])
        for failing_mol in _FAILING_MOLS_:  # noqa: F821
            if failing_mol in bam.name:
                print("who knows what happens here", file=sys.stderr)
                sys.exit(1)
        src = bam2pbi[bam.name]
        dst_name = src.name
        if bam.name.startswith("blasr.baseline"):
            dst_name.replace("11mols", "baseline")
        dst = bam.parent/dst_name
        shutil.copyfile(src, dst)
    sys.exit(_EXIT_CODE_)  # noqa: F821
