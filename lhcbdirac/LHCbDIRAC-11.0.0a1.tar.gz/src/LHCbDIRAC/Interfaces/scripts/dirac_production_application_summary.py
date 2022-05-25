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
    print("Usage: %s <Production ID> <DIRAC Status>" % (Script.scriptName))
    DIRAC.exit(2)


@Script()
def main():
    Script.parseCommandLine(ignoreErrors=True)
    from LHCbDIRAC.Interfaces.API.DiracProduction import DiracProduction

    args = Script.getPositionalArgs()

    if len(args) < 2:
        usage()

    diracProd = DiracProduction()
    prodID = args[0]
    stat = args[1]
    result = diracProd.getProductionApplicationSummary(prodID, status=stat, printOutput=True)
    if result["OK"]:
        DIRAC.exit(0)
    elif "Message" in result:
        print("Getting production application status summary failed with message:\n%s" % (result["Message"]))
        DIRAC.exit(2)
    else:
        print("Null result for getProductionApplicationSummary() call")
        DIRAC.exit(2)


if __name__ == "__main__":
    main()
