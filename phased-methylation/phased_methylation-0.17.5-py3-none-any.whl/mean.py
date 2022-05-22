#===============================================================================
#  mean.py
#===============================================================================

"""Calculate average methylation level across a genome"""




# Imports ======================================================================

from pybedtools import BedTool

import pandas as pd
import seaborn as sns




# Constants ====================================================================

COLOR_PALETTE = sns.color_palette().as_hex()




# Functions ====================================================================

def generate_data(bedtools, groups, chromosomes=None):
    """"Generator giving data from bedmethyl files

    Parameters
    ----------
    bedtools
        iterable of BedTools
    groups
        iterable giving group id for each input bedtool
    chromosomes
        iterable of chromosomes to include, or None to include all chromosomes

    Yields
    ------
    tuple
        ((chrom, methylation_level), group)
    """
    if chromosomes is not None:
        chromosomes = set(chromosomes)
    yield from ((chrom, float(meth), group)
        for chrom, _, _, _, _, _, _, _, _, _, meth, group
        in (i.fields + [g] for bt, g in zip(bedtools, groups) for i in bt)
        if (chromosomes is None) or (chrom in chromosomes))


def calculate_mean(bedmethyl, plot=None, chromosomes=None, groups=None,
              title='Methylation', legend_title='Group', width=8,
              color_palette=COLOR_PALETTE):
    """Calculate mean methylation level for each chromosome

    Parameters
    ----------
    bedmethyl
        iterable of paths to bedmethyl formatted files containing methylation results
    plot
        if given, path to output plot
    chromosomes
        iterable of chromosomes to include, or None to include all chromosomes
    groups
        iterable of group ids for bedmethyl files
    title : str
        plot title
    legend_title : str
        plot legend title
    width : float
        plot width
    """


    if not groups:
        groups = list(range(len(bedmethyl)))
    methyl = tuple(BedTool(bed) for bed in bedmethyl)
    plotting_data = pd.DataFrame(
        generate_data(methyl, groups, chromosomes),
        columns=('Chromosome', 'Methylation level (%)', legend_title))
    chromosome_means = plotting_data.groupby(by=['Chromosome', legend_title]).mean()
    print('Chromosome', legend_title, 'Methylation level (%)', sep='\t')
    for (chrom, group), row in chromosome_means.iterrows():
        print(chrom, group, row[0], sep='\t')

    if plot:
        ax = sns.barplot(x='Chromosome', y='Methylation level (%)',
                         hue=legend_title, data=plotting_data, ci=None,
                         palette=color_palette)
        ax.set_title(title)
        ax.legend(bbox_to_anchor=(1.02, 1), loc='upper left', borderaxespad=0,
                  title=legend_title)
        fig = ax.get_figure()
        fig.set_figheight(2)
        fig.set_figwidth(width)
        fig.tight_layout()
        fig.savefig(plot)
        fig.clf()


def calculate_total_mean(bedmethyl, plot=None, groups=None,
              title='Methylation', legend_title='Group', width=3,
              color_palette=COLOR_PALETTE):
    """Calculate total genomic mean methylation level

    Parameters
    ----------
    bedmethyl
        iterable of paths to bedmethyl formatted files containing methylation results
    plot
        if given, path to output plot
    groups
        iterable of group ids for bedmethyl files
    title : str
        plot title
    legend_title : str
        plot legend title
    width : float
        plot width
    """


    if not groups:
        groups = list(range(len(bedmethyl)))
    methyl = tuple(BedTool(bed) for bed in bedmethyl)
    plotting_data = pd.DataFrame(
        generate_data(methyl, groups, chromosomes=None),
        columns=('Chromosome', 'Methylation level (%)', legend_title))
    total_means = plotting_data.groupby(by=legend_title).mean()
    print(legend_title, 'Methylation level (%)', sep='\t')
    for group, row in total_means.iterrows():
        print(group, row[0], sep='\t')

    if plot:
        ax = sns.barplot(x=legend_title, y='Methylation level (%)',
                         hue=legend_title, data=plotting_data, ci=None,
                         palette=color_palette, dodge=False)
        ax.set_title(title)
        ax.legend(bbox_to_anchor=(1.02, 1), loc='upper left', borderaxespad=0,
                  title=legend_title)
        fig = ax.get_figure()
        fig.set_figheight(2)
        fig.set_figwidth(width)
        fig.tight_layout()
        fig.savefig(plot)
        fig.clf()
