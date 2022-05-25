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
"""Test_RSS_Policy_Configurations."""
import unittest

import LHCbDIRAC.ResourceStatusSystem.Policy.Configurations as moduleTested

################################################################################


class Configurations_TestCase(unittest.TestCase):
    def setUp(self):
        """Setup."""

        self.moduleTested = moduleTested

    def tearDown(self):
        """Tear down."""

        del self.moduleTested


################################################################################


class Configurations_Success(Configurations_TestCase):
    def test_PoliciesMetaLHCb(self):

        policies = self.moduleTested.POLICIESMETA_LHCB

        policyKeys = set(["description", "module", "command", "args"])

        for policyName, policy in policies.items():
            print(policyName)
            self.assertEqual(policyKeys, set(policy))
            self.assertTrue(isinstance(policy["description"], str))
            self.assertTrue(isinstance(policy["module"], str))
            self.assertTrue(isinstance(policy["command"], (tuple, None)))
            self.assertTrue(isinstance(policy["args"], (dict, None)))


if __name__ == "__main__":
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(Configurations_TestCase)
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(Configurations_Success))
    testResult = unittest.TextTestRunner(verbosity=2).run(suite)
