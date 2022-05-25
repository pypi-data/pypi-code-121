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
"""Perform comprehensive checks on the supplied log file if it exists."""
import DIRAC
from DIRAC.Core.Base.Script import Script


@Script()
def main():

    Script.registerSwitch("f:", "XMLSummary=", "Path to XML summary you wish to analyze (mandatory)")

    Script.setUsageMessage(__doc__ + "\n".join(["Usage:", "  %s [option|cfgfile] ... CE" % Script.scriptName]))
    Script.parseCommandLine(ignoreErrors=True)

    from DIRAC import gLogger
    from LHCbDIRAC.Core.Utilities.XMLSummaries import analyseXMLSummary

    args = Script.getPositionalArgs()

    logFile = ""
    projectName = ""

    # Start the script and perform checks
    if args or not Script.getUnprocessedSwitches():
        Script.showHelp()

    for switch in Script.getUnprocessedSwitches():
        if switch[0].lower() in ("f", "XMLSummary"):
            logFile = switch[1]

    exitCode = 0
    try:
        analyseXMLSummary(logFile, projectName)
    except Exception as x:
        gLogger.exception('XML summary analysis failed with exception: "%s"' % x)
        exitCode = 2
        DIRAC.exit(exitCode)

    DIRAC.exit(exitCode)


if __name__ == "__main__":
    main()
