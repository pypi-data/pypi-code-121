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
"""Set the Agent Type for a(the) given transformation(s)"""
import DIRAC

from DIRAC.Core.Base.Script import Script


@Script()
def main():
    Script.setUsageMessage(
        __doc__
        + "\n".join(
            [
                "Usage:",
                "  %s <Production ID> |<Production ID>" % Script.scriptName,
                "Arguments:",
                "  <Production ID>:      DIRAC Production Id",
            ]
        )
    )

    Script.registerSwitch("a", "automatic", "Set automatic agent type")
    Script.registerSwitch("m", "manual", "Set manual agent type")

    Script.parseCommandLine(ignoreErrors=True)

    args = Script.getPositionalArgs()
    if len(args) < 1:
        Script.showHelp(exitCode=2)

    from LHCbDIRAC.Interfaces.API.DiracProduction import DiracProduction

    diracProd = DiracProduction()
    exitCode = 0
    errorList = []
    command = args[0]

    automatic = False
    manual = False
    type = ""

    switches = Script.getUnprocessedSwitches()

    for switch in switches:
        opt = switch[0].lower()

        if opt in ("a", "automatic"):
            automatic = True
        if opt in ("m", "manual"):
            manual = True

    if automatic and manual:
        print("ERROR: decide if you want automatic or manual ( not both ).")
        DIRAC.exit(2)
    elif not (automatic or manual):
        print("ERROR: decide if you want automatic or manual.")
        DIRAC.exit(2)
    elif automatic:
        type = "automatic"
    elif manual:
        type = "manual"

    for prodID in args:
        result = diracProd.production(prodID, type, disableCheck=False)
        if "Message" in result:
            errorList.append((prodID, result["Message"]))
            exitCode = 2
        elif not result:
            errorList.append((prodID, "Null result for production() call"))
            exitCode = 2
        else:
            exitCode = 0

    for error in errorList:
        print("ERROR %s: %s" % error)

    DIRAC.exit(exitCode)


if __name__ == "__main__":
    main()
