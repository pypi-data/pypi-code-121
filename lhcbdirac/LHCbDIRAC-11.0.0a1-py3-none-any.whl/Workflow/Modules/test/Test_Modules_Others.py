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

from mock import MagicMock, patch

from DIRAC.DataManagementSystem.Client.test.mock_DM import dm_mock
from DIRAC.Resources.Catalog.test.mock_FC import fc_mock

from DIRAC import gLogger
from DIRAC.RequestManagementSystem.Client.Request import Request

# mocks
from LHCbDIRAC.Workflow.Modules.mock_Commons import (
    prod_id,
    prod_job_id,
    wms_job_id,
    workflowStatus,
    stepStatus,
    step_id,
    step_number,
    step_commons,
    wf_commons,
    rc_mock,
)
from LHCbDIRAC.BookkeepingSystem.Client.test.mock_BookkeepingClient import bkc_mock

# sut
from LHCbDIRAC.Workflow.Modules.FailoverRequest import FailoverRequest
from LHCbDIRAC.Workflow.Modules.RemoveInputData import RemoveInputData
from LHCbDIRAC.Workflow.Modules.UserJobFinalization import UserJobFinalization
from LHCbDIRAC.Workflow.Modules.StepAccounting import StepAccounting
from LHCbDIRAC.Workflow.Modules.UploadLogFile import UploadLogFile
from LHCbDIRAC.Workflow.Modules.FileUsage import FileUsage
from LHCbDIRAC.Workflow.Modules.CreateDataFile import CreateDataFile

getDestinationSEListMock = MagicMock()
getDestinationSEListMock.return_value = []
getDestinationSEListMockCNAF = MagicMock()
getDestinationSEListMockCNAF.return_value = ["CNAF"]


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
            except Exception:
                continue


# FailoverRequest.py
@patch("LHCbDIRAC.Workflow.Modules.ModuleBase.RequestValidator", side_effect=MagicMock())
class FailoverRequestSuccess(ModulesTestCase):

    #################################################

    def test_execute(self, _patch):

        fr = FailoverRequest(bkClient=bkc_mock, dm=dm_mock)
        fr.jobType = "merge"
        fr.stepInputData = ["foo", "bar"]
        fr.requestValidator = MagicMock()

        # no errors, no input data
        for wf_cs in copy.deepcopy(wf_commons):
            for s_cs in step_commons:
                self.assertTrue(
                    fr.execute(
                        prod_id, prod_job_id, wms_job_id, workflowStatus, stepStatus, wf_cs, s_cs, step_number, step_id
                    )["OK"]
                )


# RemoveInputData.py
@patch("LHCbDIRAC.Workflow.Modules.ModuleBase.RequestValidator", side_effect=MagicMock())
class RemoveInputDataSuccess(ModulesTestCase):

    #################################################

    def test_execute(self, _patch):

        rid = RemoveInputData(bkClient=bkc_mock, dm=dm_mock)
        # no errors, no input data
        for wf_cs in copy.deepcopy(wf_commons):
            if "InputData" in wf_cs:
                continue
            for s_cs in step_commons:
                self.assertTrue(
                    rid.execute(
                        prod_id, prod_job_id, wms_job_id, workflowStatus, stepStatus, wf_cs, s_cs, step_number, step_id
                    )["OK"]
                )

        # no errors, input data
        for wf_cs in copy.deepcopy(wf_commons):
            if "InputData" not in wf_cs:
                continue
            for s_cs in step_commons:
                self.assertTrue(
                    rid.execute(
                        prod_id, prod_job_id, wms_job_id, workflowStatus, stepStatus, wf_cs, s_cs, step_number, step_id
                    )["OK"]
                )


# StepAccounting.py
@patch("LHCbDIRAC.Workflow.Modules.ModuleBase.RequestValidator", side_effect=MagicMock())
class StepAccountingSuccess(ModulesTestCase):

    #################################################

    def test_execute(self, _patch):

        sa = StepAccounting(bkClient=bkc_mock, dm=dm_mock)
        sa.jobType = "merge"
        sa.stepInputData = ["foo", "bar"]
        sa.siteName = "DIRAC.Test.ch"

        for wf_cs in copy.deepcopy(wf_commons):
            for s_cs in step_commons:
                self.assertTrue(
                    sa.execute(
                        prod_id,
                        prod_job_id,
                        wms_job_id,
                        workflowStatus,
                        stepStatus,
                        wf_cs,
                        s_cs,
                        step_number,
                        step_id,
                        self.jobStep_mock,
                        self.xf_o_mock,
                    )["OK"]
                )


# UploadLogFile.py
@patch("LHCbDIRAC.Workflow.Modules.ModuleBase.RequestValidator", side_effect=MagicMock())
class UploadLogFileSuccess(ModulesTestCase):
    @patch("LHCbDIRAC.Workflow.Modules.UploadLogFile.getDestinationSEList", side_effect=getDestinationSEListMockCNAF)
    def test_execute(self, _patch, _patch1):

        # no errors, no input data
        #    for wf_commons in copy.deepcopy( wf_commons ):
        #      for step_commons in step_commons:
        #        self.assertTrue( ulf.execute( prod_id, prod_job_id, wms_job_id,
        #                                           workflowStatus, stepStatus,
        #                                           wf_commons, step_commons,
        #                                           step_number, step_id,
        #                                           dm_mock, self.ft_mock,
        #                                           bkc_mock )['OK'] )

        # putStorageDirectory returns False

        rm_mock = copy.deepcopy(dm_mock)
        rm_mock.putStorageDirectory.return_value = {"OK": False, "Message": "bih"}
        ft_mock = copy.deepcopy(self.ft_mock)
        ulf = UploadLogFile(bkClient=bkc_mock, dm=dm_mock)
        ulf.request = Request()
        ulf.failoverTransfer = ft_mock
        for wf_cs in copy.deepcopy(wf_commons):
            for s_cs in step_commons:
                self.assertTrue(
                    ulf.execute(prod_id, prod_job_id, 0, workflowStatus, stepStatus, wf_cs, s_cs, step_number, step_id)[
                        "OK"
                    ]
                )
            # self.assertTrue( ulf.finalize( rm_mock, self.ft_mock )['OK'] )

    @patch("LHCbDIRAC.Workflow.Modules.UploadLogFile.getDestinationSEList", side_effect=getDestinationSEListMockCNAF)
    def test__uploadLogToFailoverSE(self, _patch, _patch1):
        open("foo.txt", "w").close()
        tarFileName = "foo.txt"
        ulf = UploadLogFile(bkClient=bkc_mock, dm=dm_mock)
        ulf.request = Request()
        ulf.failoverTransfer = self.ft_mock
        ulf.logLFNPath = "/an/lfn/foo.txt"
        ulf.failoverSEs = ["SE1", "SE2"]
        ulf._uploadLogToFailoverSE(tarFileName)

    @patch("LHCbDIRAC.Workflow.Modules.UploadLogFile.getDestinationSEList", side_effect=getDestinationSEListMockCNAF)
    def test__determinRelevantFiles(self, _patch, _patch1):
        for fileN in ["foo.txt", "aLog.log", "aLongLog.log", "aLongLog.log.gz"]:
            try:
                os.remove(fileN)
            except OSError:
                continue

        open("foo.txt", "w").close()
        open("bar.py", "w").close()
        open("aLog.log", "w").close()
        ulf = UploadLogFile(bkClient=bkc_mock, dm=dm_mock)
        res = ulf._determineRelevantFiles()
        self.assertTrue(res["OK"])
        expected = ["foo.txt", "aLog.log"]
        if "pylint.txt" in os.listdir("."):
            expected.append("pylint.txt")
        if "nosetests.xml" in os.listdir("."):
            expected.append("nosetests.xml")
        self.assertTrue(set(res["Value"]) >= set(expected))

        fd = open("aLongLog.log", "w")
        for _x in range(2500):
            fd.writelines(
                "Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do "
                "eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim "
                "ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut "
                "aliquip ex ea commodo consequat. Duis aute irure dolor in "
                "reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla "
                "pariatur. Excepteur sint occaecat cupidatat non proident, sunt in "
                "culpa qui officia deserunt mollit anim id est laborum"
            )
        fd.close()
        res = ulf._determineRelevantFiles()
        self.assertTrue(res["OK"])
        expected = ["foo.txt", "aLog.log", "aLongLog.log"]
        if "pylint.txt" in os.listdir("."):
            expected.append("pylint.txt")
        if "nosetests.xml" in os.listdir("."):
            expected.append("nosetests.xml")
        self.assertTrue(set(res["Value"]) >= set(expected))

        open("foo.txt", "w").close()
        fd = open("aLongLog.log", "w")
        for _x in range(2500):
            fd.writelines(
                "Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do "
                "eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim "
                "ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut "
                "aliquip ex ea commodo consequat. Duis aute irure dolor in "
                "reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla "
                "pariatur. Excepteur sint occaecat cupidatat non proident, sunt in "
                "culpa qui officia deserunt mollit anim id est laborum"
            )
        fd.close()
        open("bar.py", "w").close()
        res = ulf._determineRelevantFiles()
        expected = ["foo.txt", "aLog.log", "aLongLog.log"]
        if "pylint.txt" in os.listdir("."):
            expected.append("pylint.txt")
        if "nosetests.xml" in os.listdir("."):
            expected.append("nosetests.xml")
        self.assertTrue(res["OK"])
        self.assertTrue(set(res["Value"]) >= set(expected))


# UserJobFinalization.py
@patch("LHCbDIRAC.Workflow.Modules.ModuleBase.RequestValidator", side_effect=MagicMock())
class UserJobFinalizationSuccess(ModulesTestCase):
    def test_execute(self, _patch):

        ujf = UserJobFinalization(bkClient=bkc_mock, dm=dm_mock)
        ujf.bkClient = bkc_mock
        ujf.failoverTransfer = self.ft_mock
        ujf.requestValidator = MagicMock()
        ujf.requestValidator.validate.return_value = {"OK": True}

        # no errors, no input data
        for wf_cs in copy.deepcopy(wf_commons):
            wf_cs["TotalSteps"] = step_number
            for s_cs in step_commons:
                self.assertTrue(
                    ujf.execute(
                        prod_id, prod_job_id, wms_job_id, workflowStatus, stepStatus, wf_cs, s_cs, step_number, step_id
                    )["OK"]
                )

        for wf_cs in copy.deepcopy(wf_commons):
            wf_cs["TotalSteps"] = step_number
            for s_cs in step_commons:
                wf_cs["UserOutputData"] = ["i1", "i2"]
                wf_cs["UserOutputSE"] = ["MySE"]
                wf_cs["OwnerName"] = "fstagni"
                open("i1", "w").close()
                open("i2", "w").close()
                self.assertTrue(
                    ujf.execute(
                        prod_id,
                        prod_job_id,
                        wms_job_id,
                        workflowStatus,
                        stepStatus,
                        wf_cs,
                        s_cs,
                        step_number,
                        step_id,
                        orderedSEs=["MySE1", "MySE2"],
                    )["OK"]
                )
            os.remove("i1")
            os.remove("i2")

    @patch("LHCbDIRAC.Workflow.Modules.UserJobFinalization.getDestinationSEList", side_effect=getDestinationSEListMock)
    def test__getOrderedSEsList(self, _patch, _patched):

        ujf = UserJobFinalization(bkClient=bkc_mock, dm=dm_mock)

        ujf.userOutputSE = ["userSE"]
        res = ujf._getOrderedSEsList()
        self.assertEqual(res, ["userSE"])

        ujf.defaultOutputSE = ["CERN"]
        res = ujf._getOrderedSEsList()
        self.assertEqual(res, ["userSE", "CERN"])

    @patch(
        "LHCbDIRAC.Workflow.Modules.UserJobFinalization.getDestinationSEList", side_effect=getDestinationSEListMockCNAF
    )
    def test__getOrderedSEsListCNAF(self, _patch, _patched):

        ujf = UserJobFinalization(bkClient=bkc_mock, dm=dm_mock)
        res = ujf._getOrderedSEsList()
        self.assertEqual(res, ["CNAF"])


# FileUsage.py
@patch("LHCbDIRAC.Workflow.Modules.ModuleBase.RequestValidator", side_effect=MagicMock())
class FileUsageSuccess(ModulesTestCase):

    #################################################

    def test_execute(self, _patch):

        # no errors, no input files to report
        wfStatus = copy.deepcopy(workflowStatus)
        wfC = copy.deepcopy(wf_commons)
        for wf_cs in wfC:  # copy.deepcopy( wf_commons ):
            for s_cs in step_commons:
                fu = FileUsage(bkClient=bkc_mock, dm=dm_mock)
                self.assertTrue(
                    fu.execute(
                        prod_id, prod_job_id, wms_job_id, wfStatus, stepStatus, wf_cs, s_cs, step_number, step_id
                    )["OK"]
                )
        wfC = copy.deepcopy(wf_commons)
        for wf_cs in wfC:  # copy.deepcopy( wf_commons ):
            wf_cs["ParametricInputData"] = [
                "LFN:/lhcb/data/2010/EW.DST/00008380/0000/00008380_00000287_1.ew.dst",
                "LFN:/lhcb/data/2010/EW.DST/00008380/0000/00008380_00000285_1.ew.dst",
                "LFN:/lhcb/data/2010/EW.DST/00008380/0000/00008380_00000281_1.ew.dst",
            ]
            for s_cs in step_commons:
                fu = FileUsage(bkClient=bkc_mock, dm=dm_mock)
                self.assertTrue(
                    fu.execute(
                        prod_id, prod_job_id, wms_job_id, workflowStatus, stepStatus, wf_cs, s_cs, step_number, step_id
                    )["OK"]
                )
        wfC = copy.deepcopy(wf_commons)
        for wf_cs in wfC:  # copy.deepcopy( wf_commons ):
            wf_cs["ParametricInputData"] = [
                "LFN:/lhcb/data/2010/EW.DST/00008380/0000/00008380_00000287_1.ew.dst",
                "LFN:/lhcb/data/2010/EW.DST/00008380/0000/00008380_00000285_1.ew.dst",
                "LFN:/lhcb/data/2010/PIPPO/00008380/0000/00008380_00000281_1.pippo.dst",
            ]
            for s_cs in step_commons:
                fu = FileUsage(bkClient=bkc_mock, dm=dm_mock)
                self.assertTrue(
                    fu.execute(
                        prod_id, prod_job_id, wms_job_id, workflowStatus, stepStatus, wf_cs, s_cs, step_number, step_id
                    )["OK"]
                )

        # workflow status not ok
        wfC = copy.deepcopy(wf_commons)
        for wf_cs in wfC:  # copy.deepcopy( wf_commons ):
            wfStatus = {"OK": False, "Message": "Mess"}
            for s_cs in step_commons:
                fu = FileUsage(bkClient=bkc_mock, dm=dm_mock)
                self.assertTrue(
                    fu.execute(
                        prod_id, prod_job_id, wms_job_id, wfStatus, stepStatus, wf_cs, s_cs, step_number, step_id
                    )["OK"]
                )


# FileUsage.py
@patch("LHCbDIRAC.Workflow.Modules.ModuleBase.RequestValidator", side_effect=MagicMock())
class CreateDataFileSuccess(ModulesTestCase):

    #################################################

    def test_execute(self, _patch):

        cdf = CreateDataFile(bkClient=bkc_mock, dm=dm_mock)
        cdf.jobType = "merge"
        cdf.stepInputData = ["foo", "bar"]

        for wf_cs in copy.deepcopy(wf_commons):
            for s_cs in step_commons:
                self.assertTrue(
                    cdf.execute(
                        prod_id, prod_job_id, wms_job_id, workflowStatus, stepStatus, wf_cs, s_cs, step_number, step_id
                    )["OK"]
                )


if __name__ == "__main__":
    unittest.main()
