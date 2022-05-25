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
    from LHCbDIRAC.Interfaces.API.DiracProduction import DiracProduction

    print("Usage: %s <Command> <Production ID> |<Production ID>" % Script.scriptName)
    commands = DiracProduction().getProductionCommands()["Value"]
    print("\nCommands include: %s" % ", ".join(commands))
    print("\nDescription:\n")
    for n, v in commands.items():
        print("%s:" % n)
        for i, j in v.items():
            print("     %s = %s" % (i, j))

    DIRAC.exit(2)


@Script()
def main():
    Script.parseCommandLine(ignoreErrors=True)

    args = Script.getPositionalArgs()

    from LHCbDIRAC.Interfaces.API.DiracProduction import DiracProduction

    diracProd = DiracProduction()

    if len(args) < 2:
        usage()

    exitCode = 0
    errorList = []
    command = args[0]

    for prodID in args[1:]:
        result = diracProd.production(prodID, command, disableCheck=False)
        if "Message" in result:
            errorList.append((prodID, result["Message"]))
            exitCode = 2
        elif not result:
            errorList.append((prodID, "Null result for getProduction() call"))
            exitCode = 2
        else:
            exitCode = 0

    for error in errorList:
        print("ERROR %s: %s" % error)

    DIRAC.exit(exitCode)


if __name__ == "__main__":
    main()
