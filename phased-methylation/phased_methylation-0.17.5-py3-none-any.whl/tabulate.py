#===============================================================================
# tabulate.py
#===============================================================================

# Imports ======================================================================

from argparse import ArgumentParser
from pybedtools import BedTool
import numpy as np
from statistics import mean



# Functions ====================================================================

def compute_fft_val(values, freq=[1]):
    """document fft_val
    """
    values_float = tuple(float(x) for x in values)
    abs_fft = np.abs(np.fft.fft(values_float))
    return mean(abs_fft[f] for f in freq)



def tabulate(bed, names=None, dropna=False, fft=None, exclusive=False,
             min: int = 0, max: int = 100):
    """document tabulate
    """

    if not names:
        names = list(str(n) for n in range(len(bed)))
    if len(names) != len(bed):
        raise RuntimeError('number of names does not match number of input files')
    if fft or exclusive:
        dropna = True
    merged = BedTool('\t'.join(i.fields+[str(n)])+'\n'
                     for b, n in zip(bed, names)
                     for i in BedTool(b)).sort().merge(
                        s=True, c='4,5,6,7',
                        o='distinct,collapse,first,collapse')
    if fft:
        print('chrom', 'start', 'stop', 'strand', 'gene', *names, 'fft_val', sep='\t')
    else:
        print('chrom', 'start', 'stop', 'strand', 'gene', *names, sep='\t')
    for i in merged:
        chrom, start, stop, gene, methyl, strand, name = i.fields
        methyl_dict = dict(zip(name.split(','), methyl.split(',')))
        values = tuple(methyl_dict.get(n, 'NA') for n in names)
        if (not dropna) or ('NA' not in values):
            values_float = set(float(x) for x in values if x != 'NA')
            if any(v < min or v > max for v in values_float):
                continue
            if exclusive and (0.0 in values_float or 100.0 in values_float):
                continue
            if fft:
                fft_val = compute_fft_val(values, freq=fft)
                print(chrom, start, stop, strand, gene, *values, fft_val, sep='\t')
            else:
                print(chrom, start, stop, strand, gene, *values, sep='\t')
