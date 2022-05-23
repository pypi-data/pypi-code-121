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
"""
Returns metadata of the job step(s) that created a (list of) LFNs,
or all steps for a (list of) JobID
"""
from DIRAC.Core.Utilities.DIRACScript import DIRACScript


@DIRACScript()
def main():
    from DIRAC.Core.Base import Script

    from DIRAC import gLogger
    from LHCbDIRAC.DataManagementSystem.Client.DMScript import DMScript, printDMResult

    bkScript = DMScript()
    bkScript.registerFileSwitches()
    Script.registerSwitch("", "Summary", "   Only report job IDs creating the LFN(s)")
    Script.setUsageMessage(
        __doc__
        + "\n".join(
            [
                "Usage:",
                "  %s [option|cfgfile] ... [LFN|File|JobID]" % Script.scriptName,
                "Arguments:",
                "  LFN:      Logical File Name",
                "  File:     Name of the file with a list of LFNs",
                "  JobID:    DIRAC job identifier",
            ]
        )
    )

    Script.parseCommandLine(ignoreErrors=True)
    args = Script.getPositionalArgs()
    jobIDList = []
    for arg in args:
        if arg.isdigit():
            jobIDList.append(int(arg))
        else:
            bkScript.setLFNsFromFile(arg)
    lfnList = bkScript.getOption("LFNs", [])
    if not lfnList and not jobIDList:
        Script.showHelp(exitCode=1)
    summary = False
    for switch in Script.getUnprocessedSwitches():
        if switch[0] == "Summary":
            summary = True

    from LHCbDIRAC.BookkeepingSystem.Client.BookkeepingClient import BookkeepingClient

    if lfnList:
        retVal = BookkeepingClient().bulkJobInfo(lfnList)
    elif jobIDList:
        retVal = BookkeepingClient().bulkJobInfo({"jobId": jobIDList})
        summary = False
    jobLFNs = {}
    if retVal["OK"]:
        success = retVal["Value"]["Successful"]
        jobDict = {}
        for item in list(success):
            jobs = success.pop(item)
            # Note that item may be a jobID or an LFN
            if not item.isdigit():
                #   item is an LFN, hence only one job step (job in BK)
                lfn = item
                job = jobs[0]
                jobLFNs.setdefault(job["Name"], []).append(lfn)
                jobDict.setdefault(job["Name"], job)
            else:
                jobID = item
                # item is a jobID, hence we may have a list of job steps
                if int(jobID) in retVal["Value"]["Failed"]:
                    # For some reason sometimes (always?) the jobID is also in Failed
                    retVal["Value"]["Failed"].remove(int(jobID))
                jobStr = "Job %s" % jobID
                stepDict = {"Job": {"CPUTIME": 0.0, "ExecTime": 0.0, "NumberOfSteps": len(jobs)}}
                for job in jobs:
                    # Group common info into a separate dictionary (and remove it from steps)
                    job.pop("DIRACJobId")
                    # ... and yes, it is TotalLumonosity ;-)
                    for info in (
                        "DIRACVersion",
                        "Location",
                        "Production",
                        "TotalLumonosity",
                        "WNCACHE",
                        "WNCPUHS06",
                        "WNCPUPOWER",
                        "WNMEMORY",
                        "WNMJFHS06",
                        "WNMODEL",
                        "WORKERNODE",
                    ):
                        stepDict["Job"][info] = job.pop(info, None)
                    # Sum up CPU and wall clock times
                    for info in ("CPUTIME", "ExecTime"):
                        stepDict["Job"][info] += job[info]
                    step = "Step %s" % job.pop("Name")
                    stepDict[step] = job
                success[jobStr] = stepDict

        # When LFNs were given, rearrange the success dictionary in case several files were created by the same step
        if not summary and jobLFNs:
            # Group files produced by the same job
            lfnsByJob = {}
            for name, job in jobDict.items():  # Can be an iterator
                # For each jobID get set of LFNs and job steps
                lfnsByJob.setdefault(job["DIRACJobId"], []).append((jobLFNs[name], job))
            for jobID, lfnJobs in lfnsByJob.items():  # Can be an iterator
                jobStr = "Job %s" % jobID
                # Split job and step information
                stepDict = {jobStr: {}}
                lfnSet = set()
                for lfns, job in lfnJobs:
                    job.pop("DIRACJobId")
                    lfnSet.update(lfns)
                    for info in (
                        "DIRACVersion",
                        "Location",
                        "Production",
                        "TotalLumonosity",
                        "WNCACHE",
                        "WNCPUHS06",
                        "WNCPUPOWER",
                        "WNMEMORY",
                        "WNMJFHS06",
                        "WNMODEL",
                        "WORKERNODE",
                    ):
                        stepDict[jobStr][info] = job.pop(info, None)
                    job[" LFN"] = ",".join(sorted(lfns))
                    stepDict["Step %s" % job.pop("Name")] = job
                success[",".join(sorted(lfnSet))] = stepDict

    if summary and jobLFNs:
        gLogger.always("List of DIRAC jobs:")
        gLogger.always(
            ",".join(sorted(set("%s" % val["DIRACJobId"] for val in jobDict.values())))
        )  # Can be an iterator
    else:
        printDMResult(retVal, empty="File/job does not exist in the Bookkeeping")


if __name__ == "__main__":
    main()
