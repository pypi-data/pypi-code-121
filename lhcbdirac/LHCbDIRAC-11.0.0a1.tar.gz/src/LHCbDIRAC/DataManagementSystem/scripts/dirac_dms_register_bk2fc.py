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
"""Given a (list of) LFNs and SEs, check for existence of a file and register
in the FC if the file exists."""

from DIRAC.Core.Base.Script import Script


@Script()
def main():
    from LHCbDIRAC.DataManagementSystem.Client.DMScript import DMScript

    dmScript = DMScript()
    dmScript.registerFileSwitches()
    dmScript.registerSiteSwitches()

    Script.setUsageMessage(
        "\n".join(
            [
                __doc__,
                "Usage:",
                "  %s [option|cfgfile] ...  [LFN1[,LFN2,[...]]] [--SE] Dest[,Dest2[,...]] " % Script.scriptName,
                "Arguments:",
                "  Dest:     Valid DIRAC SE(s)",
            ]
        )
    )
    Script.parseCommandLine(ignoreErrors=True)

    from LHCbDIRAC.DataManagementSystem.Client.ScriptExecutors import executeRegisterBK2FC
    from DIRAC import exit

    exit(executeRegisterBK2FC(dmScript))


if __name__ == "__main__":
    main()
