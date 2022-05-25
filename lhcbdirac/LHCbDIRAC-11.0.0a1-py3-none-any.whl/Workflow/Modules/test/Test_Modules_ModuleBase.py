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
"""Test class for ModuleBase."""
# pylint: disable=protected-access, missing-docstring, invalid-name
import os
from itertools import product
from mock import MagicMock

import pytest

# mocks
from DIRAC.DataManagementSystem.Client.test.mock_DM import dm_mock
from LHCbDIRAC.BookkeepingSystem.Client.test.mock_BookkeepingClient import bkc_mock
from LHCbDIRAC.Workflow.Modules.mock_Commons import (
    version,
    prod_id,
    prod_job_id,
    wms_job_id,
    workflowStatus,
    stepStatus,
    step_id,
    step_number,
    step_commons,
    wf_commons,
)

# sut
from LHCbDIRAC.Workflow.Modules.ModuleBase import ModuleBase


def test__enableModule(mocker):
    mocker.patch("LHCbDIRAC.Workflow.Modules.ModuleBase.RequestValidator", side_effect=MagicMock())
    mb = ModuleBase(bkClientIn=bkc_mock, dm=dm_mock)
    mb.execute(
        prod_id,
        prod_job_id,
        wms_job_id,
        workflowStatus,
        stepStatus,
        wf_commons,
        step_commons[0],
        step_number,
        step_id,
    )
    assert mb._enableModule() is True


def test__checkLocalExistance(mocker):
    mocker.patch("LHCbDIRAC.Workflow.Modules.ModuleBase.RequestValidator", side_effect=MagicMock())
    mb = ModuleBase(bkClientIn=bkc_mock, dm=dm_mock)
    with pytest.raises(OSError):
        mb._checkLocalExistance(["aaa", "bbb"])

    with open("testFile.txt", "w"):
        res = mb._checkLocalExistance(["testFile.txt"])
        assert res == ["testFile.txt"]

        with open("testSecondFile.txt", "w"):
            res = mb._checkLocalExistance(["testFile.txt", "testSecondFile.txt"])
            assert sorted(res) == sorted(["testFile.txt", "testSecondFile.txt"])

            res = mb._checkLocalExistance(["TESTFILE.TXT", "testSecondFile.txt"])
            assert sorted(res) == sorted(["testFile.txt", "testSecondFile.txt"])
    os.remove("testFile.txt")
    os.remove("testSecondFile.txt")


candidateFiles = {
    "00012345_00012345_4.dst": {"lfn": "/lhcb/MC/2010/DST/123/123_45_4.dst", "type": "dst"},
    "00012345_00012345_2.digi": {"type": "digi"},
    "00012345_00012345_3.digi": {"type": "digi"},
    "00012345_00012345_5.AllStreams.dst": {
        "lfn": "/lhcb/MC/2010/DST/123/123_45_5.AllStreams.dst",
        "type": "allstreams.dst",
    },
    "00012345_00012345_1.sim": {"type": "sim"},
    "00038941_00000004_6.B2_D2.Strip.dst": {
        "lfn": "/lhcb/MC/2012/B2_D2.STRIP.DST/B2_D2.Strip.dst",
        "type": "B2_D2.strip.dst",
    },
    "Gauss_HIST_1.root": {"type": "GAUSSHIST"},
}

fileMasks = (
    ["dst"],
    "dst",
    ["sim"],
    ["digi"],
    ["digi", "sim"],
    "allstreams.dst",
    "B2_D2.strip.dst",
    [],
    ["B2_D2.strip.dst", "digi"],
    ["gausshist", "digi"],
)
stepMasks = (
    "",
    "5",
    "",
    ["2"],
    ["1", "3"],
    "",
    "",
    ["6"],
    [],
    ["1", "3"],
)

results = (
    {"00012345_00012345_4.dst": {"lfn": "/lhcb/MC/2010/DST/123/123_45_4.dst", "type": "dst"}},
    {},
    {"00012345_00012345_1.sim": {"type": "sim"}},
    {
        "00012345_00012345_2.digi": {"type": "digi"},
    },
    {"00012345_00012345_3.digi": {"type": "digi"}, "00012345_00012345_1.sim": {"type": "sim"}},
    {
        "00012345_00012345_5.AllStreams.dst": {
            "lfn": "/lhcb/MC/2010/DST/123/123_45_5.AllStreams.dst",
            "type": "allstreams.dst",
        }
    },
    {
        "00038941_00000004_6.B2_D2.Strip.dst": {
            "lfn": "/lhcb/MC/2012/B2_D2.STRIP.DST/B2_D2.Strip.dst",
            "type": "B2_D2.strip.dst",
        }
    },
    {
        "00038941_00000004_6.B2_D2.Strip.dst": {
            "lfn": "/lhcb/MC/2012/B2_D2.STRIP.DST/B2_D2.Strip.dst",
            "type": "B2_D2.strip.dst",
        }
    },
    {
        "00012345_00012345_2.digi": {"type": "digi"},
        "00012345_00012345_3.digi": {"type": "digi"},
        "00038941_00000004_6.B2_D2.Strip.dst": {
            "lfn": "/lhcb/MC/2012/B2_D2.STRIP.DST/B2_D2.Strip.dst",
            "type": "B2_D2.strip.dst",
        },
    },
    {"00012345_00012345_3.digi": {"type": "digi"}, "Gauss_HIST_1.root": {"type": "GAUSSHIST"}},
)

allCombinations = list(zip(fileMasks, stepMasks, results))


@pytest.mark.parametrize("fileMask, stepMask, result", allCombinations)
def test__applyMask(mocker, fileMask, stepMask, result):
    mocker.patch("LHCbDIRAC.Workflow.Modules.ModuleBase.RequestValidator", side_effect=MagicMock())
    mb = ModuleBase(bkClientIn=bkc_mock, dm=dm_mock)
    res = mb._applyMask(candidateFiles, fileMask, stepMask)
    assert res == result


def test__checkSanity(mocker):
    mocker.patch("LHCbDIRAC.Workflow.Modules.ModuleBase.RequestValidator", side_effect=MagicMock())
    mb = ModuleBase(bkClientIn=bkc_mock, dm=dm_mock)
    with pytest.raises(ValueError):
        mb._checkSanity(candidateFiles)


outputList = [
    {"outputDataType": "txt", "outputDataName": "foo_1.txt"},
    {"outputDataType": "py", "outputDataName": "bar_2.py"},
    {"outputDataType": "blah", "outputDataName": "myfoo.blah"},
]
outputLFNs = [
    "/lhcb/MC/2010/DST/00012345/0001/foo_1.txt",
    "/lhcb/MC/2010/DST/00012345/0001/bar_2.py",
    "/lhcb/user/f/fstagni/2015_06/prepend_myfoo.blah",
]

fileMasks = ["txt", ["txt", "py"], ["blah"], ["aa"], "", "", ""]
stepMasks = ["", None, None, None, "2", ["2", "3"], ["3"]]
results = [
    {"foo_1.txt": {"lfn": "/lhcb/MC/2010/DST/00012345/0001/foo_1.txt", "type": outputList[0]["outputDataType"]}},
    {
        "foo_1.txt": {"lfn": "/lhcb/MC/2010/DST/00012345/0001/foo_1.txt", "type": outputList[0]["outputDataType"]},
        "bar_2.py": {"lfn": "/lhcb/MC/2010/DST/00012345/0001/bar_2.py", "type": outputList[1]["outputDataType"]},
    },
    {"myfoo.blah": {"lfn": "/lhcb/user/f/fstagni/2015_06/prepend_myfoo.blah", "type": outputList[2]["outputDataType"]}},
    {},
    {"bar_2.py": {"lfn": "/lhcb/MC/2010/DST/00012345/0001/bar_2.py", "type": outputList[1]["outputDataType"]}},
    {"bar_2.py": {"lfn": "/lhcb/MC/2010/DST/00012345/0001/bar_2.py", "type": outputList[1]["outputDataType"]}},
    {},
]

allCombinations = list(zip(fileMasks, stepMasks, results))


@pytest.mark.parametrize("fileMask, stepMask, result", allCombinations)
def test_getCandidateFiles(mocker, fileMask, stepMask, result):
    mocker.patch("LHCbDIRAC.Workflow.Modules.ModuleBase.RequestValidator", side_effect=MagicMock())
    mb = ModuleBase(bkClientIn=bkc_mock, dm=dm_mock)

    with open("foo_1.txt", "w"):
        with open("bar_2.py", "w"):
            with open("myfoo.blah", "w"):
                res = mb.getCandidateFiles(outputList, outputLFNs, fileMask, stepMask)
                assert res == result

                with pytest.raises(ValueError):
                    mb.getCandidateFiles(
                        [
                            {"outputDataType": "txt", "outputDataName": "foo_1.txt"},
                            {"outputDataType": "py", "outputDataName": "bar_2.py"},
                            {"outputDataType": "blah", "outputDataName": "myfoo.blah"},
                        ],
                        [
                            "/lhcb/MC/2010/DST/00012345/0001/foo_1.txt",
                            "/lhcb/MC/2010/DST/00012345/0001/bar_2.py",
                            "/lhcb/user/f/fstagni/2015_06/prepend_myfoo_1.blah",
                        ],
                        "blah",
                        "",
                    )
                os.remove("foo_1.txt")
                os.remove("bar_2.py")
                os.remove("myfoo.blah")


inputDatas = ["previousStep", "previousStep", "LFN:123.raw"]
workflow_commons = [
    {
        "JobType": "User",
        "outputList": [
            {
                "stepName": "Brunel_1",
                "outputDataType": "brunelhist",
                "outputBKType": "BRUNELHIST",
                "outputDataName": "Brunel_00012345_00006789_1_Hist.root",
            },
            {
                "stepName": "Brunel_1",
                "outputDataType": "sdst",
                "outputBKType": "SDST",
                "outputDataName": "00012345_00006789_1.sdst",
            },
        ],
    },
    {
        "JobType": "User",
        "outputList": [
            {
                "stepName": "Brunel_1",
                "outputDataType": "brunelhist",
                "outputBKType": "BRUNELHIST",
                "outputDataName": "Brunel_00012345_00006789_1_Hist.root",
            },
            {"stepName": "Brunel_1", "outputDataType": "sdst", "outputBKType": "SDST", "outputDataName": "some.sdst"},
            {
                "stepName": "Brunel_1",
                "outputDataType": "sdst",
                "outputBKType": "SDST",
                "outputDataName": "00012345_00006789_1.sdst",
            },
        ],
    },
    {
        "JobType": "User",
        "outputList": [
            {
                "stepName": "Brunel_1",
                "outputDataType": "brunelhist",
                "outputBKType": "BRUNELHIST",
                "outputDataName": "Brunel_00012345_00006789_1_Hist.root",
            },
            {"stepName": "Brunel_1", "outputDataType": "sdst", "outputBKType": "SDST", "outputDataName": "some.sdst"},
            {
                "stepName": "Brunel_1",
                "outputDataType": "sdst",
                "outputBKType": "SDST",
                "outputDataName": "00012345_00006789_1.sdst",
            },
        ],
    },
]
results = [["00012345_00006789_1.sdst"], ["some.sdst", "00012345_00006789_1.sdst"], ["123.raw"]]

allCombinations = list(zip(inputDatas, workflow_commons, results))


@pytest.mark.parametrize("inputData, wf_c, result", allCombinations)
def test__determineStepInputData(mocker, inputData, wf_c, result):
    mocker.patch("LHCbDIRAC.Workflow.Modules.ModuleBase.RequestValidator", side_effect=MagicMock())
    mb = ModuleBase(bkClientIn=bkc_mock, dm=dm_mock)
    mb.stepName = "DaVinci_2"

    mb.gaudiSteps = ["Brunel_1", "DaVinci_2"]
    mb.workflow_commons = wf_c
    mb.inputDataType = "SDST"
    res = mb._determineStepInputData(inputData)
    assert res == result


@pytest.mark.parametrize("s_cs", list(step_commons))
def test__determineOutputs(mocker, s_cs):
    mocker.patch("LHCbDIRAC.Workflow.Modules.ModuleBase.RequestValidator", side_effect=MagicMock())
    mb = ModuleBase(bkClientIn=bkc_mock, dm=dm_mock)
    mb.jobType = "merge"
    mb.step_id = "00000123_00000456_1"
    mb.stepInputData = ["foo", "bar"]
    mb.step_commons = dict(s_cs)
    mb.step_commons["listoutput"] = [
        {"outputDataType": "bhadron.dst;sdst", "outputDataName": "00000123_00000456_1.bhadron.dst;sdst"}
    ]
    outF, outft, histos = mb._determineOutputs()
    assert outF == [{"outputDataType": "sdst", "outputDataName": "00000123_00000456_1.sdst", "outputBKType": "SDST"}]
    assert outft == ["sdst"]
    assert histos is False

    mb.step_commons["listoutput"] = [
        {"outputDataType": "root", "outputDataName": "00000123_00000456_1.root", "outputBKType": "ROOT"}
    ]
    outF, outft, histos = mb._determineOutputs()
    assert outF == [{"outputDataType": "root", "outputDataName": "00000123_00000456_1.root", "outputBKType": "ROOT"}]
    assert outft == ["root"]
    assert histos is False

    mb.jobType = "reco"
    mb.step_commons = s_cs
    mb.step_commons["listoutput"] = [
        {"outputDataType": "sdst", "outputDataName": "00000123_00000456_1.sdst", "outputBKType": "SDST"}
    ]
    outF, outft, histos = mb._determineOutputs()
    assert outF == [{"outputDataType": "sdst", "outputDataName": "00000123_00000456_1.sdst", "outputBKType": "SDST"}]
    assert outft == ["sdst"]
    assert histos is False


def test__findOutputs(mocker):
    mocker.patch("LHCbDIRAC.Workflow.Modules.ModuleBase.RequestValidator", side_effect=MagicMock())
    mb = ModuleBase(bkClientIn=bkc_mock, dm=dm_mock)

    with pytest.raises(IOError):
        with open("aaa.Bhadron.dst", "w"):
            with open("ccc.charm.mdst", "w"):
                with open("prova.txt", "w"):
                    stepOutput = [
                        {"outputDataType": "BHADRON.DST", "outputDataName": "aaa.bhadron.dst"},
                        {"outputDataType": "CALIBRATION.DST", "outputDataName": "bbb.calibration.dst"},
                        {"outputDataType": "CHARM.MDST", "outputDataName": "ccc.charm.mdst"},
                        {
                            "outputDataType": "CHARMCONTROL.DST",
                            "outputDataName": "00012345_00012345_2.CHARMCONTROL.DST",
                        },
                        {"outputDataType": "CHARMFULL.DST", "outputDataName": "00012345_00012345_2.CHARMFULL.DST"},
                        {"outputDataType": "LEPTONIC.MDST", "outputDataName": "00012345_00012345_2.LEPTONIC.MDST"},
                        {
                            "outputDataType": "LEPTONICFULL.DST",
                            "outputDataName": "00012345_00012345_2.LEPTONICFULL.DST",
                        },
                        {"outputDataType": "MINIBIAS.DST", "outputDataName": "00012345_00012345_2.MINIBIAS.DST"},
                        {"outputDataType": "RADIATIVE.DST", "outputDataName": "00012345_00012345_2.RADIATIVE.DST"},
                        {
                            "outputDataType": "SEMILEPTONIC.DST",
                            "outputDataName": "00012345_00012345_2.SEMILEPTONIC.DST",
                        },
                        {"outputDataType": "HIST", "outputDataName": "DaVinci_00012345_00012345_2_Hist.root"},
                    ]
                    mb._findOutputs(stepOutput)
                    os.remove("aaa.Bhadron.dst")
                    os.remove("ccc.charm.mdst")
                    os.remove("prova.txt")

    stepOutput = [{"outputDataType": "BHADRON.DST", "outputDataName": "aaa.bhadron.dst"}]
    outExp = [
        {
            "outputDataType": "bhadron.dst",
            "outputBKType": "BHADRON.DST",
            "outputDataName": "aaa.Bhadron.dst",
            "stepName": "someApp_1",
        }
    ]
    bkExp = ["BHADRON.DST"]
    mb.stepName = "someApp_1"
    out, bk = mb._findOutputs(stepOutput)
    assert out == outExp
    assert bk == bkExp


def test_getFileMetadata(mocker):
    mocker.patch("LHCbDIRAC.Workflow.Modules.ModuleBase.RequestValidator", side_effect=MagicMock())
    mb = ModuleBase(bkClientIn=bkc_mock, dm=dm_mock)

    candidateFiles = {
        "foo_1.txt": {"lfn": "/lhcb/MC/2010/DST/00012345/0001/foo_1.txt", "type": "txt", "workflowSE": "SE1"},
        "bar_2.py": {"lfn": "/lhcb/MC/2010/DST/00012345/0001/bar_2.py", "type": "py", "workflowSE": "SE2"},
    }

    expectedResult = {
        "bar_2.py": {
            "filedict": {
                "Status": "Waiting",
                "LFN": "/lhcb/MC/2010/DST/00012345/0001/bar_2.py",
                "GUID": "D41D8CD9-8F00-B204-E980-0998ECF8427E",
                "Checksum": "000001",
                "ChecksumType": "ADLER32",
                "Size": 0,
            },
            "lfn": "/lhcb/MC/2010/DST/00012345/0001/bar_2.py",
            "workflowSE": "SE2",
            "localpath": os.getcwd() + "/bar_2.py",
            "guid": "D41D8CD9-8F00-B204-E980-0998ECF8427E",
            "type": "py",
        },
        "foo_1.txt": {
            "filedict": {
                "Status": "Waiting",
                "LFN": "/lhcb/MC/2010/DST/00012345/0001/foo_1.txt",
                "GUID": "D41D8CD9-8F00-B204-E980-0998ECF8427E",
                "Checksum": "000001",
                "ChecksumType": "ADLER32",
                "Size": 0,
            },
            "lfn": "/lhcb/MC/2010/DST/00012345/0001/foo_1.txt",
            "workflowSE": "SE1",
            "localpath": os.getcwd() + "/foo_1.txt",
            "guid": "D41D8CD9-8F00-B204-E980-0998ECF8427E",
            "type": "txt",
        },
    }

    with open("foo_1.txt", "w"):
        with open("bar_2.py", "w"):
            result = mb.getFileMetadata(candidateFiles)
            assert result == expectedResult
            os.remove("foo_1.txt")
            os.remove("bar_2.py")
