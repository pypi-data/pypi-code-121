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
"""Remove replicas of a (list of) LFNs at a list of sites.

It is possible to request a minimum of remaining replicas
"""

from DIRAC.Core.Base.Script import Script


@Script()
def main():
    from LHCbDIRAC.DataManagementSystem.Client.DMScript import DMScript

    dmScript = DMScript()
    dmScript.registerFileSwitches()
    dmScript.registerSiteSwitches()

    Script.registerSwitch("n", "NoFC", " use this option to force the removal from storage of replicas not in FC")
    Script.registerSwitch(
        "", "ReduceReplicas=", "  specify the number of replicas you want to keep (default SE: Tier1-USER)"
    )
    Script.registerSwitch("", "Force", " use this option for force the removal of replicas even if last one")
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
    Script.parseCommandLine()

    from LHCbDIRAC.DataManagementSystem.Client.ScriptExecutors import executeRemoveReplicas
    from DIRAC import exit

    exit(executeRemoveReplicas(dmScript))


if __name__ == "__main__":
    main()
