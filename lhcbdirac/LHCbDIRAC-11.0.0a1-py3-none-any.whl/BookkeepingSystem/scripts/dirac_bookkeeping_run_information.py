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
"""Retrieve from Bookkeeping information for a given run."""
import DIRAC
from DIRAC import gLogger, S_OK
from DIRAC.Core.Base.Script import Script


@Script()
def main():

    Script.registerSwitch("", "Production=", "   <prodID>, get the run list from a production")
    Script.registerSwitch("", "Active", "   only get Active runs")
    Script.registerSwitch("", "Information=", "   <item> returns only the relevant information item")
    Script.registerSwitch(
        "", "ByValue", "   if set, the information is a list of runs for each value of the information item"
    )
    Script.setUsageMessage(
        __doc__
        + "\n".join(
            ["Usage:", "  %s [option|cfgfile] ... Run" % Script.scriptName, "Arguments:", "  Run:      Run Number"]
        )
    )
    Script.parseCommandLine(ignoreErrors=True)
    runRanges = []
    for arg in Script.getPositionalArgs():
        runRanges += arg.split(",")

    runSet = set()
    for run in runRanges:
        try:
            if ":" in arg:
                run1, run2 = run.split(":")
                runSet.update(range(int(run1), int(run2) + 1))
            else:
                runSet.add(int(run))
        except (ValueError, IndexError) as e:
            gLogger.exception("Invalid run number", arg, lException=e)
            DIRAC.exit(1)

    production = None
    item = None
    byValue = False
    active = False
    for switch in Script.getUnprocessedSwitches():
        if switch[0] == "Production":
            try:
                production = [int(prod) for prod in switch[1].split(",")]
            except ValueError as e:
                gLogger.exception("Bad production ID", lException=e)
                DIRAC.exit(1)
        elif switch[0] == "Information":
            item = switch[1]
        elif switch[0] == "ByValue":
            byValue = True
        elif switch[0] == "Active":
            active = True

    from LHCbDIRAC.DataManagementSystem.Client.DMScript import printDMResult, ProgressBar
    from LHCbDIRAC.BookkeepingSystem.Client.BookkeepingClient import BookkeepingClient

    bk = BookkeepingClient()

    if production:
        from LHCbDIRAC.TransformationSystem.Client.TransformationClient import TransformationClient

        trClient = TransformationClient()
        condDict = {"TransformationID": production}
        if active:
            condDict["Status"] = "Active"
        res = trClient.getTransformationRuns(condDict)
        if res["OK"]:
            runSet.update(run["RunNumber"] for run in res["Value"])
        else:
            gLogger.fatal("Error getting production runs", res["Message"])
            DIRAC.exit(2)
        gLogger.notice("Found %d runs" % len(runSet))

    # Use this call to get information but also the actual list of existing runs
    res = bk.getRunStatus(list(runSet))
    if not res["OK"]:
        gLogger.fatal("Error getting the run info", res["Message"])
        DIRAC.exit(2)
    runStatus = res["Value"]["Successful"]

    sep = ""
    if item:
        result = {"Successful": {}, "Failed": {}}
        success = result["Successful"]
        failed = result["Failed"]
        if item == "Finished":
            # We can get it in a single call
            for run in runStatus:
                finished = {"N": "No", "Y": "Yes"}.get(runStatus.get(run, {}).get("Finished"), "Unknown")
                if byValue:
                    success.setdefault(finished, []).append(run)
                else:
                    success[run] = finished
        else:
            progressBar = ProgressBar(len(runStatus), title="Getting %s for %d runs" % (item, len(runStatus)), step=10)

    if item != "Finished":
        for run in sorted(runStatus):
            if item:
                progressBar.loop()
            finished = {"N": "No", "Y": "Yes"}.get(runStatus[run].get("Finished"), "Unknown")

            res = bk.getRunInformations(run)
            if res["OK"]:
                info = res["Value"]
                if item:
                    if item not in info:
                        gLogger.error("Item not found", "\n Valid items: %s" % str(sorted(info)))
                        DIRAC.exit(3)
                    itemValue = info.get(item, "Unknown")
                    if byValue:
                        success.setdefault(itemValue, []).append(run)
                    else:
                        result["Successful"][run] = itemValue
                    continue
                runstart = info.get("RunStart", "Unknown")
                runend = info.get("RunEnd", "Unknown")
                configname = info.get("Configuration Name", "Unknown")
                configversion = info.get("Configuration Version", "Unknown")
                fillnb = info.get("FillNumber", "Unknown")
                datataking = info.get("DataTakingDescription", "Unknown")
                processing = info.get("ProcessingPass", "Unknown")
                stream = info.get("Stream", "Unknown")
                fullstat = info.get("FullStat", "Unknown")
                nbofe = info.get("Number of events", "Unknown")
                nboff = info.get("Number of file", "Unknown")
                fsize = info.get("File size", "Unknown")
                totalLuminosity = info.get("TotalLuminosity", "Unknown")
                tck = info.get("Tck", "Unknown")

                if sep:
                    print(sep)
                print("Run  Informations for run %d: " % run)
                print("Run Start:".ljust(30), str(runstart))
                print("Run End:".ljust(30), str(runend))
                print("Total luminosity:".ljust(30), str(totalLuminosity))
                print("  Configuration Name:".ljust(30), configname)
                print("  Configuration Version:".ljust(30), configversion)
                print("  FillNumber:".ljust(30), fillnb)
                print("  Finished:".ljust(30), finished)
                print("  Data taking description:".ljust(30), datataking)
                print("  Processing pass:".ljust(30), processing)
                print("  TCK:".ljust(30), tck)
                print("  Stream:".ljust(30), stream)
                just = len(str(fsize)) + 3
                print("  FullStat:".ljust(30), str(fullstat).ljust(just), " Total: ".ljust(10) + str(sum(fullstat)))
                print("  Number of events:".ljust(30), str(nbofe).ljust(just), " Total:".ljust(10) + str(sum(nbofe)))
                print("  Number of files:".ljust(30), str(nboff).ljust(just), " Total: ".ljust(10) + str(sum(nboff)))
                print("  File size:".ljust(30), str(fsize).ljust(just), " Total: ".ljust(10) + str(sum(fsize)))
                sep = 20 * "="
            elif item:
                failed[run] = res["Message"]
        if item:
            progressBar.endLoop()

    if item:
        if not failed:
            del failed
        if byValue:
            for val in success:
                success[val] = ("(%d runs) - " % len(success[val])) + (
                    ",".join(sorted(str(run) for run in success[val]))
                )
        printDMResult(S_OK(result), empty="None", script="dirac-bookkeeping-run-information")


if __name__ == "__main__":
    main()
