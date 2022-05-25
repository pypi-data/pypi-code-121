"""
Concrete implementations of splitters that split pdf files
"""

import os
import re
import time
import unicodedata

from collections import OrderedDict
from tempfile import mkstemp

from .log_config import flag_report
import shutil

from PyPDF4 import PdfFileReader, PdfFileWriter

from .utils import (
    get_command_outputs,
    mkdir_p,
)
from .errors import (
    Incoherence,
    ParseError,
)
from .data_finder import FINDERS
from .log_config import mk_logger, log_doc, log_errordoc, closing_message


_UNIX_VALID = re.compile(rb'[^\w\s-]')
_NOSPACES = re.compile(rb'[-\s]+')


def unix_sanitize(some_name):
    value = unicodedata.normalize('NFKD', some_name).encode('ascii', 'ignore')
    value = _UNIX_VALID.sub(b'', value).strip()
    return _NOSPACES.sub(b'-', value).decode('utf-8')


class PdfSplitter(object):
    _UNITARY_TIME = 0.1

    def __init__(self, inputfile, config):
        self.logger = mk_logger('endi_split_pdf.splitter')

        self.inputfile = inputfile
        self.config = config

        self.doctype = self.inputfile.doctype
        self.current_config = self.config.getvalue(self.doctype)

        self.output_dir = os.path.join(
            self.doctype, self.inputfile.year, self.inputfile.month
        )
        self.pages_to_process = self.restrict = self.config.getvalue(
            'restrict'
        )
        self.pb_dir = self.config.getvalue('pb_dir')

        self.preprocessor = self.config.getvalue('preprocessor')

    def _collect_page_indexes(self, filepath):
        """
        Collect the chunks to split

        :param str filepath: The path to the pdf file
        :returns: {
            (an_code, name) : [page1, page2]
        }
        """
        result = {}
        with open(filepath, 'rb') as pdf_stream:
            inputpdf = PdfFileReader(pdf_stream)
            if inputpdf.isEncrypted:
                inputpdf.decrypt('')

            pages_nb = inputpdf.getNumPages()

            if not self.pages_to_process:
                # 0 means no restriction
                self.pages_to_process = pages_nb

            self.logger.info("%s has %d pages", filepath, pages_nb)
            self.logger.info(
                "Estimated time for completion of %d pages on "
                "an average computer: %.f seconds. Please stand by while "
                "the parsing takes place.",
                self.pages_to_process,
                self._UNITARY_TIME*self.pages_to_process
            )

            for page_nb in range(pages_nb):
                match_dict = self._collect_page_data(filepath, page_nb)

                match_values = tuple(match_dict.values())

                if None in match_values:
                    self.logger.critical(
                        "Unable to extract data from "
                        "page {}".format(page_nb)
                    )
                    break

                result.setdefault(match_values, []).append(page_nb)

                if self.restrict and page_nb + 1 >= self.restrict:
                    self.logger.info(
                        "Stopping the parsing as requested by limit "
                        "of {} pages".format(self.restrict)
                    )
                    break

        return result

    def _write_pdf(self, original_filepath, match_dict, page_numbers):
        """
        Write a pdf for the given discrimination values merging the pages in
        page_numbers

        :param str original_filepath: The original pdf file
        :param dict match_dict: The data that were matched in the pages
        :param list page_numbers: The pages to merge
        """
        output = PdfFileWriter()

        with open(original_filepath, 'rb') as pdf_stream:
            inputpdf = PdfFileReader(pdf_stream, strict=False)
            if inputpdf.isEncrypted:
                inputpdf.decrypt('')
            for page_number in page_numbers:
                output.addPage(inputpdf.getPage(page_number))

            outfname = self._get_outfname(match_dict)

            with open(outfname, 'wb') as fbuf:
                log_doc(self.logger, len(page_numbers), outfname)
                output.write(fbuf)

        if not self._check_splitpage(outfname, match_dict):
            newdest = os.path.join(self.pb_dir, os.path.basename(outfname))
            log_errordoc(self.logger, len(page_numbers), newdest)
            self.logger.critical(
                "Check failed for %s. Moved to %s",
                outfname,
                newdest
            )
            if not os.path.isdir(self.pb_dir):
                os.mkdir(self.pb_dir)
            shutil.move(outfname, newdest)

    def _write_pdfs(self, original_filepath, pages_dict):
        """
        Write the splitted pdfs

        :param dict pages_dict: As returned by _collect_page_indexes
        """
        self.logger.info("Writing to {0}".format(self.output_dir))
        for match_values, page_numbers in pages_dict.items():
            # On reconstruit le dict "nom de la données / valeurs"
            match_dict = dict(zip(
                self.current_config['datatypes'].keys(),
                match_values
            ))
            self._write_pdf(
                original_filepath, match_dict, page_numbers
            )

    def _get_outfname(self, match_dict):
        """
        Produce the output filename

        :param dict match_dict: the data that were matched
                e.g {'ancode': '5OOO'}
        """
        template = self.current_config.get(
            'filename_template',
            "{ancode}_{name}.pdf"
        )
        outfname = template.format(**match_dict)
        return "%s/%s.pdf" % (self.output_dir, unix_sanitize(outfname))

    def split(self, pdfstream):
        """
        Entry point for file splitting

        1- Collect page indexes
        2- write files

        :param obj pdfstream: A file descriptor object pointing on the pdf file
        to treat
        """
        start = time.time()

        filepath = pdfstream.name
        page_indexes = self._collect_page_indexes(filepath)

        if not page_indexes:
            raise Exception("No data to treat in this pdf")

        mkdir_p(self.output_dir, self.logger)
        self._write_pdfs(filepath, page_indexes)

        duration = time.time() - start
        closing_message(self.logger, duration)

    def _collect_page_data(self, filepath, page_nb):
        """
        :param str filepath: The path to the original pdf file
        :param int page_nb: The page number to treat

        :rtype: OrderedDict
        """
        try:
            data = self._get_page_data(filepath, page_nb)
        except Incoherence as e:
            self.logger.critical(
                "Incoherence error : %s" % e.message
            )
            return {}
        except UnicodeDecodeError:
            self.logger.critical(
                "Cannot extract text. Please check the pdf"
                "file. For instance 'file -i %s' should not return"
                "'charset=binary'",
                filepath
            )
            self.logger.critical("output of 'file -i %s':", filepath)
            command = ['/usr/bin/file', '-i', filepath]
            try:
                self.logger.info("Running command %s", " ".join(command))
                stdout, stderr, returncode = get_command_outputs(command)
            except OSError:
                self.logger.critical(
                    "Error while trying to run '%s'",
                    ' '.join(command))
                raise
            self.logger.critical(stdout.strip())
            return {}

        return data

    def _find_datatype(self, data_name, data_config, pdf_str):
        """
        find the datatype in the pdf2str result

        :param str data_name: The name of the data we're looking for
        :param dict data_config: The configuration to use for this type of data
        :param str pdf_str: The current pdf page in txt format

        :rtype: str
        """
        for finder_config in data_config:
            type_ = finder_config.get('type', 'coordinates')
            finder_class = FINDERS[type_]
            finder = finder_class(**finder_config)
            result = finder.find(pdf_str)
            if result:
                self.logger.info(
                    "Found {} with {} data finder".format(
                        data_name, type_
                    )
                )
                break
            else:
                self.logger.debug("Not found with {} data finder".format(
                    data_name,
                ))
        return result

    def _get_page_data(self, filepath, pagenb):
        """
        Return the datas found in the page pagenb of the given file

        :param str filepath: The full path to the file
        :param int pagenb: The page number (starting with 0)
        """
        pdf_str = self._get_pdf_str(filepath, pagenb)

        datatypes = self.current_config['datatypes']

        result = OrderedDict()
        for key, configuration in datatypes.items():
            value = self._find_datatype(key, configuration, pdf_str)
            if not value:
                flag_report(False)
                raise Incoherence(
                    "{} field wasn't correctly extracted."
                    "Compare the lines and columns in the <HOME>/config.yaml"
                    " file the output from the last command "
                    "(see previous log)".format(key)
                )
            else:
                result[key] = value

        self.logger.info(
            "Page {}: {}".format(
                pagenb, ",".join(result.values())
            )
        )
        return result

    def _get_pdf_str(self, filepath, pagenb):
        """
        Return the pagenb of filepath as a simple unicode string
        :param str filepath: The path to the pdf
        :param int pagenb: The number of the page
        """
        # Warning: 1 - indexed page number for pdftotext, while the current
        # software and PyPDF2 API use 0 - index.
        pdftotext_pagenb = pagenb + 1

        command = [
            self.preprocessor,
            filepath, '%d' % pdftotext_pagenb,
        ]
        try:
            self.logger.info("Running command %s", " ".join(command))
            stdout, stderr, returncode = get_command_outputs(command)
        except OSError:
            self.logger.critical(
                "Error while trying to run '%s'",
                ' '.join(command))
            raise
        strcommand = " ".join(command)
        if returncode != 0:
            raise ParseError(
                "Return code of command '%s': %d", (strcommand, returncode)
            )

        if b"Error (" in stdout:
            fdesc, temppath = mkstemp(prefix="txt_split_error-")
            with open(temppath, 'w') as tempfd:
                tempfd.write(stdout)
            raise ParseError(
                "pdf splitting failed - txt file dumped as %s - "
                "command was '%s' " % (temppath, strcommand)
            )
        return stdout.decode('utf-8')

    def _check_splitpage(self, file_to_check, match_dict):
        """
        Check that the split data are present in the given file

        convert the generated file to text and check the informations are
        present
        """
        # - is for stdout
        command = ["pdftotext", "-q", "-layout", file_to_check, '-']
        try:
            self.logger.info("Running command %s", " ".join(command))
            stdout, stderr, returncode = get_command_outputs(command)
        except OSError:
            self.logger.critical(
                "Error while trying to run '%s'",
                ' '.join(command))
            raise

        if returncode != 0:
            self.logger.critical(
                'While checking correct parsing, pdftotext '
                'exit status is %d', returncode
            )
            return False

        stdout = stdout.decode('utf-8')

        for key, value in match_dict.items():
            if value not in stdout:
                self.logger.critical(
                    'While checking correct parsing, name %s not found '
                    'in %s', key, file_to_check
                )
                return False

        return True
