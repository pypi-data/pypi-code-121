################################################################################
# IBM Confidential
# OCO Source Materials
# 5737-H76, 5725-W78, 5900-A1R
# (c) Copyright IBM Corp. 2021, 2022. All Rights Reserved.
# The source code for this program is not published or otherwise divested of its trade secrets,
# irrespective of what has been deposited with the U.S. Copyright Office.
################################################################################

import unittest
import logging

logger = logging.getLogger()

from autoai_ts_libs.transforms.imputers import (
    AutoAITSImputer,
    IMPUTER_DISPLAY_NAMES
)

class ImputerNameTest(unittest.TestCase):
    def setUp(self):
        self.imputers = AutoAITSImputer.get_default_imputer_list()
        print(self.imputers)
        print(IMPUTER_DISPLAY_NAMES)

    def test_get_imputer_display_name(self):
        # All imputers should have a display name
        for i in self.imputers:
            with self.subTest(imputer=i):
                AutoAITSImputer.get_display_name(i)

    def test_get_imputer_name(self):
        # All imputers should return a name
        # That name should end with "_imputer"
        for i in self.imputers:
            with self.subTest(imputer=i):
                n = AutoAITSImputer.get_imputer_name(i)
                self.assertTrue(n.endswith("_imputer"))

    def tearDown(self):
        pass

if __name__ == '__main__':
    unittest.main()
