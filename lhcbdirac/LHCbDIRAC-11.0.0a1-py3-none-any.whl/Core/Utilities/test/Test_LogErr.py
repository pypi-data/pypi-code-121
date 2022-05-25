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
# Test for LogErr.py

import json
import ast
import os
import pytest

# sut
from LHCbDIRAC.Core.Utilities.LogErr import createJSONtable


# Define test data
jsonDataMultiple = [
    {
        "G4Exception": [
            {"runnr": "", "eventnr": ""},
            {"runnr": "", "eventnr": ""},
            {"runnr": "", "eventnr": ""},
            {"runnr": "", "eventnr": ""},
            {"runnr": "", "eventnr": ""},
            {"runnr": "", "eventnr": ""},
            {"runnr": "", "eventnr": ""},
            {"runnr": "", "eventnr": ""},
            {"runnr": "", "eventnr": ""},
            {"runnr": "", "eventnr": ""},
        ]
    },
    {"ERROR Gap not found!": [{"runnr": "  Run 133703", "eventnr": "Evt 29"}]},
    {
        "The signal decay mode is not defined in the main DECAY.DEC table": [
            {"runnr": "  Run 133703", "eventnr": "Evt 29"},
            {"runnr": "  Run 123", "eventnr": "Evt 30"},
        ]
    },
    {
        "G4Exception : StuckTrack": [
            {"runnr": "  Run 133703", "eventnr": "Evt 29"},
            {"runnr": "  Run 123", "eventnr": "Evt 30"},
            {"runnr": "  Run 1234", "eventnr": "Evt 31"},
        ]
    },
    {
        "G4Exception : 001": [
            {"runnr": "  Run 133703", "eventnr": "Evt 29"},
            {"runnr": "  Run 123", "eventnr": "Evt 30"},
            {"runnr": "  Run 1234", "eventnr": "Evt 31"},
        ]
    },
]

expectedMultiple = json.dumps(
    {
        "ERROR Gap not found!": 1,
        "wmsID": "5",
        "ProductionID": "4",
        "JobID": "3",
        "G4Exception": 10,
        "The signal decay mode is not defined in the main DECAY.DEC table": 2,
        "G4Exception : StuckTrack": 3,
        "G4Exception : 001": 3,
    },
    indent=2,
)


jsonDataSingle = [
    {
        "G4Exception : InvalidSetup": [
            {"runnr": "", "eventnr": ""},
            {"runnr": "", "eventnr": ""},
            {"runnr": "", "eventnr": ""},
            {"runnr": "", "eventnr": ""},
            {"runnr": "", "eventnr": ""},
            {"runnr": "", "eventnr": ""},
            {"runnr": "", "eventnr": ""},
            {"runnr": "", "eventnr": ""},
            {"runnr": "", "eventnr": ""},
            {"runnr": "", "eventnr": ""},
        ]
    }
]

expectedSingle = json.dumps(
    {"G4Exception : InvalidSetup": 10, "wmsID": "5", "ProductionID": "4", "JobID": "3"}, indent=2
)

jsonDataEmpty = []

expectedEmpty = json.dumps({"wmsID": "5", "ProductionID": "4", "JobID": "3"}, indent=2)


name = "test_createJSONtable.json"


@pytest.mark.parametrize(
    "input, expected",
    [(jsonDataMultiple, expectedMultiple), (jsonDataSingle, expectedSingle), (jsonDataEmpty, expectedEmpty)],
)
def test_createJson(input, expected):
    createJSONtable(input, name, "3", "4", "5")
    with open(name, "r") as f:
        fileOutput = f.read()

    # Convert to dict()
    fileOutput = ast.literal_eval(fileOutput)
    expected = ast.literal_eval(expected)

    assert fileOutput == expected
    os.remove(name)
