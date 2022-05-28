import shutil
import os
from socket import timeout
import time
import argparse

from pywinauto.application import Application
from pywinauto.keyboard import send_keys

from pdfform import builders
from pdfform import loaders
from pdfform import config

import os, sys

# Get project's home directory,
BASEDIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
# All data directory
DATADIR = os.path.abspath(os.path.join(BASEDIR, "data"))


def check_env():
    if not os.path.isfile(config.ACROBAT_READER_PATH):
        print("Acrobat reader not found. Please install it first.")
        exit()
    if not os.path.isdir(config.OUTPUT_PATH):
        print("Output directory doesn't exist. Please check.")
        exit()


def prepare_document(form_type: str, name: str):
    """Create a new empty pdf file to fill"""

    # copy empty template file to output folder
    # dirname = os.path.dirname(os.path.abspath(__file__))
    src = DATADIR + f"/forms/{form_type}_empty.pdf"
    dst = config.OUTPUT_PATH + name + ".pdf"
    shutil.copy2(src, dst)

    # open file with acrobat reader
    app = Application(backend="uia").start(config.ACROBAT_READER_PATH + " " + dst)
    # TODO: find better way to detect ready
    time.sleep(10)  # wait 5 seconds for file open finished.
    # dlg_spec = app.window(title="Desktoptest.pdf(SECURED)-AdobeAcrobatReaderDC(64-bit)")
    # dlg_spec.wait("ready", timeout=30)
    # app.Properties.print_control_identifiers()


def finish_document():
    """Validate, save and close document"""

    send_keys("^S")  # Ctrl + S to save
    send_keys("^W")  # Ctrl + W to close


def get_args():
    """Get command-line arguments"""

    parser = argparse.ArgumentParser(
        description="PDF Filler -- automatically fill application forms.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    parser.add_argument(
        "form_name",
        help="PDF form type: currently supported form [1295, 5708, 5709, 5710]",
        default="demo",
    )

    parser.add_argument(
        "-f",
        "--file",
        help="Data file used to fill form. If no file specified, the tool will use example data to fill for demo purpose.",
        metavar="data_file_name",
        type=argparse.FileType("r"),
        default=None,
    )

    parser.add_argument(
        "-o",
        "--output",
        help="Output file name. If not specified, file name will be test.pdf.",
        metavar="output_file_name",
        default="test",
    )

    parser.add_argument(
        "-v", "--verbose", help="verbose output filling steps", action="store_true"
    )

    return parser.parse_args()


def main():
    """main function"""

    args = get_args()
    form_name = args.form_name
    in_file = args.file
    verbose = args.verbose
    out_file = "test"

    check_env()

    if form_name not in ["1295", "5708", "5709", "5710"]:
        print(f'Error: form "{form_name}" is not supported.')
        quit()

    applicant = loaders.load_form_data(in_file, form_name)
    prepare_document(form_name, out_file)
    form = builders.build_form(form_name, applicant)
    form.fill_form(0, verbose)
    finish_document()


if __name__ == "__main__":
    main()
