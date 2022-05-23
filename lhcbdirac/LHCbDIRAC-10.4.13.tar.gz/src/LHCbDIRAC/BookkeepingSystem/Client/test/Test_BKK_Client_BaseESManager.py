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
"""Test_BKK_Client_BaseESManager."""
import unittest
import LHCbDIRAC.BookkeepingSystem.Client.BaseESManager as moduleTested


class BaseESManager_TestCase(unittest.TestCase):
    def setUp(self):
        """Setup."""

        self.testClass = moduleTested.BaseESManager

    def tearDown(self):
        """TearDown."""

        del self.testClass


class BaseESManager_Success(BaseESManager_TestCase):
    def test_instantiate(self):
        """tests that we can instantiate one object of the tested class."""
        client = self.testClass()
        self.assertEqual("BaseESManager", client.__class__.__name__)
