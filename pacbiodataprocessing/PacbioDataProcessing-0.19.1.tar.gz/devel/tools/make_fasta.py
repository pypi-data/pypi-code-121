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

"""given a fasta file as input, creates its index. If a second argument
is passed, a new fasta is created and the index is done for it.
For instance:

$ ./make_fasta.py sample.fasta

will produce a ``sample.fasta.fai`` file.

But

$ ./make_fasta.py sample.fasta second.fasta

will create ``second.fasta`` as a copy of ``sample.fasta``
and an index for it will be also done: ``second.fasta.fai``.

The suffixes of fasta files can be also ``.fa``.

"""

import sys

import Bio.SeqIO
from pyfaidx import Faidx, Fasta


def make_it_with_bio(inname, outname):
    inseq = Bio.SeqIO.parse(inname, "fasta")

    with open(outname, "w") as outf:
        Bio.SeqIO.write(inseq, outf, "fasta")

def make_it_with_pyfaidx(inname, outname):
    # this is broken:
    infasta = Fasta(inname)
    outfasta = Fasta(outname)
    # How can one do this without Biopython?


def main():
    inname = sys.argv[1]
    try:
        outname = sys.argv[2]
    except IndexError:
        outname = inname
    else:
        make_it_with_bio(inname, outname)
        #make_it_with_pyfaidx(inname, outname)
    
    # this creates the index:
    idx = Faidx(outname)


if __name__ == "__main__":
    sys.exit(main())

