# -*- coding: UTF-8 -*-
# python setup.py test -s tests.BasicTests.test_utils
# Copyright 2009-2020 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)

"""
Defines a series of utility classes and functions.

Deprecated. Rather import each utility from its real place.

"""

# import six
# from six.moves import input
# from builtins import str
# from builtins import object
import re

from pathlib import Path
from pprint import pprint
from rstgen.utils import *

# def get_visual_editor():
#     """Returns the name of the visual editor, usually stored in the
#     `VISUAL` environment variable.  If `VISUAL` is not set, return the
#     value of `EDITOR`.

#     https://help.ubuntu.com/community/EnvironmentVariables

#     """
#     return os.environ.get('VISUAL') or os.environ.get('EDITOR')
