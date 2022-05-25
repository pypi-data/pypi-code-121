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
"""Check if all files have a replica in a certain (set of) SE )Tier1-Archive
default) List the files that don't have a replica in the specified SE (group)"""

from DIRAC.Core.Base.Script import Script


@Script()
def main():
    # Script initialization
    from LHCbDIRAC.DataManagementSystem.Client.DMScript import DMScript

    Script.registerSwitch("", "FixIt", "   Take action to fix the catalogs")
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
    dmScript.registerDMSwitches()  # Directory
    Script.parseCommandLine(ignoreErrors=True)
    fixIt = False
    for opt, val in Script.getUnprocessedSwitches():
        if opt == "FixIt":
            fixIt = True

    # imports
    from LHCbDIRAC.DataManagementSystem.Client.ConsistencyChecks import ConsistencyChecks

    cc = ConsistencyChecks()
    cc.directories = dmScript.getOption("Directory", [])
    cc.lfns = dmScript.getOption("LFNs", []) + [lfn for arg in Script.getPositionalArgs() for lfn in arg.split(",")]
    bkQuery = dmScript.getBKQuery(visible="All")
    if bkQuery.getQueryDict() != {"Visible": "All"}:
        bkQuery.setOption("ReplicaFlag", "All")
        cc.bkQuery = bkQuery
    seList = dmScript.getOption("SEs", [])
    if not seList:
        dmScript.setSEs("Tier1-Archive")
        seList = dmScript.getOption("SEs", [])

    from LHCbDIRAC.DataManagementSystem.Client.CheckExecutors import doCheckSE

    doCheckSE(cc, seList, fixIt)


if __name__ == "__main__":
    main()
