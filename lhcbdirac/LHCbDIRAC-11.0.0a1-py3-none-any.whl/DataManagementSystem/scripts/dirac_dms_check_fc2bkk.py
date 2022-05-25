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
"""Uses the DM script switches, and, unless a list of LFNs is provided

1. If --Directory is used: get files in FC directories, check if they are in BK and if the replica flag is set
2. If --Production is used get files in the FC directories used, and proceed as with --Directory

If --FixFC is set, remove from SE and FC
If --FixBK is set and no replica flag, set replica flag in the BK
"""

from DIRAC.Core.Base.Script import Script


@Script()
def main():
    # Script initialization
    from LHCbDIRAC.DataManagementSystem.Client.DMScript import DMScript
    import DIRAC

    Script.setUsageMessage(
        "\n".join(
            [
                __doc__,
                "Usage:",
                "  %s [option|cfgfile] [values]" % Script.scriptName,
            ]
        )
    )
    dmScript = DMScript()
    dmScript.registerNamespaceSwitches()  # Directory
    dmScript.registerFileSwitches()  # File, LFNs
    dmScript.registerBKSwitches()
    Script.registerSwitch("", "FixBK", "   Take action to fix the BK")
    Script.registerSwitch("", "FixFC", "   Take action to fix the FC")
    Script.registerSwitch("", "NoFC2SE", "   Don't execute an FC2SE check")
    Script.registerSwitch("", "AffectedRuns", "   List the runs affected by the encountered problem")
    Script.parseCommandLine(ignoreErrors=True)

    from DIRAC import gLogger

    fixBK = False
    fixFC = False
    checkFC2SE = True
    listAffectedRuns = False
    for switch in Script.getUnprocessedSwitches():
        if switch[0] == "FixFC":
            fixFC = True
        if switch[0] == "FixBK":
            fixBK = True
        elif switch[0] == "AffectedRuns":
            listAffectedRuns = True
        elif switch[0] == "NoFC2SE":
            checkFC2SE = False

    if fixFC and fixBK:
        gLogger.notice("Can't fix both FC and BK, please choose")
        DIRAC.exit(0)
    # imports
    from LHCbDIRAC.DataManagementSystem.Client.ConsistencyChecks import ConsistencyChecks

    cc = ConsistencyChecks()
    cc.directories = dmScript.getOption("Directory", [])
    cc.lfns = dmScript.getOption("LFNs", []) + [lfn for arg in Script.getPositionalArgs() for lfn in arg.split(",")]
    productions = dmScript.getOption("Productions", [])
    runs = dmScript.getOption("Runs", [])

    from LHCbDIRAC.DataManagementSystem.Client.CheckExecutors import doCheckFC2BK

    if productions and not runs:
        fileType = dmScript.getOption("FileType", [])
        if fileType:
            cc.fileType = fileType
        for prod in productions:
            cc.prod = prod
            gLogger.always("Processing production %d" % cc.prod)
            doCheckFC2BK(cc, fixFC, fixBK, listAffectedRuns)
            gLogger.always("Processed production %d" % cc.prod)
    else:
        bkQuery = dmScript.getBKQuery(visible="All")
        if bkQuery:
            bkQuery.setOption("ReplicaFlag", "All")
            cc.bkQuery = bkQuery
        doCheckFC2BK(cc, fixFC=fixFC, fixBK=fixBK, listAffectedRuns=listAffectedRuns, checkFC2SE=checkFC2SE)


if __name__ == "__main__":
    main()
