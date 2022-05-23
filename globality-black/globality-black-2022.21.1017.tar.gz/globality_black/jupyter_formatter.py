"""Helper class to use with `jupyterlab_code_formatter` Jupyter extension. See README for details"""

import logging
import re

import black
from jupyterlab_code_formatter.formatters import BaseFormatter, handle_line_ending_and_magic

from globality_black.reformat_text import reformat_text


class GlobalityBlackFormatter(BaseFormatter):

    label = "Apply Globality Black Formatter"

    def __init__(self, line_length=100):
        self.line_length = line_length

    @property
    def importable(self) -> bool:
        # returns always True as we are already inside of globality-black, so this can never fail :)
        logging.info(f"importing {self.label}")
        return True

    @handle_line_ending_and_magic
    def format_code(self, code: str, notebook: bool, **options) -> str:
        logging.info(f"Applying {self.label}")
        logging.info(f"Options: {options}")
        logging.info(f"Line length: {self.line_length}")
        black_mode = black.Mode(line_length=self.line_length)

        # Note: we cannot use \s for space here, since \s matches any whitespace character, inc. \n
        code = re.sub(r" +\n", "\n", code)

        # In the future, we might be able to get black mode from options. Not possible at the moment
        # see https://github.com/ryantam626/jupyterlab_code_formatter/issues/87
        # black_mode = black.Mode(**options)

        return reformat_text(code, black_mode)
