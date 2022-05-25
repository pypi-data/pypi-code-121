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
"""Return the BK path for the directories of a (list of) files."""

from DIRAC.Core.Base.Script import Script


@Script()
def main():
    from LHCbDIRAC.DataManagementSystem.Client.DMScript import DMScript

    dmScript = DMScript()
    dmScript.registerFileSwitches()
    Script.registerSwitch("", "Full", "   Print out full BK dictionary (default: print out BK path)")
    Script.registerSwitch("", "GroupBy=", "   Return a list of files per <metadata item>")
    Script.registerSwitch("", "GroupByPath", "   Return a list of files per BK path")
    Script.registerSwitch("", "GroupByProduction", "   Return a list of files per production")
    Script.registerSwitch("", "Summary", "   Only give the number of files in each group (default: GroupByPath)")
    Script.registerSwitch("", "List", "   Print a list of group keys")
    Script.registerSwitch("", "IgnoreFileType", "   Ignore file type in path (useful for stripping)")
    Script.setUsageMessage(
        __doc__
        + "\n".join(
            [
                "Usage:",
                "  %s [option|cfgfile] ... LFN|File" % Script.scriptName,
                "Arguments:",
                "  LFN:      Logical File Name",
                "  File:     Name of the file with a list of LFNs",
            ]
        )
    )
    Script.parseCommandLine()

    from LHCbDIRAC.BookkeepingSystem.Client.ScriptExecutors import executeFilePath

    executeFilePath(dmScript)


if __name__ == "__main__":
    main()
