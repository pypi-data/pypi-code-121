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
"""Set Quality Flag for the given files."""
import DIRAC
from DIRAC.Core.Utilities.DIRACScript import DIRACScript


@DIRACScript()
def main():
    from DIRAC.Core.Base import Script

    Script.setUsageMessage(
        __doc__
        + "\n".join(
            [
                "Usage:",
                "  %s [option|cfgfile] ... LFN|File Flag" % Script.scriptName,
                "Arguments:",
                "  LFN:      Logical File Name",
                "  File:     Name of the file with a list of LFNs",
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
    filename = args[0]
    flag = args[1]
    lfns = []
    try:
        files = open(filename)
        for f in files:
            lfns += [f.strip()]
    except Exception as ex:
        lfns = [filename]

    result = bk.setFileDataQuality(lfns, flag)

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
