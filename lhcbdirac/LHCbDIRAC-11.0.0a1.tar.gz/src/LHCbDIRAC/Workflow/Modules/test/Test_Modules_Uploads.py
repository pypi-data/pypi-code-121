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
"""Unit tests for Workflow Module Uploads."""
# pylint: disable=protected-access, missing-docstring
import os
import copy
import json

from mock import MagicMock
import pytest

from DIRAC import gLogger
from DIRAC.RequestManagementSystem.Client.Request import Request
from DIRAC.RequestManagementSystem.Client.Operation import Operation
from DIRAC.RequestManagementSystem.Client.File import File

# mocks
from DIRAC.DataManagementSystem.Client.test.mock_DM import dm_mock
from DIRAC.Resources.Catalog.test.mock_FC import fc_mock

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
from LHCbDIRAC.Workflow.Modules.UploadOutputData import UploadOutputData


ft_mock = MagicMock()
ft_mock.transferAndRegisterFile.return_value = {"OK": True, "Value": {"uploadedSE": ""}}
ft_mock.transferAndRegisterFileFailover.return_value = {"OK": True, "Value": {}}
ft_mock.request = rc_mock
ft_mock.FileCatalog = fc_mock


@pytest.fixture
def rmFiles():
    yield
    for fileProd in [
        "appLog",
        "foo.txt",
        "bar.txt",
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


def test_execute(mocker, rmFiles):
    mocker.patch("LHCbDIRAC.Workflow.Modules.ModuleBase.RequestValidator", side_effect=MagicMock())
    mocker.patch("LHCbDIRAC.Workflow.Modules.UploadOutputData.FileCatalog", side_effect=fc_mock)
    mocker.patch("LHCbDIRAC.Core.Utilities.ResolveSE.gConfig", side_effect=MagicMock())

    uod = UploadOutputData(bkClient=bkc_mock, dm=dm_mock)
    uod.log = gLogger
    uod.log.setLevel("DEBUG")
    uod.siteName = "DIRAC.Test.ch"
    uod.failoverTransfer = ft_mock

    # no errors, no input data
    for wf_cs in copy.deepcopy(wf_commons[0:1]):
        if "outputList" in wf_cs:
            continue
        for s_cs in step_commons[0:1]:
            fileDescendants = {}
            assert (
                uod.execute(
                    prod_id,
                    prod_job_id,
                    wms_job_id,
                    workflowStatus,
                    stepStatus,
                    wf_cs,
                    s_cs,
                    step_number,
                    step_id,
                    SEs=["SomeSE"],
                    fileDescendants=fileDescendants,
                )["OK"]
                is True
            )

    # no errors, input data
    for wf_cs in copy.deepcopy(wf_commons):
        for s_cs in step_commons:
            for transferAndRegisterFile in (
                {"OK": True, "Value": {"uploadedSE": ""}},
                {"OK": False, "Message": "error"},
            ):
                # for transferAndRegisterFileFailover in ( {'OK': True, 'Value': {}},
                # {'OK': False, 'Message': 'error'} ):
                ft_mock.transferAndRegisterFile.return_value = transferAndRegisterFile
                open("foo.txt", "w").close()
                open("bar.txt", "w").close()
                if "InputData" not in wf_cs:
                    continue
                if wf_cs["InputData"] == "":
                    continue
                wf_cs["outputList"] = [
                    {"outputDataType": "txt", "outputDataName": "foo.txt"},
                    {"outputDataType": "txt", "outputDataName": "bar.txt"},
                ]
                wf_cs["ProductionOutputData"] = [
                    "/lhcb/MC/2010/DST/00012345/0001/foo.txt",
                    "/lhcb/MC/2010/DST/00012345/0001/bar.txt",
                ]
                # bkc_mock.getFileDescendants.return_value = {
                #     'OK': False,
                #     'rpcStub': (
                #         ( 'Bookkeeping/BookkeepingManager',
                #         {'skipCACheck': False,
                #         'timeout': 3600} ),
                #         'getFileDescendants', ( ['foo'], 9, 0, True ) ),
                #     'Value': {'Successful': {'foo.txt': ['baaar']}, 'Failed': [], 'NotProcessed': []}
                # }
                fileDescendants = {"foo.txt": ["baaar"]}
                assert (
                    uod.execute(
                        prod_id,
                        prod_job_id,
                        wms_job_id,
                        workflowStatus,
                        stepStatus,
                        wf_cs,
                        s_cs,
                        step_number,
                        step_id,
                        SEs=["SomeSE"],
                        fileDescendants=fileDescendants,
                    )["OK"]
                    is False
                )

                # bkc_mock.getFileDescendants.return_value = {
                #     'OK': True,
                #     'rpcStub': ( (
                #         'Bookkeeping/BookkeepingManager',
                #         {'skipCACheck': False, 'timeout': 3600} ),
                #         'getFileDescendants', ( ['foo'], 9, 0, True ) ),
                #     'Value': {'Successful': {}, 'Failed': [], 'NotProcessed': []},
                # }
                if wf_cs["Request"] == "":
                    continue
                fileDescendants = {}
                res = uod.execute(
                    prod_id,
                    prod_job_id,
                    wms_job_id,
                    workflowStatus,
                    stepStatus,
                    wf_cs,
                    s_cs,
                    step_number,
                    step_id,
                    SEs=["SomeSE"],
                    fileDescendants=fileDescendants,
                )
                assert res["OK"] is True
                #            if transferAndRegisterFileFailover['OK']:
                #              self.assertTrue( res['OK'] )
                #            else:
                #              self.assertFalse( res['OK'] )
                os.remove("foo.txt")
                os.remove("bar.txt")


def test__getLFNsForBKRegistration(mocker):
    mocker.patch("LHCbDIRAC.Workflow.Modules.ModuleBase.RequestValidator", side_effect=MagicMock())

    f1 = File()
    f1.LFN = "/a/1.txt"
    f2 = File()
    f2.LFN = "/a/2.txt"
    f3 = File()
    f3.LFN = "/a/3.txt"

    o1 = Operation()
    o1.Type = "RegisterFile"
    o1.addFile(f1)
    o2 = Operation()
    o2.Type = "RegisterFile"
    o2.addFile(f2)
    o3 = Operation()
    o3.Type = "ForwardDISET"
    o4 = Operation()
    o4.Type = "RegisterFile"
    o4.addFile(f1)
    o4.addFile(f3)

    r = Request()
    r.addOperation(o4)
    r.addOperation(o1)
    r.addOperation(o2)
    r.addOperation(o3)

    uod = UploadOutputData(bkClient=bkc_mock, dm=dm_mock)
    uod.request = r

    lfns = set(["/a/1.txt", "/a/5.txt", "/a/6.txt", "/a/3.txt"])
    lfnsForBkReg = uod._getLFNsForBKRegistration(lfns)
    assert sorted(lfnsForBkReg) == sorted(["/a/5.txt", "/a/6.txt"])


def test__cleanUp(mocker):
    mocker.patch("LHCbDIRAC.Workflow.Modules.ModuleBase.RequestValidator", side_effect=MagicMock())

    f1 = File()
    f1.LFN = "/a/1.txt"
    f2 = File()
    f2.LFN = "/a/2.txt"
    f3 = File()
    f3.LFN = "/a/3.txt"

    o1 = Operation()
    o1.Type = "RegisterFile"
    o1.addFile(f1)
    o2 = Operation()
    o2.Type = "RegisterFile"
    o2.addFile(f2)
    o3 = Operation()
    o3.Type = "ForwardDISET"
    o4 = Operation()
    o4.Type = "RegisterFile"
    o4.addFile(f1)
    o4.addFile(f3)

    r = Request()
    r.addOperation(o4)
    r.addOperation(o1)
    r.addOperation(o2)
    r.addOperation(o3)

    uod = UploadOutputData(bkClient=bkc_mock, dm=dm_mock)
    uod.failoverTransfer = ft_mock
    uod.request = r

    expected = Request()
    expected.addOperation(o3)
    removeOp = Operation()
    removeOp.Type = "RemoveFile"
    fileRemove1 = File()
    fileRemove1.LFN = "/a/1.txt"
    fileRemove2 = File()
    fileRemove2.LFN = "/a/2.txt"
    fileRemove3 = File()
    fileRemove3.LFN = "/a/notPresent.txt"
    removeOp.addFile(fileRemove1)
    removeOp.addFile(fileRemove3)
    removeOp.addFile(fileRemove2)
    expected.addOperation(removeOp)

    uod._cleanUp(
        {"1.txt": {"lfn": "/a/1.txt"}, "2.txt": {"lfn": "/a/2.txt"}, "notPresent.txt": {"lfn": "/a/notPresent.txt"}}
    )

    for opsR, opsE in zip(uod.request, expected):
        opsRLoaded = json.loads(str(opsR))
        opsELoaded = json.loads(str(opsE))
        for k in set(opsRLoaded) | set(opsELoaded):
            if k == "Files":
                assert sorted(opsRLoaded[k], key=lambda x: x["LFN"]) == sorted(opsELoaded[k], key=lambda x: x["LFN"])
            else:
                assert opsRLoaded[k] == opsELoaded[k]
