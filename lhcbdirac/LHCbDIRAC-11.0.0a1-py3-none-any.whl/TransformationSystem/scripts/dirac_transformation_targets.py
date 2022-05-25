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
"""Gets all Assigned files in a transformation and reports by target SE."""

from collections import defaultdict
from DIRAC.Core.Base.Script import Script


def __getTask(transClient, transID, taskID):
    """Get a task in TS from the transformation and task IDs"""
    res = transClient.getTransformationTasks({"TransformationID": transID, "TaskID": taskID})
    if not res["OK"] or not res["Value"]:
        return None
    return res["Value"][0]


def initStat():
    """Just to initialise a defaultdict to [0,0]"""
    return [0, 0]


@Script()
def main():
    from LHCbDIRAC.TransformationSystem.Utilities.ScriptUtilities import getTransformations

    Script.parseCommandLine(ignoreErrors=True)
    transList = getTransformations(Script.getPositionalArgs())

    from LHCbDIRAC.TransformationSystem.Client.TransformationClient import TransformationClient
    from DIRAC import gLogger

    transClient = TransformationClient()

    for transID in transList:
        res = transClient.getTransformationFiles({"TransformationID": transID, "Status": "Assigned"})
        if not res["OK"]:
            gLogger.fatal("Error getting transformation files for %d" % transID)
            continue
        targetStats = defaultdict(initStat)
        taskDict = defaultdict(int)
        for fileDict in res["Value"]:
            taskID = fileDict["TaskID"]
            taskDict[taskID] += 1
        for taskID in taskDict:
            task = __getTask(transClient, transID, taskID)
            targetSE = task.get("TargetSE", None)
            targetStats[targetSE][0] += taskDict[taskID]
            targetStats[targetSE][1] += 1

        gLogger.always("Transformation %d: %d assigned files found" % (transID, len(res["Value"])))
        for targetSE, (nfiles, ntasks) in targetStats.items():
            gLogger.always("\t%s: %d files in %d tasks" % (targetSE, nfiles, ntasks))


if __name__ == "__main__":
    main()
