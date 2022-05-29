import sys

import codefast.reader
import codefast.utils as utils
from codefast.ds import fplist, nstr, pair_sample, fpjson
from codefast.io import FastJson
from codefast.io import FileIO as io
from codefast.io import FormatPrint as fp
from codefast.logger import Logger
from codefast.math import math
from codefast.network import Network as net
from codefast.network import Network as http
from codefast.network import urljoin, url_shortener
from codefast.utils import (b64decode, b64encode, cipher, decipher, retry,
                            shell, syscall, uuid)
from codefast.functools.random import random_string
from codefast.constants import constants

# Export methods and variables
csv = utils.CSVIO
os = utils._os()

logger = Logger()
info = logger.info
error = logger.error
warning = logger.warning

say = io.say
jsn = FastJson()
js = FastJson()

# Deprecated
sys.modules[__name__] = utils.wrap_mod(
    sys.modules[__name__], deprecated=['text', 'file', 'read', 'say'])
