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
"""Report info on event types for MC"""
import DIRAC
from DIRAC.Core.Base.Script import Script


@Script()
def main():

    from LHCbDIRAC.BookkeepingSystem.Client.BookkeepingClient import BookkeepingClient
    from LHCbDIRAC.BookkeepingSystem.Client.BKQuery import BKQuery

    Script.registerSwitch("", "FileType=", "FileType to search [default:ALLSTREAMS.DST]")

    Script.setUsageMessage(__doc__ + "\n".join(["Usage:", "  %s [option] eventType (mandatory)" % Script.scriptName]))
    fileType = "ALLSTREAMS.DST"
    Script.parseCommandLine(ignoreErrors=True)
    for switch in Script.getUnprocessedSwitches():
        if switch[0] == "FileType":
            fileType = str(switch[1])

    args = Script.getPositionalArgs()
    if len(args) < 1:
        Script.showHelp(exitCode=1)

    eventTypes = args[0]
    bkQuery = BKQuery({"EventType": eventTypes, "ConfigName": "MC"}, fileTypes=fileType, visible=True)
    print("bkQuery:", bkQuery)
    prods = bkQuery.getBKProductions()

    for prod in prods:
        res = BookkeepingClient().getProductionInformation(prod)
        if not res["OK"]:
            print(res["Message"])
            DIRAC.exit(1)
        value = res["Value"]
        print(value["Path"].split("\n")[1], end=" ")
        for nf in value["Number of files"]:
            if nf[1] == fileType:
                print(nf[0], end=" ")
        for ne in value["Number of events"]:
            if ne[0] == fileType:
                print(ne[1], end=" ")
        print("")


if __name__ == "__main__":
    main()
