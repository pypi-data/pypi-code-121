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
"""Unit tests for Workflow Module GaudiApplication."""
import six

import copy
import os

from mock import MagicMock
import pytest

pytestmark = pytest.mark.skipif(six.PY2, reason="This test only supports Python 3")

from DIRAC.DataManagementSystem.Client.test.mock_DM import dm_mock
from LHCbDIRAC.BookkeepingSystem.Client.test.mock_BookkeepingClient import bkc_mock
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


@pytest.fixture
def rmFiles():
    yield
    try:
        os.remove("gaudi_extra_options.py")
    except OSError:
        pass


def test_execute(mocker, rmFiles):
    from LHCbDIRAC.Workflow.Modules.GaudiApplication import GaudiApplication

    mocker.patch("LHCbDIRAC.Core.Utilities.RunApplication.RunApplication", side_effect=MagicMock())
    mocker.patch("LHCbDIRAC.Workflow.Modules.GaudiApplication.ModuleBase._manageAppOutput", side_effect=MagicMock())
    mocker.patch("LHCbDIRAC.Workflow.Modules.GaudiApplication.gConfig", side_effect=MagicMock())
    mocker.patch("LHCbDIRAC.Workflow.Modules.ModuleBase.RequestValidator", side_effect=MagicMock())

    ga = GaudiApplication(bkClient=bkc_mock, dm=dm_mock)
    ga.siteName = "LCG.PIPPO.org"
    ga.jobType = "user"

    # no errors, no input data
    for wf_cs in copy.deepcopy(wf_commons):
        for s_cs in step_commons:
            assert (
                ga.execute(
                    prod_id, prod_job_id, wms_job_id, workflowStatus, stepStatus, wf_cs, s_cs, step_number, step_id
                )["OK"]
                is True
            )
