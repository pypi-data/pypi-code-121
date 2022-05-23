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
"""Test_RSS_Policy_TransferQualityPolicy."""
import unittest

import LHCbDIRAC.ResourceStatusSystem.Policy.TransferQualityPolicy as moduleTested

################################################################################


class TransferQualityPolicy_TestCase(unittest.TestCase):
    def setUp(self):
        """Setup."""

        self.moduleTested = moduleTested
        self.testClass = self.moduleTested.TransferQualityPolicy

    def tearDown(self):
        """Tear down."""

        del self.moduleTested
        del self.testClass


################################################################################


class TransferQualityPolicy_Success(TransferQualityPolicy_TestCase):
    def test_instantiate(self):
        """tests that we can instantiate one object of the tested class."""

        module = self.testClass()
        self.assertEqual("TransferQualityPolicy", module.__class__.__name__)

    def test_evaluate(self):
        """tests the method _evaluate."""

        module = self.testClass()

        res = module._evaluate({"OK": False, "Message": "Bo!"})
        self.assertTrue(res["OK"])
        self.assertEqual("Error", res["Value"]["Status"])
        self.assertEqual("Bo!", res["Value"]["Reason"])

        res = module._evaluate({"OK": True, "Value": None})
        self.assertTrue(res["OK"])
        self.assertEqual("Unknown", res["Value"]["Status"])
        self.assertEqual("No values to take a decision", res["Value"]["Reason"])

        res = module._evaluate({"OK": True, "Value": []})
        self.assertTrue(res["OK"])
        self.assertEqual("Unknown", res["Value"]["Status"])
        self.assertEqual("No values to take a decision", res["Value"]["Reason"])

        res = module._evaluate({"OK": True, "Value": {"A": 1}})
        self.assertTrue(res["OK"])
        self.assertEqual("Error", res["Value"]["Status"])
        self.assertEqual('Missing "Name" key', res["Value"]["Reason"])

        res = module._evaluate({"OK": True, "Value": {"Name": "1"}})
        self.assertTrue(res["OK"])
        self.assertEqual("Error", res["Value"]["Status"])
        self.assertEqual('Missing "Mean" key', res["Value"]["Reason"])

        res = module._evaluate({"OK": True, "Value": {"Name": "1", "Mean": None}})
        self.assertTrue(res["OK"])
        self.assertEqual("Unknown", res["Value"]["Status"])
        self.assertEqual("No values to take a decision", res["Value"]["Reason"])

        res = module._evaluate({"OK": True, "Value": {"Name": "1", "Mean": 0}})
        self.assertTrue(res["OK"])
        self.assertEqual("Degraded", res["Value"]["Status"])
        self.assertEqual("TransferQuality: 0 -> Low", res["Value"]["Reason"])

        res = module._evaluate({"OK": True, "Value": {"Name": "1", "Mean": 70}})
        self.assertTrue(res["OK"])
        self.assertEqual("Degraded", res["Value"]["Status"])
        self.assertEqual("TransferQuality: 70 -> Mean", res["Value"]["Reason"])

        res = module._evaluate({"OK": True, "Value": {"Name": "1", "Mean": 95}})
        self.assertTrue(res["OK"])
        self.assertEqual("Active", res["Value"]["Status"])
        self.assertEqual("TransferQuality: 95 -> High", res["Value"]["Reason"])

        res = module._evaluate({"OK": True, "Value": {"Name": "1failover", "Mean": 0}})
        self.assertTrue(res["OK"])
        self.assertEqual("Degraded", res["Value"]["Status"])
        self.assertEqual("TransferQuality: 0 -> Low", res["Value"]["Reason"])

        res = module._evaluate({"OK": True, "Value": {"Name": "1failover", "Mean": 70}})
        self.assertTrue(res["OK"])
        self.assertEqual("Active", res["Value"]["Status"])
        self.assertEqual("TransferQuality: 70 -> Mean", res["Value"]["Reason"])

        res = module._evaluate({"OK": True, "Value": {"Name": "1failover", "Mean": 95}})
        self.assertTrue(res["OK"])
        self.assertEqual("Active", res["Value"]["Status"])
        self.assertEqual("TransferQuality: 95 -> High", res["Value"]["Reason"])


if __name__ == "__main__":
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(TransferQualityPolicy_TestCase)
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TransferQualityPolicy_Success))
    testResult = unittest.TextTestRunner(verbosity=2).run(suite)

################################################################################
