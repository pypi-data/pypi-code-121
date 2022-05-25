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
"""Debug files status for a (list of) transformations It is possible to do
minor fixes to those files, using options."""

from DIRAC.Core.Base.Script import Script


@Script()
def main():
    from LHCbDIRAC.DataManagementSystem.Client.DMScript import DMScript

    infoList = ("files", "runs", "tasks", "jobs", "alltasks", "flush", "log")
    statusList = (
        "Unused",
        "Assigned",
        "Done",
        "Problematic",
        "MissingInFC",
        "MaxReset",
        "Processed",
        "NotProcessed",
        "Removed",
        "ProbInFC",
    )
    dmScript = DMScript()
    dmScript.registerFileSwitches()
    Script.registerSwitch("", "Info=", "Specify what to print out from %s" % str(infoList))
    Script.registerSwitch("", "Status=", "Select files with a given status from %s" % str(statusList))
    Script.registerSwitch("", "Runs=", "Specify a (list of) runs")
    Script.registerSwitch(
        "", "ExceptActiveRunsFromProduction=", "Do not consider runs with active files from these prods"
    )
    Script.registerSwitch("", "SEs=", "Specify a (list of) target SEs")
    Script.registerSwitch("", "Tasks=", "Specify a (list of) tasks")
    Script.registerSwitch("", "Jobs=", "Specify a (list of) jobs")
    Script.registerSwitch("", "DumpFiles", "Dump the list of LFNs on stdout")
    Script.registerSwitch("", "Statistics", "Get the statistics of tasks per status and SE")
    Script.registerSwitch("", "FixRun", "Fix the run number in transformation table")
    Script.registerSwitch("", "FixIt", "Fix the FC")
    Script.registerSwitch("", "KickRequests", "Reset old Assigned requests to Waiting")
    Script.registerSwitch("", "CheckWaitingTasks", "Check if waiting tasks are failed, done or orphan")
    Script.registerSwitch("", "CheckSubmittedTasks", "Check Submitted tasks that do not have an external ID")
    Script.registerSwitch("v", "Verbose", "")
    Script.setUsageMessage(
        "\n".join([__doc__, "Usage:", "  dirac-transformation-debug [options] transID[,transID2[,transID3[,...]]]"])
    )

    Script.parseCommandLine(ignoreErrors=True)

    from LHCbDIRAC.TransformationSystem.Client.TransformationDebug import TransformationDebug

    TransformationDebug().debugTransformation(dmScript, infoList, statusList)


if __name__ == "__main__":
    main()
