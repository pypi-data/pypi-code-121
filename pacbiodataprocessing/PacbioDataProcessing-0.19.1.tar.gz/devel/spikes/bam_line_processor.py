#######################################################################
#
# Copyright (C) 2022 David Palao
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

"""Little program to explore performance of line processing
"""

from timeit import timeit
from random import randint

from pacbio_data_processing.bam import BamFile


TEST_BAM = "/home/palao/projects/pacbio/data/ini4D05/m54099_200711_014004.subreads.bam"


def process_each_line():
    bam = BamFile(TEST_BAM)
    molid = b"2322"
    found = False
    for line in bam:
        if line.molecule_id == molid:
            found = True


def process_1thousandth_of_lines():
    bam = BamFile(TEST_BAM)
    molid = b"2322"
    found = False
    count = 0
    for line in bam:
        if count == 1000:
            if line.molecule_id == molid:
                found = True
            count = 0
        else:
            count += 1

def process_1thousandth_of_lines_random():
    bam = BamFile(TEST_BAM)
    molid = b"2322"
    found = False
    for line in bam:
        if randint(1, 1000) == 2:
            if line.molecule_id == molid:
                found = True


def process_1st_hundredth_of_lines():
    bam = BamFile(TEST_BAM)
    molid = b"2322"
    found = False
    for i, line in enumerate(bam):
        if line.molecule_id == molid:
            found = True
        if i == 999:
            break


if __name__ == "__main__":
    for func in (
            # "process_each_line",
            # "process_1thousandth_of_lines",
            # "process_1thousandth_of_lines_random"
            "process_1st_hundredth_of_lines",):
        result = timeit(f"{func}()", globals=globals(), number=3)
        print(f"{func:20s} -> {result} s")
