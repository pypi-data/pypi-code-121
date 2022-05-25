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
"""Test class for BookkeepingReport."""
# pylint: disable=missing-docstring, invalid-name, protected-access
import importlib
from itertools import product

import pytest
from mock import MagicMock

# mocks
from DIRAC.DataManagementSystem.Client.test.mock_DM import dm_mock
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
)
from LHCbDIRAC.BookkeepingSystem.Client.test.mock_BookkeepingClient import bkc_mock

# sut
from LHCbDIRAC.Workflow.Modules.BookkeepingReport import BookkeepingReport


rv_m = importlib.import_module("LHCbDIRAC.Workflow.Modules.ModuleBase")
rv_m.RequestValidator = MagicMock()

mock_pxc = MagicMock()
mock_pxc.return_value = dict()
p_m = importlib.import_module("LHCbDIRAC.Resources.Catalog.PoolXMLFile")
p_m.getOutputType = mock_pxc

bkr = BookkeepingReport(bkClient=bkc_mock, dm=dm_mock)

allCombinations = list(product(wf_commons, step_commons))


@pytest.mark.parametrize("wf_cs, s_cs", allCombinations)
def test_execute(wf_cs, s_cs):
    assert (
        bkr.execute(
            prod_id, prod_job_id, wms_job_id, workflowStatus, stepStatus, wf_cs, s_cs, step_number, step_id, False
        )["OK"]
        is True
    )


@pytest.mark.parametrize(
    "output, outputType, xf_o_r, expected",
    [
        ("/this/is/an/output.txt", "txt", {"/this/is/an/output.txt": {}}, ("{}", "/this/is/an/output.txt")),
        ("/this/is/an/output.hist", "hist", {"/this/is/an/output.txt": {}}, ("Unknown", "/this/is/an/output.hist")),
        ("/this/is/an/output.txt", "txt", {"/this/is/an/OutPut.txt": {}}, ("{}", "/this/is/an/OutPut.txt")),
    ],
)
def test__getFileStatsFromXMLSummary(output, outputType, xf_o_r, expected):
    mock_xfo = MagicMock()
    mock_xfo.outputsEvents = xf_o_r
    bkr.xf_o = mock_xfo

    res = bkr._getFileStatsFromXMLSummary(output, outputType)
    assert res == expected
