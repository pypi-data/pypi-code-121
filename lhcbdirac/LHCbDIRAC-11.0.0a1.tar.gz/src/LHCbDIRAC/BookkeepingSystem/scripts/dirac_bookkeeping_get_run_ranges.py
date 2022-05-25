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
"""Returns run ranges, split by conditions and by run gaps or time interval between them."""

from DIRAC.Core.Base.Script import Script


@Script()
def main():
    from LHCbDIRAC.DataManagementSystem.Client.DMScript import Script

    Script.registerSwitch("", "Activity=", "Specify the BK activity (e.g. Collision15)")
    Script.registerSwitch("", "Runs=", "Run range or list (can be used with --Activity to reduce the run range)")
    Script.registerSwitch("", "Fast", "Include runs even if no FULL stream is present (much faster)")
    Script.registerSwitch("", "DQFlag=", "Specify the DQ flag (default: all)")
    Script.registerSwitch("", "RunGap=", "Gap between run ranges, in number of runs")
    Script.registerSwitch("", "TimeGap=", "Gap between run ranges, in number of days")
    Script.setUsageMessage(__doc__ + "\n".join(["Usage:", "  %s [option|cfgfile] ... " % Script.scriptName]))

    Script.parseCommandLine(ignoreErrors=True)

    from LHCbDIRAC.BookkeepingSystem.Client.ScriptExecutors import executeRunInfo

    executeRunInfo("Ranges")


if __name__ == "__main__":
    main()
