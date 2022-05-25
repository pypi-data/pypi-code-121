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
"""Test of the ProductionRequest and Production modules."""
import pytest

from LHCbDIRAC.ProductionManagementSystem.Client.Production import Production

# Production.py
prod = Production()


@pytest.mark.parametrize(
    "input, expected",
    [
        (["T1", "T2"], [{"outputDataType": "t1"}, {"outputDataType": "t2"}]),
        (["T1", "HIST"], [{"outputDataType": "t1"}, {"outputDataType": "hist"}]),
    ],
)
def test__constructOutputFilesList(input, expected):
    res = prod._constructOutputFilesList(input)
    assert res == expected
