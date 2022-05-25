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
"""Unit tests for Workflow Module UploadMC."""
# pylint: disable=protected-access, missing-docstring, invalid-name, line-too-long
from itertools import product

from mock import MagicMock
import pytest

from LHCbDIRAC.Workflow.Modules.mock_Commons import wf_commons, step_commons

# sut
from LHCbDIRAC.Workflow.Modules.UploadMC import UploadMC


def test_instantiation(mocker):
    mocker.patch("LHCbDIRAC.Workflow.Modules.ModuleBase.RequestValidator", side_effect=MagicMock())
    uploadMC = UploadMC()
    assert isinstance(uploadMC, UploadMC)


def test__resolveInputVariables(mocker):
    mocker.patch("LHCbDIRAC.Workflow.Modules.ModuleBase.RequestValidator", side_effect=MagicMock())
    mocker.patch("LHCbDIRAC.Workflow.Modules.ModuleBase.FileReport", side_effect=MagicMock())
    uploadMC = UploadMC()
    uploadMC.workflow_commons = {}
    uploadMC.step_commons = {}
    uploadMC._resolveInputVariables()


allCombinations = list(product(wf_commons + [{}], step_commons + [{}]))


@pytest.mark.parametrize("wf_common, s_common", allCombinations)
def test_execute(mocker, wf_common, s_common):
    mocker.patch("LHCbDIRAC.Workflow.Modules.ModuleBase.RequestValidator", side_effect=MagicMock())
    mocker.patch("LHCbDIRAC.Workflow.Modules.ModuleBase.FileReport", side_effect=MagicMock())
    uploadMC = UploadMC()
    uploadMC.STEP_NUMBER = "1"
    uploadMC.workflow_commons = wf_common
    uploadMC.step_commons = s_common
    uploadMC.execute()
