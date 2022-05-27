#######################################################################
#
# Copyright (C) 2021 David Palao
#
# This file is part of PacBio data processing.
#
#  PacBioDataProcessing is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  PacBio data processing is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with PacBioDataProcessing. If not, see <http://www.gnu.org/licenses/>.
#
#######################################################################

import unittest

from pacbio_data_processing.errors import high_level_handler
from pacbio_data_processing.constants import EXIT_CODE_FAILURE


class HighLevelHandlerTestCase(unittest.TestCase):
    def test_catches_all(self):
        msg = "oh, oh! I died"

        @high_level_handler
        def fail():
            raise Exception(msg)

        with self.assertLogs() as cm:
            ret = fail()
        self.assertEqual(cm.output, ["CRITICAL:root:oh, oh! I died"])
        self.assertEqual(ret, EXIT_CODE_FAILURE)

    def test_does_nearly_nothing_if_no_error(self):
        @high_level_handler
        def fine(a):
            return 2*a
        result = fine(5)
        self.assertEqual(result, 10)
        self.assertEqual(fine.__name__, "fine")
