import os
from os import path
import sys
from va.version import __version__

sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
# sys.path.append(path.dirname(path.abspath(__file__)))
BASE_DIR = os.path.dirname(os.path.realpath(__file__))

name = 'va'