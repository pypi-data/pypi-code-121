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
"""Check input files availability for a (list of) jobs."""
import six

from DIRAC import gLogger
from DIRAC.Core.Base.Script import Script


def inaccessibleReplicas(lfn, se):
    from DIRAC.DataManagementSystem.Client.DataManager import DataManager

    if isinstance(se, six.string_types):
        seList = [se]
    else:
        seList = se
    failed = {}
    for se in seList:
        res = DataManager().getReplicaMetadata(lfn, se)
        if not res["OK"]:
            gLogger.always("Error getting metadata of %s at %s" % (lfn, se), res["Message"])
            continue
        if lfn in res["Value"]["Failed"]:
            failed[se] = res["Value"]["Failed"][lfn]
    return failed


def prettyMsg(msg, msgList):
    areIs = "s are" if len(msgList) > 1 else " is"
    gLogger.always("The following file%s %s:\n%s" % (areIs, msg, "\n".join(msgList)))


@Script()
def main():
    from LHCbDIRAC.DataManagementSystem.Client.DMScript import DMScript, ProgressBar

    dmScript = DMScript()

    Script.registerSwitch("v", "Verbose", "   Set verbose mode")
    Script.registerSwitch("", "Production=", "   Select a production from which jobs in IDR will be used")
    Script.registerSwitch("", "User=", "  Select a user")

    Script.parseCommandLine(ignoreErrors=True)
    import DIRAC
    from DIRAC.WorkloadManagementSystem.Client.JobMonitoringClient import JobMonitoringClient

    verbose = False
    production = None
    userName = None
    for opt, val in Script.getUnprocessedSwitches():
        if opt in ("v", "Verbose"):
            verbose = True
        if opt == "Production":
            val = val.split(",")
            production = ["%08d" % int(prod) for prod in val if prod.isdigit()]
            production += [prod for prod in val if not prod.isdigit()]
        if opt == "User":
            userName = val

    jobs = []
    for arg in Script.getPositionalArgs():
        try:
            jobs += [int(job) for job in arg.split(",")]
        except ValueError:
            gLogger.fatal("Invalid list of jobIDs")
            DIRAC.exit(2)

    from DIRAC.DataManagementSystem.Client.DataManager import DataManager
    from LHCbDIRAC.BookkeepingSystem.Client.BookkeepingClient import BookkeepingClient
    from DIRAC.Core.Utilities.SiteSEMapping import getSEsForSite

    dm = DataManager()
    bk = BookkeepingClient()

    monitoring = JobMonitoringClient()

    if not jobs:
        conditions = {
            "Status": "Failed",
            "MinorStatus": "Maximum of reschedulings reached",
            "ApplicationStatus": "Failed Input Data Resolution ",
        }
        prStr = "all jobs"
        if production:
            prStr = "production %s" % " ".join(production)
            if len(production) == 1:
                production = production[0]
            conditions["JobGroup"] = production
        if userName:
            prStr = "user %s" % userName
            conditions["Owner"] = userName
        gLogger.always("Obtaining IDR jobs for %s" % prStr)
        res = monitoring.getJobs(conditions)
        if not res["OK"]:
            gLogger.always("Error selecting jobs for production %s" % str(production), res["Message"])
            DIRAC.exit(2)
        if not res["Value"]:
            gLogger.always("No jobs found with IDR for production %s" % str(production))
        elif verbose:
            gLogger.always("Selected %d jobs from production %s" % (len(res["Value"]), str(production)))
        jobs = [int(job) for job in res["Value"]]
        gLogger.always("Obtained %d jobs... Now analyzing them" % len(jobs))
    if not jobs:
        gLogger.always("No jobs to check, exiting...")
        DIRAC.exit(0)

    res = monitoring.getJobsSites(jobs)
    if not res["OK"]:
        gLogger.fatal("Error getting job sites", res["Message"])
        DIRAC.exit(2)
    gLogger.setLevel("FATAL")
    jobSites = res["Value"]
    filesAtSite = {}
    progressBar = ProgressBar(len(jobs), title="Getting JDL for %d jobs" % len(jobs), step=2)
    errors = {}
    for jobID in jobs:
        progressBar.loop()
        res = monitoring.getJobJDL(jobID, False)
        if not res["OK"]:
            gLogger.always("Error getting job %d JDL" % jobID, res["Message"])
            continue
        jdl = res["Value"].splitlines()
        ind = 0
        found = 0
        for line in jdl:
            if "InputData =" in line:
                found = ind
            if ind == found + 1:
                if "{" in line:
                    found = ind + 1
                else:
                    end = ind
            if found and "}" in line:
                end = ind
                break
            ind += 1
        if not found:
            errors.setdefault("No InputData field found in JDL", set()).add(jobID)
            continue
        if end == found + 1:
            inputData = dmScript.getLFNsFromList(jdl[found].split('"')[1])
        else:
            inputData = dmScript.getLFNsFromList(eval("[" + "".join(jdl[found:end]) + "]"))
        inputData.sort()
        if verbose:
            gLogger.always("Input Data for job %d\n%s" % (jobID, "\n".join(inputData)))
        site = jobSites.get(jobID, {}).get("Site", "Unknown")
        if verbose:
            gLogger.always("Site: %s" % site)
        for lfn in inputData:
            filesAtSite.setdefault(site, {}).setdefault(lfn, []).append(jobID)

    progressBar.endLoop()
    sep = ""
    for site in filesAtSite:
        seUsed = ""
        try:
            jobs = []
            for lfn in filesAtSite[site]:
                for jobID in filesAtSite[site][lfn]:
                    jobID = str(jobID)
                    if jobID not in jobs:
                        jobs.append(jobID)
            res = getSEsForSite(site)
            if not res["OK"] or not res["Value"]:
                gLogger.always("Couldn't find SEs for site %s" % site)
                continue
            seList = res["Value"]
            inputData = sorted(filesAtSite[site])
            if verbose:
                gLogger.always("%sSite: %s, jobs: %s, %d files" % (sep, site, ",".join(jobs), len(inputData)))
            else:
                gLogger.always("%sSite: %s, %d jobs, %d files" % (sep, site, len(jobs), len(inputData)))
            sep = "=====================================\n"
            if verbose:
                gLogger.always("For %s, SEs: %s" % (site, str(seList)))
            pbFound = False

            res = dm.getReplicas(inputData)
            if not res["OK"]:
                gLogger.always("Error getting replicas for %d files" % len(inputData), res["Message"])
                continue
            replicas = res["Value"]["Successful"]
            notInFC = res["Value"]["Failed"]
            if notInFC:
                # Check if files has replica flag in the FC, If not ignore the problem
                res = bk.getFileMetadata(list(notInFC))
                if not res["OK"]:
                    gLogger.always("Error getting BK metadata for %d files" % len(notInFC), res["Message"])
                    continue
                metadata = res["Value"]["Successful"]
                notInFC = [lfn for lfn in notInFC if metadata.get(lfn, {}).get("GotReplica") == "Yes"]
                if notInFC:
                    pbFound = True
                    prettyMsg("not in the FC but in BK", notInFC)
            notFoundReplicas = list(replicas)
            missingReplicas = []
            accessibleReplicas = []
            seUsed = []
            for lfn in [x for x in inputData if x in replicas]:
                for se in [se for se in replicas[lfn] if se in seList]:
                    # Found a replica at the site
                    if se not in seUsed:
                        seUsed.append(se)
                    if lfn in notFoundReplicas:
                        notFoundReplicas.remove(lfn)
                    inaccessible = inaccessibleReplicas(lfn, se)
                    if se in inaccessible:
                        reason = inaccessible[se]
                        otherReplicas = [s for s in replicas[lfn] if s != se]
                        inaccessible = inaccessibleReplicas(lfn, otherReplicas)
                        accessible = [s for s in otherReplicas if s not in inaccessible]
                        missingReplicas.append(
                            (
                                lfn,
                                se,
                                reason,
                                "Accessible at %s" % str(accessible) if accessible else "No other accessible replicas",
                            )
                        )
                        prStr = "not"
                    else:
                        prStr = ""
                    if verbose:
                        gLogger.always("%s is %s accessible at %s" % (lfn, prStr, se))
            if missingReplicas:
                pbFound = True
                msgList = ["%s at %s: %s\n\t%s" % x for x in missingReplicas]
                prettyMsg("not accessible", msgList)
            if notFoundReplicas:
                pbFound = True
                gLogger.always(
                    "%d files not found at SE close to %s, but have other replicas" % (len(notFoundReplicas), site)
                )
        except Exception as e:
            gLogger.always("%s" % e)
            pass
        finally:
            if not pbFound:
                gLogger.always(
                    "No particular problem was found with %d input file%s at %s (SEs: %s)"
                    % (len(inputData), "s" if len(inputData) > 1 else "", site, str(seUsed))
                )


if __name__ == "__main__":
    main()
