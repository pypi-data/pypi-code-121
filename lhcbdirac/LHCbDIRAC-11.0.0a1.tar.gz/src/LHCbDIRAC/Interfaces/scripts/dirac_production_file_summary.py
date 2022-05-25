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


def getBoolean(value):
    if value.lower() == "true":
        return True
    elif value.lower() == "false":
        return False
    else:
        print("ERROR: expected boolean")
        DIRAC.exit(2)


def usage():
    """usage.

    Prints script usage
    """
    print("Usage: %s <ProductionID> <Options> [Try -h,--help for more information]" % Script.scriptName)
    DIRAC.exit(2)


@Script()
def main():
    # Default values
    status = None
    outFile = None
    summary = True
    printVerbose = False

    Script.registerSwitch("", "Status=", "ProductionDB file status to select")
    Script.registerSwitch("", "OutputFile=", "Output file to store file records")
    Script.registerSwitch("", "Summary=", "Print a summary of the files (True/False) default is True")
    Script.registerSwitch("", "PrintOutput=", "Print all file records (extremely verbose) default is False")
    Script.parseCommandLine(ignoreErrors=True)

    from LHCbDIRAC.Interfaces.API.DiracProduction import DiracProduction

    for switch in Script.getUnprocessedSwitches():
        if switch[0].lower() == "status":
            status = switch[1]
        elif switch[0].lower() == "outputfile":
            outFile = switch[1]
        elif switch[0].lower() == "summary":
            summary = getBoolean(switch[1])
        elif switch[0].lower() == "printoutput":
            printVerbose = getBoolean(switch[1])

    args = Script.getPositionalArgs()

    if len(args) != 1:
        usage()

    exitCode = 0

    diracProd = DiracProduction()

    productionID = args[0]
    try:
        productionID = int(productionID)
    except Exception as x:
        print("Production ID must be an integer, not %s:\n%s" % (productionID, x))
        DIRAC.exit(2)

    result = diracProd.productionFileSummary(
        productionID,
        selectStatus=status,
        outputFile=outFile,
        printSummary=summary,
        printOutput=printVerbose,
    )
    if not result["OK"]:
        print("ERROR %s" % result["Message"])
        exitCode = 2

    DIRAC.exit(exitCode)


if __name__ == "__main__":
    main()
