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
"""Report sisters or cousins (i.e. descendant of a parent or ancestor) for a (list of) LFN(s)"""

from DIRAC.Core.Base.Script import Script


@Script()
def main():
    from LHCbDIRAC.DataManagementSystem.Client.DMScript import DMScript

    dmScript = DMScript()
    dmScript.registerFileSwitches()
    Script.registerSwitch("", "All", "Do not restrict to sisters with replicas")
    Script.registerSwitch("", "Full", "Get full metadata information on sisters")
    level = 1
    Script.registerSwitch(
        "", "Depth=", "Number of ancestor levels (default: %d), 2 would be cousins, 3 grand-cousins etc..." % level
    )
    Script.registerSwitch("", "Production=", "Production to check for sisters (default=same production)")
    Script.registerSwitch("", "AllFileTypes", "Consider also files with a different type")
    Script.setUsageMessage(
        __doc__ + "\n".join(["Usage:", "  %s [option|cfgfile] ... [LFN|File] [Level]" % Script.scriptName])
    )

    Script.parseCommandLine(ignoreErrors=True)

    from LHCbDIRAC.BookkeepingSystem.Client.ScriptExecutors import executeFileSisters

    executeFileSisters(dmScript, level=level)


if __name__ == "__main__":
    main()
