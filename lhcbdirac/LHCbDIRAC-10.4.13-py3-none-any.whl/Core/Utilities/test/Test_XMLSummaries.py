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
"""Unittest for:
LHCbDIRAC.HCbDIRAC.Core.Utilities.XMLSummaries."""
import pytest
from LHCbDIRAC.Core.Utilities.XMLSummaries import xmltojsonCat1, xmltojsonCat2, xmltojsonCat3, difisnotnull, ranges


lCategory1 = [
    {"@name": "MCVeloHitPacker/# PackedData", "#text": "244708"},
    {"@name": "MCPuVetoHitPacker/# PackedData", "#text": "9800"},
    {"@name": "MCTTHitPacker/# PackedData", "#text": "73624"},
    {"@name": "MCITHitPacker/# PackedData", "#text": "86436"},
]
dictCategory1 = {
    "MCITHitPacker": {"PackedData": 86436},
    "MCPuVetoHitPacker": {"PackedData": 9800},
    "MCTTHitPacker": {"PackedData": 73624},
    "MCVeloHitPacker": {"PackedData": 244708},
}


@pytest.mark.parametrize("test_input,expected", [(lCategory1, dictCategory1), ([], {})])
def test_xmltojsonCat1(test_input, expected):
    assert xmltojsonCat1(test_input) == expected


lCategory2 = [
    {"@name": "TTHitMonitor/DeltaRay", "#text": "10184"},
    {"@name": "TTHitMonitor/betaGamma", "#text": "72641099"},
    {"@name": "TTHitMonitor/numberHits", "#text": "73624"},
    {"@name": "ITHitMonitor/DeltaRay", "#text": "4208"},
    {"@name": "ITHitMonitor/betaGamma", "#text": "224730238"},
    {"@name": "ITHitMonitor/numberHits", "#text": "86436"},
    {"@name": "OTHitMonitor/DeltaRay", "#text": "16893"},
    {"@name": "OTHitMonitor/betaGamma", "#text": "338754733"},
    {"@name": "OTHitMonitor/numberHits", "#text": "253748"},
]

dictCategory2 = {
    "ITHitMonitor": {"DeltaRay": 4208, "betaGamma": 224730238, "numberHits": 86436},
    "OTHitMonitor": {"DeltaRay": 16893, "betaGamma": 338754733, "numberHits": 253748},
    "TTHitMonitor": {"DeltaRay": 10184, "betaGamma": 72641099, "numberHits": 73624},
}


@pytest.mark.parametrize("test_input,expected", [(lCategory2, dictCategory2), ([], {})])
def test_xmltojsonCat2(test_input, expected):
    assert xmltojsonCat2(test_input) == expected


lCategory3 = [
    {"@name": "CheckPuVetoHits/Diff.    - Displacement x", "#text": "0"},
    {"@name": "CheckPuVetoHits/Diff.    - Displacement y", "#text": "0"},
    {"@name": "CheckPuVetoHits/Diff.    - Displacement z", "#text": "0"},
    {"@name": "CheckPuVetoHits/Diff.    - Energy", "#text": "0"},
    {"@name": "CheckPuVetoHits/Diff.    - Entry Point x", "#text": "0"},
    {"@name": "CheckPuVetoHits/Diff.    - Entry Point y", "#text": "0"},
    {"@name": "CheckPuVetoHits/Diff.    - Entry Point z", "#text": "0"},
    {"@name": "CheckPuVetoHits/Diff.    - Parent |P|", "#text": "3"},
    {"@name": "CheckPuVetoHits/Diff.    - TOF", "#text": "0"},
]
dictCategory3 = {
    "CheckPuVetoHits/Diff.": {
        "Displacement": {"x": 0, "y": 0, "z": 0},
        "Energy": 0,
        "Entry Point": {"x": 0, "y": 0, "z": 0},
        "Parent |P|": 3,
        "TOF": 0,
    }
}


@pytest.mark.parametrize("test_input,expected", [(lCategory3, dictCategory3), ([], {})])
def test_xmltojsonCat3(test_input, expected):
    assert xmltojsonCat3(test_input) == expected


dictCategory3NotNull = {
    "CheckPuVetoHits/Diff.": {
        "Displacement": {"x": 0, "y": 0, "z": 0},
        "Energy": 0,
        "Entry Point": {"x": 0, "y": 0, "z": 0},
        "Parent |P|": 3,
        "TOF": 0,
    }
}

dictCategory3Null = {
    "CheckRichOpPhot/Diff.": {
        "Cherenkov": {"Phi": 0, "Theta": 0},
        "Emission Point": {"x": 0, "y": 0, "z": 0},
        "Energy": 0,
        "HPD In. Point": {"x": 0, "y": 0, "z": 0},
        "HPD QW Point": {"x": 0, "y": 0, "z": 0},
        "Parent Momentum": {"x": 0, "y": 0, "z": 0},
        "Prim. Mirr.": {"x": 0, "y": 0, "z": 0},
        "Sec. Mirr.": {"x": 0, "y": 0, "z": 0},
    }
}


@pytest.mark.parametrize("test_input,expected", [(dictCategory3NotNull, True), (dictCategory3Null, False)])
def test_difisnotnull(test_input, expected):
    assert difisnotnull(test_input) == expected


def test_ranges():
    testList = [0, 1, 2, 3, 4, 5, 6, 7, 8, 10, 11, 12, 13, 14, 20, 21, 22, 23]

    assert ranges(testList) == [0, 8, 10, 14, 20, 23]
