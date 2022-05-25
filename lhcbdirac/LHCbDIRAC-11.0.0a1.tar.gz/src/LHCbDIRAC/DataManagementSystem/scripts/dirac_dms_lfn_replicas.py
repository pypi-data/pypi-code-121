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
"""Show replicas for a (set of) LFNs."""

from DIRAC.Core.Base.Script import Script


@Script()
def main():
    from LHCbDIRAC.DataManagementSystem.Client.DMScript import DMScript

    dmScript = DMScript()
    dmScript.registerFileSwitches()
    Script.registerSwitch("a", "All", "  Also show inactive replicas")
    Script.registerSwitch("", "DiskOnly", "  Show only disk replicas")
    Script.registerSwitch("", "PreferDisk", "  If disk replica, don't show tape replicas")
    Script.registerSwitch("", "ForJobs", "  Select only replicas that can be used for jobs")

    Script.setUsageMessage(
        "\n".join(
            [
                __doc__,
                "Usage:",
                "  %s [option|cfgfile] [<LFN>] [<LFN>...]" % Script.scriptName,
            ]
        )
    )

    Script.parseCommandLine(ignoreErrors=False)

    from LHCbDIRAC.DataManagementSystem.Client.ScriptExecutors import executeLfnReplicas
    from DIRAC import exit

    exit(executeLfnReplicas(dmScript))


if __name__ == "__main__":
    main()
