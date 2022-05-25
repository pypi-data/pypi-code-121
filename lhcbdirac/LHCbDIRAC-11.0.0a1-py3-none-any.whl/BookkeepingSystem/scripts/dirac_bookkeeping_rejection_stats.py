#! /usr/bin/env python
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
"""Get statistical information on a dataset."""

from DIRAC.Core.Base.Script import Script


@Script()
def main():
    from LHCbDIRAC.DataManagementSystem.Client.DMScript import DMScript

    dmScript = DMScript()
    dmScript.registerBKSwitches()
    dmScript.registerFileSwitches()

    Script.registerSwitch("", "ByStream", "   Get rejection for each stream")

    Script.setUsageMessage(
        __doc__
        + "\n".join(
            [
                "Usage:",
                "  %s [option|cfgfile]" % Script.scriptName,
            ]
        )
    )

    Script.parseCommandLine(ignoreErrors=False)

    from LHCbDIRAC.BookkeepingSystem.Client.ScriptExecutors import executeRejectionStats

    executeRejectionStats(dmScript)


if __name__ == "__main__":
    main()
