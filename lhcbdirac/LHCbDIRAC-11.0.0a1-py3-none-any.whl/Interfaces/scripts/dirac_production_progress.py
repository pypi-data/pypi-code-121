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

from DIRAC.Core.Base.Script import Script


@Script()
def main():

    Script.parseCommandLine(ignoreErrors=True)

    import DIRAC
    from LHCbDIRAC.Interfaces.API.DiracProduction import DiracProduction

    args = Script.getPositionalArgs()

    diracProd = DiracProduction()

    exitCode = 0
    for prodID in args:
        result = diracProd.getProductionProgress(prodID, printOutput=True)
        if "Message" in result:
            print("Listing production summary failed with message:\n%s" % result["Message"])
            exitCode = 2
        elif not result:
            print("Null result for getProduction() call", prodID)
            exitCode = 2
        else:
            exitCode = 0

    if not args:
        result = diracProd.getProductionProgress(printOutput=True)
        if "Message" in result:
            print("Listing production summary failed with message:\n%s" % result["Message"])
            exitCode = 2
        elif not result:
            print("Null result for getProduction() call")
            exitCode = 2
        else:
            exitCode = 0

    DIRAC.exit(exitCode)


if __name__ == "__main__":
    main()
