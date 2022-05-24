# -*- coding: utf-8 -*-
# Copyright (c) 2022 Salvador E. Tropea
# Copyright (c) 2022 Instituto Nacional de Tecnología Industrial
# License: GPL-3.0
# Project: KiBot (formerly KiPlot)
import re
import os
import glob
from sys import exit
from subprocess import check_output, STDOUT, CalledProcessError
from .gs import GS
from .error import KiPlotConfigurationError
from .kiplot import config_output, get_output_dir, run_output
from .misc import MISSING_TOOL, WRONG_INSTALL, WRONG_ARGUMENTS, INTERNAL_ERROR, W_NOTPDF
from .optionable import Optionable, BaseOptions
from .registrable import RegOutput
from .create_pdf import create_pdf_from_pages
from .macros import macros, document, output_class  # noqa: F401
from . import log

logger = log.get_logger()


class FilesList(Optionable):
    def __init__(self):
        super().__init__()
        with document:
            self.source = '*.pdf'
            """ File names to add, wildcards allowed. Use ** for recursive match.
                By default this pattern is applied to the output dir specified with `-d` command line option.
                See the `from_cwd` option """
            self.from_cwd = False
            """ Use the current working directory instead of the dir specified by `-d` """
            self.from_output = ''
            """ Collect files from the selected output.
                When used the `source` option is ignored """
            self.filter = r'.*\.pdf'
            """ A regular expression that source files must match """


class PDFUniteOptions(BaseOptions):
    def __init__(self):
        with document:
            self.output = GS.def_global_output
            """ Name for the generated PDF (%i=name of the output %x=pdf) """
            self.outputs = FilesList
            """ [list(dict)] Which files will be included """
            self.use_external_command = False
            """ Use the `pdfunite` tool instead of PyPDF2 Python module """
        super().__init__()
        self._expand_ext = 'pdf'

    def config(self, parent):
        super().config(parent)
        if isinstance(self.outputs, type):
            KiPlotConfigurationError('Nothing to join')
        self._expand_id = parent.name

    def get_files(self, output, no_out_run=False):
        output_real = os.path.realpath(output)
        files = []
        out_dir_cwd = os.getcwd()
        out_dir_default = self.expand_filename_pcb(GS.out_dir)
        for f in self.outputs:
            # Get the list of candidates
            files_list = None
            if f.from_output:
                out = RegOutput.get_output(f.from_output)
                if out is not None:
                    config_output(out)
                    files_list = out.get_targets(get_output_dir(out.dir, out, dry=True))
                else:
                    logger.error('Unknown output `{}` selected in {}'.format(f.from_output, self._parent))
                    exit(WRONG_ARGUMENTS)
                if not no_out_run:
                    for file in files_list:
                        if not os.path.isfile(file):
                            # The target doesn't exist
                            if not out._done:
                                # The output wasn't created in this run, try running it
                                run_output(out)
                            if not os.path.isfile(file):
                                # Still missing, something is wrong
                                logger.error('Unable to generate `{}` from {}'.format(file, out))
                                exit(INTERNAL_ERROR)
            else:
                out_dir = out_dir_cwd if f.from_cwd else out_dir_default
                source = f.expand_filename_both(f.source, make_safe=False)
                files_list = glob.iglob(os.path.join(out_dir, source), recursive=True)
            # Filter and adapt them
            for fname in filter(re.compile(f.filter).match, files_list):
                fname_real = os.path.realpath(fname)
                # Avoid including the output
                if fname_real == output_real:
                    continue
                files.append(fname_real)
        return files

    def get_targets(self, out_dir):
        return [self._parent.expand_filename(out_dir, self.output)]

    def get_dependencies(self):
        output = self.get_targets(self.expand_filename_pcb(GS.out_dir))[0]
        files = self.get_files(output, no_out_run=True)
        return files

    def run_external(self, files, output):
        cmd = ['pdfunite']+files+[output]
        logger.debug('Running: {}'.format(cmd))
        try:
            check_output(cmd, stderr=STDOUT)
        except FileNotFoundError:
            logger.error('Missing `pdfunite` command, install it (poppler-utils)')
            exit(MISSING_TOOL)
        except CalledProcessError as e:
            logger.error('Failed to invoke pdfunite command, error {}'.format(e.returncode))
            if e.output:
                logger.error('Output from command: '+e.output.decode())
            exit(WRONG_INSTALL)

    def run(self, output):
        # Output file name
        logger.debug('Collecting files')
        # Collect the files
        files = self.get_files(output)
        for fn in files:
            with open(fn, 'rb') as f:
                sig = f.read(4)
                if sig != b'%PDF':
                    logger.warning(W_NOTPDF+'Joining a non PDF file `{}`, will most probably fail'.format(fn))
        logger.debug('Generating `{}` PDF'.format(output))
        if os.path.isfile(output):
            os.remove(output)
        if self.use_external_command:
            self.run_external(files, output)
        else:
            create_pdf_from_pages(files, output)


@output_class
class PDFUnite(BaseOutput):  # noqa: F821
    """ PDF joiner
        Generates a new PDF from other outputs.
        This is just a PDF joiner, using `pdfunite` from Poppler Utils. """
    def __init__(self):
        super().__init__()
        with document:
            self.options = PDFUniteOptions
            """ [dict] Options for the `pdfunite` output """
        self._none_related = True

    def get_dependencies(self):
        return self.options.get_dependencies()
