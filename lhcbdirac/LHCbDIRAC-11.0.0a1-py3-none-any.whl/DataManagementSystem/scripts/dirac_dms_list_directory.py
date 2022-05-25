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
"""Get the list of all the user files."""

from DIRAC.Core.Base.Script import Script


@Script()
def main():
    from LHCbDIRAC.DataManagementSystem.Client.DMScript import DMScript

    days = 0
    months = 0
    years = 0
    depth = 1
    wildcard = "*"
    dmScript = DMScript()
    dmScript.registerNamespaceSwitches()
    Script.registerSwitch("", "Days=", "Match files older than number of days [%s]" % days)
    Script.registerSwitch("", "Months=", "Match files older than number of months [%s]" % months)
    Script.registerSwitch("", "Years=", "Match files older than number of years [%s]" % years)
    Script.registerSwitch("", "Wildcard=", "Wildcard for matching filenames [%s]" % wildcard)
    Script.registerSwitch("", "Output", "Write list to an output file")
    Script.registerSwitch("", "EmptyDirs", "Create a list of empty directories")
    Script.registerSwitch("", "Depth=", "Depth to which recursively browse (default = %d)" % depth)
    Script.registerSwitch("r", "Recursive", "Set depth to infinite")
    Script.registerSwitch("", "NoDirectories", "Only print out only files, not subdirectories")
    dmScript.registerBKSwitches()

    Script.setUsageMessage(
        __doc__
        + "\n".join(
            [
                "Usage:",
                "  %s [option|cfgfile] ..." % Script.scriptName,
            ]
        )
    )

    Script.parseCommandLine(ignoreErrors=False)
    from LHCbDIRAC.DataManagementSystem.Client.ScriptExecutors import executeListDirectory
    from DIRAC import exit

    exit(executeListDirectory(dmScript, days, months, years, wildcard, depth))


if __name__ == "__main__":
    main()
