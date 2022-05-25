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
"""Unit tests for Workflow Modules."""
# pylint: disable=protected-access, missing-docstring, invalid-name, line-too-long

import unittest
import os
import copy
import shutil
from textwrap import dedent

from mock import MagicMock, patch

from DIRAC import gLogger
from DIRAC.TransformationSystem.Client.FileReport import FileReport

# mocks
from DIRAC.DataManagementSystem.Client.test.mock_DM import dm_mock
from DIRAC.Resources.Catalog.test.mock_FC import fc_mock


from LHCbDIRAC.Core.Utilities.XMLSummaries import XMLSummary

# mocks
from LHCbDIRAC.Workflow.Modules.mock_Commons import (
    step_commons,
    wf_commons,
    prod_id,
    prod_job_id,
    wms_job_id,
    workflowStatus,
    stepStatus,
    step_id,
    step_number,
    rc_mock,
)
from LHCbDIRAC.BookkeepingSystem.Client.test.mock_BookkeepingClient import bkc_mock

# sut
from LHCbDIRAC.Workflow.Modules.AnalyseXMLSummary import AnalyseXMLSummary


class ModulesTestCase(unittest.TestCase):
    """Base class for the Modules test cases."""

    def setUp(self):

        gLogger.setLevel("DEBUG")
        self.maxDiff = None

        self.jsu_mock = MagicMock()
        self.jsu_mock.setJobApplicationStatus.return_value = {"OK": True, "Value": ""}

        self.jsu_mock = MagicMock()
        self.jsu_mock.setJobApplicationStatus.return_value = {"OK": True, "Value": ""}

        self.ft_mock = MagicMock()
        self.ft_mock.transferAndRegisterFile.return_value = {"OK": True, "Value": {"uploadedSE": ""}}
        self.ft_mock.transferAndRegisterFileFailover.return_value = {"OK": True, "Value": {}}
        self.ft_mock.request = rc_mock
        self.ft_mock.FileCatalog = fc_mock

        self.nc_mock = MagicMock()
        self.nc_mock.sendMail.return_value = {"OK": True, "Value": ""}

        self.xf_o_mock = MagicMock()
        self.xf_o_mock.inputFileStats = {"a": 1, "b": 2}
        self.xf_o_mock.outputFileStats = {"a": 1, "b": 2}
        self.xf_o_mock.analyse.return_value = True

        self.jobStep_mock = MagicMock()
        self.jobStep_mock.commit.return_value = {"OK": True, "Value": ""}
        self.jobStep_mock.setValuesFromDict.return_value = {"OK": True, "Value": ""}
        self.jobStep_mock.checkValues.return_value = {"OK": True, "Value": ""}

    def tearDown(self):
        for fileProd in [
            "appLog",
            "foo.txt",
            "aaa.Bhadron.dst",
            "bbb.Calibration.dst",
            "bar.py",
            "aLongLog.log",
            "bookkeeping_123_00000456_321.xml",
            "aLongLog.log.gz",
            "ccc.charm.mdst",
            "ccc.charm.mdst",
            "prova.txt",
            "aLog.log",
            "BAR.txt",
            "FooBAR.ext.txt",
            "foo_1.txt",
            "bar_2.py",
            "bar.txt",
            "ErrorLogging_Step1_coredump.log",
            "123_00000456_request.xml",
            "lfn1",
            "lfn2",
            "XMLSummaryFile",
            "aaa.bhadron.dst",
            "bbb.calibration.dst",
            "ProductionOutputData",
            "data.py",
            "123_00000456_request.json",
            "00000123_00000456.tar",
            "someOtherDir",
            "DISABLE_WATCHDOG_CPU_WALLCLOCK_CHECK",
            "myfoo.blah",
            "prodConf_someApp__.py",
            "prodConf_someApp___.py",
        ]:
            try:
                os.remove(fileProd)
            except OSError:
                continue

        for directory in ["./job", "job"]:
            try:
                shutil.rmtree(directory)
            except BaseException:
                continue


@patch("LHCbDIRAC.Workflow.Modules.ModuleBase.RequestValidator", side_effect=MagicMock())
class AnalyseXMLSummarySuccess(ModulesTestCase):

    #################################################

    def test_execute(self, _patch):

        axlf = AnalyseXMLSummary(bkClient=bkc_mock, dm=dm_mock)
        axlf.stepInputData = ["some.sdst", "00012345_00006789_1.sdst"]
        axlf.jobType = "merge"

        logAnalyser = MagicMock()

        logAnalyser.return_value = True
        axlf.logAnalyser = logAnalyser
        axlf.XMLSummary_o = self.xf_o_mock
        axlf.nc = self.nc_mock
        axlf.XMLSummary = "XMLSummaryFile"
        with open(axlf.XMLSummary, "w") as f:
            f.write(
                dedent(
                    """<?xml version="1.0" encoding="UTF-8"?>

          <summary version="1.0" xsi:noNamespaceSchemaLocation="$XMLSUMMARYBASEROOT/xml/XMLSummary.xsd" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
                  <success>True</success>
                  <step>finalize</step>
                  <usage>
                          <stat unit="KB" useOf="MemoryMaximum">866104.0</stat>
                  </usage>
                  <input>
                          <file GUID="CCE96707-4BE9-E011-81CD-003048F35252" name="LFN:00012478_00000532_1.sim" status="full">200</file>
                  </input>
                  <output>
                          <file GUID="229BBEF1-66E9-E011-BBD0-003048F35252" name="PFN:00012478_00000532_2.xdigi" status="full">200</file>
                  </output>
          </summary>
          """  # noqa
                )
            )

        # no errors, all ok
        for wf_cs in copy.deepcopy(wf_commons):
            for s_cs in step_commons:
                self.assertTrue(
                    axlf.execute(
                        prod_id, prod_job_id, wms_job_id, workflowStatus, stepStatus, wf_cs, s_cs, step_number, step_id
                    )["OK"]
                )

        # logAnalyser gives errors
        axlf.jobType = "reco"

        logAnalyser.return_value = False
        axlf.logAnalyser = logAnalyser

        for wf_cs in copy.deepcopy(wf_commons):
            for s_cs in step_commons:
                self.assertTrue(
                    axlf.execute(
                        prod_id, prod_job_id, wms_job_id, workflowStatus, stepStatus, wf_cs, s_cs, step_number, step_id
                    )["OK"]
                )

    def test__basicSuccess(self, _patch):

        axlf = AnalyseXMLSummary(bkClient=bkc_mock, dm=dm_mock)

        with open("XMLSummaryFile", "w") as f:
            f.write(
                dedent(
                    """<?xml version="1.0" encoding="UTF-8"?>

          <summary version="1.0" xsi:noNamespaceSchemaLocation="$XMLSUMMARYBASEROOT/xml/XMLSummary.xsd" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
                  <success>True</success>
                  <step>finalize</step>
                  <usage>
                          <stat unit="KB" useOf="MemoryMaximum">866104.0</stat>
                  </usage>
                  <input>
                          <file GUID="CCE96707-4BE9-E011-81CD-003048F35252" name="LFN:00012478_00000532_1.sim" status="full">200</file>
                  </input>
                  <output>
                          <file GUID="229BBEF1-66E9-E011-BBD0-003048F35252" name="PFN:00012478_00000532_2.xdigi" status="full">200</file>
                  </output>
          </summary>
          """  # noqa
                )
            )
        axlf.XMLSummary_o = XMLSummary("XMLSummaryFile")
        res = axlf._basicSuccess()
        self.assertFalse(res)

        axlf.XMLSummary_o.inputFileStats = {"full": 2, "part": 1, "fail": 0, "other": 0}
        axlf.XMLSummary_o.inputStatus = [("aa/1.txt", "full"), ("aa/2.txt", "part")]
        axlf.inputDataList = ["aa/1.txt", "aa/2.txt"]
        axlf.numberOfEvents = -1
        axlf.fileReport = FileReport()
        axlf.production_id = "123"
        res = axlf._basicSuccess()
        self.assertTrue(res)
        self.assertEqual(axlf.fileReport.statusDict, {"aa/2.txt": "Problematic"})

        axlf.XMLSummary_o.inputFileStats = {"full": 2, "part": 0, "fail": 1, "other": 0}
        axlf.XMLSummary_o.inputStatus = [("aa/1.txt", "fail"), ("aa/2.txt", "full")]
        axlf.inputDataList = ["aa/1.txt", "aa/2.txt"]
        axlf.numberOfEvents = -1
        axlf.fileReport = FileReport()
        axlf.production_id = "123"
        res = axlf._basicSuccess()
        self.assertTrue(res)
        self.assertEqual(axlf.fileReport.statusDict, {"aa/1.txt": "Problematic"})

        axlf.XMLSummary_o.inputFileStats = {"full": 2, "part": 0, "fail": 1, "other": 0}
        axlf.XMLSummary_o.inputStatus = [("aa/1.txt", "fail"), ("aa/2.txt", "full")]
        axlf.inputDataList = ["aa/3.txt"]
        axlf.numberOfEvents = -1
        axlf.fileReport = FileReport()
        axlf.production_id = "123"
        res = axlf._basicSuccess()
        self.assertFalse(res)
        self.assertEqual(axlf.fileReport.statusDict, {})

        axlf.XMLSummary_o.inputFileStats = {"full": 2, "part": 1, "fail": 1, "other": 0}
        axlf.XMLSummary_o.inputStatus = [("aa/1.txt", "fail"), ("aa/2.txt", "part")]
        axlf.inputDataList = ["aa/1.txt", "aa/2.txt"]
        axlf.numberOfEvents = -1
        axlf.fileReport = FileReport()
        axlf.production_id = "123"
        res = axlf._basicSuccess()
        self.assertTrue(res)
        self.assertEqual(axlf.fileReport.statusDict, {"aa/1.txt": "Problematic", "aa/2.txt": "Problematic"})

        axlf.XMLSummary_o.inputFileStats = {"full": 2, "part": 1, "fail": 1, "other": 0}
        axlf.XMLSummary_o.inputStatus = [("aa/1.txt", "fail"), ("aa/2.txt", "part")]
        axlf.inputDataList = ["aa/1.txt", "aa/2.txt"]
        axlf.numberOfEvents = "10"
        axlf.fileReport = FileReport()
        axlf.production_id = "123"
        res = axlf._basicSuccess()
        self.assertTrue(res)
        self.assertEqual(axlf.fileReport.statusDict, {"aa/1.txt": "Problematic"})


if __name__ == "__main__":
    unittest.main()
