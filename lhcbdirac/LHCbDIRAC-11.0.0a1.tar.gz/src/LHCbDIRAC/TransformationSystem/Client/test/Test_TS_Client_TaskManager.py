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
"""Test_TS_Client_TaskManager."""
import unittest

import LHCbDIRAC.TransformationSystem.Client.TaskManager as moduleTested

################################################################################


class TaskManager_TestCase(unittest.TestCase):
    def setUp(self):
        """Setup."""
        self.moduleTested = moduleTested
        self.testClass = self.moduleTested.LHCbWorkflowTasks

    def tearDown(self):
        """TearDown."""
        del self.testClass
        del self.moduleTested


################################################################################
# Tests


class TaskManager_Success(TaskManager_TestCase):
    def test_instantiate(self):
        """tests that we can instantiate one object of the tested class."""
        instance = self.testClass()
        self.assertEqual("LHCbWorkflowTasks", instance.__class__.__name__)


################################################################################
