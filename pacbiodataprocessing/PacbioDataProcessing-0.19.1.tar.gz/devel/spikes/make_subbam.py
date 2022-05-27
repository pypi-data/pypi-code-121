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

"""Create a bam file from an input bam and a set of molecule ids 
(that are supposed to be in the input bam).
"""

import sys
import argparse
from pathlib import Path

from pacbio_data_processing.bam import BamFile


def parse_cl():
    parser = argparse.ArgumentParser(__doc__)
    parser.add_argument(
        "input_bam", type=Path, metavar="INPUT-BAM",
        help="source file for the selected molecules"
    )
    parser.add_argument(
        "output_bam", type=Path, metavar="OUTPUT-BAM",
        help="destination file for the selected molecules"
    )
    parser.add_argument(
        "-m", "--molecules", nargs="+",
        help="molecules from input to include in the output"
    )
    return parser.parse_args()


def gen_body(inbam, molecules):
    for line in inbam:
        if line.molecule_id.decode() in molecules:
            yield line

    
def main():
    conf = parse_cl()
    inbam = BamFile(conf.input_bam)
    gbody = gen_body(inbam, conf.molecules)
    outbam = BamFile(conf.output_bam, "w")
    outbam.write(header=inbam.header.rstrip(b"\n")+b"\n", body=gbody)
    

if __name__ == "__main__":
    sys.exit(main())
