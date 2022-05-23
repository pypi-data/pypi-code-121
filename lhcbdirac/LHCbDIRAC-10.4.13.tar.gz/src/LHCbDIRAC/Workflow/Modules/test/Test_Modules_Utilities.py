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
"""Unit tests for Workflow Modules utilities."""
# pylint: disable=protected-access, missing-docstring, invalid-name, line-too-long

import unittest
import os

from mock import patch

from DIRAC import gConfig, gLogger, S_OK, S_ERROR
from DIRAC.ConfigurationSystem.Client.Helpers import Resources

from LHCbDIRAC.Workflow.Modules.ModulesUtilities import (
    lowerExtension,
    getEventsToProduce,
    getCPUNormalizationFactorAvg,
    getProductionParameterValue,
)


class ModulesUtilitiesTestCase(unittest.TestCase):
    """Base class for the ModulesUtilities test cases."""

    def setUp(self):

        gLogger.setLevel("DEBUG")
        self.maxDiff = None

    def tearDown(self):
        for fileProd in ["foo.txt", "BAR.txt", "FooBAR.ext.txt"]:
            try:
                os.remove(fileProd)
            except OSError:
                continue


#############################################################################
# ModulesUtilities.py
#############################################################################


class ModulesUtilitiesSuccess(ModulesUtilitiesTestCase):

    #################################################

    def test_lowerExtension(self):

        open("foo.tXt", "w").close()
        open("BAR.txt", "w").close()
        open("FooBAR.eXT.TXT", "w").close()

        lowerExtension()

        self.assertTrue("foo.txt" in os.listdir("."))
        self.assertTrue("BAR.txt" in os.listdir("."))
        self.assertTrue("FooBAR.ext.txt" in os.listdir("."))

    #################################################

    def test_getEventsToProduce(self):

        CPUe = 2.0
        CPUTime = 1000000.0
        CPUNormalizationFactor = 0.5

        out = getEventsToProduce(CPUe, CPUTime, CPUNormalizationFactor)
        outExp = 187500
        self.assertEqual(out, outExp)

        out = getEventsToProduce(CPUe, CPUTime, CPUNormalizationFactor, maxNumberOfEvents=1000)
        outExp = 1000
        self.assertEqual(out, outExp)

        out = getEventsToProduce(CPUe, CPUTime, CPUNormalizationFactor, jobMaxCPUTime=100000)
        outExp = 18750
        self.assertEqual(out, outExp)

        out = getEventsToProduce(CPUe, CPUTime, CPUNormalizationFactor, maxNumberOfEvents=1000, jobMaxCPUTime=100000)
        outExp = 1000
        self.assertEqual(out, outExp)

    #################################################

    def test_getCPUNormalizationFactorAvg(self):

        with patch.object(gConfig, "getSections") as mockGetSections:  # @UndefinedVariable
            with patch.object(Resources, "getQueues") as mockGetQueues:  # @UndefinedVariable

                # gConfig.getSection error
                mockGetSections.return_value = S_ERROR()
                self.assertRaises(RuntimeError, getCPUNormalizationFactorAvg)

                # Resources.getQueues error
                mockGetSections.return_value = S_OK(["LCG.CERN.ch"])
                mockGetQueues.return_value = S_ERROR()
                self.assertRaises(RuntimeError, getCPUNormalizationFactorAvg)

                # no queues
                mockGetQueues.return_value = S_OK({"LCG.CERN.ch": {}})
                self.assertRaises(RuntimeError, getCPUNormalizationFactorAvg)

                # success
                mockGetQueues.return_value = S_OK(
                    {
                        "LCG.CERN.ch": {
                            "ce201.cern.ch": {
                                "CEType": "CREAM",
                                "OS": "ScientificCERNSLC_Boron_5.5",
                                "Pilot": "True",
                                "Queues": {
                                    "cream-lsf-grid_2nh_lhcb": {
                                        "MaxTotalJobs": "1000",
                                        "MaxWaitingJobs": "20",
                                        "SI00": "1000",
                                        "maxCPUTime": "120",
                                    },
                                    "cream-lsf-grid_lhcb": {
                                        "MaxTotalJobs": "1000",
                                        "MaxWaitingJobs": "100",
                                        "SI00": "1000",
                                        "WaitingToRunningRatio": "0.2",
                                        "maxCPUTime": "10080",
                                    },
                                },
                                "SI00": "5242",
                                "SubmissionMode": "Direct",
                                "architecture": "x86_64",
                                "wnTmpDir": ".",
                            },
                            "ce202.cern.ch": {
                                "CEType": "CREAM",
                                "OS": "ScientificCERNSLC_Boron_5.8",
                                "Pilot": "True",
                                "Queues": {
                                    "cream-lsf-grid_2nh_lhcb": {
                                        "MaxTotalJobs": "1000",
                                        "MaxWaitingJobs": "20",
                                        "SI00": "1000",
                                        "maxCPUTime": "120",
                                    },
                                    "cream-lsf-grid_lhcb": {
                                        "MaxTotalJobs": "1000",
                                        "MaxWaitingJobs": "100",
                                        "SI00": "1000",
                                        "WaitingToRunningRatio": "0.2",
                                        "maxCPUTime": "10080",
                                    },
                                },
                                "SI00": "5242",
                                "SubmissionMode": "Direct",
                                "architecture": "x86_64",
                                "wnTmpDir": ".",
                            },
                        }
                    }
                )
                out = getCPUNormalizationFactorAvg()
                self.assertEqual(out, 4.0)

    #################################################

    def test_getProductionParameterValue(self):

        emptyXML = "<Workflow></Workflow>"
        noValueProductionXML = """
      <Workflow>
        <origin></origin>
        <description><![CDATA[prodDescription]]></description>
        <descr_short></descr_short>
        <version>0.0</version>
        <type></type>
        <name>Request_12416_MCSimulation_Sim08a/Digi13/Trig0x40760037/Reco14a/Stripping20r1NoPrescalingFlagged_EventType_13296003__1</name>
        <Parameter name="JobType" type="JDL" linked_module="" linked_parameter="" in="True" out="False" description="User specified type">
          <value></value>
        </Parameter>
      </Workflow>
    """  # noqa
        productionXML = """
      <Workflow>
        <origin></origin>
        <description><![CDATA[prodDescription]]></description>
        <descr_short></descr_short>
        <version>0.0</version>
        <type></type>
        <name>Request_12416_MCSimulation_Sim08a/Digi13/Trig0x40760037/Reco14a/Stripping20r1NoPrescalingFlagged_EventType_13296003__1</name>
        <Parameter name="JobType" type="JDL" linked_module="" linked_parameter="" in="True" out="False" description="User specified type">
          <value><![CDATA[MCSimulation]]></value>
        </Parameter>
      </Workflow>
    """  # noqa

        parameterName = "JobType"

        valueExp = "MCSimulation"

        value = getProductionParameterValue(emptyXML, parameterName)
        self.assertEqual(value, None)

        value = getProductionParameterValue(noValueProductionXML, parameterName)
        self.assertEqual(value, None)

        value = getProductionParameterValue(productionXML, parameterName)
        self.assertEqual(value, valueExp)


#############################################################################
# Test Suite run
#############################################################################

if __name__ == "__main__":
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(ModulesUtilitiesTestCase)
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(ModulesUtilitiesSuccess))
    testResult = unittest.TextTestRunner(verbosity=2).run(suite)

# EOF#EOF#EOF#EOF#EOF#EOF#EOF#EOF#EOF#EOF#EOF#EOF#EOF#EOF#EOF#EOF#EOF#EOF#EOF#
