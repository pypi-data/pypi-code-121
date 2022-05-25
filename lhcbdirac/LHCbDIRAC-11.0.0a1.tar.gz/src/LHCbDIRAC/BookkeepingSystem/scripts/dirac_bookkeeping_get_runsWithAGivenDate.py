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
"""Retrieve from the Bookkeeping runs from a given date range."""

from DIRAC.Core.Base.Script import Script


@Script()
def main():
    from DIRAC import gLogger, exit as DIRACexit

    Script.setUsageMessage(
        __doc__
        + "\n".join(
            [
                "Usage:",
                "  %s [option|cfgfile] ... Start [End]" % Script.scriptName,
                "Arguments:",
                "  Start:    Start date (Format: YYYY-MM-DD) (mandatory)",
                "  End:      End date (Format: YYYY-MM-DD). Default is Start",
            ]
        )
    )
    Script.parseCommandLine(ignoreErrors=True)
    args = Script.getPositionalArgs()

    from LHCbDIRAC.BookkeepingSystem.Client.BookkeepingClient import BookkeepingClient

    start = ""
    end = ""
    if len(args) < 2:
        Script.showHelp(exitCode=1)

    if len(args) == 2:
        end = args[1]
    start = args[0]

    in_dict = {}
    in_dict["StartDate"] = start
    in_dict["EndDate"] = end if end else start

    res = BookkeepingClient().getRunsForAGivenPeriod(in_dict)
    if not res["OK"]:
        gLogger.error("Failed to retrieve runs: %s" % res["Message"])
        DIRACexit(1)

    if not res["Value"]["Runs"]:
        gLogger.notice("No runs found for the date range", (start, end))
    else:
        gLogger.notice("Runs:", res["Value"]["Runs"])
        if "ProcessedRuns" in res["Value"]:
            gLogger.notice("Processed runs:", res["Value"]["ProcessedRuns"])
        if "NotProcessedRuns" in res["Value"]:
            gLogger.notice("Not processed runs:", res["Value"]["NotProcessedRuns"])


if __name__ == "__main__":
    main()
