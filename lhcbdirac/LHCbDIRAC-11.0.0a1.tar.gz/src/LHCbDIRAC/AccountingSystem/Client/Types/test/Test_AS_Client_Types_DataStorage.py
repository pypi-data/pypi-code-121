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
"""Test_AS_Client_Type_DataStorage."""
import unittest

dummyResults = {}


class DummyReturn(object):
    def __init__(self, *args, **kwargs):
        pass

    def __getattr__(self, name):
        return self.dummyMethod

    def dummyMethod(self, *args, **kwargs):
        return dummyResults[self.__class__.__name__]


class dBaseAccountingType(DummyReturn):
    pass


################################################################################


class DataStorage_TestCase(unittest.TestCase):
    def setUp(self):
        """Setup."""

        # We need the proper software, and then we overwrite it.
        import LHCbDIRAC.AccountingSystem.Client.Types.DataStorage as moduleTested

        moduleTested.BaseAccountingType = dBaseAccountingType
        moduleTested.DataStorage.__bases__ = (dBaseAccountingType,)

        self.accountingType = moduleTested.DataStorage

    def tearDown(self):
        """TearDown."""
        del self.accountingType


class DataStorage_Success(DataStorage_TestCase):
    def test_instantiate(self):
        """tests that we can instantiate one object of the tested class."""
        global dummyResults
        dummyResults["DataStorage"] = None

        accountingType = self.accountingType()
        self.assertEqual("DataStorage", accountingType.__class__.__name__)


################################################################################


if __name__ == "__main__":
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(DataStorage_TestCase)
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(DataStorage_Success))
    testResult = unittest.TextTestRunner(verbosity=2).run(suite)
