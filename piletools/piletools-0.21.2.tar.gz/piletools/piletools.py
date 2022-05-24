#!/usr/bin/python

import argparse
import re
import os

import wiggelen

from . import docSplit, version, usage

def findall(string, substring):
    """
    Find the index of all occurences of a substring in a string.

    @arg string:
    @type string: string
    @arg substring:
    @type substring: string

    @returns: List of indices.
    @rtype: list[int]
    """
    occurences = []

    for i in re.finditer(substring, string):
        occurences.append(i.start())

    return occurences
#findall

class PileRecord(object):
    """
    Container for a pileup record.
    """
    def __init__(self, line):
        """
        Initialise the class.

        @arg line: One line of a pileup file.
        @type line: str
        """
        field = line.strip().split()

        self.chrom = field[0]
        self.pos = int(field[1])
        self.ref = field[2]
        self.coverage = int(field[3])

        self.bases = ""
        self.qual = ""
        if self.coverage:
            self.bases = field[4]
            self.qual = field[5]
        #if
    #__init__

    def __str__(self):
        return "%s\t%i\t%s\t%i\t%s\t%s" % (self.chrom, self.pos, self.ref,
            self.coverage, self.bases, self.qual)
#PileRecord

class PileReader(object):
    """
    Pileup parser.
    """
    def __init__(self, handle):
        """
        Initialise the class.

        @arg handle: Open readable handle to a pileup file.
        @type handle: stream
        """
        self.__handle = handle
    #__init__

    def __iter__(self):
        return self

    def __next__(self):
        """
        Return a PileRecord obect for each line in the pileup file.
        """
        line = self.__handle.readline()

        if not line:
            raise StopIteration

        return PileRecord(line)
    #next
#PileReader

def mpileup2tagwig(handle, forward, threePrime):
    """
    Scan a pileup file for start of reads, determine whether the read is in
    forward or reverse orientation and return this information, depending on
    which strand we are looking at.

    @arg handle: Open handle to the pileup file.
    @type handle: file handle
    @arg forward: Record reads that map to the forward strand.
    @type forward: bool
    @arg threePrime: Record the 3' end of the read instead of the 5' end.
    @arg threePrime: bool
    """
    for record in PileReader(handle):
        depth = 0

        for i in findall(record.bases, '\^'):   # Find all starts of reads.
            if record.bases[i + 2] in ".ACGTN": # Mapped to the forward strand?
                if forward and not threePrime:
                    depth += 1
            else:
                if not forward and threePrime:
                    depth += 1
        #for

        for i in findall(record.bases, '\$'):   # Find all ends of reads.
            if record.bases[i - 1] in ",acgtn": # Mapped to the reverse strand?
                if not forward and not threePrime:
                    depth += 1
            else:
                if forward and threePrime:
                    depth += 1
        #for

        if depth:
            yield (record.chrom, record.pos, depth)
    #for
#mpileup2tagwig

def mpileup2wig(handle, gaps):
    """
    Convert an mpileup file to to a wiggle file.

    @arg handle: Open readable handle to an mpileup file.
    @type handle: stream
    @arg gaps: Select what to do with large gaps.
    @type gaps: enum(None, "remove", "show")
    """
    for record in PileReader(handle):
        coverage = record.coverage

        if gaps: # Do something special with gaps.
            gapsCoverage = record.bases.count('>') + record.bases.count('<')

            if gaps == "remove":  # Ignore gaps.
                coverage -= gapsCoverage
            if gaps == "show":    # Only show gaps.
                coverage = gapsCoverage
        #if

        if coverage:
            yield (record.chrom, record.pos, coverage)
    #for
#mpileup2wig

def main():
    """
    Main entry point.
    """
    input_parser = argparse.ArgumentParser(add_help=False)
    input_parser.add_argument("INPUT", type=argparse.FileType('r'),
        help="pileup file")

    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=usage[0], epilog=usage[1])
    parser.add_argument('-v', action="version", version=version(parser.prog))
    subparsers = parser.add_subparsers(dest="subcommand")
    subparsers.required = True

    parser_pileup2wig = subparsers.add_parser("mpileup2wig",
        parents=[input_parser], description=docSplit(mpileup2wig))
    parser_pileup2wig.add_argument("OUTPUT", type=argparse.FileType('w'),
        help="output file")
    parser_pileup2wig.add_argument('-g', dest='gaps', action="store_const",
        const="remove", help='Remove large gaps.')
    parser_pileup2wig.add_argument('-G', dest='gaps', action="store_const",
        const="show", help='Only show large gaps.')

    parser_pileup2tagwig = subparsers.add_parser("mpileup2tagwig",
        parents=[input_parser], description=docSplit(mpileup2tagwig))
    parser_pileup2tagwig.add_argument("OUTPUT", type=argparse.FileType('w'),
        nargs=2, help="forward and reverse output files")
    parser_pileup2tagwig.add_argument('-p', dest='threePrime', default=False,
        action="store_true", help="record the 3' end of the reads")

    args = parser.parse_args()
    name = os.path.splitext(os.path.basename(args.INPUT.name))[0]

    if args.subcommand == "mpileup2wig":
        wiggelen.write(mpileup2wig(args.INPUT, args.gaps), args.OUTPUT, str,
            name, name)

    if args.subcommand == "mpileup2tagwig":
        wiggelen.write(mpileup2tagwig(args.INPUT, True, args.threePrime),
            args.OUTPUT[0], str, name + "_forward", name + "_forward")
        args.INPUT.seek(0)
        wiggelen.write(mpileup2tagwig(args.INPUT, False, args.threePrime),
            args.OUTPUT[1], str, name + "_reverse", name + "_reverse")
    #if
#main

if __name__ == "__main__":
    main()
