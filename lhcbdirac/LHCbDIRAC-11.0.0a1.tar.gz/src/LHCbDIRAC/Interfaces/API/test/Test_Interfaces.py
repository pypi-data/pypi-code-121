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
"""Test Interfaces API DiracProduction."""
import os

import LHCbDIRAC.Interfaces.API.DiracProduction as moduleTested
from LHCbDIRAC.Interfaces.API.LHCbJob import LHCbJob

lj = LHCbJob()


def test_LJ_setApplication():
    open("optionsFiles", "a").close()
    res = lj.setApplication("appName", "v1r0", "optionsFiles", systemConfig="x86_64-slc6-gcc-44-opt")
    assert res["OK"] is True
    res = lj.setApplication("appName", "v1r0", "optionsFiles", systemConfig="x86_64-slc5-gcc-41-opt")
    assert res["OK"] is True
    res = lj.setApplication("appName", "v1r0", "optionsFiles", systemConfig="x86_64-slc5-gcc-43-opt")
    assert res["OK"] is True
    os.remove("optionsFiles")


def test_instantiate():
    """tests that we can instantiate one object of the tested class."""
    testClass = moduleTested.DiracProduction
    prod = testClass(1)
    assert "DiracProduction" == prod.__class__.__name__
