###############################################################################
# (c) Copyright 2022 CERN for the benefit of the LHCb Collaboration           #
#                                                                             #
# This software is distributed under the terms of the GNU General Public      #
# Licence version 3 (GPL Version 3), copied verbatim in the file "COPYING".   #
#                                                                             #
# In applying this licence, CERN does not waive the privileges and immunities #
# granted to it by virtue of its status as an Intergovernmental Organization  #
# or submit itself to any jurisdiction.                                       #
###############################################################################
import pytest

from LHCbDIRAC.ProductionManagementSystem.Service.ProductionRequestHandler import ProductionRequestHandler


@pytest.fixture
def fakeProdRequestHandler(monkeypatch):
    monkeypatch.setattr(
        "LHCbDIRAC.ProductionManagementSystem.Service.ProductionRequestHandler.ProductionRequestHandler.__init__",
        lambda self, handlerInitDict, trid: None,
    )
    yield ProductionRequestHandler(None, None)


def test_listTemplates(fakeProdRequestHandler):
    ret = fakeProdRequestHandler.export_getProductionTemplateList()
    templates = [x["WFName"] for x in ret["Value"]]
    assert "MCSimulation_run.py" in templates
    assert "MCSimulation_simplified_run.py" in templates


def test_getTemplates(fakeProdRequestHandler):
    ret = fakeProdRequestHandler.export_getProductionTemplate("non-existant.py")
    assert not ret["OK"]
    assert "non-existant.py" in ret["Message"]
    assert "doesn't exist" in ret["Message"]

    ret = fakeProdRequestHandler.export_getProductionTemplate("MCSimulation_run.py")
    assert "pr.buildAndLaunchRequest()" in ret["Value"]
    assert "MCSimulation_run.py" in ret["Value"]

    ret = fakeProdRequestHandler.export_getProductionTemplate("MCSimulation_simplified_run.py")
    assert "pr.buildAndLaunchRequest()" in ret["Value"]
    assert "MCSimulation_simplified_run.py" in ret["Value"]
