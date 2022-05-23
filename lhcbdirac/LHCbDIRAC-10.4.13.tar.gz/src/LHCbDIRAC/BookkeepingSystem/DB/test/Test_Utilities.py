###############################################################################
# (c) Copyright 2019 CERN for the benefit of the LHCb Collaboration           #
#                                                                             #
# This software is distributed under the terms of the GNU General Public      #
# Licence version 3 (GPL Version 3), copied verbatim in the file "LICENSE".   #
#                                                                             #
# In applying this licence, CERN does not waive the privileges and immunities #
# granted to it by virtue of its status as an Intergovernmental Organization  #
# or submit itself to any jurisdiction.                                       #
###############################################################################
"""It is used to test the Bookkeeping utilities."""
import unittest

from LHCbDIRAC.BookkeepingSystem.DB.Utilities import enoughParams, _ONE, _TWO


class UtilitiesTestCase(unittest.TestCase):
    def test_enoughParams(self):

        result = enoughParams({})
        self.assertEqual(result, False)

        result = enoughParams({"ReplicaFlag": "Test", "Visible": "Test"})
        self.assertEqual(result, False)

        for i in _ONE:
            result = enoughParams({i: "Test"})
            self.assertEqual(result, False)

        for i in _TWO:
            for j in _TWO:
                result = enoughParams({i: "Test", j: "Test"})
                self.assertEqual(result, False)

        result = enoughParams({"ConfigName": "Test", "ConfigVersion": "Test", "Production": "Test"})
        self.assertEqual(result, True)

        result = enoughParams({"Production": "Test", "ReplicaFlag": "Test", "Visible": "Test"})
        self.assertEqual(result, True)


if __name__ == "__main__":

    suite = unittest.defaultTestLoader.loadTestsFromTestCase(UtilitiesTestCase)
    testResult = unittest.TextTestRunner(verbosity=2).run(suite)
