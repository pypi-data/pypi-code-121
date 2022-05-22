#===============================================================================
# phase_methylation.py
#===============================================================================

# Imports ======================================================================

from argparse import ArgumentParser
from tempfile import gettempdir


from phased_methylation.env import (MEGALODON_DEVICES,
                                    MEGALODON_MOD_BINARY_THRESHOLD,
                                    MEGALODON_GPU_LOAD,
                                    MEGALODON_GPU_MEM,
                                    GUPPY_PARAMS,
                                    GUPPY_CONFIG,
                                    GUPPY_SERVER_PATH,
                                    ECOLI_REFERENCE,
                                    ECOLI_READS,
                                    ECOLI_FAST5)
from phased_methylation.launch import (check_dir_validity,
                                      launch_phased_methylation, index_and_map,
                                      phase_reads, call_methylation)
from phased_methylation.mean import calculate_mean, calculate_total_mean
from phased_methylation.promoter_methylation import promoter_methylation
from phased_methylation.gene_body_methylation import gene_body_methylation
from phased_methylation.tabulate import tabulate
from phased_methylation.plot import plot, COLOR_PALETTE
from phased_methylation.plot_genes import plot_genes
from phased_methylation.plot_repeats import plot_repeats
from phased_methylation.merge import merge_bedmethyl
from phased_methylation.intersect import intersect_bedmethyl
from phased_methylation.export_metilene import export_metilene
from phased_methylation.export_bedgraph import export_bedgraph




# Functions ====================================================================

def _launch_phased_methylation(args):
    if args.processes > 1:
        args.processes -= 1
    launch_phased_methylation(args.reference, args.fast5s_dir, args.output_dir,
                              args.query, processes=args.processes,
                              devices=args.devices,
                              mod_binary_threshold = args.mod_binary_threshold,
                              gpu_load=args.gpu_load, gpu_mem=args.gpu_mem,
                              guppy_params=args.guppy_params,
                              guppy_config=args.guppy_config,
                              guppy_server_path=args.guppy_server_path,
                              overwrite=args.overwrite, temp_dir=args.tmp_dir,
                              skip_phasing=args.skip_phasing)


def _map_reads(args):
    if args.processes > 1:
        args.processes -= 1
    index_and_map(args.reference, args.query, args.output_dir,
                  processes=args.processes, temp_dir=args.tmp_dir)


def _phase_reads(args):
    phase_reads(args.reference, args.output_dir)


def _call_methylation(args):
    if args.processes > 1:
        args.processes -= 1
    check_dir_validity(args.fast5s_dir, args.output_dir)
    call_methylation(args.reference, args.fast5s_dir, args.output_dir,
                     args.processes, devices=args.devices,
                     mod_binary_threshold=args.mod_binary_threshold,
                     guppy_params=args.guppy_params,
                     guppy_config=args.guppy_config,
                     guppy_server_path=args.guppy_server_path,
                     overwrite=args.overwrite,
                     skip_phasing=args.skip_phasing)


def _test_run(args):
    if args.processes > 1:
        args.processes -= 1
    launch_phased_methylation(ECOLI_REFERENCE, ECOLI_FAST5, args.output_dir,
                              ECOLI_READS, processes=args.processes,
                              devices=args.devices,
                              mod_binary_threshold=args.mod_binary_threshold,
                              gpu_load=args.gpu_load, gpu_mem=args.gpu_mem,
                              guppy_params=args.guppy_params,
                              guppy_config=args.guppy_config,
                              guppy_server_path=args.guppy_server_path,
                              overwrite=args.overwrite)


def _calculate_mean(args):
    if args.total:
        calculate_total_mean(args.bedmethyl, plot=args.plot,
                             groups=args.groups, title=args.title,
                             legend_title=args.legend_title, width=args.width,
                             color_palette=args.color_palette)
    else:
        calculate_mean(args.bedmethyl, plot=args.plot,
                       chromosomes=args.chromosomes, groups=args.groups,
                       title=args.title, legend_title=args.legend_title,
                       width=args.width, color_palette=args.color_palette)


def _promoter_methylation(args):
    promoter_methylation(args.features, args.bedmethyl,
        upstream_flank=args.upstream_flank,
        downstream_flank=args.downstream_flank, chromosomes=args.chromosomes,
        cytosines=args.cytosines, coverage=args.coverage,
        min_coverage=args.min_coverage, bins=args.bins, levels=args.levels,
        kde=args.kde, palette=args.palette)


def _gene_body_methylation(args):
    gene_body_methylation(args.features, args.bedmethyl,
        upstream_flank=args.upstream_flank,
        downstream_flank=args.downstream_flank, chromosomes=args.chromosomes,
        cytosines=args.cytosines, coverage=args.coverage,
        min_coverage=args.min_coverage, bins=args.bins, levels=args.levels,
        kde=args.kde, palette=args.palette)


def _tabulate(args):
    tabulate(args.bed, names=args.names, dropna=args.dropna,
        fft=args.fft, exclusive=args.exclusive, min=args.min, max=args.max)


def _plot(args):
    plot(args.bedmethyl, args.output, reference=args.reference,
         chromosomes=args.chromosomes, groups=args.groups, title=args.title,
         legend=args.legend, legend_title=args.legend_title,
         bin_size=args.bin_size, width=args.width,
         color_palette=args.color_palette, alpha=args.alpha)


def _plot_genes(args):
    plot_genes(args.features, args.bedmethyl, args.output, groups=args.groups,
               flank=args.flank, smooth=args.smooth, title=args.title,
               confidence_interval=args.confidence_interval,
               gene_bins=args.gene_bins, gene_levels=args.gene_levels,
               legend=args.legend, legend_title=args.legend_title,
               palette=args.palette, width=args.width, alpha=args.alpha)

def _plot_repeats(args):
    plot_repeats(args.features, args.bedmethyl, args.output, type=args.type,
                 groups=args.groups, flank=args.flank, smooth=args.smooth,
                 title=args.title, confidence_interval=args.confidence_interval,
                 legend=args.legend, legend_title=args.legend_title,
                 palette=args.palette, width=args.width, alpha=args.alpha)


def _merge(args):
    merge_bedmethyl(args.bedmethyl, chromosomes=args.chromosomes)

def _intersect(args):
    intersect_bedmethyl(args.bedmethyl, chromosomes=args.chromosomes)


def _export_metilene(args):
    export_metilene(args.bedmethyl, args.output, groups=args.groups,
                    chromosomes=args.chromosomes)


def _export_bedgraph(args):
    export_bedgraph(args.bedmethyl, chromosomes=args.chromosomes,
                    coverage=args.coverage)


def construct_subparser(parser, func, reference: bool = False,
                        fast5s_dir: bool = False,
                        query: bool = False, processes: bool = False,
                        temp_dir: bool = False,
                        megalodon: bool = False, skip_phasing: bool = False):
    parser.set_defaults(func=func)
    if reference:
        parser.add_argument('reference', metavar='<reference.fa>',
                            help='reference genome')
    if fast5s_dir:
        parser.add_argument('fast5s_dir', metavar='<fast5s_dir/>',
                            help='directory containing fast5 files')
    parser.add_argument('output_dir', metavar='<output_dir/>',
                        help='output directory')
    if query:
        parser.add_argument('query', metavar='<query.fastq>',
                          help='fastq reads to be aligned and phased')
    if processes:
        resource_group = parser.add_argument_group('resource arguments')
        resource_group.add_argument('--processes', metavar='<int>', type=int,
                                    default=1, help='number of processes [1]')
    if megalodon:
        devices_str = ' '.join(str(d) for d in (MEGALODON_DEVICES))
        resource_group.add_argument('--devices', metavar='<int>', type=int,
            default=MEGALODON_DEVICES,
            nargs='+',
            help=f'devices parameter passed to megalodon [{devices_str}]')
        resource_group.add_argument('--gpu-load', metavar='<float>', type=float,
            default=MEGALODON_GPU_LOAD,
            help=f'minimum GPU load availability required [{MEGALODON_GPU_LOAD}]')
        resource_group.add_argument('--gpu-mem', metavar='<float>', type=float,
            default=MEGALODON_GPU_MEM,
            help=f'minimum GPU memory availability required [{MEGALODON_GPU_MEM}]')
    if temp_dir:
        resource_group.add_argument('--tmp-dir', metavar='<tmp_dir/>',
            default=gettempdir(),
            help=f'directory for temporary files [{gettempdir()}]')
    if megalodon:
        guppy_group = parser.add_argument_group('guppy arguments')
        guppy_group.add_argument('--guppy-params', metavar='<"-x param">',
            default=GUPPY_PARAMS,
            help=f'dict of parameters passed to guppy [{GUPPY_PARAMS}]')
        guppy_group.add_argument('--guppy-config', metavar='<config_file.cfg>',
            default=GUPPY_CONFIG,
            help=f'config file passed to guppy [{GUPPY_CONFIG}]')
        guppy_group.add_argument('--guppy-server-path',
            metavar='<guppy_basecall_server>', default=GUPPY_SERVER_PATH,
            help=f'path to guppy server executable [{GUPPY_SERVER_PATH}]')
        megalodon_group = parser.add_argument_group('megalodon arguments')
        megalodon_group.add_argument('--mod-binary-threshold', metavar='<float>',
            type=float, default=MEGALODON_MOD_BINARY_THRESHOLD,
            help=f'Hard threshold for modified base aggregation [{MEGALODON_MOD_BINARY_THRESHOLD}]')
        megalodon_group.add_argument('--overwrite', action='store_true',
            help='overwrite any existing megalodon files in the output directory')
    if skip_phasing:
        config_group = parser.add_argument_group('configuration arguments')
        config_group.add_argument('--skip-phasing', action='store_true',
            help='skip the phasing step')


def parse_arguments():
    parser = ArgumentParser(description='pipeline for methylation calling')
    subparsers = parser.add_subparsers()
    parser_launch = subparsers.add_parser('launch', help='launch full pipeline')
    construct_subparser(parser_launch, _launch_phased_methylation,
                        reference=True, fast5s_dir=True, query=True,
                        processes=True, temp_dir=True, megalodon=True,
                        skip_phasing=True)
    parser_map = subparsers.add_parser('map', help='perform mapping step')
    construct_subparser(parser_map, _map_reads, reference=True, query=True,
                        processes=True, temp_dir=True)
    parser_phase = subparsers.add_parser('phase', help='perform phasing step')
    construct_subparser(parser_phase, _phase_reads, reference=True)
    parser_call = subparsers.add_parser('call', help='perform methylation calling step')
    construct_subparser(parser_call, _call_methylation, reference=True,
                        fast5s_dir=True, processes=True, temp_dir=True,
                        megalodon=True, skip_phasing=True)
    parser_test = subparsers.add_parser('test', help='execute test run')
    construct_subparser(parser_test, _test_run, processes=True, temp_dir=True,
                        megalodon=True)
    
    # mean parser
    parser_mean = subparsers.add_parser('mean',
        help='calculate average methylation across chromosomes or in total')
    parser_mean.set_defaults(func=_calculate_mean)
    parser_mean.add_argument('bedmethyl', metavar='<bedmethyl.bed>',
        nargs='+', help='bedMethyl file containing methylation data')
    parser_mean.add_argument('--plot', metavar='<output.{pdf,png,svg}>',
        help='path to output plot')
    domain_group = parser_mean.add_mutually_exclusive_group()
    domain_group.add_argument('--chromosomes', metavar='<X>', nargs='+',
        help='chromosomes to include')
    domain_group.add_argument('--total', action='store_true',
        help='calculate total genomic mean')
    parser_mean.add_argument('--groups', metavar='<"Group">', nargs='+',
        help='list of groups for provided bedmethyl files [0]')
    parser_mean.add_argument('--title', metavar='<"Plot title">',
        default='Methylation', help='set the title for the plot')
    parser_mean.add_argument('--legend-title', metavar='<Title>',
        default='Group', help='title of legend')
    parser_mean.add_argument('--width', metavar='<float>', type=float,
        default=8, help='set width of figure in inches')
    parser_mean.add_argument('--color-palette', metavar='<#color>', nargs='+',
        default=COLOR_PALETTE, help='color palette to use')

    # promoter methylation parser
    parser_promoter = subparsers.add_parser('promoter',
        help='quantify promoter methylation')
    parser_promoter.set_defaults(func=_promoter_methylation)
    parser_promoter.add_argument('features', metavar='<features.gff3>',
        help='gff3 file of genomic features')
    parser_promoter.add_argument('bedmethyl', metavar='<bedmethyl.bed>',
        help='bedMethyl file containing methylation data')
    parser_promoter.add_argument('--upstream-flank', metavar='<int>', type=int,
        default=2000, help='length of upstream flank in bp [2000]')
    parser_promoter.add_argument('--downstream-flank', metavar='<int>',
        type=int, default=0, help='length of upstream flank in bp [0]')
    parser_promoter.add_argument('--chromosomes', metavar='<X>', nargs='+',
        help='chromosomes to include')
    parser_promoter.add_argument('--cytosines', action='store_true',
        help='output a column with number of cytosines in each promoter')
    parser_promoter.add_argument('--coverage', action='store_true',
        help='output a column of coverage for each promoter')
    parser_promoter.add_argument('--min-coverage', metavar='<int>',
        type=int, default=1, help='minimum coverage to include promoter [1]')
    parser_promoter.add_argument('--bins', action='store_true',
        help='output a column binning promoters by discrete methylation level')
    parser_promoter.add_argument('--levels', metavar='<Level>',
        nargs='+', default=['Min', 'Low', 'Mid', 'High', 'Max'],
        help='discrete methylation levels')
    parser_promoter.add_argument('--kde', metavar='<file.{pdf,png,svg}>',
        help='generate KDE plot of methylation levels')
    parser_promoter.add_argument('--palette', metavar='<palette>',
        default='mako_r', help='name of seaborn color palette [mako_r]')
    
    # gene body methylation parser
    parser_gene_body = subparsers.add_parser('gene-body',
        help='quantify gene body methylation')
    parser_gene_body.set_defaults(func=_gene_body_methylation)
    parser_gene_body.add_argument('features', metavar='<features.gff3>',
        help='gff3 file of genomic features')
    parser_gene_body.add_argument('bedmethyl', metavar='<bedmethyl.bed>',
        help='bedMethyl file containing methylation data')
    parser_gene_body.add_argument('--upstream-flank', metavar='<int>', type=int,
        default=0, help='length of upstream flank in bp [0]')
    parser_gene_body.add_argument('--downstream-flank', metavar='<int>',
        type=int, default=0, help='length of upstream flank in bp [0]')
    parser_gene_body.add_argument('--chromosomes', metavar='<X>', nargs='+',
        help='chromosomes to include')
    parser_gene_body.add_argument('--cytosines', action='store_true',
        help='output a column with number of cytosines in each promoter')
    parser_gene_body.add_argument('--coverage', action='store_true',
        help='output a column of coverage for each gene')
    parser_gene_body.add_argument('--min-coverage', metavar='<int>',
        type=int, default=1, help='minimum coverage to include gene [1]')
    parser_gene_body.add_argument('--bins', action='store_true',
        help='output  a column binning promoters by discrete methylation level')
    parser_gene_body.add_argument('--levels', metavar='<Level>',
        nargs='+', default=['Min', 'Low', 'Mid', 'High', 'Max'],
        help='discrete methylation levels')
    parser_gene_body.add_argument('--kde', metavar='<file.{pdf,png,svg}>',
        help='generate KDE plot of methylation levels')
    parser_gene_body.add_argument('--palette', metavar='<palette>',
        default='mako_r', help='name of seaborn color palette [mako_r]')

    # tabulate parser
    parser_tabulate = subparsers.add_parser('tabulate',
        help='merge BED6 files generated by `gene-body` or `promoter` into a table')
    parser_tabulate.set_defaults(func=_tabulate)
    parser_tabulate.add_argument('bed', metavar='<file.bed>', nargs='+',
        help='BED6 files')
    parser_tabulate.add_argument('--names', metavar='<name>', nargs='+',
        help='sample names for input files')
    parser_tabulate.add_argument('--dropna', action='store_true',
        help='include only genes with no missing data')
    parser_tabulate.add_argument('--fft', metavar='<int>', type=int, nargs='+',
        help='calculate fft scores for indicated frequencies')
    parser_tabulate.add_argument('--exclusive', action='store_true',
        help='restrict to exclusive methylation inverval (no 0 or 100)')
    parser_tabulate.add_argument('--min', metavar='<int>', type=float,
        default=0.0,
        help='filter results by a minimum methylation level [0]')
    parser_tabulate.add_argument('--max', metavar='<int>', type=float,
        default=100.0,
        help='filter results by a maximum methylation level [100]')

    # plot parser
    parser_plot = subparsers.add_parser('plot',
        help='plot methylation across chromosomes')
    parser_plot.set_defaults(func=_plot)
    parser_plot.add_argument('bedmethyl', metavar='<bedmethyl.bed>',
        nargs='+', help='bedMethyl file containing methylation data')
    parser_plot.add_argument('output', metavar='<output.{pdf,png,svg}>',
        help='path to output file')
    parser_plot.add_argument('--reference', metavar='<reference.fa>',
        help='reference genome')
    parser_plot.add_argument('--chromosomes', metavar='<X>', nargs='+',
        help='chromosomes to plot')
    parser_plot.add_argument('--groups', metavar='<"Group">', nargs='+',
        help='list of groups for provided bedmethyl files [0]')
    parser_plot.add_argument('--title', metavar='<"Plot title">',
        default='Methylation', help='set the title for the plot')
    parser_plot.add_argument('--legend', action='store_true',
        help='include a legend with the plot')
    parser_plot.add_argument('--legend-title', metavar='<"Title">',
        default='Group', help='title of legend')
    parser_plot.add_argument('--bin-size', metavar='<int>', type=int, default=0,
        choices=(-2,-1,0,1,2),
        help=('Set bin size. The input <int> is converted to the bin size by '
              'the formula: 10^(<int>+6) bp. The default value is 0, i.e. '
              '1-megabase bins. [0]'))
    parser_plot.add_argument('--width', metavar='<float>', type=float,
        default=8, help='set width of figure in inches [8.0]')
    parser_plot.add_argument('--color-palette', metavar='<#color>', nargs='+',
        default=COLOR_PALETTE, help='color palette to use')
    parser_plot.add_argument('--alpha', metavar='<float>', type=float,
        default=0.5, help='transparency value for lines [0.5]')
    
    
    # plot_genes parser
    parser_plot_genes = subparsers.add_parser('plot-genes',
        help='plot methylation profiles over genomic features')
    parser_plot_genes.set_defaults(func=_plot_genes)
    parser_plot_genes.add_argument('features', metavar='<features.gff3>',
        help='gff3 file of genomic features')
    parser_plot_genes.add_argument('bedmethyl', metavar='<bedmethyl.bed>',
        nargs='+', help='bedMethyl file containing methylation data')
    parser_plot_genes.add_argument('output', metavar='<output.{pdf,png,svg}>',
        help='path to output file')
    parser_plot_genes.add_argument('--groups', metavar='<"Group">', nargs='+',
        help='list of groups for provided bedmethyl files [0]')
    parser_plot_genes.add_argument('--flank', metavar='<int>', type=int,
        default=1000, help='size of flanking regions in bp [1000]')
    parser_plot_genes.add_argument('--smooth', action='store_true',
        help='draw a smoother plot')
    parser_plot_genes.add_argument('--confidence-interval', metavar='<int>',
        type=int, help='draw a confidence interval')
    parser_plot_genes.add_argument('--title', metavar='<"Plot title">',
        default='Methylation',
        help='set the title for the plot')
    parser_plot_genes.add_argument('--gene-bins', metavar='<gene_bins.json>',
        help='gene bins')
    parser_plot_genes.add_argument('--gene-levels', metavar='<Level>',
        nargs='+', default=['Min', 'Low', 'Mid', 'High', 'Max'],
        help='gene expression levels')
    parser_plot_genes.add_argument('--legend', action='store_true',
        help='include a legend with the plot')
    parser_plot_genes.add_argument('--legend-title', metavar='<Title>',
        default='Group', help='title of legend')
    parser_plot_genes.add_argument('--width', metavar='<float>', type=float,
        default=4, help='set width of figure in inches')
    parser_plot_genes.add_argument('--palette', metavar='<palette>',
        default='deep', help='name of seaborn color palette [deep]')
    parser_plot_genes.add_argument('--alpha', metavar='<float>', type=float,
        default=1, help='transparency value for lines [1.0]')
    
    # plot_repeats parser
    parser_plot_repeats = subparsers.add_parser('plot-repeats',
        help='plot methylation profiles over genomic features')
    parser_plot_repeats.set_defaults(func=_plot_repeats)
    parser_plot_repeats.add_argument('features', metavar='<features.gff3>',
        help='gff3 file of genomic features')
    parser_plot_repeats.add_argument('bedmethyl', metavar='<bedmethyl.bed>',
        nargs='+', help='bedMethyl file containing methylation data')
    parser_plot_repeats.add_argument('output', metavar='<output.{pdf,png,svg}>',
        help='path to output file')
    parser_plot_repeats.add_argument('--type', metavar='<"feature_type">',
        help='generate plot for a specific type of repeat')
    parser_plot_repeats.add_argument('--groups', metavar='<"Group">', nargs='+',
        help='list of groups for provided bedmethyl files [0]')
    parser_plot_repeats.add_argument('--flank', metavar='<int>', type=int,
        default=500, help='size of flanking regions in bp [500]')
    parser_plot_repeats.add_argument('--smooth', action='store_true',
        help='draw a smoother plot')
    parser_plot_repeats.add_argument('--confidence-interval', metavar='<int>',
        type=int, help='draw a confidence interval')
    parser_plot_repeats.add_argument('--title', metavar='<"Plot title">',
        default='Methylation',
        help='set the title for the plot')
    parser_plot_repeats.add_argument('--legend', action='store_true',
        help='include a legend with the plot')
    parser_plot_repeats.add_argument('--legend-title', metavar='<Title>',
        default='Group', help='title of legend')
    parser_plot_repeats.add_argument('--width', metavar='<float>', type=float,
        default=4, help='set width of figure in inches')
    parser_plot_repeats.add_argument('--palette', metavar='<palette>',
        default='deep', help='name of seaborn color palette [deep]')
    parser_plot_repeats.add_argument('--alpha', metavar='<float>', type=float,
        default=1, help='transparency value for lines [1.0]')
    
    # merge parser
    parser_merge = subparsers.add_parser('merge',
        help='merge two or more bedmethyl files')
    parser_merge.set_defaults(func=_merge)
    parser_merge.add_argument('bedmethyl', metavar='<bedmethyl.bed>',
        nargs='+', help='bedMethyl file containing methylation data')
    parser_merge.add_argument('--chromosomes', metavar='<X>',
        nargs='+', help='chromosomes to include')
    
    # intersect parser
    parser_intersect = subparsers.add_parser('intersect',
        help='intersect two or more bedmethyl files')
    parser_intersect.set_defaults(func=_intersect)
    parser_intersect.add_argument('bedmethyl', metavar='<bedmethyl.bed>',
        nargs='+', help='bedMethyl file containing methylation data')
    parser_intersect.add_argument('output_prefix', metavar='<output-prefix>',
        help='prefix for output files')
    parser_intersect.add_argument('--chromosomes', metavar='<X>',
        nargs='+', help='chromosomes to include')

    # export_metilene parser
    parser_export_metilene = subparsers.add_parser('export-metilene',
        help='export methylation data formatted for input into metilene')
    parser_export_metilene.set_defaults(func=_export_metilene)
    parser_export_metilene.add_argument('bedmethyl', metavar='<bedmethyl.bed>',
        nargs='+', help='bedMethyl file containing methylation data')
    parser_export_metilene.add_argument('output', metavar='<output.tsv>',
        help='path to output file')
    parser_export_metilene.add_argument('--groups', metavar='<"Group">',
        nargs='+', help='list of groups for provided bedmethyl files [0]')
    parser_export_metilene.add_argument('--chromosomes', metavar='<X>',
        nargs='+', help='chromosomes to include')
    

    # export_bedgraph parser
    parser_export_bedgraph = subparsers.add_parser('export-bedgraph',
        help='export methylation data in bedgraph format')
    parser_export_bedgraph.set_defaults(func=_export_bedgraph)
    parser_export_bedgraph.add_argument('bedmethyl', metavar='<bedmethyl.bed>',
        help='bedMethyl file containing methylation data')
    parser_export_bedgraph.add_argument('--chromosomes', metavar='<X>',
        nargs='+', help='chromosomes to include')
    parser_export_bedgraph.add_argument('--coverage', action='store_true',
        help='write coverage track instead of methylation track')

    return parser.parse_args()


def main():
    args = parse_arguments()
    args.func(args)
