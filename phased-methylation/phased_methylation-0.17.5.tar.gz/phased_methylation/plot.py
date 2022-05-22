#===============================================================================
# plot.py
#===============================================================================

"""Plot methylation data across chromosomes"""




# Imports ======================================================================

from itertools import chain, groupby, accumulate, islice, cycle
from operator import itemgetter
from pybedtools import BedTool
from pyfaidx import Fasta

import pandas as pd
import seaborn as sns




# Constants ====================================================================

COLOR_PALETTE = sns.color_palette().as_hex()




# Functions ====================================================================

def get_chromosome_sizes_from_ref(reference: str):
    """Extract chromosome sizes from reference FASTA

    Parameters
    ----------
    reference : str
        path to reference FASTA file

    Returns
    -------
    DataFrame
        name and size of each chromosome
    """

    return pd.DataFrame(((k, len(v)) for k, v in Fasta(reference).items()),
                        columns=('name', 'size'))


def approx_chromosome_sizes_from_data(bedtools):
    """Approximate chromosome sizes from BED data

    Parameters
    ----------
    bedtools
        iterble of bedtools generated from methylbed files

    Returns
    -------
    DataFrame
        name and approximate size of each chromosome
    """

    return pd.DataFrame(((key, max(tuple(zip(*val))[1]))
        for key, val in groupby(sorted((k, (max(int(x[2]) for x in v)))
            for k, v in groupby((i.fields for bt in bedtools for i in bt),
                key=itemgetter(0))),
            key=itemgetter(0))), columns=('name', 'size'))


def generate_plotting_data(bedtools, groups, size, scale: float = 1,
                           shift: float = 0, bin_size: int = 0):
    """Construct rows of preprocessed data for the plotting data frame. Data
    are binned by rounding to the nearest bin coordinate, while bin coordinates
    are determined by the bin size parameter.

    Parameters
    ----------
    bedtools
        iterable of bedtools generated from methylbed data
    groups
        iterable of group names
    size
        chromosome size in bp
    scale
        ratio of chromosome size to mean chromosome size
    shift
        x-axis shift of this chromosome, for plots showing multiple chromosomes
        consecutively
    bin_size
        set bin size. The input <int> is converted to the bin size by the
        formula: 10^(<int>+6) bp. The default value is 0, i.e. 1-megabase bins.

    Yields
    ------
    tuple
        bin coordinate, value, and group ID of a methylation data point
    """

    yield from ((min(round(int(pos), -6-bin_size), size)/size*scale + shift,
                float(meth), group, f'{group}_{chrom}')
        for chrom, _, pos, _, _, _, _, _, _, _, meth, group
        in (i.fields+[g] for bt, g in zip(bedtools, groups) for i in bt))


def plot(bedmethyl, output, reference=None, chromosomes=['1'], groups=None,
         title: str = 'Methylation', legend: bool = False,
         legend_title: str = 'Group', bin_size: int = 0,
         width: float = 8.0, color_palette=COLOR_PALETTE, alpha: float = 0.5):
    """Generate a plot of average methylation levels across one or more
    chromosomes

    Parameters
    ----------
    bedmethyl
        iterable of paths path to input bedmethyl files
    output
        path to output file (pdf, png, or svg)
    reference
        path to FASTA file for reference genome
    chromosomes
        iterable of chromosomes to include in plot
    groups
        iterable of group ids for input files
    title : str
        title for plot
    legend : bool
        if true, draw a levend for the plot
    legend_title : str
        title for plot legend
    bin_size : int
        set bin size. The input <int> is converted to the bin size by the
        formula: 10^(<int>+6) bp. The default value is 0, i.e. 1-megabase bins.
    width : float
        width of plot in inches
    color_palette
        color palette for lines
    alpha
        transparency of lines
    """

    if not groups:
        groups = list(range(len(bedmethyl)))
    print('importing data')
    methyl = tuple(BedTool(bed) for bed in bedmethyl)
    sizes = (get_chromosome_sizes_from_ref(reference) if reference
             else approx_chromosome_sizes_from_data(methyl))
    sizes.index = sizes.name
    sizes = sizes.loc[chromosomes, 'size']
    scales = sizes / sizes.mean()
    shifts = pd.Series(accumulate(chain((0,),scales[:-1])), index=scales.index)

    print('generating plotting data')
    plotting_data = pd.DataFrame(
        chain.from_iterable((generate_plotting_data(
                (m.intersect(BedTool(((chrom, 0, size),))) for m in methyl),
                groups, size, scale=scale, shift=shift, bin_size=bin_size)
            for chrom, size, scale, shift
            in zip(chromosomes, sizes, scales, shifts))),
        columns=('Chromosome', 'Methylation level (%)', legend_title,
                 f'{legend_title}_chrom'))

    print('generating plot')
    palette = tuple(islice(cycle(color_palette[:len(groups)]),
                                 len(chromosomes) * len(groups)))
    ax = sns.lineplot(x='Chromosome', y='Methylation level (%)',
                      hue=f'{legend_title}_chrom', data=plotting_data, ci=None,
                      linewidth=3, palette=palette, alpha=alpha,
                      legend='auto' if legend else False)
    ax.set_title(title)
    ax.set_xticks(shifts)
    ax.set_xticklabels(chromosomes, ha='left')
    if legend:
        leg = ax.legend(bbox_to_anchor=(1.02, 1), loc='upper left',
                        borderaxespad=0, title=legend_title)
        for line in leg.get_lines():
            line.set_linewidth(3)
    fig = ax.get_figure()
    fig.set_figheight(2)
    fig.set_figwidth(width)
    fig.tight_layout()
    fig.savefig(output)
    fig.clf()
