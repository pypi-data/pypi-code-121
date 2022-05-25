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
"""Get statistics on number of replicas for a given directory or production."""

from DIRAC.Core.Base.Script import Script


@Script()
def main():
    from LHCbDIRAC.DataManagementSystem.Client.DMScript import DMScript

    dmScript = DMScript()
    dmScript.registerBKSwitches()
    dmScript.registerNamespaceSwitches()
    dmScript.registerFileSwitches()

    Script.setUsageMessage(
        __doc__
        + "\n".join(
            [
                "Usage:",
                "  %s [option|cfgfile] [<LFN>] [<LFN>...]" % Script.scriptName,
            ]
        )
    )

    Script.registerSwitch("", "Size", "   Get the LFN size [No]")
    Script.registerSwitch("", "DumpNoReplicas", "   Print list of files without a replica [No]")
    Script.registerSwitch("", "DumpWithArchives=", "   =<n>, print files with <n> archives")
    Script.registerSwitch("", "DumpWithReplicas=", "   =<n>, print files with <n> replicas")
    Script.registerSwitch(
        "", "DumpFailover", "   print files with failover replica (can be used with Dump[With/No]Replicas)"
    )
    Script.registerSwitch("", "DumpAtSE=", "   print files present at a (list of) SE")
    Script.registerSwitch("", "DumpNotAtSE=", "   print files absent at a (list of) SE")
    Script.registerSwitch("", "DumpAtSite=", "   print files present at a (list of) sites")
    Script.registerSwitch("", "Summary", "   do not print stats per SE nor site")

    Script.parseCommandLine(ignoreErrors=False)

    from LHCbDIRAC.DataManagementSystem.Client.ScriptExecutors import executeReplicaStats
    from DIRAC import exit

    exit(executeReplicaStats(dmScript))


if __name__ == "__main__":
    main()
