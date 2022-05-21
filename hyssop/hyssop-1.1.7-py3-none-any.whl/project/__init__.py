# Copyright (C) 2020-Present the hyssop authors and contributors.
#
# This module is part of hyssop and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

'''
File created: November 21st 2020

Modified By: hsky77
Last Updated: November 22nd 2020 12:21:26 pm
'''

from ..util import join_path, BaseLocal
from ..util.constants import Localization_File

BaseLocal.import_csv([join_path(__path__[0], Localization_File)])
