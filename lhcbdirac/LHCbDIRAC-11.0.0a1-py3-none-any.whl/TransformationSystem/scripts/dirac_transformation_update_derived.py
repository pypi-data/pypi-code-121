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
"""Move files that are Unused or MaxReset from a parent production to its
derived production The argument is a list of productions: comma separated list
of ranges (a range has the form p1:p2)"""

from DIRAC.Core.Base.Script import Script


@Script()
def main():

    Script.setUsageMessage(
        "\n".join(
            [
                __doc__,
                "Usage:",
                "  %s [option|cfgfile] [prod1[:prod2][,prod3[:prod4]]" % Script.scriptName,
            ]
        )
    )
    Script.registerSwitch("", "NoReset", "Don't reset the MaxRest files to unused (default is to reset)")
    Script.parseCommandLine(ignoreErrors=True)

    import DIRAC
    from LHCbDIRAC.TransformationSystem.Client.TransformationClient import TransformationClient

    transClient = TransformationClient()

    resetUnused = True
    switches = Script.getUnprocessedSwitches()
    for switch in switches:
        if switch[0] == "NoReset":
            resetUnused = False
    args = Script.getPositionalArgs()

    if not len(args):
        print("Specify transformation number...")
        DIRAC.exit(0)
    else:
        ids = args[0].split(",")
        idList = []
        for transId in ids:
            r = transId.split(":")
            if len(r) > 1:
                for i in range(int(r[0]), int(r[1]) + 1):
                    idList.append(i)
            else:
                idList.append(int(r[0]))

    for prod in idList:
        res = transClient.getTransformation(prod, extraParams=True)
        if not res["OK"]:
            print("Error getting transformation %s" % prod, res["Message"])
        else:
            res = transClient.moveFilesToDerivedTransformation(res["Value"], resetUnused)
            if not res["OK"]:
                print("Error updating a derived transformation %d:" % prod, res["Message"])
            else:
                parentProd, movedFiles = res["Value"]
                if movedFiles:
                    print("Successfully moved files from %d to %d:" % (parentProd, prod))
                    for status, val in movedFiles.items():
                        print("\t%d files to status %s" % (val, status))


if __name__ == "__main__":
    main()
