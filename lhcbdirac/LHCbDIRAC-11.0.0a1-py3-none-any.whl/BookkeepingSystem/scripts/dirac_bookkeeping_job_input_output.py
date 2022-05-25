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
"""It returns the input and output files of a given list of DIRAC Jobids."""
import os
from DIRAC.Core.Base.Script import Script


@Script()
def main():
    from LHCbDIRAC.DataManagementSystem.Client.DMScript import DMScript, printDMResult

    bkScript = DMScript()
    bkScript.registerJobsSwitches()
    Script.registerSwitch("", "InputFiles", "  Only input files")
    Script.registerSwitch("", "OutputFiles", "  Only output files")
    Script.setUsageMessage(
        __doc__
        + "\n".join(
            [
                "Usage:",
                "  %s [option|cfgfile] ... [DIRACJobid|File]" % Script.scriptName,
                "Arguments:",
                "  DIRACJobid:      DIRAC Jobids",
                "  File:     Name of the file with contains a list of DIRACJobids",
            ]
        )
    )

    Script.parseCommandLine(ignoreErrors=True)
    args = Script.getPositionalArgs()
    inputFiles = False
    outputFiles = False
    for switch in Script.getUnprocessedSwitches():
        if switch[0] == "InputFiles":
            inputFiles = True
        if switch[0] == "OutputFiles":
            outputFiles = True
    if not inputFiles and not outputFiles:
        inputFiles = True
        outputFiles = True
    jobidList = []
    for jobid in args:
        if os.path.exists(jobid):
            bkScript.setJobidsFromFile(jobid)
        else:
            jobidList += jobid.split(",")
    jobidList += bkScript.getOption("JobIDs", [])
    if not jobidList:
        print("No jobID provided!")
        Script.showHelp(exitCode=1)

    from LHCbDIRAC.BookkeepingSystem.Client.BookkeepingClient import BookkeepingClient

    retVal = BookkeepingClient().getJobInputOutputFiles(jobidList)
    if retVal["OK"]:
        success = retVal["Value"]["Successful"]
        for job in success:
            # Remove from input the files that are also output!
            # This happens because the output of step 1 can be the input of step 2...
            # only worth if input files are requested though
            if inputFiles:
                success[job]["InputFiles"] = sorted(set(success[job]["InputFiles"]) - set(success[job]["OutputFiles"]))

            if not inputFiles or not outputFiles:
                success[job].pop("InputFiles" if not inputFiles else "OutputFiles")

    printDMResult(retVal, empty="File does not exists in the Bookkeeping")


if __name__ == "__main__":
    main()
