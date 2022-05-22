#===============================================================================
# export_metilene.py
#===============================================================================

"""Export methylation data formatted for input into methylene"""




# Imports ======================================================================

from itertools import groupby, chain
from functools import reduce
from operator import itemgetter
from pybedtools import BedTool
import pandas as pd




# Functions ====================================================================

def generate_rows(methyl_grouped: dict, chromosomes=None):
    """Parse a dict to generate rows of a metilene input file

    Parameters
    ----------
    methyl_grouped : dict
        dictionary of methylation values per input file/group
    chromosomes
        iterable of chromosomes to include in output

    Yields
    ------
    tuple
        data for a row of a metilene input file
    """

    for intervals in zip(*chain.from_iterable(methyl_grouped.values())):
        coord_set = {(i.chrom, i.stop) for i in intervals}
        if len(coord_set) == 1:
            chrom, pos = coord_set.pop()
            if (chromosomes is None) or (chrom in chromosomes):
                yield (chrom, pos) + tuple(i.fields[10] for i in intervals)
        else:
            raise RuntimeError(f'Mismatched intervals: {" ".join(repr(i) for i in intervals)}')


def export_metilene(bedmethyl, output, groups=None, chromosomes=None):
    """Convert methylation results to metilene input format and write to output
    file

    Parameters
    ----------
    bedmethyl
        iterable of paths to bedmethyl formatted files of methylation results
    output
        path to output file
    groups
        iterable of group labels to use
    chromosomes
        iterable of chromosomes to include in output
    """

    if not groups:
        groups = list(range(len(bedmethyl)))
    bedtools = tuple(BedTool(bed).sort() for bed in bedmethyl)
    intersection = reduce(lambda a, b: a.intersect(b), bedtools)
    methyl = tuple(bt.intersect(intersection) for bt in bedtools)
    methyl_grouped = {f'g{i}_{k}': tuple(p[1] for p in v) for i, (k, v) in
        enumerate(groupby(sorted(zip(groups, methyl), key=itemgetter(0)),
                          key=itemgetter(0)), start=1)}
    columns = ('chr', 'pos') + tuple(chain.from_iterable(
        (k,)*len(v) for k, v in methyl_grouped.items()))
    pd.DataFrame(generate_rows(methyl_grouped, chromosomes=set(chromosomes)),
        columns=columns).sort_values(by=['chr', 'pos']).to_csv(output,
                                                               index=False,
                                                               sep='\t')
