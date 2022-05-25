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
"""Set Data Quality Flag for the given run."""
import DIRAC
from DIRAC.Core.Base.Script import Script


@Script()
def main():

    Script.setUsageMessage(
        __doc__
        + "\n".join(
            [
                "Usage:",
                "  %s [option|cfgfile] ... Run Flag" % Script.scriptName,
                "Arguments:",
                "  Run:      Run number",
                "  Flag:     Quality Flag",
            ]
        )
    )
    Script.parseCommandLine(ignoreErrors=True)
    args = Script.getPositionalArgs()

    from LHCbDIRAC.BookkeepingSystem.Client.BookkeepingClient import BookkeepingClient

    bk = BookkeepingClient()

    if len(args) < 2:
        result = bk.getAvailableDataQuality()
        if not result["OK"]:
            print("ERROR: %s" % (result["Message"]))
            DIRAC.exit(2)
        flags = result["Value"]
        print("Available Data Quality Flags")
        for flag in flags:
            print(flag)
        Script.showHelp()

    exitCode = 0
    rnb = int(args[0])
    flag = args[1]
    result = bk.setRunDataQuality(rnb, flag)

    if not result["OK"]:
        print("ERROR: %s" % (result["Message"]))
        exitCode = 2
    else:
        succ = result["Value"]["Successful"]
        failed = result["Value"]["Failed"]
        print("The data quality has been set for the following files:")
        for i in succ:
            print(i)

        if len(failed) != 0:
            print("The data quality has not been set for the following files:")
            for i in failed:
                print(i)

    DIRAC.exit(exitCode)


if __name__ == "__main__":
    main()
