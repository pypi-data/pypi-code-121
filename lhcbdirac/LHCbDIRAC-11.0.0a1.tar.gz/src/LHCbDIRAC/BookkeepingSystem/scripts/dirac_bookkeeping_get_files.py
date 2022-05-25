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
"""Retrieve files of a BK query."""

from DIRAC.Core.Base.Script import Script


@Script()
def main():
    from LHCbDIRAC.DataManagementSystem.Client.DMScript import DMScript

    dmScript = DMScript()
    dmScript.registerBKSwitches()
    Script.registerSwitch("", "File=", "   Provide a list of BK paths")
    Script.registerSwitch("", "Term", "   Provide the list of BK paths from terminal")
    Script.registerSwitch("", "Output=", "  Specify a file that will contain the list of files")
    Script.registerSwitch("", "OptionsFile=", "   Create a Gaudi options file")
    maxFiles = 20
    Script.registerSwitch(
        "", "MaxFiles=", "   Print only <MaxFiles> lines on stdout (%d if output, else All)" % maxFiles
    )
    Script.setUsageMessage(__doc__ + "\n".join(["Usage:", "  %s [option|cfgfile] ... " % Script.scriptName]))

    Script.parseCommandLine()

    from LHCbDIRAC.BookkeepingSystem.Client.ScriptExecutors import executeGetFiles

    executeGetFiles(dmScript, maxFiles)


if __name__ == "__main__":
    main()
