import os
import errno
from subprocess import (
    Popen,
    PIPE,
)


def make_process(argv_seq):
    return Popen(argv_seq, stdout=PIPE, stderr=PIPE)


def get_command_outputs(argv_seq):
    """
    :return: stdout and stderr as unicode decodable strings, return code as
    int
    """
    process = make_process(argv_seq)
    stdout, stderr = process.communicate()
    returncode = process.returncode
    return stdout, stderr, returncode


def get_page_text(pdf_file_path, page_number):
    """
    get the text content of the page

    :param str pdf_file_path: Path to the pdf file
    :param int page_number: The page to extract
    :rtype: str
    """
    script = "endi-split-pdf-page2text"
    args = [script, pdf_file_path, str(page_number)]
    return get_command_outputs(args)[0]


def mkdir_p(path, logger):
    """
    http://stackoverflow.com/questions/600268/mkdir-p-functionality-in-python
    """
    try:
        os.makedirs(path)
    except OSError as exc:
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            fullpath = os.path.join(os.getcwd(), path)
            logger.critical(
                "Error while creating directory {} -see trace".format(fullpath)
            )
            raise
