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
"""Retrieve files of a given type for a production."""
from DIRAC.Core.Utilities.DIRACScript import DIRACScript


@DIRACScript()
def main():
    from DIRAC.Core.Base import Script

    Script.setUsageMessage(
        __doc__
        + "\n".join(
            [
                "Usage:",
                "  %s [option|cfgfile] ... ProdID Type" % Script.scriptName,
                "Arguments:",
                "  ProdID:   Production ID (integer)",
                "  Type:     File Type (For example: ALL, DST, SIM, DIGI, RDST, MDF)",
            ]
        )
    )
    Script.parseCommandLine()
    args = Script.getPositionalArgs()

    if not len(args) == 2:
        Script.showHelp(exitCode=1)

    try:
        prodID = int(args[0])
    except BaseException:
        Script.showHelp(exitCode=1)
    filetype = args[1]

    from DIRAC import gLogger, exit as DIRACexit
    from LHCbDIRAC.BookkeepingSystem.Client.BookkeepingClient import BookkeepingClient

    client = BookkeepingClient()
    res = client.getProductionFiles(prodID, filetype)
    if not res["OK"]:
        gLogger.error("ERROR: Failed to retrieve production files", res["Message"])
        DIRACexit(1)

    if not res["Value"]:
        gLogger.notice("No files found for production %s with type %s" % (prodID, filetype))
    else:
        gLogger.notice(
            "%s %s %s %s %s"
            % ("FileName".ljust(100), "Size".ljust(10), "GUID".ljust(40), "Replica".ljust(8), "Visible".ljust(8))
        )
        for lfn in sorted(res["Value"]):
            size = res["Value"][lfn]["FileSize"]
            guid = res["Value"][lfn]["GUID"]
            hasReplica = res["Value"][lfn]["GotReplica"]
            visible = res["Value"][lfn]["Visible"]
            gLogger.notice(
                "%s %s %s %s %s"
                % (lfn.ljust(100), str(size).ljust(10), guid.ljust(40), str(hasReplica).ljust(8), str(visible).ljust(8))
            )


if __name__ == "__main__":
    main()
