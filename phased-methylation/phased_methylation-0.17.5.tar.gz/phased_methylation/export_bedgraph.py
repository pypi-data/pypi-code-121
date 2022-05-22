#===============================================================================
# export_bedgraph.py
#===============================================================================

"""Export methylation data in bedgraph format"""

from pybedtools import BedTool

def export_bedgraph(bedmethyl: str, chromosomes=None, coverage: bool = False):
    """Convert methylation results to bedgraph format and print to stdout

    Parameters
    ----------
    bedmethyl : str
        path to a bedmethyl formatted file of methylation results
    chromosomes
        iterable of chromosomes to include in output
    coverage : bool
        if true, write a coverage track instead of a methylation track
    """

    bedtool = BedTool(bedmethyl).sort()
    if chromosomes:
        c = set(chromosomes)
        if coverage:
            for chrom, start, stop, *_, cov, _ in (i.fields for i in bedtool):
                if chrom in  c:
                    print(chrom, start, stop, cov, sep='\t')
        else:
            for chrom, start, stop, *_, methyl in (i.fields for i in bedtool):
                if chrom in  c:
                    print(chrom, start, stop, methyl, sep='\t')
    else:
        if coverage:
            for chrom, start, stop, *_, cov, _ in (tuple(i) for i in bedtool):
                print(chrom, start, stop, cov, sep='\t')
        else:
            for chrom, start, stop, *_, methyl in (tuple(i) for i in bedtool):
                print(chrom, start, stop, methyl, sep='\t')
