#===============================================================================
# phase_methylation.call
#===============================================================================

"""Functions for methylation calling step
"""




# Imports ======================================================================

import shutil
import subprocess
from itertools import chain
from phased_methylation.env import (MEGALODON_DEVICES,
                                    MEGALODON_MOD_BINARY_THRESHOLD,
                                    GUPPY_PARAMS,
                                    GUPPY_CONFIG,
                                    GUPPY_SERVER_PATH)




# Functions ====================================================================

def megalodon(fast5_dir: str, vcf_file: str, reference_mmi: str,
              output_directory: str, read_ids_hap1_file: str,
              read_ids_hap2_file: str, processes: int = 1,
              devices: str = MEGALODON_DEVICES,
              mod_binary_threshold: float = MEGALODON_MOD_BINARY_THRESHOLD,
              guppy_params: str = GUPPY_PARAMS,
              guppy_config: str = GUPPY_CONFIG,
              guppy_server_path: str = GUPPY_SERVER_PATH,
              overwrite: bool = False):
    """Run Megalodon

    Parameters
    ----------
    fast5_dir : str
        path to directory containing FAST5 files
    vcf_file : str
        path to VCF containing variants
    reference_mmi : str
        path to .mmi index of a reference genome
    output_directory : str
        path to output directory
    read_ids_hap1_file : str
        path to file listing hap1 read ids
    read_ids_hap2_file : str
        path to file listing hap2 read ids
    processes : int
        number of processes to use [1]
    devices : str
        GPU devices parameter passed to megalodon
    mod_binary_threshold : float
        hard threshold for modified base aggregation
    guppy_params : str
        string of parameters passed to guppy basecaller
    guppy_config : str
        path to config file for guppy basecaller
    guppy_server_path : str
        path to guppy server executable
    overwrite : bool
        if True, overwrite any existing megalodon files in the output directory
    """

    subprocess.run((shutil.which('megalodon'), fast5_dir,
        '--outputs', 'mods', 'basecalls', 'mod_basecalls', 'variants',
            'variant_mappings',
        '--variant-filename', vcf_file,
        '--reference', reference_mmi,
        '--sort-mappings',
        '--devices', *(str(d) for d in devices),
        '--processes', str(processes),
        '--mod-binary-threshold', str(mod_binary_threshold),
        '--guppy-params', guppy_params,
        '--guppy-config', guppy_config,
        '--output-directory', output_directory,
        '--guppy-server-path', guppy_server_path)
        + overwrite * ('--overwrite',))

    subprocess.run((shutil.which('megalodon_extras'), 'aggregate', 'run',
        '--outputs', 'mods',
        '--megalodon-directory', output_directory,
        '--read-ids-filename', read_ids_hap1_file,
        '--output-suffix', 'hp1'))

    subprocess.run((shutil.which('megalodon_extras'), 'aggregate', 'run',
        '--outputs', 'mods',
        '--megalodon-directory', output_directory,
        '--read-ids-filename', read_ids_hap2_file,
        '--output-suffix', 'hp2'))


def megalodon_unphased(fast5_dir: str, reference_mmi: str,
              output_directory: str, processes: int = 1,
              devices: str = MEGALODON_DEVICES,
              mod_binary_threshold: float = MEGALODON_MOD_BINARY_THRESHOLD,
              guppy_params: str = GUPPY_PARAMS,
              guppy_config: str = GUPPY_CONFIG,
              guppy_server_path: str = GUPPY_SERVER_PATH,
              overwrite: bool = False):
    """Run Megalodon without phasing

    Parameters
    ----------
    fast5_dir : str
        path to directory containing FAST5 files
    reference_mmi : str
        path to .mmi index of a reference genome
    output_directory : str
        path to output directory
    processes : int
        number of processes to use [1]
    devices : str
        GPU devices parameter passed to megalodon
    mod_binary_threshold : float
        hard threshold for modified base aggregation
    guppy_params : str
        string of parameters passed to guppy basecaller
    guppy_config : str
        path to config file for guppy basecaller
    guppy_server_path : str
        path to guppy server executable
    overwrite : bool
        if True, overwrite any existing megalodon files in the output directory
    """

    subprocess.run((shutil.which('megalodon'), fast5_dir,
        '--outputs', 'mods', 'basecalls', 'mod_basecalls',
        '--reference', reference_mmi,
        '--sort-mappings',
        '--devices', *(str(d) for d in devices),
        '--mod-binary-threshold', str(mod_binary_threshold),
        '--processes', str(processes),
        '--guppy-params', guppy_params,
        '--guppy-config', guppy_config,
        '--output-directory', output_directory,
        '--guppy-server-path', guppy_server_path)
        + overwrite * ('--overwrite',))
