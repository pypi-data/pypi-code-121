#===============================================================================
# phase_methylation.map
#===============================================================================

"""Functions for read mapping step
"""




# Imports ======================================================================

from argparse import ArgumentParser

import pysam
import shutil
import subprocess

from tempfifo import NamedTemporaryFIFO
from tempfile import gettempdir



# Functions ====================================================================

def minimap2(reference: str, query: str = None, output_bam: str = None,
             preset: str = None, index: bool = False, threads: int = 1,
             temp_dir=gettempdir()):
    """Run minimap2

    Parameters
    ----------
    reference : str
        path to the reference genome (FASTA)
    query : str
        path to the query sequence (FASTQ)
    output_bam : str
        path to the output BAM file
    preset : str
        a preset (-x) value for minimap2
    index : bool
        if True, index the reference [False]
    threads : int
        number of threads to use [1]

    Returns
    -------
    str or None
        either the path to the output BAM or None
    """

    if output_bam:
        if not query:
            raise RuntimeError('no query specified')
        with NamedTemporaryFIFO(dir=temp_dir) as pipe:
            with subprocess.Popen((shutil.which('sh'), '-c',
                                  f'minimap2 -t {threads} -a '
                                  + bool(preset) * f'-x {preset} '
                                  + index * f'-d {reference}.mmi '
                                  + f'{reference} {query} > {pipe.name}')):
                pysam.sort('-@', str(threads), '-o', output_bam, pipe.name)
        pysam.index(output_bam)
        return output_bam
    else:
        if query:
            raise RuntimeError('no output specified')
        subprocess.run((shutil.which('minimap2'), '-t', str(threads))
                       + bool(preset) * ('-x', preset)
                       + index * ('-d', f'{reference}.mmi')
                       + (reference,))
    

def index_reference(reference: str, threads: int = 1, temp_dir=gettempdir()):
    """Index a reference genome with minimap2 and samtools

    Parameters
    ----------
    reference : str
        path to the reference genome (FASTA)
    threads : int
        number of threads to use [1]

    Returns
    -------
    str, str
        file paths for the minimap2 index and the faidx index
    """

    minimap2(reference, preset='map-ont', index=True, threads=threads,
             temp_dir=temp_dir)
    pysam.faidx(reference)
    return f'{reference}.mmi', f'{reference}.fai'


def map_reads(reference: str, query: str, output_bam: str, threads: int = 1,
              temp_dir=gettempdir()):
    """Map ONT reads with minimap2

    Parameters
    ----------
    reference
        path to the reference genome (FASTA)
    query : str
        path to the query sequence (FASTQ)
    output_bam : str
        path to the output BAM file
    preset : str
        a preset (-x) value for minimap2
    
    Returns
    -------
    str
        path to the output BAM
    """

    return minimap2(reference, query=query, output_bam=output_bam,
                    preset='map-ont', threads=threads, temp_dir=temp_dir)


def parse_arguments():
    parser = ArgumentParser(
        description='Read mapping step for phase-methylation')
    parser.add_argument('reference', metavar='<reference.fa>',
                          help='reference genome')
    parser.add_argument('output_dir', metavar='<output_dir/>',
                          help='output directory')
    parser.add_argument('query', metavar='<query.fastq>',
                          help='fastq reads to be aligned and tagged')
    resource_group = parser.add_argument_group('resource arguments')
    resource_group.add_argument('--processes', metavar='<int>', type=int,
                                default=1, help='number of processes [1]')
    resource_group.add_argument('--tmp-dir', metavar='<tmp_dir/>',
        default=gettempdir(),
        help=f'directory for temporary files [{gettempdir()}]')
    return parser.parse_args()


def main():
    args = parse_arguments()
    if args.processes > 1:
        args.processes -= 1
    print(f'running on ref {args.reference}')
    print(f'placing files here {args.output_dir}')
    print(f'running on query {args.query}')
    minimap2_ont_bam = os.path.join(args.output_dir, 'minimap2.ont.bam')
    index_reference(args.reference, threads=args.processes,
                    temp_dir=args.temp_dir)
    map_reads(args.reference, args.query, minimap2_ont_bam,
              threads=args.processes, temp_dir=args.temp_dir)

