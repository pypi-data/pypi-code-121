#===============================================================================
# intersect.py
#===============================================================================

"""intersect several bedmethyl files"""

# Imports ======================================================================

from pybedtools import BedTool
from functools import reduce




# Functions ====================================================================


def intersect_bedmethyl(bedmethyl, output_prefix, chromosomes=None):
    """Intersect two or more bedmethyl files

    Parameters
    ----------
    bedmethyl
        iterable of paths to bedmethyl formatted files of methylation results
    output_prefix
        prefix for output files
    chromosomes
        iterable of chromosomes to include in output
    """
    
    bedtools = tuple(BedTool(bed) for bed in bedmethyl)
    chromosomes=set(chromosomes) if chromosomes else None
    intersection = reduce(lambda a, b: a.intersect(b), bedtools)
    for bedtool, filename in zip((bt.intersect(intersection) for bt in bedtools), bedmethyl):
        bedtool.saveas(f'{output_prefix}-{filename}')
