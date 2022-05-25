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

import DIRAC
from DIRAC.Core.Base.Script import Script


def usage():
    """usage.

    Prints script usage
    """
    print("Usage: %s <LFN> [<LFN>] [--ProductionID=<ID>] [Try -h,--help for more information]" % Script.scriptName)
    DIRAC.exit(2)


@Script()
def main():
    Script.registerSwitch(
        "",
        "ProductionID=",
        "Restrict query to given production ID (default is to show status for all)",
    )
    Script.parseCommandLine(ignoreErrors=True)

    from LHCbDIRAC.Interfaces.API.DiracProduction import DiracProduction

    prodID = ""
    for switch in Script.getUnprocessedSwitches():
        if switch[0].lower() == "productionid":
            prodID = switch[1]

    args = Script.getPositionalArgs()

    if len(args) < 1:
        usage()

    if prodID:
        try:
            prodID = int(prodID)
        except Exception as x:
            print("ERROR ProductionID should be an integer")
            DIRAC.exit(2)

    diracProd = DiracProduction()
    exitCode = 0
    result = diracProd.checkFilesStatus(args, prodID, printOutput=False)
    if not result["OK"]:
        print("ERROR %s" % (result["Message"]))
        exitCode = 2

    DIRAC.exit(exitCode)


if __name__ == "__main__":
    main()
