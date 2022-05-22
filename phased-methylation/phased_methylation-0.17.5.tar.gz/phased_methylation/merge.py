#===============================================================================
# merge.py
#===============================================================================

"""merge two bedmethyl files"""

# Imports ======================================================================

from pybedtools import BedTool
from itertools import chain
import numpy as np




# Functions ====================================================================


def merge_bedmethyl(bedmethyl, chromosomes=None):
    """Merge two or more bedmethyl files

    Parameters
    ----------
    bedmethyl
        iterable of paths to bedmethyl formatted files of methylation results
    chromosomes
        iterable of chromosomes to include in output
    """
    
    bedtools = tuple(BedTool(bed) for bed in bedmethyl)
    chromosomes=set(chromosomes) if chromosomes else None
    merged = BedTool((i for i in chain(*bedtools)
        if (chromosomes is None) or (i.chrom in chromosomes))).sort().merge(
        s=True,
        c='4,5,6,7,8,9,10,11',
        o='first,sum,first,first,last,first,collapse,collapse')
    for i in merged:
        chrom, start, stop = i.fields[:3]
        score = min(int(i.fields[4]), 1000)
        strand, thick_start, thick_stop = i.fields[5:8]
        coverage, methyl = (tuple(x) for x in zip(
            *((int(c), float(m))
            for c, m in zip(i.fields[9].split(','), i.fields[10].split(','))
            if (m != '.'))))
        if sum(coverage) == 0:
            continue
        print(chrom, start, stop, '.', score, strand, thick_start,
                thick_stop, '0,0,0', sum(coverage),
                np.average(methyl, weights=coverage), sep='\t')
