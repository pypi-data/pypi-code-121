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
"""Check if the files are in the BK, the FC and the SEs they are supposed to be
in.

Uses the DM script switches, and, unless a list of LFNs is provided

1) If --Directory is used: get files in FC directories
2) If --Production or --BK options is used get files in the FC directories from the BK

If an (list of) SE or SE-group is specified option --SE) and the file is not in the FC,
check if it is in these SEs

- If the file is in the SE and in the BK, it can be registered in the FC using --FixIt

If --FixIt is set, takes actions:
  Missing files: remove from SE and FC
  No replica flag: set it (in the BK)
  Not existing in SE: remove replica or file from the catalog
  Existing in SE and BK: register it in the FC
  Bad checksum: remove replica or file from SE and catalogs if no good replica
"""

from DIRAC.Core.Base.Script import Script


def __getSEsFromOptions(dmScript):
    from DIRAC.DataManagementSystem.Utilities.DMSHelpers import DMSHelpers

    seList = dmScript.getOption("SEs", [])
    sites = dmScript.getOption("Sites", [])
    if sites:
        siteSEs = []
        dmsHelper = DMSHelpers()
        for site in sites:
            siteSEs += dmsHelper.getSEsForSite(site).get("Value", [])
        if seList and siteSEs:
            seList = list(set(seList) & set(siteSEs))
        else:
            seList += siteSEs
    return seList


@Script()
def main():
    # Script initialization
    from LHCbDIRAC.DataManagementSystem.Client.DMScript import DMScript

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
    dmScript.registerDMSwitches()
    maxFiles = 20
    Script.registerSwitch("", "FixIt", "   Take action to fix the catalogs and storage")
    Script.registerSwitch("", "Replace", "   Replace bad or missing replicas (default=False)")
    Script.registerSwitch("", "NoBK", "   Do not check with BK")
    Script.registerSwitch("", "Verbose", "   Set logging mode to INFO")
    Script.registerSwitch("", "MaxFiles=", "   Set maximum number of files to be printed (default %d)" % maxFiles)
    Script.parseCommandLine(ignoreErrors=True)

    from DIRAC import gLogger

    fixIt = False
    bkCheck = True
    replace = False
    verbose = False
    for switch in Script.getUnprocessedSwitches():
        if switch[0] == "FixIt":
            fixIt = True
        elif switch[0] == "NoBK":
            bkCheck = False
        elif switch[0] == "Replace":
            replace = True
        elif switch[0] == "Verbose":
            verbose = True
        elif switch[0] == "MaxFiles":
            try:
                maxFiles = int(switch[1])
            except Exception as e:
                gLogger.exception("Invalid value for MaxFiles", lException=e)
                pass

    # imports
    from LHCbDIRAC.DataManagementSystem.Client.ConsistencyChecks import ConsistencyChecks

    if verbose:
        gLogger.setLevel("INFO")
    cc = ConsistencyChecks()
    cc.directories = dmScript.getOption("Directory", [])
    cc.lfns = dmScript.getOption("LFNs", []) + [lfn for arg in Script.getPositionalArgs() for lfn in arg.split(",")]
    bkQuery = dmScript.getBKQuery(visible="All")
    if bkQuery:
        bkQuery.setOption("ReplicaFlag", "All")
        cc.bkQuery = bkQuery

    cc.seList = __getSEsFromOptions(dmScript)
    from LHCbDIRAC.DataManagementSystem.Client.CheckExecutors import doCheckFC2SE

    try:
        doCheckFC2SE(cc, bkCheck=bkCheck, fixIt=fixIt, replace=replace, maxFiles=maxFiles)
    except RuntimeError as e:
        gLogger.fatal(str(e))
    except Exception as e:
        gLogger.exception("Exception", lException=e)


if __name__ == "__main__":
    main()
