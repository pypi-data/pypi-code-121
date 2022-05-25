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
"""
Uses the DM script switches, and, unless a list of LFNs is provided

1. If --BKQuery is used: get files in BK directories, check if they are in FC
2. If --Production is used get files using the bk query of the given production

Then check if files registered as having a replica in the BK are also in the FC.

If --FixIt is set, take actions

- add files to the BK if they exist in the FC, but have replica = NO in the BK
- set replicaFlag = No in the BK for those files that are not in the FC
"""

from DIRAC.Core.Base.Script import Script


@Script()
def main():
    # Script initialization
    from LHCbDIRAC.DataManagementSystem.Client.DMScript import DMScript
    from DIRAC import gLogger

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
    dmScript.registerBKSwitches()
    dmScript.registerFileSwitches()
    Script.registerSwitch("", "FixIt", "   Take action to fix the catalogs")
    Script.registerSwitch("", "CheckAllFlags", "   Consider also files with replica flag NO")
    Script.parseCommandLine(ignoreErrors=True)

    fixIt = False
    checkAll = False
    for opt, val in Script.getUnprocessedSwitches():
        if opt == "FixIt":
            fixIt = True
        elif opt == "CheckAllFlags":
            checkAll = True

    # imports
    from LHCbDIRAC.DataManagementSystem.Client.ConsistencyChecks import ConsistencyChecks

    gLogger.setLevel("INFO")
    cc = ConsistencyChecks()
    bkQuery = dmScript.getBKQuery(visible="All")
    cc.bkQuery = bkQuery
    cc.lfns = dmScript.getOption("LFNs", [])
    productions = dmScript.getOption("Productions", [])

    from LHCbDIRAC.DataManagementSystem.Client.CheckExecutors import doCheckBK2FC

    if productions:
        for prod in productions:
            cc.prod = prod
            gLogger.always("Processing production %d" % cc.prod)
            doCheckBK2FC(cc, checkAll, fixIt)
            gLogger.always("Processed production %d" % cc.prod)
    else:
        doCheckBK2FC(cc, checkAll, fixIt)


if __name__ == "__main__":
    main()
