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
LHCbDIRAC.HCbDIRAC.Core.Utilities.GeneratorLog"""
import pytest
from LHCbDIRAC.Core.Utilities.GeneratorLog import (
    counterJson,
    efficiencyJson,
    fractionJson,
    crossSectionJson,
    methodGeneratorJson,
)  # noqa


listCounters = [
    {"@name": "all events (including empty events)", "value": "556"},
    {"@name": "events with 0 interaction", "value": "51"},
    {"@name": "generated events", "value": "505"},
    {"@name": "generated interactions", "value": "1395"},
    {"@name": "generated interactions with >= 1b", "value": "7"},
    {"@name": "generated interactions with >= 3b", "value": "1"},
    {"@name": "generated interactions with 1 prompt B", "value": "0"},
    {"@name": "generated interactions with >= 1c", "value": "91"},
    {"@name": "generated interactions with >= 3c", "value": "10"},
    {"@name": "generated interactions with >= prompt C", "value": "2"},
    {"@name": "generated interactions with b and c", "value": "1"},
    {"@name": "accepted events", "value": "1"},
]

dictCounters = {
    "accepted events": 1,
    "all events (including empty events)": 556,
    "events with 0 interaction": 51,
    "generated events": 505,
    "generated interactions": 1395,
    "generated interactions with 1 prompt B": 0,
    "generated interactions with >= 1b": 7,
    "generated interactions with >= 1c": 91,
    "generated interactions with >= 3b": 1,
    "generated interactions with >= 3c": 10,
    "generated interactions with >= prompt C": 2,
    "generated interactions with b and c": 1,
}


@pytest.mark.parametrize("test_input,expected", [(listCounters, dictCounters), ([], {})])
def test_counterJson(test_input, expected):
    assert counterJson(test_input) == expected


listEfficiencies = [
    {"@name": "generator level cut", "after": "1", "before": "4", "error": "0.21651", "value": "0.25"},
    {"@name": "generator particle level cut", "after": "0", "before": "1", "error": "0", "value": "0"},
    {"@name": "generator anti-particle level cut", "after": "1", "before": "3", "error": "0.27217", "value": "0.33333"},
]

dictEfficiencies = {
    "generator anti-particle level cut": {"after": 1, "before": 3, "error": 0.27217, "value": 0.33333},
    "generator level cut": {"after": 1, "before": 4, "error": 0.21651, "value": 0.25},
    "generator particle level cut": {"after": 0, "before": 1, "error": 0.0, "value": 0.0},
}


@pytest.mark.parametrize("test_input,expected", [(listEfficiencies, dictEfficiencies), ([], {})])
def test_efficiencyJson(test_input, expected):
    assert efficiencyJson(test_input) == expected


listFractions = [
    {"@name": "accepted B+", "error": "0.35355", "number": "1", "value": "0.5"},
    {"@name": "accepted B-", "error": "0", "number": "1", "value": "1"},
    {"@name": "accepted B0", "error": "0.35355", "number": "1", "value": "0.5"},
]

dictFractions = {
    "accepted B+": {"error": 0.35355, "number": 1, "value": 0.5},
    "accepted B-": {"error": 0.0, "number": 1, "value": 1.0},
    "accepted B0": {"error": 0.35355, "number": 1, "value": 0.5},
}


@pytest.mark.parametrize("test_input,expected", [(listFractions, dictFractions), ([], {})])
def test_fractionJson(test_input, expected):
    assert fractionJson(test_input) == expected


listCrossSections = [
    {"@id": "101", "description": '"non-diffractive"', "generated": "776", "value": "52.116"},
    {"@id": "102", "description": '"A B -> A B elastic"', "generated": "300", "value": "19.892"},
    {"@id": "103", "description": '"A B -> X B single diffractive"', "generated": "120", "value": "6.24"},
]

dictCrossSections = {
    "A B -> A B elastic": {"ID": 102, "generated": 300, "value": 19.892},
    "A B -> X B single diffractive": {"ID": 103, "generated": 120, "value": 6.24},
    "non-diffractive": {"ID": 101, "generated": 776, "value": 52.116},
}


@pytest.mark.parametrize("test_input,expected", [(listCrossSections, dictCrossSections), ([], {})])
def test_crossSectionJson(test_input, expected):
    assert crossSectionJson(test_input) == expected


listMethods = ["GenerationSignal.SignalPlain", "Generation.SignalRepeatedHadronization"]
listGenerators = ["Redecay", "Pythia8"]
dictMethodsGenerators = {"GenerationSignal.SignalPlain": "Redecay", "Generation.SignalRepeatedHadronization": "Pythia8"}

Method = "Generation.SignalRepeatedHadronization"
Generator = "Pythia8"
dictMethodGenerator = {"Generation.SignalRepeatedHadronization": "Pythia8"}


@pytest.mark.parametrize(
    "test_input1,test_input2,test_input3,expected",
    [(listMethods, listGenerators, 2, dictMethodsGenerators), (Method, Generator, 1, dictMethodGenerator)],  # noqa
)
def test_methodGeneratorJson(test_input1, test_input2, test_input3, expected):
    assert methodGeneratorJson(test_input1, test_input2, test_input3) == expected
