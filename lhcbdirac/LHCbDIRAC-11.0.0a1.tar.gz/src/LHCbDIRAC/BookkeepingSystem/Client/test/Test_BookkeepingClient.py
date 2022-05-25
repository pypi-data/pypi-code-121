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
""" pytest for BookkeepingClient
"""
# pylint: disable=protected-access,missing-docstring,invalid-name

import pytest
from mock import MagicMock

# sut
from LHCbDIRAC.BookkeepingSystem.Client.BookkeepingClient import BookkeepingClient

bk = BookkeepingClient()

# mocks
mockRPC = MagicMock()
mockTC = MagicMock()
mockPR = MagicMock()

# test data
Step1 = ("gauss", "Gauss", "v1r1", "/some/gauss/option/files", "gauss-dddb_1", "gauss-conddb_1", None, 1, "Y")
Step2 = ("gauss", "Gauss", "v1r1", "/some/gauss/option/files", "gauss-dddb_2", "gauss-conddb_2", None, 2, "Y")
Step3 = ("gauss", "Gauss", "v1r1", "/some/gauss/option/files", "fromPreviousStep", "fromPreviousStep", None, 3, "Y")
Step3Corr_1 = ("gauss", "Gauss", "v1r1", "/some/gauss/option/files", "gauss-dddb_1", "gauss-conddb_1", None, 3, "Y")
Step3Corr_2 = ("gauss", "Gauss", "v1r1", "/some/gauss/option/files", "gauss-dddb_2", "gauss-conddb_2", None, 3, "Y")
Step4 = ("gauss", "Gauss", "v1r1", "/some/gauss/option/files", "fromPreviousStep", "fromPreviousStep", None, 4, "Y")
Step4Corr_1 = ("gauss", "Gauss", "v1r1", "/some/gauss/option/files", "gauss-dddb_1", "gauss-conddb_1", None, 4, "Y")
Step4Corr_2 = ("gauss", "Gauss", "v1r1", "/some/gauss/option/files", "gauss-dddb_2", "gauss-conddb_2", None, 4, "Y")


# Actual tests


@pytest.mark.parametrize(
    "mockTCResponse, mockPRResponse, expected, expectedRes",
    [
        ({"OK": False, "Message": "bof"}, {}, False, None),
        ({"OK": True, "Value": {"Status": "Archived"}}, {}, False, None),
        ({"OK": True, "Value": {"RequestID": 1, "Status": "Archived"}}, {"OK": False, "Message": "bif"}, False, None),
        ({"OK": True, "Value": {"RequestID": 1, "Status": "Archived"}}, {"OK": True, "Value": [1]}, True, []),
        ({"OK": True, "Value": {"RequestID": 1, "Status": "Archived"}}, {"OK": True, "Value": [2, 1]}, True, [2]),
        ({"OK": True, "Value": {"RequestID": 1, "Status": "Archived"}}, {"OK": True, "Value": [3, 2, 1]}, True, [2, 3]),
        ({"OK": True, "Value": {"RequestID": 1, "Status": "Archived"}}, {"OK": True, "Value": [3, 1, 2]}, True, [3]),
        (
            {"OK": True, "Value": {"RequestID": 1, "Status": "Archived"}},
            {"OK": True, "Value": [4, 3, 1, 2]},
            True,
            [3, 4],
        ),
        (
            {"OK": True, "Value": {"RequestID": 1, "Status": "Cleaned"}},
            {"OK": True, "Value": [4, 3, 1, 2]},
            False,
            None,
        ),
    ],
)
def test__getPreviousProductions(mocker, mockTCResponse, mockPRResponse, expected, expectedRes):
    mocker.patch("LHCbDIRAC.BookkeepingSystem.Client.BookkeepingClient.TransformationClient", return_value=mockTC)
    mocker.patch("LHCbDIRAC.BookkeepingSystem.Client.BookkeepingClient.ProductionRequestClient", return_value=mockPR)

    mockTC.getTransformation.return_value = mockTCResponse
    mockPR.getProductionList.return_value = mockPRResponse

    res = bk._getPreviousProductions(1)
    assert res["OK"] is expected
    if res["OK"]:
        assert res["Value"] == expectedRes


@pytest.mark.parametrize(
    "steps, expected",
    [
        ([], []),
        ([Step1], [Step1]),
        ([Step1, Step2], [Step1, Step2]),
        ([Step1, Step2, Step3], [Step1, Step2, Step3Corr_2]),
        ([Step1, Step2, Step3, Step4], [Step1, Step2, Step3Corr_2, Step4Corr_2]),
        ([Step1, Step3, Step2, Step4], [Step1, Step3Corr_1, Step2, Step4Corr_2]),
        ([Step1, Step4, Step3, Step2], [Step1, Step4Corr_1, Step3Corr_1, Step2]),
        ([Step3, Step4, Step2, Step1], [Step3, Step4, Step2, Step1]),
        ([Step3], [Step3]),
    ],
)
def test__resolveProductionSteps(steps, expected):
    res = bk._resolveProductionSteps(steps)
    assert res == expected


@pytest.mark.parametrize(
    "mockRPCResponse, mockTCResponse, mockPRResponse, expected, expectedRes",
    [
        ({"OK": False, "Message": "bif"}, {}, {}, False, {}),
        ({"OK": True, "Value": []}, {}, {}, False, {}),
        ({"OK": True, "Value": [Step1]}, {}, {}, True, [Step1]),
        ({"OK": True, "Value": [Step1, Step2]}, {}, {}, True, [Step1, Step2]),
        ({"OK": True, "Value": [Step1, Step3]}, {}, {}, True, [Step1, Step3Corr_1]),
        ({"OK": True, "Value": [Step1, Step3, Step4]}, {}, {}, True, [Step1, Step3Corr_1, Step4Corr_1]),
        (
            {"OK": True, "Value": [Step3]},
            {"OK": True, "Value": {"RequestID": 1, "Status": "Archived"}},
            {"OK": True, "Value": [2, 1]},
            True,
            [Step3],
        ),
        (
            {"OK": True, "Value": [Step3, Step4]},
            {"OK": True, "Value": {"RequestID": 1, "Status": "Archived"}},
            {"OK": True, "Value": [3, 2, 1]},
            True,
            [Step3, Step4],
        ),
    ],
)
def test_getSteps(mocker, mockRPCResponse, mockTCResponse, mockPRResponse, expected, expectedRes):
    mocker.patch("LHCbDIRAC.BookkeepingSystem.Client.BookkeepingClient.Client._getRPC", return_value=mockRPC)
    mocker.patch("LHCbDIRAC.BookkeepingSystem.Client.BookkeepingClient.TransformationClient", return_value=mockTC)
    mocker.patch("LHCbDIRAC.BookkeepingSystem.Client.BookkeepingClient.ProductionRequestClient", return_value=mockPR)

    mockRPC.getSteps.return_value = mockRPCResponse
    mockTC.getTransformation.return_value = mockTCResponse
    mockPR.getProductionList.return_value = mockPRResponse

    res = bk.getSteps(1)
    assert res["OK"] is expected
    if res["OK"]:
        assert res["Value"] == expectedRes
