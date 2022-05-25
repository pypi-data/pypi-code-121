#! /usr/bin/env python
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
"""Set the visibility flag to a dataset."""

from DIRAC import exit as dExit, gLogger
from DIRAC.Core.Base.Script import Script


@Script()
def main():
    from LHCbDIRAC.DataManagementSystem.Client.DMScript import DMScript

    dmScript = DMScript()
    dmScript.registerBKSwitches()
    dmScript.registerFileSwitches()

    Script.registerSwitch("", "List", "   Print out the list of LFNs")
    Script.setUsageMessage(
        __doc__
        + "\n".join(
            [
                "Usage:",
                "  %s [option|cfgfile]" % Script.scriptName,
            ]
        )
    )

    Script.parseCommandLine(ignoreErrors=False)
    dumpList = False
    for switch in Script.getUnprocessedSwitches():
        if switch[0] == "List":
            dumpList = True

    bkQuery = dmScript.getBKQuery()
    lfns = dmScript.getOption("LFNs", [])
    if not bkQuery and not lfns:
        gLogger.error("No BKQuery and no files given...")
        dExit(1)
    # Invert the visibility flag as want to set Invisible those that are visible and vice-versa
    from LHCbDIRAC.BookkeepingSystem.Client.BookkeepingClient import BookkeepingClient

    bk = BookkeepingClient()

    visibilityFlag = dmScript.getOption("Visibility", None)
    if visibilityFlag is None:
        gLogger.error("Visibility option should be given")
        dExit(2)
    visibilityFlag = str(visibilityFlag).lower() == "yes"
    if bkQuery:
        # Query with visibility opposite to what is requested to be set ;-)
        bkQuery.setOption("Visible", "No" if visibilityFlag else "Yes")
        gLogger.notice("BQ query:", bkQuery)
        lfns += bkQuery.getLFNs()
    if not lfns:
        gLogger.notice("No files found...")
    else:
        res = {"OK": True}
        if visibilityFlag:
            res = bk.setFilesVisible(lfns)
            msg = "visible"
        else:
            res = bk.setFilesInvisible(lfns)
            msg = "invisible"
        if not res["OK"]:
            gLogger.error("Error setting files", msg)
            dExit(1)
        gLogger.notice("Successfully set %d files %s" % (len(lfns), msg + (":" if dumpList else "")))
        if dumpList:
            gLogger.notice("\n".join(lfns))


if __name__ == "__main__":
    main()
