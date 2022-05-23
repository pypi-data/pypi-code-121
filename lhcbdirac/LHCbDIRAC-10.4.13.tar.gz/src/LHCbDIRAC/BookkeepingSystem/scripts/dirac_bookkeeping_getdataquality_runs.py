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
"""Get Data Quality Flag for the given run."""
import DIRAC

from DIRAC import gLogger
from DIRAC.Core.Utilities.DIRACScript import DIRACScript


@DIRACScript()
def main():
    from DIRAC.Core.Base import Script

    Script.setUsageMessage(
        __doc__
        + "\n".join(
            ["Usage:", "  %s [option|cfgfile] ... Run ..." % Script.scriptName, "Arguments:", "  Run:      Run number"]
        )
    )
    Script.parseCommandLine(ignoreErrors=True)
    runSet = set(int(id) for arg in Script.getPositionalArgs() for id in arg.split(","))

    if not runSet:
        Script.showHelp(exitCode=1)

    gLogger.showHeaders(False)
    from LHCbDIRAC.BookkeepingSystem.Client.BookkeepingClient import BookkeepingClient

    cl = BookkeepingClient()

    gLogger.notice("Run Number".ljust(15) + "Stream".ljust(10) + "Flag".ljust(10))

    error = False
    for runId in sorted(runSet):
        retVal = cl.getRunFilesDataQuality(runId)
        if retVal["OK"]:
            for run, stream, flag in sorted((run, stream, flag) for run, flag, stream in retVal["Value"]):
                gLogger.notice(str(run).ljust(15) + str(stream).ljust(10) + str(flag).ljust(10))
            gLogger.notice("-----------------------------------")
        else:
            gLogger.error(retVal["Message"])
            error = True

    if error:
        DIRAC.exit(1)


if __name__ == "__main__":
    main()
