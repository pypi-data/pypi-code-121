#===============================================================================
# plot_genes.py
#===============================================================================

from itertools import chain
from pybedtools import BedTool

import pandas as pd
import seaborn as sns
import json

from statistics import median
from phased_methylation.parse_gff import (parse_gff, generate_flank, 
                                          generate_feature_body)
from phased_methylation.plot_bedtools import generate_plotting_data



def plot_genes(features, bedmethyl, output, groups=None, flank: int = 1000,
               smooth: bool = False, title: str = 'Methylation', gene_bins=None,
               gene_levels=['Min', 'Low', 'Mid', 'High', 'Max'],
               confidence_interval=None,
               legend=False, legend_title='Group', width: float = 4.0,
               palette='deep', alpha=1):
    """Plot methylation profile of genes across the genome

    Parameters
    ----------
    features
        path to GFF3 file containing gene coordinates
    bedmethyl
        iterable of paths to bedmethyl files
    output
        path to output file (pdf, png, or svg)
    groups
        iterable of group names for input files
    flank : int
        size of flanking regions to plot, in bp
    smooth : bool
        if True, draw a smoother plot
    title : str
        title for plot
    gene_bins
        path to json or tsv file providing genes binned by expression
    gene_levels
        iterable of names for discrete gene expression levels
    confidence_interval
        int from 1-99 giving % size of confidence interval, or None for
        no confidence interval
    legend : bool
        if True, draw a legend
    legend title : str
        title for plot legend
    width : float
        width of plot in inches
    palette : str
        color palette for lines
    alpha : float
        transparency of lines
    """

    if not groups:
        groups = list(range(len(bedmethyl)))
    print('importing data')
    genes = pd.DataFrame(parse_gff(features, flank=flank),
        columns=('seqid', 'start', 'end', 'strand', 'attributes'))
    genes.index = (attr['ID'] for attr in genes['attributes'])
    gene_size=median(genes['end'] - genes['start'])
    xticks = (0, 3*flank/(gene_size+2*flank),
              3*(gene_size+flank)/(gene_size+2*flank), 3)
    upstream = BedTool(tuple(generate_flank(genes, side='up', flank=flank)))
    downstream = BedTool(tuple(generate_flank(genes, side='down', flank=flank)))
    gene_body = BedTool(tuple(generate_feature_body(genes)))
    methyl = tuple(BedTool(bed) for bed in bedmethyl)

    print('intersecting')
    methyl_upstream = (m.intersect(upstream, wo=True) for m in methyl)
    methyl_gene_body = (m.intersect(gene_body, wo=True) for m in methyl)
    methyl_downstream = (m.intersect(downstream, wo=True) for m in methyl)

    print('generating plotting data')
    plotting_data = pd.DataFrame(chain(
        generate_plotting_data(methyl_upstream, groups, scale=xticks[1],
            smooth=smooth),
        generate_plotting_data(methyl_gene_body, groups,
            scale=xticks[2] - xticks[1], shift=xticks[1], smooth=smooth),
        generate_plotting_data(methyl_downstream, groups,
            scale=xticks[3] - xticks[2], shift=xticks[2], smooth=smooth)),
        columns=('Relative position', 'Methylation level (%)', legend_title,
                 'ID'))
    
    if gene_bins:
        print('applying bins')
        if gene_bins.endswith('.json'):
            with open(gene_bins, 'r') as f:
                bins = json.load(f)
        else:
            bins = pd.read_table(gene_bins, header=None, index_col=0,
                                 squeeze=True)
        plotting_data[legend_title] = tuple(bins.get(f'{gene_id}')
            for gene_id in plotting_data['ID'])
        plotting_data.dropna()

    print('generating plot')
    if gene_bins:
        palette = sns.color_palette(palette,
            len(plotting_data[legend_title].unique()))[-1*len(gene_levels):]
    else:
        palette = sns.color_palette(palette, n_colors=len(groups))
    ax = sns.lineplot(x='Relative position', y='Methylation level (%)',
                      hue=legend_title, data=plotting_data,
                      ci=confidence_interval, linewidth=3,
                      hue_order=(gene_levels if gene_bins else None),
                      palette=palette, legend='auto' if legend else False,
                      alpha=alpha)
    ax.set_title(title)
    ax.set_xticks(xticks)
    ax.set_xticklabels((f'-{int(flank/1e3)}kb', 'TSS', 'TTS',
                        f'+{int(flank/1e3)}kb'),
                       rotation=30, ha='right')
    ax.axvline(x=xticks[1], color='lightgray', linestyle='dashed')
    ax.axvline(x=xticks[2], color='lightgray', linestyle='dashed')
    if legend:
        leg = ax.legend(bbox_to_anchor=(1.02, 1), loc='upper left',
                        borderaxespad=0, title=legend_title)
        for line in leg.get_lines():
            line.set_linewidth(3)
    fig = ax.get_figure()
    fig.set_figheight(3)
    fig.set_figwidth(width)
    fig.tight_layout()
    fig.savefig(output)
    fig.clf()
    
