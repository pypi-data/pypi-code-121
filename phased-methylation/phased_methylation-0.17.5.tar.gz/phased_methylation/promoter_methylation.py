#===============================================================================
# promoter_methylation.py
#===============================================================================

"""Quantify promoter methylation"""

# Imports ======================================================================

from pybedtools import BedTool
import pandas as pd

from phased_methylation.parse_gff import (parse_gff, generate_promoter)
from phased_methylation.plot_bedtools import generate_feature_data
from phased_methylation.methylation_kde import methylation_kde




# Functions ====================================================================

def promoter_methylation(features, bedmethyl, upstream_flank: int = 2000,
                         downstream_flank: int = 0, chromosomes=None,
                         cytosines: bool = False, coverage: bool = False,
                         min_coverage: int = 1, bins: bool = False,
                         levels=['Min', 'Low', 'Mid', 'High', 'Max'], kde=None,
                         palette='mako_r'):
    """Quantify methylation in gene promoters

    Parameters
    ----------
    features
        path to GFF3 file containing gene coordinates
    bedmethyl
        path to bedmethyl formatted file containing methylation results
    upstream_flank : int
        size of upstream flank to include in promoter, in bp [2000]
    downstream_flank : int
        size of downstream flank to include in promoter, in bp [0]
    chromosomes
        iterable of chromosomes to include, or None to include all chromosomes
    cytosines : bool
        if True, include a column with the number of cytosines
    coverage : bool
        if True, include a coverage column in the results
    min_coverage : int
        minimum coverage for a gene to be included
    bins : bool
        if True, add an extra column binning promoters by methylation level
    kde
        if given, write a KDE plot of promoter bin methylation levels
    levels
        iterable of labels for binning by methylation level
    palette : str
        color palette for KDE plot
    """

    genes = pd.DataFrame(parse_gff(features,
        flank=max(upstream_flank, downstream_flank)),
        columns=('seqid', 'start', 'end', 'strand', 'attributes'))
    genes.index = (attr['ID'] for attr in genes['attributes'])
    promoter = BedTool(tuple(generate_promoter(genes,
        upstream_flank=upstream_flank, downstream_flank=downstream_flank)))
    methyl = BedTool(bedmethyl)
    methyl_promoter = methyl.intersect(promoter, wo=True)
    df = pd.DataFrame(
        generate_feature_data(methyl_promoter, chromosomes=chromosomes),
        columns=('chrom', 'start', 'end', 'gene', 'strand', 'cytosines', 'coverage', 'methyl_sum')
    ).groupby(by=['chrom', 'start', 'end', 'gene', 'strand'], as_index=False).sum().sort_values(by=['chrom', 'start'])
    df.index = df['gene']
    df['Methylation level (%)'] = df['methyl_sum'] / df['cytosines']
    df['Discrete level'] = pd.qcut(df['Methylation level (%)'].rank(method='first'), q=len(levels), labels=levels)
    if kde:
        methylation_kde(df, kde, palette=palette)
    for _, (chrom, start, end, gene, strand, cyt, cov, methyl, level) in df.iloc[:,[0,1,2,3,4,5,6,8,9]].iterrows():
        row = (chrom, start, end, gene, f'{methyl:.2f}', strand) + cytosines*(cyt,) + coverage*(cov,) + bins*(level,)
        if cov >= min_coverage:
            print(*row, sep='\t')
