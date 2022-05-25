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
"""Test the logic to detect successful and failed file accesses via xroot.

We use test pool and summary xml files that correspond to 3 LFNs:
* one that worked at the first attempt
* one that worked at the second attempt
* one that did not work at all
"""
import os
from collections import defaultdict
from mock import MagicMock, patch

from LHCbDIRAC.Core.Utilities.XMLSummaries import XMLSummary
from DIRAC.Resources.Catalog.PoolXMLCatalog import PoolXMLCatalog

from LHCbDIRAC.Workflow.Modules.AnalyseFileAccess import AnalyseFileAccess

testdir = os.path.dirname(__file__)
poolFile = os.path.join(testdir, "pool_xml_catalog.xml")
summaryFile = os.path.join(testdir, "summary.xml")


@patch("LHCbDIRAC.Workflow.Modules.ModuleBase.RequestValidator", side_effect=MagicMock())
def test_analyseFileAccess(mockRequestValidator):
    """Analyze the file accesses from a pool xml catalog and the xml summary."""

    xmlCatalog = PoolXMLCatalog(xmlfile=poolFile)
    xmlSummary = XMLSummary(summaryFile)

    fileAccessAnalyzer = AnalyseFileAccess()
    accessAttempts = fileAccessAnalyzer._checkFileAccess(xmlCatalog, xmlSummary)

    # Count how many successes
    accessPerSE = defaultdict(lambda: defaultdict(int))

    for se, success in accessAttempts:
        accessPerSE[se][success] += 1

    # 'NEVERUSED-DST' should not have any counter
    assert "NEVERUSED-DST" not in accessPerSE

    # GOOD-DST should have 2 good reads and no bad
    assert False not in accessPerSE["GOOD-DST"]
    assert accessPerSE["GOOD-DST"][True] == 2

    # BAD-DST should have 2 bad reads and no good
    assert True not in accessPerSE["BAD-DST"]
    assert accessPerSE["BAD-DST"][False] == 2

    # OTHERBAD-DST should have no good read and 1 bad read
    assert True not in accessPerSE["OTHERBAD-DST"]
    assert accessPerSE["OTHERBAD-DST"][False] == 1
