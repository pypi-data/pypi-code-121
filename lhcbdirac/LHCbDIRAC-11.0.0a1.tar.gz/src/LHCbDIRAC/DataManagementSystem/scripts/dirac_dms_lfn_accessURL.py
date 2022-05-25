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
"""Retrieve an access URL for an LFN replica given a valid DIRAC SE."""

from DIRAC.Core.Base.Script import Script


@Script()
def main():
    from LHCbDIRAC.DataManagementSystem.Client.DMScript import DMScript

    dmScript = DMScript()
    dmScript.registerFileSwitches()
    dmScript.registerSiteSwitches()
    Script.registerSwitch("a", "All", "  Also show inactive replicas")
    Script.registerSwitch("", "DiskOnly", "  Show only disk replicas")
    Script.registerSwitch("", "PreferDisk", "  If disk replica, don't show tape replicas")
    Script.registerSwitch("", "ForJobs", "  Select only replicas that can be used for jobs")
    Script.registerSwitch("", "Protocol=", "   Define the protocol for which a tURL is requested (default:root)")
    Script.registerSwitch(
        "",
        "Metalink",
        "   Generate metalink files for parallel download with xrdcp \
                            (one file per lfn). Implies Protocol=root",
    )
    Script.setUsageMessage(
        "\n".join(
            [
                __doc__,
                "Usage:",
                "  %s [option|cfgfile] ... [LFN[,LFN2[,LFN3...]]] SE[,SE2...]" % Script.scriptName,
                "Arguments:",
                "  LFN:      Logical File Name or file containing LFNs",
                "  SE:       Valid DIRAC SE",
            ]
        )
    )
    Script.parseCommandLine(ignoreErrors=True)

    from LHCbDIRAC.DataManagementSystem.Client.ScriptExecutors import executeAccessURL
    from DIRAC import exit

    exit(executeAccessURL(dmScript))


if __name__ == "__main__":
    main()
