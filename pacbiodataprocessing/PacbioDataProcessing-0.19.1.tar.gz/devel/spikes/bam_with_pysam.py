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

"""Reads or writes a bam file using pysam.

Usage:
bam_with_pysam.py MODE filename.bam [inputfile.bam]

Where MODE can be 'read' or 'write'

The 'write' mode requires another argument, inputfile.bam, 
that is taken as source for the header
"""

import sys

import pysam

MODES = ("read", "write")


def transform_back_and_forth(line, head):
    sline = line.to_string().encode()
    return pysam.AlignedSegment.fromstring(sline.decode(), head)

def read(filename, *ignored):
    f = pysam.AlignmentFile(filename, "rb", check_sq=False)
    header = f.header
    bheader = str(header).encode()
    print("Header type:", type(header))
    print("Header contents:")
    print(header.to_dict())
    print("Raw Header:")
    print(bheader)
    print("-"*40)
    #nlines = sum(1 for line in f)
    #print("The bam file contains", nlines, "lines")
    line = next(f)
    print(line)
    print(type(line))
    print("x"*40)
    h = pysam.AlignmentHeader.from_text(bheader.decode())
    print(str(h))

def write(filename, infilename, *ignored):
    f = pysam.AlignmentFile(infilename, "rb", check_sq=False)
    header = f.header.to_dict()
    with pysam.AlignmentFile(filename, "wb", header=header) as g:
        for line in f:
            newline = transform_back_and_forth(line, g.header)
            g.write(newline)


def main():
    try:
        mode, filename, *rest = sys.argv[1:]
    except ValueError:
        print(__doc__, file= sys.stderr)
        return 1

    if mode not in MODES:
        print(f"Unknown mode ({mode})", file= sys.stderr)
        print("", file= sys.stderr)
        print(__doc__, file= sys.stderr)
        return 1

    modef = globals()[mode]
    modef(filename, *rest)


if __name__ == "__main__":
    sys.exit(main())
