#===============================================================================
# split_methyl_bed.py
#===============================================================================

# Imports ======================================================================

import pandas
from itertools import groupby
import argparse
from contextlib import ExitStack




# Functions ====================================================================

def load_fasta(f):
    """ reads fasta data located at f and returns a dataframe of shape 3xN
        where N is the number of entries in the fasta file. The columns are:
        ID, INFO, SEQ. 
    """
    with open(f) as fin:
        grouper = groupby(fin, lambda l: l[0]==">")
        grouper = ("".join(v) for k, v in grouper)
        data = {h[1:-1]: v.replace("\n", "") for h, v in zip(grouper, grouper)}
    ret = pandas.Series(data).to_frame().reset_index()
    ret.columns = ["HEADER", "SEQ"]
    # ret.SEQ = ret.SEQ.upper()
    ret["ID"] = ret.HEADER.str.split().str[0]
    ret["INFO"] = ret.HEADER.str.split().str[1:].str.join(" ")
    return ret[["ID", "INFO", "SEQ"]]


def load_bed_file(f):
    """ load a methylbed as a dataframe ## NO LONGER USED
    """
    head = "REF START END NAME SCORE STRAND START_THICK END_THICK COLOR COVERAGE METH_RATE"
    head = head.split()
    df = pandas.read_csv(f, sep="\t", header=None, names=head)
    return df



def rev_comp(seq, language=dict(zip('ACTGN', "TGACN"))):
    return ''.join(language[c] for c in seq)[::-1]


def split_methyl_bed(methylbed, fasta, outprefix):
    ref = load_fasta(fasta).set_index("ID").sort_index()
    ref.SEQ = ref.SEQ.str.upper()
    suffixes = ['.CpG.bed', ".ChG.bed", ".Chh.bed"]
    outpaths = [outprefix + suf for suf in suffixes]
    with ExitStack() as stack, open(methylbed) as bed:
        outfiles = [stack.enter_context(open(f, "w")) for f in outpaths]
        for line in bed:
            fields = line.split("\t")
            start = int(fields[1])
            ctg = fields[0]
            strand = fields[5]
            if(strand == "+"):
                context = ref.loc[ctg].SEQ[start:start+3]
            else:
                context = rev_comp(ref.loc[ctg].SEQ[start-2:start+1])
            if(context[:2] == "CG"):
                outfiles[0].write(line)
            elif(context[0] == "C" and context[2] == "G"):
                outfiles[1].write(line)
            elif(context[0] == "C"):
                outfiles[2].write(line)
            else:
                raise ValueError(f"invalid context : {context}")



#takes input in order without flags
def get_args():
    parser = argparse.ArgumentParser(
        description=(
            "parses a methylbed into contexts by reference to a fasta file"
        )
    )
    parser.add_argument(
        "methylbed",
        help="a methylbed file from megalodon"
    )
    parser.add_argument(
        "fasta",
        help="the reference genome that the methylbed is paired with"
    )
    parser.add_argument(
        "outprefix",
        help="the prefix used for output files"
    )
    args = parser.parse_args()
    return args


def main():
    args = get_args()
    split_methyl_bed(args.methylbed, args.fasta, args.outprefix)
    

if(__name__ == "__main__"):
    main()
