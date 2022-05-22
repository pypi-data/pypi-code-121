#===============================================================================
# phase_methylation.phase
#===============================================================================

"""Functions for phasing step
"""




# Imports ======================================================================

import pysam
import shutil
import subprocess

from itertools import groupby
from operator import itemgetter



# Functions ====================================================================

def longshot(reference: str, input_bam: str, output_vcf: str,
             tagged_bam: str = None):
    """Run longshot for phased SNV calls and haplotype tags

    Parameters
    ----------
    reference : str
        path to FASTA file for the reference genome
    input_bam : str
        path to input BAM file
    output_vcf : str
        path to output VCF file
    tagged_bam : str
        path to output tagged BAM file

    Returns
    -------
    str, str
        tuple of strings giving paths to the output VCF and tagged BAM
    """

    subprocess.run((shutil.which('longshot'), '--bam', input_bam,
                    '--ref', reference, '--out', output_vcf, '-F')
                    + bool(tagged_bam) * ('-O', tagged_bam))
    if tagged_bam:
        pysam.index(tagged_bam)
    return output_vcf, tagged_bam


def extract_phased_read_ids(tagged_bam):
    """Extract ids of haplotype tagged reads

    Parameters
    ----------
    tagged_bam : str
        BAM file containing phased reads

    Returns
    -------
    tuple, tuple, tuple
       tuple of tuples listing the ids of unphased, hap1, and hap2 reads,
       respectively
    """

    alignment = pysam.AlignmentFile(tagged_bam, 'rb')
    tagged_ids = sorted(((read.get_tag('HP') if read.has_tag('HP') else 0,
                          read.query_name)
                         for read in alignment.fetch()),
                        key=itemgetter(0))
    alignment.close()
    return (tuple(n for _, n in g) for _, g in groupby(tagged_ids,
                                                       key=itemgetter(0)))


def add_contigs_to_vcf(reference: str, longshot_vcf: str, fixed_vcf: str):
    """Add contig entries to VCF header
    
    Parameters
    ----------
    reference : str
        reference genome (FASTA) from which to draw contig information
    longshot_vcf : str
        VCF file produced by longshot
    fixed_vcf : str
        path to output file
    
    Returns
    -------
    str
        path to fixed VCF file with contigs in header
    """

    ref = pysam.FastaFile(reference)
    vcf_in = pysam.VariantFile(longshot_vcf)
    for name, length in zip(ref.references, ref.lengths):
        vcf_in.header.add_line(f'##contig=<ID={name},length={length}>')
    vcf_out = pysam.VariantFile(fixed_vcf, 'w', header=vcf_in.header)
    for rec in vcf_in.fetch():
        vcf_out.write(rec)
    return fixed_vcf
