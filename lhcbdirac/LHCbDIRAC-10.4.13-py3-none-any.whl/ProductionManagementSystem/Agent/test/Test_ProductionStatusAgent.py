###############################################################################
# (c) Copyright 2021 CERN for the benefit of the LHCb Collaboration           #
#                                                                             #
# This software is distributed under the terms of the GNU General Public      #
# Licence version 3 (GPL Version 3), copied verbatim in the file "LICENSE".   #
#                                                                             #
# In applying this licence, CERN does not waive the privileges and immunities #
# granted to it by virtue of its status as an Intergovernmental Organization  #
# or submit itself to any jurisdiction.                                       #
###############################################################################
from copy import deepcopy

import pytest

import DIRAC
from DIRAC.Core.Base.AgentModule import AgentModule
from LHCbDIRAC.ProductionManagementSystem.Agent import ProductionStatusAgent as PSAModule
from LHCbDIRAC.ProductionManagementSystem.Agent.ProductionStatusAgent import ProductionStatusAgent


@pytest.fixture()
def psa(monkeypatch):
    monkeypatch.setattr(AgentModule, "__init__", lambda *a, **kw: None)
    gDoRealUpdate = PSAModule.gDoRealUpdate
    gDoRealTracking = PSAModule.gDoRealTracking
    PSAModule.gDoRealUpdate = False
    PSAModule.gDoRealTracking = False
    psa = ProductionStatusAgent(
        "ProductionManagement/ProductionStatusAgent",
        "ProductionManagement/ProductionStatusAgent",
    )
    psa.log = DIRAC.gLogger
    yield psa
    PSAModule.gDoRealUpdate = gDoRealUpdate
    PSAModule.gDoRealTracking = gDoRealTracking


anaProdBase = {
    -86392: {
        "type": "AnalysisProduction",
        "bkTotal": 900,
        "isDone": False,
        "isFinished": False,
        "master": 0,
        "prTotal": 475522154,
        "prods": {
            -139165: {
                "Events": 0,
                "Used": 0,
                "filesMaxReset": 0,
                "filesProcessed": 12387,
                "filesTotal": 12387,
                "filesUnused": 0,
                "hasActiveInput": False,
                "inputIDs": [-75559, -75557, -79436, -77434],
                "isIdle": "Yes",
                "isProcIdle": "Yes",
                "isSimulation": False,
                "state": "Active",
            },
            -139166: {
                "Events": 900,
                "Used": 1,
                "filesMaxReset": 0,
                "filesProcessed": 900,
                "filesTotal": 1275,
                "filesUnused": 375,
                "hasActiveInput": True,
                "inputIDs": [-139165],
                "isIdle": "No",
                "isProcIdle": "No",
                "isSimulation": False,
                "state": "Active",
            },
        },
    }
}

statesTestCases = []
# Do nothing
statesTestCases += [
    (
        {
            -85397: {
                "type": "Simulation",
                "master": -85318,
                "bkTotal": 249822,
                "prTotal": 250000,
                "isDone": False,
                "prods": {
                    -138943: {
                        "Events": 260179,
                        "Used": 0,
                        "state": "Active",
                        "isIdle": "Yes",
                        "isProcIdle": "Yes",
                        "isSimulation": True,
                        "filesTotal": 0,
                        "filesProcessed": 0,
                        "filesUnused": 0,
                        "filesMaxReset": 0,
                    },
                    -138944: {
                        "Events": 249822,
                        "Used": 1,
                        "state": "Active",
                        "isIdle": "No",
                        "isProcIdle": "No",
                        "isSimulation": False,
                        "filesTotal": 1177,
                        "filesProcessed": 1132,
                        "filesUnused": 45,
                        "filesMaxReset": 0,
                    },
                },
                "isFinished": False,
            }
        },
        {},
        [],
    ),
]

# --------------------
# Analysis Productions
# --------------------
# 1a. Active with all files processed goes to Idle
statesTestCases += [
    (
        deepcopy(anaProdBase),
        {-139165: {"from": "Active", "to": "Idle"}},
        [],
    )
]
# 1b. Active with all files processed except those in MaxReset goes to Idle
statesTestCases += [
    (
        deepcopy(anaProdBase),
        {-139165: {"from": "Active", "to": "Idle"}},
        [],
    )
]
statesTestCases[-1][0][-86392]["prods"][-139165]["filesMaxReset"] = 1
statesTestCases[-1][0][-86392]["prods"][-139165]["filesProcessed"] -= 1

# 2a. Idle with all files processed goes to Completed
statesTestCases += [
    (
        deepcopy(anaProdBase),
        {-139165: {"from": "Idle", "to": "Completed"}},
        [],
    )
]
statesTestCases[-1][0][-86392]["prods"][-139165]["state"] = "Idle"
# 2b. Idle with some files in MaxReset does nothing
statesTestCases += [(deepcopy(anaProdBase), {}, [])]
statesTestCases[-1][0][-86392]["prods"][-139165]["state"] = "Idle"
statesTestCases[-1][0][-86392]["prods"][-139165]["filesMaxReset"] = 1
statesTestCases[-1][0][-86392]["prods"][-139165]["filesProcessed"] -= 1

# 3a. When the first transformation is done the second will flushed if all files are proccessed
statesTestCases += [
    (
        deepcopy(anaProdBase),
        {-139166: {"from": "Active", "to": "Flush"}},
        [],
    )
]
statesTestCases[-1][0][-86392]["prods"][-139165]["state"] = "Finished"
statesTestCases[-1][0][-86392]["prods"][-139166]["hasActiveInput"] = False
# 3b. When the first transformation is done the second will not flushed if some files are still processing
statesTestCases += [(deepcopy(anaProdBase), {}, [])]
statesTestCases[-1][0][-86392]["prods"][-139165]["state"] = "Finished"
statesTestCases[-1][0][-86392]["prods"][-139166]["hasActiveInput"] = False
statesTestCases[-1][0][-86392]["prods"][-139166]["filesUnused"] -= 1
# 3c. When the first transformation is done the second will not flushed if some files are in maxReset
statesTestCases += [(deepcopy(anaProdBase), {}, [])]
statesTestCases[-1][0][-86392]["prods"][-139165]["state"] = "Finished"
statesTestCases[-1][0][-86392]["prods"][-139166]["hasActiveInput"] = False
statesTestCases[-1][0][-86392]["prods"][-139166]["filesMaxReset"] = 1
statesTestCases[-1][0][-86392]["prods"][-139166]["filesUnused"] -= 1

anaProdBaseFinished = deepcopy(anaProdBase)
anaProdBaseFinished[-86392]["prods"][-139165]["state"] = "Finished"
anaProdBaseFinished[-86392]["prods"][-139166]["hasActiveInput"] = False
anaProdBaseFinished[-86392]["prods"][-139166]["isIdle"] = "Yes"
anaProdBaseFinished[-86392]["prods"][-139166]["filesUnused"] = 0
filesTotal = anaProdBaseFinished[-86392]["prods"][-139166]["filesTotal"]
anaProdBaseFinished[-86392]["prods"][-139166]["filesProcessed"] = filesTotal
# 4a. When both second transformation has processed all files it moves to Idle
statesTestCases += [
    (
        deepcopy(anaProdBaseFinished),
        {-139166: {"from": "Active", "to": "Idle"}},
        [],
    )
]
# 4b. It then moves to ValidatingOutput
statesTestCases += [
    (
        deepcopy(anaProdBaseFinished),
        {-139166: {"from": "Idle", "to": "ValidatingOutput"}},
        [],
    )
]
statesTestCases[-1][0][-86392]["prods"][-139166]["state"] = "Idle"
# 4c. It then stays in ValidatingOutput until another agent handles it
statesTestCases += [(deepcopy(anaProdBaseFinished), {}, [])]
statesTestCases[-1][0][-86392]["prods"][-139166]["state"] = "ValidatingOutput"
# 4c. After validation it then moves from ValidatedOutput to Completed
statesTestCases += [
    (
        deepcopy(anaProdBaseFinished),
        {-139166: {"from": "ValidatedOutput", "to": "Completed"}},
        [],
    )
]
statesTestCases[-1][0][-86392]["prods"][-139166]["state"] = "ValidatedOutput"
# 4c. The production request is then marked as Done
statesTestCases += [(deepcopy(anaProdBaseFinished), {}, [-86392])]
statesTestCases[-1][0][-86392]["prods"][-139166]["state"] = "Finished"
# 4d. When both second transformation has processed all files it moves to Idle if the input is still Active
statesTestCases += [
    (
        deepcopy(anaProdBaseFinished),
        {-139166: {"from": "Active", "to": "Idle"}},
        [],
    )
]
statesTestCases[-1][0][-86392]["prods"][-139165]["state"] = "Idle"
statesTestCases[-1][0][-86392]["prods"][-139165]["hasActiveInput"] = True
statesTestCases[-1][0][-86392]["prods"][-139166]["hasActiveInput"] = True
# 4e. When both second transformation has processed all files it stays in Idle if the input is still Active
statesTestCases += [(deepcopy(anaProdBaseFinished), {}, [])]
statesTestCases[-1][0][-86392]["prods"][-139165]["state"] = "Idle"
statesTestCases[-1][0][-86392]["prods"][-139165]["hasActiveInput"] = True
statesTestCases[-1][0][-86392]["prods"][-139166]["state"] = "Idle"
statesTestCases[-1][0][-86392]["prods"][-139166]["hasActiveInput"] = True


@pytest.mark.parametrize("prSummary, expected_updatedT, expected_updatedPr", statesTestCases)
def test_stateTransitions(psa, prSummary, expected_updatedT, expected_updatedPr):
    psa.prSummary = prSummary
    updatedT, updatedPr = {}, []
    psa._applyProductionRequestsLogic(updatedT, updatedPr)
    assert updatedT == expected_updatedT
    assert updatedPr == expected_updatedPr
