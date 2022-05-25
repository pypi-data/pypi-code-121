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
"""Set the Start or End Run for a given Transformation of add a set runs.

Examples of Usage :
  with 1234 = ProdID
  with 99000 = RunNumber
  dirac-production-set-run 1234 --List        (list of runs.)
  dirac-production-set-run 1234 --AddRuns 99000   (only for list of runs.)
  dirac-production-set-run 1234 --EndRun 99000   (change endrun.)
  dirac-production-set-run 1234 --StartRun 99000 (change startrun.)
"""
import DIRAC
from DIRAC.Core.Base.Script import Script


@Script()
def main():
    from DIRAC import gLogger

    Script.setUsageMessage(
        f"{__doc__}"
        f"Usage:\n"
        f"  {Script.scriptName} [option|cfgfile] ... Prod -Option [RunNumber|RunList]\n"
        "Arguments:\n"
        "  Prod:      DIRAC Production Id\n"
        "  RunNumber: New Start or End run\n"
        "  RunList: List of Runs to be added\n"
        "Examples:\n"
        "  # show the list of runs for transformation 92\n"
        "  dirac-production-set-run.py 92 --List\n"
        "  # add some discrete run to transformation 92\n"
        "  dirac-production-set-run.py 92 --AddRuns 98200,98201\n"
        "  # add some discrete run and a range of runs to transformation 92\n"
        "  dirac-production-set-run.py 92 --AddRuns 98200,98201,99000:99100\n"
        "  # change the start run for transformation 92\n"
        "  dirac-production-set-run.py 92 --StartRun 98200\n"
        "  # change the end run  for transformation 92\n"
        "  dirac-production-set-run.py 92 --EndRun   98200\n"
    )

    Script.registerSwitch("", "EndRun=", "Specify endrun for the transformation")
    Script.registerSwitch("", "StartRun=", "Specify startrun for the transformation")
    Script.registerSwitch("", "AddRuns=", "add List of runs to the transformation")
    Script.registerSwitch("", "List", "List the runs for the transformation")

    Script.parseCommandLine(ignoreErrors=True)

    from LHCbDIRAC.TransformationSystem.Utilities.ScriptUtilities import getTransformations

    transList = getTransformations(Script.getPositionalArgs())

    settings = {}
    for opt, val in Script.getUnprocessedSwitches():
        if opt in ("StartRun", "EndRun"):
            try:
                settings[opt] = int(val)
            except TypeError:
                gLogger.error("Invalid run number:", str(val))
                DIRAC.exit(1)
        elif opt == "AddRuns":
            try:
                settings[opt] = [int(runID) for runID in val.split(",")]
            except TypeError:
                gLogger.error("Invalid run list", str(val))
                DIRAC.exit(1)
        elif opt == "List":
            settings[opt] = True
    if "AddRuns" in settings and ("StartRun" in settings or "EndRun" in settings):
        gLogger.error("Incompatible requests, cannot set run list and start/end run")
        DIRAC.exit(1)

    from LHCbDIRAC.TransformationSystem.Client.TransformationClient import TransformationClient

    client = TransformationClient()

    for prodId in transList:
        res = client.getBookkeepingQuery(prodId)
        if not res["OK"]:
            gLogger.error("Error retrieving BKQuery for transformation %s" % prodId, res["Message"])
            DIRAC.exit(2)
        bkDict = res["Value"]
        startRun = bkDict.get("StartRun", 0)
        endRun = bkDict.get("EndRun", 0)
        runNumbers = bkDict.get("RunNumbers", "All")

        if ("StartRun" in settings or "EndRun" in settings) and runNumbers and runNumbers != "All":
            gLogger.notice("Transformation %d has RunNumbers key" % prodId)
            settings = {"List": True}

        if "AddRuns" in settings and (startRun or endRun):
            gLogger.notice("Transformation %d has start run or end run: %s:%s" % (prodId, str(startRun), str(endRun)))
            settings = {"List": True}

        if "AddRuns" in settings and (not runNumbers or runNumbers == "All"):
            gLogger.notice("Transformation %d doesn't have RunNumbers key or set to All" % prodId)
            settings = {"List": True}

        if not isinstance(runNumbers, list):
            runNumbers = [runNumbers]

        changed = False
        if "StartRun" in settings:
            changed = True
            runId = settings["StartRun"]
            res = client.setBookkeepingQueryStartRun(prodId, runId)
            if res["OK"]:
                gLogger.notice("Start run of transformation %d is now %d" % (prodId, runId))
                startRun = runId
            else:
                gLogger.error("Error setting start run", res["Message"])

        if "EndRun" in settings:
            changed = True
            runId = settings["EndRun"]
            res = client.setBookkeepingQueryEndRun(prodId, runId)
            if res["OK"]:
                gLogger.notice("End run of transformation %d is now %d" % (prodId, runId))
                endRun = runId
            else:
                gLogger.error("Error setting end run", res["Message"])

        if "AddRuns" in settings:
            changed = True
            runList = [int(run) for run in settings["AddRuns"] if run not in runNumbers]
            res = client.addBookkeepingQueryRunList(prodId, runList)
            if res["OK"]:
                gLogger.notice("Run list modified for transformation %d" % prodId)
                runNumbers += runList
            else:
                gLogger.error("Error modifying run list:", res["Message"])

        if "List" in settings:
            gLogger.notice("%sRun selection settings for transformation %d:" % ("\n" if changed else "", prodId))
            if runNumbers:
                gLogger.notice("List of runs: %s" % ",".join([str(run) for run in sorted(runNumbers)]))
            else:
                if startRun:
                    gLogger.notice("Start run is %s" % startRun)
                else:
                    gLogger.notice("No start run defined ")
                if endRun:
                    gLogger.notice("End run is %s" % endRun)
                else:
                    gLogger.notice("No end run defined ")


if __name__ == "__main__":
    main()
