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
"""Replicate a (list of) existing LFN(s) to (set of) Storage Element(s)"""

from DIRAC.Core.Base.Script import Script


@Script()
def main():
    from LHCbDIRAC.DataManagementSystem.Client.DMScript import DMScript

    dmScript = DMScript()
    dmScript.registerFileSwitches()
    dmScript.registerSiteSwitches()

    Script.registerSwitch("", "RemoveSource", "   If set, the source replica(s) will be removed")

    Script.setUsageMessage(
        "\n".join(
            [
                __doc__,
                "Usage:",
                "  %s [option|cfgfile] ...  [LFN1[,LFN2,[...]]] Dest[,Dest2[,...]] [Source [Cache]]"
                % Script.scriptName,
                "Arguments:",
                "  Dest:     Valid DIRAC SE(s)",
                "  Source:   Valid DIRAC SE",
                "  Cache:    Local directory to be used as cache",
            ]
        )
    )
    Script.parseCommandLine(ignoreErrors=True)

    from LHCbDIRAC.DataManagementSystem.Client.ScriptExecutors import executeReplicateLfn
    from DIRAC import exit

    exit(executeReplicateLfn(dmScript))


if __name__ == "__main__":
    main()
