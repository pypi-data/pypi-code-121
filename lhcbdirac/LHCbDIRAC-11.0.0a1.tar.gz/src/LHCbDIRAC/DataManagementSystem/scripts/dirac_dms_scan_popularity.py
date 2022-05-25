#!/usr/bin/env python
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
"""Script for scanning the popularity table."""
from DIRAC.Core.Base.Script import Script


@Script()
def main():

    since = 30
    getAllDatasets = False
    Script.registerSwitch("", "Since=", "   Number of days to look for (default: %d)" % since)
    Script.registerSwitch("", "All", "   If used, gets all existing datasets, not only the used ones")
    Script.setUsageMessage(
        "\n".join(
            [
                __doc__,
                "Usage:",
                "  %s [option|cfgfile]" % Script.scriptName,
            ]
        )
    )
    Script.parseCommandLine(ignoreErrors=True)
    for switch in Script.getUnprocessedSwitches():
        if switch[0] == "Since":
            try:
                since = int(switch[1])
            except ValueError:
                pass
        elif switch[0] == "All":
            getAllDatasets = True

    from LHCbDIRAC.DataManagementSystem.Client.ScanPopularity import scanPopularity

    scanPopularity(since, getAllDatasets)


if __name__ == "__main__":
    main()
