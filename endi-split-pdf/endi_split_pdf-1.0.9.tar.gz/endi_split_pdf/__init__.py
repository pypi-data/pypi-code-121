"""
Autosplitter for pdf files
"""

__author__ = "Feth Arezki, Julien Miotte, Gaston Tjebbes"
__copyright__ = "Copyright 2020, Majerti"
__credits__ = ["Feth Arezki", "Julien Miotte", "Gaston Tjebbes", "Vinay Sajip"]
__license__ = "GPLv3"
__version__ = "1.0.7"
__maintainer__ = "Tjebbes Gaston"
__email__ = "gaston@majerti.fr"
__status__ = "Development"


import hashlib
import logging
import os.path
import sys

from .config import Config, DEFAULT_CONFIGFILE, Error as ConfigError
from .log_config import log_exception, mk_logger, flag_report
from .splitter import PdfSplitter
from .errors import AutosplitError


def get_md5sum(openfile):
    """
    from http://www.pythoncentral.io/hashing-files-with-python/
    """
    BLOCKSIZE = 65536
    hasher = hashlib.md5()
    buf = openfile.read(BLOCKSIZE)
    while len(buf) > 0:
        hasher.update(buf)
        buf = openfile.read(BLOCKSIZE)
    return hasher.hexdigest()


def version():
    return 'endi_split_pdf version: %s' % __version__


def main():
    """
    Method to call from the command line. Parses sys.argv arguments.
    """
    import argparse

    parser = argparse.ArgumentParser(description='Sage files parsing')
    parser.add_argument(
        'files',
        type=argparse.FileType('r'),
        help='pdf filename named DOCTYPE_YEAR_MONTH.pdf',
        nargs='+'
    )
    parser.add_argument(
        '-c', '--configfile',
        help='configuration file, defaults to %s' % DEFAULT_CONFIGFILE,
        default=None,
        type=argparse.FileType('r')
    )
    parser.add_argument(
        '-v',
        '--verbose',
        action='store_true',
        help='verbose output',
    )
    parser.add_argument(
        '-r',
        '--restrict',
        help="Restrict to n first pages",
        type=int,
        default=0
    )
    parser.add_argument(
        "-d",
        "--debug",
        action="store_true",
        help="Debug mode ?",
    )
    parser.add_argument(
        '-V', '--version',
        action='version',
        version="%%(prog)s (pdf split for endi version %s)" % __version__
    )

    arguments = parser.parse_args()

    error = None
    config = Config.getinstance()
    try:
        config.load_args(arguments)
    except Exception as exception:
        error = exception

    logger = mk_logger("endi_split_pdf.main")
    logger.info(version())
    logger.info("Command line: %s", sys.argv)
    logger.info("Parsed arguments: %s", arguments)
    logger.info("Current config : %s", config.confvalues)
    logger.info("Current working directory: %s", os.getcwd())

    logger.info("Verbosity set to %s", config.getvalue("verbosity"))
    limit = config.getvalue('restrict')

    if limit != 0:
        logger.info("Analysis restricted to pages <= %d", limit)

    if error:
        # We wait until the logger is configured, especially if log_to_mail
        # is True, to get a proper logging of the exception
        logger.error(error)
        log_exception(logger)
        raise AutosplitError(error)

    for inputfile in config.inputfiles:

        logger.info('Loading PDF "%s"', inputfile.filepath)
        logger.info('md5 hash: %s', get_md5sum(open(inputfile.filepath, 'rb')))

        try:
            splitter = PdfSplitter(inputfile, config)
        except ConfigError as exception:
            logger.critical(
                "Error in your configuration: %s", exception.message
            )
            log_exception(logger)
            raise
        except Exception:
            logger.critical("Error initializing splitter")
            log_exception(logger)
            flag_report(False)
            raise

        try:
            splitter.split(inputfile.filedescriptor)
        except AutosplitError as error:
            logger.exception("error")
            logger.error(error.message)
            flag_report(False)
        except BaseException:
            logger.exception(
                "Exception not handled by the splitter, that's a bug, sorry."
                )
            log_exception(logger)
            flag_report(False)
            raise
        else:
            flag_report(True)
        finally:
            logging.shutdown()


__all__ = 'PdfTweaker', 'Config'
