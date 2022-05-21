# Copyright (C) 2020-Present the hyssop authors and contributors.
#
# This module is part of hyssop and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

'''
File created: August 21st 2020

Modified By: hsky77
Last Updated: November 21st 2020 21:18:14 pm
'''

import time
from unittest import TestCase
from typing import List

from ..util import DynamicTypeEnum

from ..project.constants import Component_Module_Folder, Controller_Module_Folder


class UnitTestTypes(DynamicTypeEnum):
    """base abstract unitest enum class"""

    @staticmethod
    def get_unittest_enum_class() -> List[DynamicTypeEnum]:
        from ..project.constants import Unittest_Module_Folder
        try:
            return DynamicTypeEnum.get_dynamic_class_enum_class(Unittest_Module_Folder)
        except:
            pass

    def import_class(self):
        return super().import_class(cls_type=UnitTestCase)


class UnitTestCase(TestCase):
    """hyssop unittest case abstract class"""

    def test(self):
        raise NotImplementedError()
