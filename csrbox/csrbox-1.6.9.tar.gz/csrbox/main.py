import click
import sys
import os
import shutil

import logging
import csrbox.utils as utils
import csrbox.csr_gen as csr_gen
from   csrbox import __version__ as version
from   csrbox.errors import ValidationError
import riscv_config.checker as riscv_config


@click.command()
@click.version_option(prog_name="RISC-V CSRBox Generator",version=version)
@click.option('--verbose', '-v', default='info', help='Set verbose level', type=click.Choice(['info','error','debug'],case_sensitive=False))

@click.option ('--isaspec','-ispec', type=click.Path(exists=True, resolve_path=True, readable=True), help = "RISCV-CONFIG ISA File" )
@click.option ('--grpspec','-gspec', type=click.Path(resolve_path=True, readable=True, exists=True), help = "Grouping YAML File" )
@click.option ('--customspec','-cspec', type=click.Path(exists=True, resolve_path=True, readable=True), help = "CUSTOM CSR File" )
@click.option ('--debugspec','-dspec', type=click.Path(exists=True, resolve_path=True, readable=True), help = "Debug CSR File" )
@click.option ('--customattr','-cattr', type=click.Path(exists=True, resolve_path=True, readable=True), help = "CUSTOM CSR Attributes File" )
@click.option ('--workdir', default='./csrbox_work', type=click.Path(resolve_path=True, writable=True), help='Work directory path')
@click.option ('--probeinst','-pinst',default='soc', type=str, help='Instance name of the module to be used for probe')
@click.option ('--checked','-chk',default=False, is_flag=True, help='Assumes the *spec arguments are already checked and avoids calling riscv_config for validation')
def cli(verbose, isaspec, grpspec, customspec, debugspec, customattr, workdir, probeinst, checked):
    utils.setup_logging(verbose)
    logger = logging.getLogger()
    logger.handlers = []
    ch = logging.StreamHandler()
    ch.setFormatter(utils.ColoredFormatter())
    logger.addHandler(ch)

    logger.info('****** RISC-V CSRBox Generator {0} *******'.format(version))
    logger.info('Copyright (c) 2020, IIT-Madras, InCore Semiconductors Pvt. Ltd.')
    if not os.path.exists(workdir):
        logger.debug('Creating new work directory: ' + workdir)
        os.mkdir(workdir)
    else:
        logger.debug('Removing old work directory and creating new one: ' + workdir)
        shutil.rmtree(workdir)
        os.mkdir(workdir)
    if not checked:

        try:
            isa_file = riscv_config.check_isa_specs(isaspec, workdir, True)
        except ValidationError as msg:
            logger.error(msg)
            return 1

        if debugspec:
            try:
                debug_file = riscv_config.check_debug_specs(debugspec, isa_file, workdir, True)
            except ValidationError as msg:
                logger.error(msg)
                return 1
        else:
            debug_file = None


        if customspec:
            try:
                custom_file = riscv_config.check_custom_specs(customspec, workdir, True)
            except ValidationError as msg:
                logger.error(msg)
                return 1
        else:
            custom_file = None
    else:
        isa_file = isaspec
        custom_file = customspec
        debug_file = debugspec
    bsv_dir  = os.path.join(workdir, "bsv/")
    if not os.path.exists(bsv_dir):   
        logger.debug('Creating new bsv directory: ' + bsv_dir) 
        os.mkdir(bsv_dir)

    csr_gen.csr_gen(isa_file, grpspec, custom_file, debug_file, customattr, bsv_dir,
            probeinst, logging=True)


 
