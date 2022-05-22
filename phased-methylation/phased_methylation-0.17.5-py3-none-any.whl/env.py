#===============================================================================
# env.py
#===============================================================================

"""Handling environment variables for phase_methylation"""




# Imports ======================================================================

import os
import os.path



# Constants ====================================================================

MEGALODON_DEVICES = tuple(int(d) for d in
                          tuple(os.environ.get('MEGALODON_DEVICES', (0,))))

MEGALODON_MOD_BINARY_THRESHOLD = float(os.environ.get(
                                       'MEGALODON_MOD_BINARY_THRESHOLD', 0.75))

MEGALODON_GPU_LOAD = float(os.environ.get('MEGALODON_GPU_LOAD', 0.83))

MEGALODON_GPU_MEM = float(os.environ.get('MEGALODON_GPU_MEM', 0.83))

GUPPY_PARAMS = os.environ.get('GUPPY_PARAMS', '-d /data/rerio/basecall_models')

GUPPY_CONFIG = os.environ.get('GUPPY_CONFIG',
                              'res_dna_r941_prom_modbases_5mC_v001.cfg')

GUPPY_SERVER_PATH = os.environ.get('GUPPY_SERVER_PATH',
                                   '/usr/bin/guppy_basecall_server')

MINIMAP2_EXAMPLE_HUMAN = os.path.join(os.path.dirname(__file__), 
                                      'minimap2_example_data',
                                      'MT-human.fa')

MINIMAP2_EXAMPLE_ORANG = os.path.join(os.path.dirname(__file__), 
                                      'minimap2_example_data',
                                      'MT-orang.fa')

MINIMAP2_EXAMPLE_ALIGNMENT = os.path.join(os.path.dirname(__file__), 
                                          'minimap2_example_data',
                                          'test.bam')

LONGSHOT_EXAMPLE_REFERENCE = os.path.join(os.path.dirname(__file__), 
                                          'longshot_example_data',
                                          'genome.fa')

LONGSHOT_EXAMPLE_READS = os.path.join(os.path.dirname(__file__), 
                                      'longshot_example_data',
                                      'pacbio_reads_30x.bam')

LONGSHOT_EXAMPLE_VARIANTS = os.path.join(os.path.dirname(__file__), 
                                         'longshot_example_data',
                                         'ground_truth_variants.vcf.gz')

LONGSHOT_EXACT_VARIANTS = os.path.join(os.path.dirname(__file__), 
                                       'longshot_example_data',
                                       'out.vcf.gz')

LONGSHOT_UNPHASED_IDS = os.path.join(os.path.dirname(__file__), 
                                     'longshot_example_data',
                                     'read_ids_unphased.txt')

LONGSHOT_PHASED_IDS_1 = os.path.join(os.path.dirname(__file__), 
                                     'longshot_example_data',
                                     'read_ids_hap1.txt')

LONGSHOT_PHASED_IDS_2 = os.path.join(os.path.dirname(__file__), 
                                     'longshot_example_data',
                                     'read_ids_hap2.txt')

ECOLI_REFERENCE = os.path.join(os.path.dirname(__file__),
                               'ecoli_example_data',
                               'draft.fa')

ECOLI_READS = os.path.join(os.path.dirname(__file__),
                           'ecoli_example_data',
                           'reads.fasta')

ECOLI_FAST5 = os.path.join(os.path.dirname(__file__),
                           'ecoli_example_data',
                           'fast5_files')
