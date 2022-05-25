from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import p1
import sys

from p1.colors import *
from p1.utils import cprint

def main():
    print("uso: p1 [login | logout | checkout | commit | info]", file=sys.stderr)
