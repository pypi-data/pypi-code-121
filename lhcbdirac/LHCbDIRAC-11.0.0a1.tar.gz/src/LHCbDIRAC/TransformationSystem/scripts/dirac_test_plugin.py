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
 Test a plugin
"""
import DIRAC
from DIRAC import S_OK
from DIRAC.Core.Base.Script import Script


class FakeClient(object):
    def __init__(self, trans, transID, lfns, asIfProd):
        self.trans = trans
        self.transID = transID
        from DIRAC.TransformationSystem.Client.TransformationClient import TransformationClient

        self.transClient = TransformationClient()
        from LHCbDIRAC.BookkeepingSystem.Client.BookkeepingClient import BookkeepingClient

        self.bk = BookkeepingClient()
        from DIRAC.DataManagementSystem.Client.DataManager import DataManager

        self.dm = DataManager()
        self.asIfProd = asIfProd

        (self.transFiles, self.transReplicas) = self.prepareForPlugin(lfns)

    def addFilesToTransformation(self, transID, lfns):
        return S_OK({"Failed": {}, "Successful": dict([(lfn, "Added") for lfn in lfns])})

    def getTransformation(self, transID, extraParams=False):
        if transID == self.transID and self.asIfProd:
            transID = self.asIfProd
        if transID != self.transID:
            return self.transClient.getTransformation(transID)
        res = self.trans.getType()
        return DIRAC.S_OK({"Type": res["Value"]})

    def getReplicas(self):
        return self.transReplicas

    def getFiles(self):
        return self.transFiles

    def getCounters(self, table, attrList, condDict):
        if condDict["TransformationID"] == self.transID and self.asIfProd:
            condDict["TransformationID"] = self.asIfProd
        if condDict["TransformationID"] != self.transID:
            return self.transClient.getCounters(table, attrList, condDict)
        possibleTargets = [
            "CERN-RAW",
            "CNAF-RAW",
            "GRIDKA-RAW",
            "IN2P3-RAW",
            "SARA-RAW",
            "PIC-RAW",
            "RAL-RAW",
            "RRCKI-RAW",
        ]
        counters = [({"UsedSE": se}, 0) for se in possibleTargets]
        return DIRAC.S_OK(counters)

    def getTransformations(self, cond):
        res = self.transClient.getTransformations(cond)
        if res["OK"]:
            res["Value"].append({"TransformationID": self.transID})
            if self.asIfProd and self.asIfProd not in [t["TransformationID"] for t in res["Value"]]:
                res["Value"].append({"TransformationID": self.asIfProd})
        return res

    def getBookkeepingQuery(self, transID):
        if transID == self.transID and self.asIfProd:
            return self.transClient.getBookkeepingQuery(self.asIfProd)
        return self.trans.getBkQuery()

    def insertTransformationRun(self, transID, runID, xx):
        return DIRAC.S_OK()

    def getTransformationRuns(self, condDict):
        if condDict["TransformationID"] == self.transID and self.asIfProd:
            condDict["TransformationID"] = self.asIfProd
        if condDict["TransformationID"] == self.transID:
            transRuns = []
            runs = condDict.get("RunNumber", [])
            if not runs and self.transFiles:
                res = self.bk.getFileMetadata([fileDict["LFN"] for fileDict in self.transFiles])
                if not res["OK"]:
                    return res
                runs = list(set(meta["RunNumber"] for meta in res["Value"]["Successful"].values()))
            for run in runs:
                transRuns.append({"RunNumber": run, "Status": "Active", "SelectedSite": None})
            return DIRAC.S_OK(transRuns)
        else:
            return self.transClient.getTransformationRuns(condDict)

    def getTransformationFiles(self, condDict=None):
        if condDict.get("TransformationID") == self.transID and self.asIfProd:
            condDict["TransformationID"] = self.asIfProd
        if condDict.get("TransformationID") == self.transID:
            transFiles = []
            if "Status" in condDict and "Unused" not in condDict["Status"]:
                return DIRAC.S_OK(transFiles)
            runs = None
            if "RunNumber" in condDict:
                runs = condDict["RunNumber"]
                if not isinstance(runs, list):
                    runs = [runs]
            for fileDict in self.transFiles:
                if not runs or fileDict["RunNumber"] in runs:
                    transFiles.append({"LFN": fileDict["LFN"], "Status": "Unused", "RunNumber": fileDict["RunNumber"]})
            return DIRAC.S_OK(transFiles)
        else:
            return self.transClient.getTransformationFiles(condDict=condDict)

    def setParameterToTransformationFiles(self, transID, lfnDict):
        """Update the transFiles with some parameters."""
        if transID == self.transID:
            for fileDict in self.transFiles:
                fileDict.update(lfnDict.get(fileDict["LFN"], {}))
            return S_OK()
        else:
            return self.transClient.setParameterToTransformationFiles(transID, lfnDict)

    def getTransformationFilesCount(self, transID, field, selection=None):
        if selection is None:
            selection = {}
        if transID == self.transID or selection.get("TransformationID") == self.transID:
            runs = selection.get("RunNumber")
            if runs and not isinstance(runs, list):
                runs = [runs]
            if field == "Status":
                counters = {"Unused": 0}
                for fileDict in self.transFiles:
                    if not runs or fileDict["RunNumber"] in runs:
                        counters["Unused"] += 1
            elif field == "RunNumber":
                counters = {}
                for fileDict in self.transFiles:
                    runID = fileDict["RunNumber"]
                    if not runs or runID in runs:
                        counters.setdefault(runID, 0)
                        counters[runID] += 1
            else:
                return DIRAC.S_ERROR("Not implemented for field " + field)
            counters["Total"] = sum(count for count in counters.values())
            return DIRAC.S_OK(counters)
        else:
            return self.transClient.getTransformationFilesCount(transID, field, selection=selection)

    def getTransformationRunStats(self, transIDs):
        counters = {}
        for transID in transIDs:
            if transID == self.transID:
                for fileDict in self.transFiles:
                    runID = fileDict["RunNumber"]
                    counters[transID][runID]["Unused"] = (
                        counters.setdefault(transID, {}).setdefault(runID, {}).setdefault("Unused", 0) + 1
                    )
                for runID in counters[transID]:
                    counters[transID][runID]["Total"] = counters[transID][runID]["Unused"]
            else:
                res = self.transClient.getTransformationRunStats(transIDs)
                if res["OK"]:
                    counters.update(res["Value"])
                else:
                    return res
        return DIRAC.S_OK(counters)

    def addRunsMetadata(self, runID, val):
        return self.transClient.addRunsMetadata(runID, val)

    def getRunsMetadata(self, runID):
        return self.transClient.getRunsMetadata(runID)

    def setTransformationRunStatus(self, transID, runID, status):
        return DIRAC.S_OK()

    def setTransformationRunsSite(self, transID, runID, site):
        return DIRAC.S_OK()

    def setFileStatusForTransformation(self, transID, status, lfns):
        return DIRAC.S_OK()

    def addTransformationRunFiles(self, transID, run, lfns):
        return DIRAC.S_OK()

    def setDestinationForRun(self, runID, site):
        return DIRAC.S_OK()

    def getDestinationForRun(self, runID):
        return self.transClient.getDestinationForRun(runID)

    def prepareForPlugin(self, lfns):
        import time

        print("Preparing the plugin input data (%d files)" % len(lfns))
        type = self.trans.getType()["Value"]
        if not lfns:
            return (None, None)
        res = self.bk.getFileMetadata(lfns)
        if res["OK"]:
            files = []
            for lfn, metadata in res["Value"]["Successful"].items():
                runID = metadata.get("RunNumber", 0)
                runDict = {"RunNumber": runID, "LFN": lfn}
                files.append(runDict)
        else:
            print("Error getting BK metadata", res["Message"])
            return ([], {})
        replicas = {}
        startTime = time.time()
        from DIRAC.Core.Utilities.List import breakListIntoChunks

        for lfnChunk in breakListIntoChunks(lfns, 200):
            # print lfnChunk
            if type.lower() in ("replication", "removal"):
                res = self.dm.getReplicas(lfnChunk, getUrl=False)
            else:
                res = self.dm.getReplicasForJobs(lfnChunk, getUrl=False)
            # print res
            if res["OK"]:
                for lfn, ses in res["Value"]["Successful"].items():
                    if ses:
                        replicas[lfn] = sorted(ses)
            else:
                print("Error getting replicas of %d files:" % len(lfns), res["Message"])
        print("Obtained replicas of %d files in %.3f seconds" % (len(lfns), time.time() - startTime))
        return (files, replicas)


def printFinalSEs(transType, location, targets):
    targets = targets.split(",")
    if transType == "Removal":
        remain = []
        for x in location:
            r = ",".join([se for se in x.split(",") if se not in targets])
            remain.append(r)
        print("    Remaining SEs:", remain)
    if transType == "Replication":
        total = []
        for x in location:
            r = x + "," + ",".join([se for se in targets if se not in x.split(",")])
            total.append(r)
        print("    Final SEs:", total)


@Script()
def main():
    import DIRAC
    from LHCbDIRAC.TransformationSystem.Utilities.PluginScript import PluginScript

    pluginScript = PluginScript()
    pluginScript.registerPluginSwitches()
    pluginScript.registerFileSwitches()

    Script.registerSwitch("", "AsIfProduction=", "   Production # that this test using as source of information")
    Script.registerSwitch("", "AllFiles", "   Sets visible = False (useful if files were marked invisible)")
    Script.registerSwitch("", "NoReplicaFiles", "   Also gets the files without replica (just for BK test)")
    Script.registerSwitch("", "DefaultOptions", "   Gets from CS the default options for a plugin")

    Script.setUsageMessage(
        __doc__
        + "\n".join(
            [
                "Usage:",
                "  %s [option|cfgfile] ..." % Script.scriptName,
            ]
        )
    )

    Script.parseCommandLine(ignoreErrors=True)

    from DIRAC.ConfigurationSystem.Client.Helpers.Operations import Operations
    from LHCbDIRAC.TransformationSystem.Client.Transformation import Transformation
    from LHCbDIRAC.TransformationSystem.Utilities.PluginUtilities import getRemovalPlugins, getReplicationPlugins
    from DIRAC import gLogger

    asIfProd = None
    allFiles = False
    noRepFiles = False
    defaultOptions = False
    switches = Script.getUnprocessedSwitches()
    for opt, val in switches:
        if opt == "AsIfProduction":
            asIfProd = int(val)
        elif opt == "AllFiles":
            allFiles = True
        elif opt == "NoReplicaFiles":
            noRepFiles = True
        elif opt == "DefaultOptions":
            defaultOptions = True
    # print pluginScript.getOptions()
    plugin = pluginScript.getOption("Plugin")

    # Just get and print default options from the CS
    if defaultOptions:
        if not plugin:
            gLogger.fatal("No plugin specified")
            DIRAC.exit(1)
        # Get default options from CS
        res = Operations().getOptionsDict("TransformationPlugins/%s" % plugin)
        if res["OK"]:
            gLogger.notice("Parameters for plugin %s (*<param> means it is a generic parameter)" % plugin)
            options = res["Value"]
            # Get default options for all plugins
            res = Operations().getOptionsDict("TransformationPlugins")
            if res["OK"]:
                allOptions = res["Value"]
                for opt in set(allOptions) - set(options):
                    if opt in pluginScript.seParameters:
                        options["*" + opt] = allOptions[opt]
            # SE options first
            for opt in [opt for opt in sorted(options) if "SEs" in opt]:
                gLogger.notice("\t%s : %s" % (opt, options[opt]))
            # Other options
            for opt in [opt for opt in sorted(options) if "SEs" not in opt]:
                gLogger.notice("\t%s : %s" % (opt, options[opt]))
            DIRAC.exit(0)
        else:
            gLogger.error("Plugin has no specific parameters")
            DIRAC.exit(1)

    requestID = pluginScript.getOption("RequestID", 0)
    requestedLFNs = pluginScript.getOption("LFNs")
    # print pluginParams

    # FIXME: can be removed when the subLoggers can do it...
    gLogger.showHeaders()

    gLogger.setLevel("INFO")
    # Create the transformation
    transformation = Transformation()
    transType = ""
    if plugin in getRemovalPlugins():
        transType = "Removal"
    elif plugin in getReplicationPlugins():
        transType = "Replication"
    else:
        transType = "Processing"
    transType = pluginScript.getOption("Type", transType)
    transformation.setType(transType)

    visible = "Yes"
    if (
        allFiles
        or not plugin
        or plugin == "DestroyDataset"
        or pluginScript.getOption("Productions")
        or transType == "Processing"
    ):
        visible = "All"
    bkQueryDict = {}
    checkReplica = True
    if not requestedLFNs:
        bkQuery = pluginScript.getBKQuery(visible=visible)
        if noRepFiles and not plugin:
            # FIXME: this should work but doesn't yet...
            # bkQuery.setOption( 'ReplicaFlag', "ALL" )
            checkReplica = False
        bkQueryDict = bkQuery.getQueryDict()
        if list(bkQueryDict) in ([], ["Visible"]):
            print("No BK query was given...")
            Script.showHelp(exitCode=2)

    reqID = pluginScript.getRequestID()
    if not requestID and reqID:
        requestID = reqID

    pluginParams = pluginScript.getPluginParameters()
    pluginSEParams = pluginScript.getPluginSEParameters()
    if pluginSEParams:
        for key, val in pluginSEParams.items():
            res = transformation.setSEParam(key, val)
            if not res["OK"]:
                print(res["Message"])
                DIRAC.exit(2)
    if pluginParams:
        for key, val in pluginParams.items():
            res = transformation.setAdditionalParam(key, val)
            if not res["OK"]:
                print(res["Message"])
                DIRAC.exit(2)

    print("Transformation type:", transType)
    if requestedLFNs:
        print("%d requested LFNs" % len(requestedLFNs))
    else:
        print("BK Query:", bkQueryDict)
    print("Plugin:", plugin)
    print("Parameters:", pluginParams)
    if pluginSEParams:
        print("SE parameters:", pluginSEParams)
    if requestID:
        print("RequestID:", requestID)
    # get the list of files from BK
    if requestedLFNs:
        lfns = requestedLFNs
    else:
        print("Getting the files from BK")
        lfns = bkQuery.getLFNs(
            printSEUsage=(
                (transType == "Removal" or not plugin)
                and not pluginScript.getOption("Runs")
                and not pluginScript.getOption("DQFlags")
            ),
            printOutput=checkReplica,
            visible=visible,
        )
        if not checkReplica:
            bkQuery.setOption("ReplicaFlag", "No")
            lfns += bkQuery.getLFNs(printSEUsage=False, printOutput=False, visible=visible)
            print("%d files in directories:" % len(lfns))
            directories = {}
            import os

            for lfn in lfns:
                dd = os.path.dirname(lfn)
                directories[dd] = directories.setdefault(dd, 0) + 1
            for dd in sorted(directories):
                print(dd, directories[dd])
    if len(lfns) == 0:
        print("No files found in BK...Exiting now")
        DIRAC.exit(0)

    if not plugin:
        print("No plugin to be tested...")
        DIRAC.exit(0)

    print("\nNow testing the %s plugin %s" % (transType.lower(), plugin))
    transformation.setPlugin(plugin)
    transformation.setBkQuery(bkQueryDict)

    from LHCbDIRAC.TransformationSystem.Agent.TransformationPlugin import TransformationPlugin

    transID = -9999
    pluginParams["TransformationID"] = transID
    pluginParams["Status"] = "Active"
    pluginParams["Type"] = transType
    # Create a fake transformation client
    fakeClient = FakeClient(transformation, transID, lfns, asIfProd)
    from LHCbDIRAC.BookkeepingSystem.Client.BookkeepingClient import BookkeepingClient
    from DIRAC.DataManagementSystem.Client.DataManager import DataManager

    oplugin = TransformationPlugin(
        plugin, transClient=fakeClient, dataManager=DataManager(), bkClient=BookkeepingClient()
    )
    pluginParams["TransformationID"] = transID
    pluginParams.update(pluginSEParams)
    oplugin.setParameters(pluginParams)
    replicas = fakeClient.getReplicas()
    files = fakeClient.getFiles()
    if not replicas:
        print("No replicas were found, exit...")
        DIRAC.exit(2)
    oplugin.setInputData(replicas)
    oplugin.setTransformationFiles(files)
    oplugin.setDebug(pluginScript.getOption("Debug", False))
    import time

    startTime = time.time()
    res = oplugin.run()
    print("Plugin took %.1f seconds" % (time.time() - startTime))
    print("")
    if res["OK"]:
        print(len(res["Value"]), "tasks created")
        i = 0
        previousTask = {"First": 0, "SEs": None, "Location": None, "Tasks": 0}
        noReplicaLFNs = [lfn for _targetSE, lfnList in res["Value"] for lfn in lfnList if lfn not in replicas]
        if noReplicaLFNs:
            result = DataManager().getReplicas(noReplicaLFNs, getUrl=False)
            if res["OK"]:
                replicas.update(result["Value"]["Successful"])
        for task in res["Value"]:
            i += 1
            location = []
            for lfn in task[1]:
                ll = ",".join(sorted(replicas.get(lfn, ["Unknown"])))
                # print "LFN", lfn, l
                if ll not in location:
                    location.append(ll)
            if len(task[1]) == 1:
                # Only 1 file in task
                if previousTask["Tasks"]:
                    if task[0] == previousTask["SEs"] and location == previousTask["Location"]:
                        # Accumulate tasks for the same site and with same origin
                        previousTask["Tasks"] += 1
                        continue
                    else:
                        # Print out previous tasks
                        if previousTask["First"] == i - 1:
                            print("%d" % previousTask["First"], "- Target SEs:", previousTask["SEs"], end=" ")
                            "- 1 file - Current locations:", previousTask["Location"]
                        else:
                            print(
                                "%d:%d (%d tasks)" % (previousTask["First"], i - 1, i - previousTask["First"]), end=" "
                            )
                            "- Target SEs:", previousTask["SEs"], "- 1 file", " - Current locations:", previousTask[
                                "Location"
                            ]
                        printFinalSEs(transType, previousTask["Location"], previousTask["SEs"])
                previousTask = {"First": i, "SEs": task[0], "Location": location, "Tasks": 1}
            else:
                if previousTask["Tasks"]:
                    print("%d:%d (%d tasks)" % (previousTask["First"], i - 1, i - previousTask["First"]), end=" ")
                    "- Target SEs:", previousTask["SEs"], "- 1 file", " - Current locations:", previousTask["Location"]
                    printFinalSEs(transType, previousTask["Location"], previousTask["SEs"])
                    previousTask = {"First": 0, "SEs": None, "Location": None, "Tasks": 0}
                print(i, "- Target SEs:", task[0], "- %d files" % len(task[1]), " - Current locations:", location)
                printFinalSEs(transType, location, task[0])
        if previousTask["Tasks"]:
            i += 1
            if i - previousTask["First"] == 1:
                print("%d" % previousTask["First"], "- Target SEs:", previousTask["SEs"], "- 1 file", end=" ")
                " - Current locations:", previousTask["Location"]
            else:
                print("%d:%d (%d tasks)" % (previousTask["First"], i - 1, i - previousTask["First"]), end=" ")
                "- Target SEs:", previousTask["SEs"], "- 1 file", " - Current locations:", previousTask["Location"]
            printFinalSEs(transType, previousTask["Location"], previousTask["SEs"])
    else:
        print(res["Message"])
    DIRAC.exit(0)


if __name__ == "__main__":
    main()
