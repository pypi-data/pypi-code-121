#===============================================================================
# phase_methylation.py
#===============================================================================

# Imports ======================================================================

import os.path
from tempfile import gettempdir


from phased_methylation.env import (MEGALODON_DEVICES,
                                    MEGALODON_MOD_BINARY_THRESHOLD,
                                    MEGALODON_GPU_LOAD,
                                    MEGALODON_GPU_MEM,
                                    GUPPY_PARAMS,
                                    GUPPY_CONFIG,
                                    GUPPY_SERVER_PATH)
from phased_methylation.map import index_reference, map_reads
from phased_methylation.phase import (longshot, extract_phased_read_ids,
                                      add_contigs_to_vcf)
from phased_methylation.call import megalodon, megalodon_unphased
from phased_methylation.split_methyl_bed import split_methyl_bed
from phased_methylation.check_gpu_availability import check_gpu_availability




# Constants ====================================================================

MINIMAP2_ONT_BAM_BASENAME = 'minimap2.ont.bam'
FIXED_VCF_BASENAME = 'fixed.vcf'
READ_IDS_HAP1_BASENAME = 'read_ids_hap1.txt'
READ_IDS_HAP2_BASENAME = 'read_ids_hap2.txt'




# Functions ====================================================================

def check_dir_validity(fast5s_dir, output_dir):
    """Check that the provided fast5s dir and output dir are, in fact,
    directories, and raise an error if not

    Parameters
    ----------
    fast5s_dir : str
        path to input fast5s directory
    output_dir : str
        path to output directory
    """

    if not os.path.isdir(fast5s_dir):
        raise RuntimeError('fast5s_dir argument must be a directory')
    if not os.path.isdir(output_dir):
        raise RuntimeError('output_dir argument must be a directory')


def index_and_map(reference, query, output_dir, processes: int = 1,
                  temp_dir=gettempdir()):
    """Generate a minimap2 index for the reference genome and map reads

    Parameters
    ----------
    reference
        path to a FASTA file for the reference genome
    query
        path to directory of FASTQ reads
    output_dir
        path to output directory
    """

    minimap2_ont_bam = os.path.join(output_dir, MINIMAP2_ONT_BAM_BASENAME)
    index_reference(reference, threads=processes, temp_dir=temp_dir)
    map_reads(reference, query, minimap2_ont_bam, threads=processes,
              temp_dir=temp_dir)


def phase_reads(reference, output_dir):
    """Phase reads with Longshot
    
    Parameters
    ----------
    reference
        path to FASTA file for reference genome
    output_dir
        path to output directory
    """

    minimap2_ont_bam = os.path.join(output_dir, MINIMAP2_ONT_BAM_BASENAME)
    longshot_vcf = os.path.join(output_dir, 'longshot.vcf')
    fixed_vcf = os.path.join(output_dir, FIXED_VCF_BASENAME)
    tagged_bam = os.path.join(output_dir, 'longshot.tagged.bam')
    read_ids_unphased = os.path.join(output_dir, 'read_ids_unphased.txt')
    read_ids_hap1 = os.path.join(output_dir, READ_IDS_HAP1_BASENAME)
    read_ids_hap2 = os.path.join(output_dir, READ_IDS_HAP2_BASENAME)
    longshot(reference, minimap2_ont_bam, longshot_vcf,
             tagged_bam=tagged_bam)
    for file, read_ids in zip((read_ids_unphased, read_ids_hap1, read_ids_hap2),
                              extract_phased_read_ids(tagged_bam)):
        with open(file, 'w') as f:
            f.write('\n'.join(read_ids) + '\n')
    add_contigs_to_vcf(reference, longshot_vcf, fixed_vcf)


def call_methylation(reference, fast5s_dir, output_dir, processes: int = 1,
                     devices=MEGALODON_DEVICES,
                     mod_binary_threshold=MEGALODON_MOD_BINARY_THRESHOLD,
                     guppy_params=GUPPY_PARAMS,
                     guppy_config=GUPPY_CONFIG,
                     guppy_server_path=GUPPY_SERVER_PATH,
                     overwrite: bool = False,
                     skip_phasing: bool = False):
    """Run megalodon for methylation calling

    Parameters
    ----------
    reference
        path to FASTA file for reference genome
    fast5s_dir
        path to directory containing FAST5 files
    output_dir
        path to output directory
    processes : int
        number of processes to use
    devices
        iterable of CUDA device IDs to use
    mod_binary_threshold : float
        hard threshold for mod base calling [0.75]
    guppy_params
        parameters passed to guppy basecaller
    guppy_config
        configuraton for guppy basecaller
    guppy_server_path
        path to guppy basecall server executable
    overwrite : bool
        if True, overwrite any existing megalodon files in the output dir [False]
    skip_phasing : bool
        if True, assume phasing step has been skipped and run without phasing
        inputs [False]
    """

    megalodon_output_dir = os.path.join(output_dir, 'megalodon')
    methyl_bed_all = os.path.join(megalodon_output_dir,
                                'modified_bases.5mC.bed')
    if not skip_phasing:
        fixed_vcf = os.path.join(output_dir, FIXED_VCF_BASENAME)
        read_ids_hap1 = os.path.join(output_dir, READ_IDS_HAP1_BASENAME)
        read_ids_hap2 = os.path.join(output_dir, READ_IDS_HAP2_BASENAME)
        methyl_bed_hp1 = os.path.join(megalodon_output_dir,
                                    'modified_bases.hp1.5mC.bed')
        methyl_bed_hp2 = os.path.join(megalodon_output_dir,
                                    'modified_bases.hp2.5mC.bed')
        megalodon(fast5s_dir, fixed_vcf, f'{reference}.mmi',
                  megalodon_output_dir, processes=processes,
                  read_ids_hap1_file=read_ids_hap1,
                  read_ids_hap2_file=read_ids_hap2,
                  devices=devices,
                  mod_binary_threshold=mod_binary_threshold,
                  guppy_params=guppy_params,
                  guppy_config=guppy_config,
                  guppy_server_path=guppy_server_path,
                  overwrite=overwrite)
        for m_bed, prefix in zip((methyl_bed_all, methyl_bed_hp1, methyl_bed_hp2),
                                (os.path.join(output_dir, p) for p in
                                ('all', 'hp1', 'hp2'))):
            print(f'split_methyl_bed: {m_bed}, {reference}, {prefix}')
            split_methyl_bed(m_bed, reference, prefix)
    else:
        megalodon_unphased(fast5s_dir, f'{reference}.mmi', megalodon_output_dir,
                           processes=processes, devices=devices,
                           mod_binary_threshold=mod_binary_threshold,
                           guppy_params=guppy_params,
                           guppy_config=guppy_config,
                           guppy_server_path=guppy_server_path,
                           overwrite=overwrite)
        print(f'split_methyl_bed: {methyl_bed_all}, {reference}')
        split_methyl_bed(methyl_bed_all, reference, os.path.join(output_dir, 'all'))



def launch_phased_methylation(reference, fast5s_dir, output_dir, query,
                              processes=1, devices=MEGALODON_DEVICES,
                              mod_binary_threshold=MEGALODON_MOD_BINARY_THRESHOLD,
                              gpu_load=MEGALODON_GPU_LOAD,
                              gpu_mem=MEGALODON_GPU_MEM,
                              guppy_params=GUPPY_PARAMS,
                              guppy_config=GUPPY_CONFIG,
                              guppy_server_path=GUPPY_SERVER_PATH,
                              overwrite=False, skip_phasing=False,
                              temp_dir=gettempdir()):
    """Launch full methylation calling pipeline

    Parameters
    ----------
    reference
        path to FASTA file for reference genome
    fast5s_dir
        path to directory containing FAST5 files
    output_dir
        path to output directory
    query
        path to directory of input FASTQ files
    processes : int
        number of processes to use
    devices
        iterable of CUDA device IDs to use
    mod_binary_threshold : float
        hard threshold for mod base calling [0.75]
    gpu_load : float
        minimum GPU load avaliability required to launch
    gpu_mem : float
        minimum GPU memory availability required to launch
    guppy_params
        parameters passed to guppy basecaller
    guppy_config
        configuraton for guppy basecaller
    guppy_server_path
        path to guppy basecall server executable
    overwrite : bool
        if True, overwrite any existing megalodon files in the output dir [False]
    skip_phasing : bool
        if True, assume phasing step has been skipped and run without phasing
        inputs [False]
    temp_dir
        directory for temporary files
    """

    check_dir_validity(fast5s_dir, output_dir)
    check_gpu_availability(devices, gpu_load=gpu_load, gpu_mem=gpu_mem)
    print(f'running on ref {reference}')
    print(f'running on fast5s {fast5s_dir}')
    print(f'placing files here {output_dir}')
    print(f'running on query {query}')
    index_and_map(reference, query, output_dir, processes=processes,
                  temp_dir=temp_dir)
    if not skip_phasing:
        phase_reads(reference, output_dir)
    check_gpu_availability(devices, gpu_load=gpu_load, gpu_mem=gpu_mem)
    call_methylation(reference, fast5s_dir, output_dir, processes=processes,
                     devices=devices,
                     mod_binary_threshold=mod_binary_threshold,
                     guppy_params=guppy_params,
                     guppy_config=guppy_config,
                     guppy_server_path=guppy_server_path,
                     overwrite=overwrite,
                     skip_phasing=skip_phasing)
