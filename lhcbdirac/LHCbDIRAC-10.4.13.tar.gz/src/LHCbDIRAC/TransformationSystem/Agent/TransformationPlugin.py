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

"""TransformationPlugin is a class wrapping the supported LHCb transformation
plugins."""
# pylint: disable=too-many-lines
# pylint: disable=missing-docstring
from collections import defaultdict
import time
import random
import sys
import six

from DIRAC import S_OK, S_ERROR
from DIRAC.Core.Utilities.List import breakListIntoChunks, randomize

# from DIRAC.Core.Utilities.Time import timeThis
from DIRAC.DataManagementSystem.Utilities.DMSHelpers import resolveSEGroup
from DIRAC.Resources.Catalog.FileCatalog import FileCatalog
from DIRAC.Resources.Storage.StorageElement import StorageElement
from DIRAC.ResourceStatusSystem.Client.ResourceManagementClient import ResourceManagementClient
from DIRAC.TransformationSystem.Agent.TransformationPlugin import TransformationPlugin as DIRACTransformationPlugin
from DIRAC.TransformationSystem.Client.Utilities import getFileGroups, sortExistingSEs

from LHCbDIRAC.BookkeepingSystem.Client.BookkeepingClient import BookkeepingClient
from LHCbDIRAC.TransformationSystem.Client.TransformationClient import TransformationClient
from LHCbDIRAC.TransformationSystem.Utilities.PluginUtilities import PluginUtilities, getActiveSEs


class TransformationPlugin(DIRACTransformationPlugin):
    """Extension of DIRAC TransformationPlugin - instantiated by the TransformationAgent"""

    def __init__(self, plugin, transClient=None, dataManager=None, bkClient=None, rmClient=None, fc=None, debug=False):
        """The clients can be passed in."""
        super(TransformationPlugin, self).__init__(plugin, transClient=transClient, dataManager=dataManager, fc=fc)

        if not bkClient:
            self.bkClient = BookkeepingClient()
        else:
            self.bkClient = bkClient

        if not rmClient:
            self.rmClient = ResourceManagementClient()
        else:
            self.rmClient = rmClient

        if not fc:
            self.fileCatalog = FileCatalog()
        else:
            self.fileCatalog = fc

        self.params = {}
        self.workDirectory = None
        self.pluginCallback = self.voidMethod
        self.startTime = time.time()
        self.transReplicas = {}
        self.transFiles = []
        self.transID = None
        self.debug = debug
        if transClient is None:
            self.transClient = TransformationClient()
        else:
            self.transClient = transClient
        self.util = PluginUtilities(
            plugin=plugin,
            transClient=transClient,
            dataManager=dataManager,
            bkClient=self.bkClient,
            rmClient=self.rmClient,
            debug=debug,
        )
        self.setDebug(self.util.getPluginParam("Debug", False))

        self.processingShares = ({}, {})
        self._alreadyProcessedLFNs = {}
        self.pendingTasksPerSE = {}
        self.throttledFilesPerSE = defaultdict(int)

    def voidMethod(self, _id, invalidateCache=False):
        return

    def setInputData(self, data):
        """self.transReplicas are the replica location of the transformation files.

        However if some don't have a replica, they are not in this
        dictionary self.transReplicas[lfn] == [ SE1, SE2...]
        """
        # data is a synonym as used in DIRAC
        self.transReplicas = data.copy()
        self.data = self.transReplicas
        self.util.transReplicas = self.transReplicas

    def setTransformationFiles(self, files):
        """
        self.transFiles are all the Unused files for that transformation
        It is a list of dictionaries, of which ``lfn = fileDict['LFN']``

        Keys are: ``ErrorCount``, ``FileID``, ``InsertedTime``, ``LFN``, ``LastUpdate``,
          ``RunNumber``, ``Status``, ``TargetSE``, ``TaskID``, ``TransformationID`` and ``UsedSE``
        """
        # files is a synonym, as used in DIRAC
        self.transFiles = [fileDict for fileDict in files]
        self.files = self.transFiles
        self.util.transFiles = self.transFiles

    def setParameters(self, params):
        super(TransformationPlugin, self).setParameters(params)
        self.transID = params["TransformationID"]
        self.setDebug(self.util.getPluginParam("Debug", False))

    def setDebug(self, val=True):
        self.debug = val or self.debug
        self.util.setDebug(val)

    def __del__(self):
        self.util.logInfo("Execution finished, timing: %.3f seconds" % (time.time() - self.startTime))

    # @timeThis
    def _removeProcessedFiles(self):
        """Checks if the LFNs have descendants in the same transformation.

        Removes them from self.transReplicas and sets them 'Processed'
        """
        self.util.logVerbose("Checking if %d files are processed" % len(self.transReplicas))
        descendants = self.util.getProcessedFiles(list(self.transReplicas))
        if descendants:
            processedLfns = [lfn for lfn in descendants if descendants[lfn]]
            self.util.logVerbose(
                "Found %d input files that have already been processed (setting status)" % len(processedLfns)
            )
            if processedLfns:
                res = self.transClient.setFileStatusForTransformation(self.transID, "Processed", processedLfns)
                if res["OK"]:
                    self.util.logInfo(
                        "Found %d input files that have already been processed (status set)" % len(processedLfns)
                    )
                    for lfn in processedLfns:
                        self.transReplicas.pop(lfn, None)
                    for fileDict in [fileDict for fileDict in self.transFiles if fileDict["LFN"] in processedLfns]:
                        self.transFiles.remove(fileDict)
            else:
                # Here one should check descendants of children
                self.util.logVerbose("No input files have already been processed")

    def _RAWReplication(self):
        """Plugin for replicating RAW data to Tier1s according to shares, and
        defining the processing destination site."""
        self.util.logInfo("Starting execution of plugin")
        sourceSE = "CERN-RAW"
        rawTargets = self.util.getPluginParam("RAWStorageElements", ["Tier1-RAW"])
        rawTargets = set(resolveSEGroup(rawTargets)) - set([sourceSE])
        bufferTargets = self.util.getPluginParam("ProcessingStorageElements", ["Tier1-Buffer"])
        bufferTargets = set(resolveSEGroup(bufferTargets))
        useRunDestination = self.util.getPluginParam("UseRunDestination", False)
        preStageShares = self.util.getPluginParam("PrestageShares", "CPUforRAW")
        if preStageShares not in ("CPUforRAW", "CPUforReprocessing") or not bufferTargets:
            self.util.logInfo("No prestaging required")
            preStageShares = None
        self.util.logVerbose("Targets for replication are %s and %s" % (sorted(rawTargets), sorted(bufferTargets)))
        if preStageShares:
            self.util.logInfo("Using prestage shares from %s" % preStageShares)

        # Get the requested shares from the CS
        res = self.util.getPluginShares(section="RAW")
        if not res["OK"]:
            self.util.logError("Section RAW in Shares not available")
            return res
        existingCount, targetShares = res["Value"]

        runFileDict = self.util.getFilesGroupedByRun()
        if not runFileDict:
            return S_OK([])

        # For each of the runs determine the destination of any previous files
        res = self.util.getTransformationRuns(runFileDict)
        if not res["OK"]:
            self.util.logError(
                "Error when getting transformation runs",
                "for runs %s : %s" % (",".join(sorted(runFileDict)), res["Message"]),
            )
            return res
        runSEDict = dict((runDict["RunNumber"], runDict["SelectedSite"]) for runDict in res["Value"])

        # Choose the destination SE
        tasks = []
        alreadyReplicated = []
        for runID in set(runFileDict) & set(runSEDict):
            bufferLogged = False
            rawLogged = False
            # It may happen that files are not in the replica dictionary
            runLfns = set(runFileDict[runID]) & set(self.transReplicas)
            if not runLfns:
                continue
            assignedSE = runSEDict[runID]
            if assignedSE:
                # We already know where this run should go
                ses = set(assignedSE.split(","))
                assignedRAW = ses & rawTargets
                assignedBuffer = ses & bufferTargets
            else:
                assignedRAW = None
                assignedBuffer = None
            # Now determine where these files should go
            # Group by location
            replicaGroups = getFileGroups(
                dict((lfn, self.transReplicas[lfn]) for lfn in runLfns if lfn in self.transReplicas)
            )
            runSEs = set()
            for replicaSE in replicaGroups:
                # Get all locations where files are
                ses = set(replicaSE.split(","))
                runSEs.update(ses)
            # Find potential locations
            if not assignedRAW:
                assignedRAW = runSEs & rawTargets
            if assignedRAW:
                assignedRAW = list(assignedRAW)[0]
            if not assignedBuffer and preStageShares:
                assignedBuffer = runSEs & bufferTargets
            if assignedBuffer:
                assignedBuffer = list(assignedBuffer)[0]
            updated = False
            for replicaSE, lfns in replicaGroups.items():  # can be an iterator
                replicaSE = set(replicaSE.split(","))
                if not assignedRAW:
                    # Files are not yet at a Tier1-RAW, if a destination already exists, use it
                    assignedRAW = self.util.getSEForDestination(runID, rawTargets)
                    if assignedRAW:
                        self.util.logVerbose(
                            "RAW destination obtained from run %d destination: %s" % (runID, assignedRAW)
                        )
                    elif not useRunDestination:
                        # Define the destination only if not requested to use it from the run destination
                        res = self._getNextSite(existingCount, targetShares)
                        if not res["OK"]:
                            self.util.logError("Failed to get next destination SE", res["Message"])
                            return res
                        else:
                            assignedRAW = res["Value"]
                            self.util.logVerbose("RAW destination assigned for run %d: %s" % (runID, assignedRAW))
                    elif rawTargets:
                        self.util.logVerbose("Run destination not yet defined for run %d" % runID)
                        # We can go to next in the loop there
                        continue
                    rawLogged = True
                elif not rawLogged:
                    self.util.logVerbose("RAW destination existing for run %d: %s" % (runID, assignedRAW))

                # # Now get a buffer destination is prestaging is required
                if preStageShares and not assignedBuffer:
                    assignedBuffer = self.util.getSEForDestination(runID, bufferTargets)
                    if assignedBuffer:
                        bufferLogged = True
                        self.util.logVerbose(
                            "Buffer destination obtained from run %d destination: %s" % (runID, assignedBuffer)
                        )
                    elif not useRunDestination:
                        # Files are not at a buffer for processing
                        res = self._selectRunSite(
                            runID,
                            sourceSE,
                            replicaSE | set([assignedRAW]),
                            bufferTargets,
                            preStageShares=preStageShares,
                        )
                        if not res["OK"]:
                            self.util.logError("Error selecting the destination site", res["Message"])
                            return res
                        assignedBuffer = res["Value"]
                        if assignedBuffer:
                            bufferLogged = True
                            self.util.logVerbose("Selected destination SE for run %d: %s" % (runID, assignedBuffer))
                        else:
                            self.util.logWarn("Failed to find Buffer destination SE for run", str(runID))
                            continue
                    elif bufferTargets:
                        self.util.logVerbose("Run destination not yet defined for run %d" % runID)
                elif assignedBuffer and not bufferLogged:
                    self.util.logVerbose("Buffer destination existing for run %d: %s" % (runID, assignedBuffer))

                # # Find out if the replication is necessary
                assignedSE = []
                if assignedRAW:
                    assignedSE.append(assignedRAW)
                if assignedBuffer:
                    assignedSE.append(assignedBuffer)
                if assignedSE:
                    if not updated:
                        updated = True
                        res = self.transClient.setTransformationRunsSite(self.transID, runID, ",".join(assignedSE))
                        if not res["OK"]:
                            self.util.logError("Failed to assign TransformationRun SE", res["Message"])
                            return res
                    ses = sorted(set(assignedSE) - replicaSE)
                    # Update the counters as we know the number of files
                    if assignedRAW in ses:
                        # Here we pass both the number of files and the runID as we can use either metrics
                        self.util.updateSharesUsage(existingCount, assignedRAW, len(lfns), runID)
                    assignedSE = ",".join(ses)
                if assignedSE:
                    self.util.logVerbose(
                        "Creating a task (%d files, run %d) for SEs %s" % (len(lfns), runID, assignedSE)
                    )
                    tasks.append((assignedSE, lfns))
                else:
                    alreadyReplicated += lfns
                    self.util.logVerbose(
                        "%d files in run %d found already replicated at %s"
                        % (len(lfns), runID, ",".join(sorted(replicaSE)))
                    )

        if alreadyReplicated:
            for lfn in alreadyReplicated:
                self.transReplicas.pop(lfn)
            self.util.cleanFiles(self.transFiles, self.transReplicas, status="Processed")

        self.util.printShares(
            "Final target shares and usage (%)", targetShares, existingCount, log=self.util.logVerbose
        )
        return S_OK(tasks)

    def _RAWProcessing(self):
        """Create tasks for RAW data processing using the run destination table."""
        # Let's create jobs only at active SEs
        fromSEs = set(
            se for se in resolveSEGroup(self.util.getPluginParam("FromSEs", [])) if StorageElement(se).status()["Read"]
        )
        if not fromSEs:
            self.util.logWarn("No processing active SEs are provided")
            return S_OK([])

        # Split the files in run groups
        runFileDict = self.util.getFilesGroupedByRun()
        if not runFileDict:
            # No files, no tasks!
            self.util.logVerbose("No runs found!")
            return S_OK([])
        self.util.logVerbose("Obtained %d runs" % len(runFileDict))

        # For each of the runs determine the destination of any previous files
        res = self.util.getTransformationRuns(runFileDict)
        if not res["OK"]:
            self.util.logError(
                "Error when getting transformation runs",
                "for runs %s : %s" % (",".join(sorted(runFileDict)), res["Message"]),
            )
            return res
        runSEDict = dict((runDict["RunNumber"], runDict["SelectedSite"]) for runDict in res["Value"])

        # Get status of all runs (finished or not)
        runSet = set(runFileDict) & set(runSEDict)
        res = self.bkClient.getRunStatus(list(runSet))
        success = res.get("Value", {}).get("Successful", {})
        runFinished = dict((runID, success[runID]["Finished"] == "Y") for runID in success)

        # Choose the destination SE
        tasks = []
        for runID in runSet:
            assignedSE = runSEDict[runID]
            runSEs = set(assignedSE.split(",")) if assignedSE and isinstance(assignedSE, six.string_types) else set()
            if not runSEs:
                # Check that the run tick is present, but if an SE is already assigned, this is not needed
                runTick = self.util.checkCondDBRunTick(runID)
                if runTick is False:
                    # If runTick is None it means the CondDB was not available in CVMFS, we ignore (but a warning is printed)
                    self.util.logInfo("Run tick not present yet in OnlineCondDB for run %d" % runID)
                    continue
            runLfns = runFileDict[runID]
            # Now determine where these files should go
            # Group by location
            update = False
            replicaGroups = getFileGroups(
                dict((lfn, self.transReplicas[lfn]) for lfn in runLfns if lfn in self.transReplicas)
            )
            notAtSE = 0
            for replicaSE, lfns in replicaGroups.items():  # can be an iterator
                targetSEs = set(replicaSE.split(",")) & fromSEs
                if targetSEs:
                    # The files are at at least one of the requested SEs, set in run site for transformation
                    #   and create task
                    update = targetSEs - runSEs
                    if update:
                        runSEs |= targetSEs
                    targetSEs = ",".join(sorted(targetSEs))
                    self.util.logVerbose(
                        "Creating tasks with %d files for run %s at %s" % (len(lfns), runID, targetSEs)
                    )
                    # We flush the run only if it is finished
                    toFlush = (self.params["Status"] == "Flush") or runFinished.get(runID, False)
                    newTasks = self.util.createTasksBySize(lfns, targetSEs, flush=toFlush)
                    tasks += newTasks
                    self.util.logVerbose("Created %d tasks" % len(newTasks))
                else:
                    notAtSE += len(lfns)
            if notAtSE:
                self.util.logVerbose("Found %d files not yet at required SEs for run %d" % (notAtSE, runID))
            # If there are new run site destination SEs, set them
            if update:
                res = self.transClient.setTransformationRunsSite(self.transID, runID, ",".join(sorted(runSEs)))
                if not res["OK"]:
                    self.util.logError("Failed to assign TransformationRun SE", res["Message"])
                    return res

        if self.pluginCallback:
            self.pluginCallback(self.transID, invalidateCache=True)
        return S_OK(tasks)

    def _selectRunSite(self, runID, backupSE, rawSEs, bufferTargets, preStageShares=None):
        if not preStageShares:
            return S_OK()

        if not self.processingShares[0]:
            res = self.util.getPluginShares(section=preStageShares, backupSE=backupSE)
            if not res["OK"]:
                self.util.logError("Error getting CPU shares for RAW processing", res["Message"])
                return res
            else:
                self.processingShares = res["Value"]

        self.util.logVerbose("Select processing SE for run %d within %s" % (runID, sorted(rawSEs)))
        rawFraction, cpuShares = self.processingShares
        if len(rawSEs) == 1:
            selectedSE = list(rawSEs)[0]
        else:
            existingSEs = set(cpuShares) & rawSEs
            if not existingSEs:
                errStr = "Could not find shares for SEs"
                self.util.logError(errStr, sorted(rawSEs))
                return S_ERROR(errStr)

            prob = 0
            seProbs = {}
            rawSEs = sorted((rawSEs & set(rawFraction)) - set([backupSE]))
            for se in rawSEs:
                prob += rawFraction[se] / len(rawSEs)
                seProbs[se] = prob
            rawSEs.append(backupSE)
            seProbs[backupSE] = 1.0
            rand = random.uniform(0.0, 1.0)
            strProbs = ",".join([" %s:%.3f" % (se, seProbs[se]) for se in rawSEs])
            self.util.logInfo("For run %d, SE integrated fraction =%s, random number = %.3f" % (runID, strProbs, rand))
            selectedSE = None
            for se in rawSEs:
                prob = seProbs[se]
                if rand <= prob:
                    selectedSE = se
                    break

        # Find out the site associated to that SE
        res = self.util.dmsHelper.getLocalSiteForSE(selectedSE)
        if not res["OK"]:
            return res
        site = res["Value"]
        if site is None:
            return S_ERROR("No site found for SE")
        res = self.transClient.setDestinationForRun(runID, site)
        if not res["OK"]:
            return res
        self.util.logVerbose("Successfully set destination for run %d: %s" % (runID, site))

        return self.util.dmsHelper.getSEInGroupAtSite(bufferTargets, site)

    def _groupBySize(self, files=None):
        """Generate a task for a given amount of data at a (set of) SE."""
        if not files:
            files = self.transReplicas
        else:
            files = dict(zip(files, [self.transReplicas[lfn] for lfn in files]))
        return self.util.groupBySize(files, self.params["Status"])

    def _LHCbStandard(self):
        """Plugin grouping files at same sites based on number of files, used for
        example for stripping or WG productions."""
        return self.util.groupByReplicas(self.transReplicas, self.params["Status"])

    def _ByRun(self, param="", plugin="LHCbStandard", requireFlush=False, forceFlush=False):
        try:
            return self.__byRun(param=param, plugin=plugin, requireFlush=requireFlush, forceFlush=forceFlush)
        except Exception as x:
            self.util.logException("Exception in _ByRun plugin:", "", lException=x)
            return S_ERROR([])

    # @timeThis
    def __byRun(self, param="", plugin="LHCbStandard", requireFlush=False, forceFlush=False):
        """Basic plugin for when you want to group files by run."""
        self.util.logInfo("Starting execution of plugin")
        allTasks = []
        if not self.transReplicas:
            self.util.logVerbose("No data to be processed by plugin")
            return S_OK(allTasks)
        # If flush is force, it is obviously required! try and get forcing from parameter
        if self.util.getPluginParam("ForceFlush", False):
            forceFlush = True
        requireFlush |= forceFlush
        pluginStartTime = time.time()
        groupSize = self.util.getPluginParam("GroupSize")
        typesWithNoCheck = self.util.getPluginParam(
            "NoCheckTypes", ["Merge", "MCMerge", "HistoMerge", "Replication", "Removal"]
        )
        # Only consider active SEs for read
        fromSEs = set(
            se for se in resolveSEGroup(self.util.getPluginParam("FromSEs", [])) if StorageElement(se).status()["Read"]
        )
        maxTime = self.util.getPluginParam("MaxTimeAllowed", 0)
        # Read the cached information from disk
        self.util.readCacheFile(self.workDirectory)
        # Is throttling on pending tasks requested?
        throttleLimit = self.util.getPluginParam("ThrottlePendingTasks", 0)
        if throttleLimit:
            # Get the number of not yet running jobs for this trans type at each SE
            res = self.util.getPendingTasks(self.params["Type"])
            if not res["OK"]:
                self.util.logError("Error getting number of pending tasks", res["Message"])
                return res
            if res["Value"] is None:
                return S_OK([])
            self.pendingTasksPerSE = res["Value"]
            # If throttling is requested, remove some files
            self.util.throttleFiles(fromSEs, self.pendingTasksPerSE, throttleLimit)
            if not self.transFiles:
                return S_OK([])

        # Check if ancestors are required: this flag defaults to True for DataStripping transformations
        lfn = list(self.transReplicas)[0]
        fileType = self.util.getMetadataFromTSorBK(lfn, "FileType")[lfn]
        addAncestors = self.util.getPluginParam(
            "UseAncestors", bool(self.params["Type"] == "DataStripping") and fileType != "FULL.DST"
        )

        # Group files by run number and value of parameter "param"
        self.util.logInfo("Grouping %d files by runs %s " % (len(self.transFiles), "and %s" % param if param else ""))
        runFileDict = self.util.getFilesGroupedByRunAndParam(param=param)

        transStatus = self.params["Status"]
        res = self.util.getTransformationRuns(runFileDict)
        if not res["OK"]:
            self.util.logError(
                "Error when getting transformation runs",
                "for runs %s : %s" % (",".join(sorted(runFileDict)), res["Message"]),
            )
            return res
        transRuns = res["Value"]
        runSites = dict((run["RunNumber"], run["SelectedSite"]) for run in transRuns if run["SelectedSite"])
        # Loop on all runs that have new files
        inputData = self.transReplicas.copy()
        setInputData = set(inputData)
        runEvtType = {}

        # Get the list of runs as we may have a reduced list
        res = self.util.getRunList(transRuns, runFileDict)
        if not res["OK"] or not res["Value"]:
            return res
        runList = res["Value"]
        nRunsLeft = len(runList)
        #
        # # # # # # # Loop on all selected runs # # # # # # #
        #
        timeout = False
        processedFiles = 0
        missingAtSEs = False
        for run in runList:
            runID = run["RunNumber"]
            self.util.logVerbose("Processing run %d, still %d runs left" % (runID, nRunsLeft))
            nRunsLeft -= 1
            runStatus = "Flush" if transStatus == "Flush" else run["Status"]
            paramDict = runFileDict.get(runID, {})
            runTargetSEs = set(se for se in runSites.get(runID, "").split(",") if se)
            #
            # Loop on parameters (None if not by param)
            #
            flushed = []
            for paramValue in sorted(paramDict):
                paramStr = " (%s : %s) " % (param, paramValue) if paramValue else " "
                runParamLfns = set(paramDict[paramValue])
                processedFiles += len(runParamLfns)
                # Check if something was new since last time...
                cachedLfns = self.util.getCachedRunLFNs(runID, paramValue)
                newLfns = runParamLfns - cachedLfns
                checkForNewFiles = (
                    not forceFlush
                    and self.transID > 0
                    and runStatus != "Flush"
                    and not self.util.cacheExpired(runID)
                    and (plugin != "LHCbStandard" or groupSize != 1)
                )

                if checkForNewFiles and not len(newLfns):
                    self.util.logInfo("No new files since last time for run %d%s: skip..." % (runID, paramStr))
                    continue
                self.util.logVerbose(
                    "Of %d files, %d are new for %d%s" % (len(runParamLfns), len(newLfns), runID, paramStr)
                )
                runFlush = requireFlush
                if runFlush:
                    evtType = self.util.getEventType(paramDict[paramValue][0], runEvtType, paramValue)
                    self.util.logDebug("Event type%s: %s" % (paramStr, evtType))
                    if not evtType:
                        runFlush = False
                runParamReplicas = {}
                notAtSEs = 0
                for lfn in runParamLfns & setInputData:
                    runParamReplicas[lfn] = [
                        se
                        for se in inputData[lfn]
                        if self.util.dmsHelper.isSEForJobs(se, checkSE=False) and (not fromSEs or se in fromSEs)
                    ]
                    if not runParamReplicas[lfn]:
                        notAtSEs += 1
                        del runParamReplicas[lfn]
                if notAtSEs:
                    missingAtSEs = True
                    self.util.logInfo(
                        "For run %d, %d files are not at required SEs: tasks cannot be created" % (runID, notAtSEs)
                    )

                # We need to replace the input replicas by those of this run before calling the helper plugin
                # As it may use self.data, set both transReplicas and data members
                self.transReplicas = runParamReplicas
                # Check if files have already been processed
                # Skipped as this is taking quite some time... Leave it here as reminder, in case it becomes mandatory
                if False and self.params["Type"] not in typesWithNoCheck:
                    self.util.logInfo("Removing processed files for %s" % paramStr)
                    self._removeProcessedFiles()
                # Backward compatibility for calling helper plugin
                self.data = self.transReplicas
                # If flush is requested, check for it
                if runFlush and runStatus != "Flush":
                    runStatus = self.util.checkRunForFlush(
                        runID, runStatus, forceFlush, param, paramValue, paramStr, evtType
                    )
                if runStatus == "Flush":
                    flushed.append((paramValue, len(self.transReplicas)))
                # Now calling the helper plugin for that run... Set status to the run status
                self.params["Status"] = runStatus
                res = eval("self._%s()" % plugin)  # pylint: disable=eval-used
                if not res["OK"]:
                    return res
                # Resetting status
                self.params["Status"] = transStatus
                # Check that files (and ancestors) are at fromSEs if requested
                tasks, missing = self.util.selectTasksFromSEs(runID, res["Value"], addAncestors, fromSEs)
                missingAtSEs |= missing
                self.util.logInfo("Created %d tasks for run %d%s" % (len(tasks), runID, paramStr))
                allTasks.extend(tasks)
                taskLfns = set(lfn for task in tasks for lfn in task[1])
                # If there are new SEs used for that run, add them to the DB
                targetSEs = set(se for task in tasks for se in task[0].split(","))
                if targetSEs - runTargetSEs:
                    targetSEs = ",".join(targetSEs | runTargetSEs)
                    self.util.logVerbose("Set target SEs for run %d as %s" % (runID, targetSEs))
                    res = self.transClient.setTransformationRunsSite(self.transID, runID, targetSEs)
                    if not res["OK"]:
                        self.util.logError(
                            "Failed to set target SEs", "to run %d as %s: %s" % (runID, targetSEs, res["Message"])
                        )
                # Cache the remaining files
                self.util.setCachedRunLfns(runID, paramValue, set(runParamLfns) - taskLfns)
            # # # # # # # # # # #
            # End of param loop #
            # # # # # # # # # # #
            if flushed:
                # Print out info about what was flushed
                prStr = "Run %d is flushed%s:" % (runID, " for %s" % param if param else "")
                prStr += ",".join(
                    " %s (%d files)" % flTuple if flTuple[0] else " %d files" % flTuple[1]
                    for flTuple in sorted(flushed)
                )
                self.util.logInfo(prStr)

            # if enough time already spent, exit
            timeSpent = time.time() - pluginStartTime
            lastRun = runID
            if maxTime and timeSpent > maxTime:
                timeout = True
                self.util.logInfo(
                    "Enough time spent in plugin (%.1f seconds), exit at run %d, %d runs left"
                    % (timeSpent, runID, nRunsLeft)
                )
                break
        # # # # # # # # # #
        # End of run loop #
        # # # # # # # # # #
        timeSpent = time.time() - pluginStartTime
        self.util.logInfo("Processed %d files in %.1f seconds" % (processedFiles, timeSpent))
        self.util.setCachedLastRun(lastRun)
        # reset the input data as it was when calling the plugin
        self.setInputData(inputData)
        self.util.writeCacheFile()
        if missingAtSEs and self.pluginCallback:
            # If some files could not be scheduled, clear the cache
            self.pluginCallback(self.transID, invalidateCache=True)
        ret = S_OK(allTasks)
        ret["Timeout"] = timeout
        return ret

    def _ByRunWithFlush(self):
        # If groupSize is 1, no need to flush!
        groupSize = self.util.getPluginParam("GroupSize")
        return self._ByRun(requireFlush=groupSize != 1)

    def _ByRunForceFlush(self):
        # If groupSize is 1, no need to flush!
        groupSize = self.util.getPluginParam("GroupSize")
        return self._ByRun(forceFlush=groupSize != 1)

    def _ByRunSize(self):
        return self._ByRun(plugin="BySize")

    def _ByRunSizeWithFlush(self):
        return self._ByRun(plugin="BySize", requireFlush=True)

    def _ByRunSizeForceFlush(self):
        return self._ByRun(plugin="BySize", forceFlush=True)

    def _ByRunFileType(self):
        return self._ByRun(param="FileType")

    def _ByRunFileTypeWithFlush(self):
        # If groupSize is 1, no need to flush!
        groupSize = self.util.getPluginParam("GroupSize")
        return self._ByRun(param="FileType", requireFlush=groupSize != 1)

    def _ByRunFileTypeForceFlush(self):
        # If groupSize is 1, no need to flush!
        groupSize = self.util.getPluginParam("GroupSize")
        return self._ByRun(param="FileType", forceFlush=groupSize != 1)

    def _ByRunFileTypeSize(self):
        return self._ByRun(param="FileType", plugin="BySize")

    def _ByRunFileTypeSizeWithFlush(self):
        return self._ByRun(param="FileType", plugin="BySize", requireFlush=True)

    def _ByRunFileTypeSizeForceFlush(self):
        return self._ByRun(param="FileType", plugin="BySize", forceFlush=True)

    def _ByRunEventType(self):
        return self._ByRun(param="EventTypeId")

    def _ByRunEventTypeWithFlush(self):
        # If groupSize is 1, no need to flush!
        groupSize = self.util.getPluginParam("GroupSize")
        return self._ByRun(param="EventTypeId", requireFlush=groupSize != 1)

    def _ByRunEventTypeForceFlush(self):
        # If groupSize is 1, no need to flush!
        groupSize = self.util.getPluginParam("GroupSize")
        return self._ByRun(param="EventTypeId", forceFlush=groupSize != 1)

    def _ByRunEventTypeSize(self):
        return self._ByRun(param="EventTypeId", plugin="BySize")

    def _ByRunEventTypeSizeWithFlush(self):
        return self._ByRun(param="EventTypeId", plugin="BySize", requireFlush=True)

    def _ByRunEventTypeSizeForceFlush(self):
        return self._ByRun(param="EventTypeId", plugin="BySize", forceFlush=True)

    # Plugins for RootMerging -
    # here only to distinguish from the others as "RootMerging" is meaningful at production creation

    def _ByRunSizeWithFlushRootMerging(self):
        return self._ByRun(plugin="BySize", requireFlush=True)

    def _BySizeRootMerging(self):
        return self._BySize()

    def _LHCbDSTBroadcast(self):
        """This plug-in broadcasts files according to CS settings
        to one archiveSE (if set) and <numberOfCopies> secondarySEs
        One can force some mandatorySEs and exclude some SEs
        All files for the same run have the same target
        Usually for replication of real data (2 copies)"""
        archiveSEs = resolveSEGroup(self.util.getPluginParam("ArchiveSEs", []))
        mandatorySEs = resolveSEGroup(self.util.getPluginParam("MandatorySEs", []))
        # In order to not have to change the SEGroups when excluding temporarily a site, add exclusion list...
        excludedSEs = resolveSEGroup(self.util.getPluginParam("ExcludedSEs", []))
        secondarySEs = list(set(resolveSEGroup(self.util.getPluginParam("SecondarySEs", []))) - set(excludedSEs))
        numberOfCopies = self.util.getPluginParam("NumberOfReplicas", 2)

        self.util.logInfo("Starting execution of plugin")

        # We need at least all mandatory copies
        numberOfCopies = max(numberOfCopies, len(mandatorySEs))

        # Group the remaining data by run
        runFileDict = self.util.getFilesGroupedByRun()
        if not runFileDict:
            # No files, no tasks!
            return S_OK([])

        # For each of the runs determine the destination of any previous files
        runSEDict = {}
        runUpdate = {}
        # Make a list of SEs already assigned to runs
        res = self.util.getTransformationRuns(runFileDict)
        if not res["OK"]:
            self.util.logError(
                "Error when getting transformation runs",
                "for runs %s : %s" % (",".join(sorted(runFileDict)), res["Message"]),
            )
            return res
        for runDict in res["Value"]:
            runID = runDict["RunNumber"]
            # If the run already has a selected site, use it for that run
            if runDict["SelectedSite"]:
                runSEDict[runID] = runDict["SelectedSite"]
                runUpdate[runID] = False
            else:
                # Check if some files are assigned to an SE in this run
                res = self.transClient.getTransformationFiles(
                    condDict={"TransformationID": self.transID, "RunNumber": runID, "Status": ["Assigned", "Processed"]}
                )
                if not res["OK"]:
                    self.util.logError("Failed to get transformation files for run", "%s %s" % (runID, res["Message"]))
                else:
                    if res["Value"] and res["Value"][0]["UsedSE"]:
                        runSEDict[runID] = res["Value"][0]["UsedSE"]
                        runUpdate[runID] = True

        fileTargetSEs = {}
        alreadyCompleted = []
        # Consider all runs in turn
        for runID, runLfns in runFileDict.items():  # can be an iterator
            # Check if the run is already assigned
            stringTargetSEs = runSEDict.get(runID, None)
            # No SE assigned yet, determine them
            if not stringTargetSEs:
                # Sort existing SEs where most of the files are already
                existingSEs = sortExistingSEs(self.transReplicas, runLfns)
                # this may happen when all files are in FAILOVER
                if existingSEs:
                    # Now select the target SEs
                    self.util.logVerbose("Selecting SEs for %d files" % len(runLfns))
                    self.util.logDebug("Files: %s" % str(runLfns))
                    stringTargetSEs = self.util.setTargetSEs(
                        numberOfCopies, archiveSEs, mandatorySEs, secondarySEs, existingSEs, exclusiveSEs=False
                    )
                    runUpdate[runID] = True

            # Update the TransformationRuns table with the assigned SEs (don't continue if it fails)
            if stringTargetSEs:
                if runUpdate[runID]:
                    res = self.transClient.setTransformationRunsSite(self.transID, runID, stringTargetSEs)
                    if not res["OK"]:
                        self.util.logError("Failed to assign TransformationRun site", res["Message"])
                        return S_ERROR("Failed to assign TransformationRun site")

                # Now assign the individual files to their targets
                runFileTargetSEs, runCompleted = self.util.assignTargetToLfns(
                    runLfns, self.transReplicas, stringTargetSEs
                )
                alreadyCompleted += runCompleted
                fileTargetSEs.update(runFileTargetSEs)

        # Update the status of the already done files
        if alreadyCompleted:
            self.util.logInfo("Found %s files that are already completed" % len(alreadyCompleted))
            self.transClient.setFileStatusForTransformation(self.transID, "Processed", alreadyCompleted)

        # Now group all of the files by their target SEs
        storageElementGroups = {}
        for lfn, stringTargetSEs in fileTargetSEs.items():  # can be an iterator
            storageElementGroups.setdefault(stringTargetSEs, []).append(lfn)

        return S_OK(self.util.createTasks(storageElementGroups))

    def _LHCbWGBroadcastRandom(self):
        """This plugin is specific for randomly broadcasting real data files that don't have a run number
        It calls the MCDSTBroadcast plugin but should have different CS settings
        """
        return self._LHCbMCDSTBroadcastRandom()

    def _LHCbMCDSTBroadcastRandom(self):
        """This plug-in broadcasts files to
        one archiveSE (if set) and to random
        <NumberOfReplicas> secondary SEs."""

        self.util.logInfo("Starting execution of plugin")
        archiveSEs = resolveSEGroup(self.util.getPluginParam("ArchiveSEs", []))
        mandatorySEs = resolveSEGroup(self.util.getPluginParam("MandatorySEs", []))
        # In order to not have to change the SEGroups when excluding temporarily a site, add exclusion list...
        excludedSEs = resolveSEGroup(self.util.getPluginParam("ExcludedSEs", []))
        secondarySEs = list(set(resolveSEGroup(self.util.getPluginParam("SecondarySEs", []))) - set(excludedSEs))
        numberOfCopies = self.util.getPluginParam("NumberOfReplicas", 2)
        excludedFileTypes = self.util.getPluginParam("ExcludedFileTypes", ["GAUSSHIST", "BRUNELHIST", "DAVINCIHIST"])

        # We need at least all mandatory copies
        numberOfCopies = max(numberOfCopies, len(mandatorySEs))

        # Filter file types
        if excludedFileTypes:
            excludedLfns = []
            for lfn, fileType in self.util.getMetadataFromTSorBK(
                self.transReplicas, "FileType"
            ).items():  # can be an iterator
                if fileType in excludedFileTypes:
                    self.transReplicas.pop(lfn)
                    excludedLfns.append(lfn)
            if excludedLfns:
                self.util.logInfo("Found %d files with excluded file type, set them Excluded" % len(excludedLfns))
                res = self.transClient.setFileStatusForTransformation(self.transID, "Excluded", excludedLfns)
                if not res["OK"]:
                    self.util.logError("Error setting files Excluded", res["Message"])
                    return res

        storageElementGroups = {}
        for replicaSE, lfnGroup in getFileGroups(self.transReplicas).items():  # can be an iterator
            existingSEs = [se for se in replicaSE.split(",") if not self.util.dmsHelper.isSEFailover(se)]
            for lfns in breakListIntoChunks(lfnGroup, 100):

                stringTargetSEs = self.util.setTargetSEs(
                    numberOfCopies, archiveSEs, mandatorySEs, secondarySEs, existingSEs, exclusiveSEs=True
                )
                if stringTargetSEs:
                    storageElementGroups.setdefault(stringTargetSEs, []).extend(lfns)
                else:
                    self.util.logInfo("Found %d files that are already completed, set them Processed" % len(lfns))
                    res = self.transClient.setFileStatusForTransformation(self.transID, "Processed", lfns)
                    if not res["OK"]:
                        self.util.logError("Error setting files Processed", res["Message"])
                        return res

        return S_OK(self.util.createTasks(storageElementGroups))

    def _ReplicateDataset(self, maxFiles=None):
        """Plugin for replicating files to specified SEs."""
        destSEs = resolveSEGroup(self.util.getPluginParam("DestinationSEs", []))
        if not destSEs:
            destSEs = resolveSEGroup(self.util.getPluginParam("MandatorySEs", []))
        secondarySEs = resolveSEGroup(self.util.getPluginParam("SecondarySEs", []))
        fromSEs = resolveSEGroup(self.util.getPluginParam("FromSEs", []))
        numberOfCopies = self.util.getPluginParam("NumberOfReplicas", 0)
        return self._simpleReplication(destSEs, secondarySEs, numberOfCopies, fromSEs=fromSEs, maxFiles=maxFiles)

    def _ReplicateToRunDestination(self):
        """Plugin for replicating files to the run destination."""
        # Get replication throttling parameters and destination
        res = self.util.getMaxFilesToReplicate(self.workDirectory)
        if not res["OK"]:
            return res
        watermark, maxFilesAtSE = res["Value"]
        # This is a convention, to skip the loop or to stop replicating
        if watermark is None:
            return S_OK([])
        destSEs = list(maxFilesAtSE)
        runFileDict = self.util.getFilesGroupedByRun()

        # Make a list of SEs already assigned to runs
        res = self.util.getTransformationRuns(runFileDict)
        if not res["OK"]:
            self.util.logError(
                "Error when getting transformation runs",
                "for runs %s : %s" % (",".join(sorted(runFileDict)), res["Message"]),
            )
            return res
        runSEDict = dict(
            (runDict["RunNumber"], runDict["SelectedSite"]) for runDict in res["Value"] if runDict["SelectedSite"]
        )

        maxFiles = self.util.getPluginParam("MaxFilesPerTask", 100)
        tasks = []
        alreadyReplicated = set()
        for runID in runFileDict:
            lfns = set(runFileDict[runID]) & set(self.transReplicas)
            if not lfns:
                continue
            candidateSE = runSEDict.get(runID, self.util.getSEForDestination(runID, destSEs))
            if candidateSE:
                # If necessary, set the run target in the TS
                if runID not in runSEDict:
                    res = self.transClient.setTransformationRunsSite(self.transID, runID, candidateSE)
                    if not res["OK"]:
                        self.util.logError("Failed to assign TransformationRun site", res["Message"])
                        return S_ERROR("Failed to assign TransformationRun site")
                freeSpace = self.util.getStorageFreeSpace([candidateSE])
                if freeSpace[candidateSE] < watermark:
                    self.util.logInfo("No enough space (%s TB) found at %s" % (watermark, candidateSE))
                else:
                    replicated = set(lfn for lfn in lfns if candidateSE in self.transReplicas[lfn])
                    lfns -= replicated
                    alreadyReplicated.update(replicated)
                    if lfns:
                        maxToReplicate = maxFilesAtSE.get(candidateSE, sys.maxsize)
                        if len(lfns) < maxFilesAtSE.get(candidateSE, sys.maxsize):
                            self.util.logVerbose("Number of files for %s: %d" % (candidateSE, len(lfns)))
                            for lfnChunk in breakListIntoChunks(lfns, maxFiles):
                                tasks.append((candidateSE, lfnChunk))
                        else:
                            self.util.logInfo(
                                "Limit number of files for %s to %d (out of %d)"
                                % (candidateSE, maxToReplicate, len(lfns))
                            )

        if alreadyReplicated:
            self.util.logInfo(
                "Found %d files that are already present at destination SE,"
                " set them Processed" % len(alreadyReplicated)
            )
            res = self.transClient.setFileStatusForTransformation(self.transID, "Processed", alreadyReplicated)
            if not res["OK"]:
                self.util.logError("Error setting files Processed", res["Message"])
                return res

        return S_OK(tasks)

    def _ArchiveDataset(self):
        """Plugin for archiving datasets, randomly chosen"""
        archiveSEs = resolveSEGroup(self.util.getPluginParam("ArchiveSEs", []))
        numberOfCopies = self.util.getPluginParam("NumberOfReplicas", 1)
        archiveActiveSEs = getActiveSEs(archiveSEs)
        if not archiveActiveSEs:
            archiveActiveSEs = archiveSEs
        return self._simpleReplication([], archiveActiveSEs, numberOfCopies=numberOfCopies)

    def _simpleReplication(self, mandatorySEs, secondarySEs, numberOfCopies=0, fromSEs=None, maxFiles=None):
        """Actually creates the replication tasks for replication plugins."""
        self.util.logInfo("Starting execution of plugin")
        mandatorySEs = set(mandatorySEs)
        secondarySEs = set(secondarySEs) - mandatorySEs
        if not numberOfCopies:
            numberOfCopies = len(secondarySEs) + len(mandatorySEs)
            activeSecondarySEs = secondarySEs
        else:
            activeSecondarySEs = getActiveSEs(secondarySEs)
            numberOfCopies = max(len(mandatorySEs), numberOfCopies)

        self.util.logVerbose(
            "%d replicas, mandatory at %s, optional at %s" % (numberOfCopies, mandatorySEs, activeSecondarySEs)
        )

        alreadyCompleted = []
        fileTargetSEs = {}
        for replicaSE, lfnGroup in getFileGroups(self.transReplicas).items():  # can be an iterator
            existingSEs = [se for se in replicaSE.split(",") if not self.util.dmsHelper.isSEFailover(se)]
            # If a FromSEs parameter is given, only keep the files that are at one of those SEs, mark the others NotProcessed
            if fromSEs:
                if not isinstance(fromSEs, list):
                    return S_ERROR("fromSEs parameter should be a list")
                if not set(existingSEs) & set(fromSEs):
                    res = self.transClient.setFileStatusForTransformation(self.transID, "NotProcessed", lfnGroup)
                    if not res["OK"]:
                        self.util.logError("Error setting files NotProcessed", res["Message"])
                    else:
                        self.util.logVerbose(
                            "Found %d files that are not in %s, set NotProcessed" % (len(lfnGroup), fromSEs)
                        )
                    continue

            # If there is no choice on the SEs, send all files at once, otherwise make chunks
            if numberOfCopies >= len(mandatorySEs) + len(activeSecondarySEs):
                lfnChunks = [lfnGroup]
            else:
                lfnChunks = breakListIntoChunks(lfnGroup, 100)

            self.util.logDebug("Split lfns in %d chunks" % len(lfnChunks))

            for lfns in lfnChunks:
                candidateSEs = self.util.closerSEs(existingSEs, secondarySEs)
                self.util.logDebug("Candidate SEs = %s" % ", ".join(candidateSEs))
                # Remove duplicated SEs (those that are indeed the same), but keep existing ones
                for se1 in [se for se in candidateSEs if se not in existingSEs]:
                    if self.util.isSameSEInList(se1, [se for se in candidateSEs if se != se1]):
                        candidateSEs.remove(se1)
                # Remove existing SEs from list of candidates
                ncand = len(candidateSEs)
                candidateSEs = [se for se in candidateSEs if se not in existingSEs]
                self.util.logDebug("Candidate SEs after removal = %s" % ", ".join(candidateSEs))
                needToCopy = numberOfCopies - (ncand - len(candidateSEs))
                stillMandatory = [se for se in mandatorySEs if se not in candidateSEs]
                candidateSEs = self.util.uniqueSEs(
                    stillMandatory + [se for se in candidateSEs if se in activeSecondarySEs]
                )
                needToCopy = max(needToCopy, len(stillMandatory))
                targetSEs = []
                if needToCopy > 0:
                    if needToCopy <= len(candidateSEs):
                        targetSEs = candidateSEs[0:needToCopy]
                    else:
                        targetSEs = candidateSEs
                        needToCopy -= len(targetSEs)
                        # Try and replicate to non active SEs
                        otherSEs = [se for se in secondarySEs if se not in targetSEs]
                        if otherSEs:
                            targetSEs += otherSEs[0 : min(needToCopy, len(otherSEs))]
                else:
                    alreadyCompleted += lfns
                if targetSEs:
                    stringTargetSEs = ",".join(sorted(targetSEs))
                    # Now assign the individual files to their targets
                    chunkFileTargetSEs, completed = self.util.assignTargetToLfns(
                        lfns, self.transReplicas, stringTargetSEs
                    )
                    alreadyCompleted += completed
                    fileTargetSEs.update(chunkFileTargetSEs)

        # Update the status of the already done files
        if alreadyCompleted:
            self.util.logInfo("Found %s files that are already completed" % len(alreadyCompleted))
            self.transClient.setFileStatusForTransformation(self.transID, "Processed", alreadyCompleted)

        # Now group all of the files by their target SEs
        storageElementGroups = {}
        for lfn, stringTargetSEs in fileTargetSEs.items():  # can be an iterator
            storageElementGroups.setdefault(stringTargetSEs, []).append(lfn)

        self.util.logDebug("Storage Element Groups created: %s" % storageElementGroups)

        return S_OK(self.util.createTasks(storageElementGroups, chunkSize=maxFiles))

    def _FakeReplication(self):
        """Creates replication tasks for to the existing SEs.

        Used only for tests!
        """
        storageElementGroups = {}
        for replicaSE, lfnGroup in getFileGroups(self.transReplicas).items():  # can be an iterator
            existingSEs = replicaSE.split(",")
            for lfns in breakListIntoChunks(lfnGroup, 100):
                stringTargetSEs = existingSEs[0]
                storageElementGroups.setdefault(stringTargetSEs, []).extend(lfns)
        if self.pluginCallback:
            self.pluginCallback(self.transID, invalidateCache=True)
        return S_OK(self.util.createTasks(storageElementGroups))

    def _DestroyDataset(self):
        """Plugin setting all existing SEs as targets."""
        self.util.logInfo("Starting execution of plugin")
        res = self._removeReplicas(keepSEs=[], minKeep=0)
        if not res["OK"] or not res["Value"]:
            return res
        tasks = res["Value"]
        if self.util.getPluginParam("CleanTransformations", False):
            lfns = sum((task[1] for task in tasks), [])
            # Check if some of these files are used by transformations
            selectDict = {"LFN": lfns}
            res = self.transClient.getTransformationFiles(selectDict)
            if not res["OK"]:
                self.util.logError("Error getting transformation files for %d files" % len(lfns), res["Message"])
            else:
                processedFiles = set()
                self.util.logVerbose(
                    "Out of %d files, %d occurrences were found in transformations" % (len(lfns), len(res["Value"]))
                )
                transDict = defaultdict(list)
                for fileDict in res["Value"]:
                    # Processed files are immutable, and don't kill yourself!
                    if fileDict["TransformationID"] != self.transID:
                        if fileDict["Status"] not in ("Processed", "Removed"):
                            transDict[fileDict["TransformationID"]].append(fileDict["LFN"])
                        else:
                            processedFiles.add(fileDict["LFN"])
                if transDict:
                    self.util.logVerbose(
                        "Files to be set Removed in transformations %s"
                        % ",".join("%d" % trans for trans in sorted(transDict))
                    )
                else:
                    self.util.logVerbose("No files to be set Removed in other transformations")
                if processedFiles:
                    self.util.logInfo(
                        "%d files are being removed but were already"
                        " Processed or Removed in other transformations" % len(processedFiles)
                    )
                for trans, lfns in transDict.items():  # can be an iterator
                    # Do not actually take action for a fake transformation (dirac-test-plugin)
                    if self.transID > 0:
                        res = self.transClient.setFileStatusForTransformation(trans, "Removed", lfns)
                        action = "set"
                    else:
                        res = {"OK": True, "Value": lfns}
                        action = "to be set"
                    if not res["OK"]:
                        self.util.logError(
                            "Error setting %d files in transformation %d to status Removed" % (len(lfns), trans),
                            res["Message"],
                        )
                    else:
                        self.util.logInfo(
                            "%d files out of %d %s as 'Removed' in transformation %d"
                            % (len(res["Value"]), len(lfns), action, trans)
                        )

        return S_OK(tasks)

    def _ReduceReplicasKeepDestination(self):
        """Plugin for reducing the number of replicas to NumberOfReplicas."""
        # this is the number of replicas to be kept in addition to keepSEs and mandatorySEs
        minKeep = -abs(self.util.getPluginParam("NumberOfReplicas", 1))
        return self._RemoveReplicasKeepDestination(minKeep=minKeep)

    def _RemoveReplicasKeepDestination(self, minKeep=None):
        """Plugin used to remove all replicas from a set of SEs except at run
        destination."""
        fromSEs = set(resolveSEGroup(self.util.getPluginParam("FromSEs", [])))
        keepSEs = resolveSEGroup(self.util.getPluginParam("KeepSEs", ["Tier1-Archive"]))
        # this is the number of replicas to be kept in addition to keepSEs and mandatorySEs
        # Remove 1 as we keep the run destination as well...
        if minKeep is None:
            minKeep = abs(self.util.getPluginParam("NumberOfReplicas", 1))

        # Group the  data by run
        runFileDict = self.util.getFilesGroupedByRun()
        if not runFileDict:
            # No files, no tasks!
            return S_OK([])

        res = self.util.getTransformationRuns(runFileDict)
        if not res["OK"]:
            self.util.logError(
                "Error when getting transformation runs",
                "for runs %s: %s" % (",".join(str(run) for run in runFileDict), res["Message"]),
            )
            return res
        runSites = dict(
            (run["RunNumber"], set(run["SelectedSite"].split(","))) for run in res["Value"] if run["SelectedSite"]
        )

        # Consider all runs in turn
        tasks = []
        for runID, runLfns in runFileDict.items():  # can be an iterator
            replicas = dict(
                (lfn, ses) for lfn, ses in self.transReplicas.items() if lfn in runLfns
            )  # can be an iterator
            existingSEs = set(se for ses in replicas.values() for se in ses if se not in keepSEs)  # can be an iterator
            destinationSE = self.util.getSEForDestination(runID, existingSEs)
            if destinationSE is None:
                # If there is no replica at destination, remove randomly
                self.util.logInfo("No replicas found at destination for %d files of run %d" % (len(runLfns), runID))
                replicasWithKeep = {}
                replicasNoKeep = replicas
            else:
                self.util.logVerbose("Preparing tasks for run %d, destination %s" % (runID, destinationSE))
                replicasWithKeep = dict(
                    (lfn, ses) for lfn, ses in replicas.items() if destinationSE in ses
                )  # can be an iterator
                replicasNoKeep = dict(
                    (lfn, ses) for lfn, ses in replicas.items() if destinationSE not in ses
                )  # can be an iterator
            # We keep one more replica @ destinationSE, therefore decrease the number to be kept
            for reps, keep, kSEs in (
                (replicasNoKeep, minKeep, keepSEs),
                (replicasWithKeep, (abs(minKeep) - 1) * minKeep // abs(minKeep), keepSEs + [destinationSE]),
            ):
                if reps:
                    res = self._removeReplicas(replicas=reps, fromSEs=fromSEs, keepSEs=kSEs, minKeep=keep)
                    if not res["OK"]:
                        self.util.logError("Error creating tasks", res["Message"])
                    elif res["Value"]:
                        tasks += res["Value"]
                        targetSEs = set(se for targets, _lfns in res["Value"] for se in targets.split(","))
                        runTargets = runSites.get(runID, set())
                        if targetSEs - runTargets:
                            # Set destination sites for that run
                            runTargets = ",".join(sorted(targetSEs | runTargets))
                            self.util.logVerbose("Setting destination for run %d to %s" % (runID, runTargets))
                            res = self.transClient.setTransformationRunsSite(self.transID, runID, runTargets)
                            if not res["OK"]:
                                self.util.logError(
                                    "Failed to set target SEs to run %d as %s" % (runID, runTargets), res["Message"]
                                )
        if self.throttledFilesPerSE:
            self.util.logInfo("Throttled removal of files", str(dict(self.throttledFilesPerSE)))
        return S_OK(tasks)

    def _RemoveDatasetFromDisk(self):
        """Plugin used to remove disk replicas, keeping some (e.g. archives)"""
        keepSEs = resolveSEGroup(self.util.getPluginParam("KeepSEs", ["Tier1-Archive"]))
        self.util.logInfo("Starting execution of plugin")
        return self._removeReplicas(keepSEs=keepSEs, minKeep=0)

    def _RemoveReplicas(self, minKeep=None):
        """Plugin for removing replicas from specific SEs specified in FromSEs."""
        fromSEs = resolveSEGroup(self.util.getPluginParam("FromSEs", []))
        keepSEs = resolveSEGroup(self.util.getPluginParam("KeepSEs", ["Tier1-Archive"]))
        mandatorySEs = resolveSEGroup(self.util.getPluginParam("MandatorySEs", []))
        # Allow removing explicitly from SEs in mandatorySEs
        mandatorySEs = [se for se in mandatorySEs if se not in fromSEs]
        # this is the minimum number of replicas to be kept in addition to keepSEs and mandatorySEs
        if minKeep is None:
            minKeep = abs(self.util.getPluginParam("NumberOfReplicas", 1))

        self.util.logInfo("Starting execution of plugin")
        return self._removeReplicas(fromSEs=fromSEs, keepSEs=keepSEs, mandatorySEs=mandatorySEs, minKeep=minKeep)

    def _ReduceReplicas(self):
        """Plugin for reducing the number of replicas to NumberOfReplicas."""
        # this is the number of replicas to be kept in addition to keepSEs and mandatorySEs
        self.util.logInfo("Starting execution of plugin")
        minKeep = -abs(self.util.getPluginParam("NumberOfReplicas", 1))
        return self._RemoveReplicas(minKeep=minKeep)

    def _removeReplicas(self, replicas=None, fromSEs=None, keepSEs=None, mandatorySEs=None, minKeep=999):
        """Utility actually implementing the logic to remove replicas or files."""
        if fromSEs is None:
            fromSEs = []
        if keepSEs is None:
            keepSEs = []
        if mandatorySEs is None:
            mandatorySEs = []
        reduceSEs = minKeep < 0
        minKeep = abs(minKeep)
        if replicas is None:
            replicas = self.transReplicas

        # Read the cached information from disk
        self.util.readCacheFile(self.workDirectory)
        # Is throttling on pending transfers requested?
        throttleLimit = self.util.getPluginParam("ThrottlePendingTasks", 0)
        if throttleLimit and not self.pendingTasksPerSE:
            # Get the number of not yet running jobs for this trans type at each SE
            res = self.util.getPendingTasks(self.params["Type"])
            if not res["OK"]:
                self.util.logError("Error getting number of pending tasks", res["Message"])
                return res
            if res["Value"] is None:
                return S_OK([])
            # Set them as data members as the method can be called in a loop
            self.pendingTasksPerSE = res["Value"]

        storageElementGroups = {}
        notInKeepSEs = []
        for replicaSE, lfns in getFileGroups(replicas).items():  # can be an iterator
            replicaSE = replicaSE.split(",")
            if minKeep == 0 and keepSEs:
                # Check that the dataset exists at least at 1 keepSE
                if not [se for se in replicaSE if se in keepSEs]:
                    notInKeepSEs.extend(lfns)
                    continue
            existingSEs = [se for se in replicaSE if se not in keepSEs and not self.util.dmsHelper.isSEFailover(se)]
            if minKeep == 0:
                # We only keep the replicas in keepSEs
                targetSEs = sorted(existingSEs)
            else:
                targetSEs = []
                # Take into account the mandatory SEs
                existingSEs = [se for se in existingSEs if se not in mandatorySEs]
                self.util.logVerbose(
                    "%d files, non-keep SEs: %s, removal from %s, keep %d" % (len(lfns), existingSEs, fromSEs, minKeep)
                )
                # print existingSEs, fromSEs, minKeep
                fromSet = set(fromSEs)
                existingSet = set(existingSEs)
                if len(existingSEs) > minKeep:
                    # explicit deletion
                    if fromSEs and not reduceSEs:
                        # check how  many replicas would be left if we remove all from fromSEs
                        nLeft = len(existingSet - fromSet)
                        # we can delete all replicas in fromSEs
                        targetSEs = list(existingSet & fromSet)
                        self.util.logVerbose(
                            "Target SEs, 1st level: %s, number of left replicas: %d" % (targetSEs, nLeft)
                        )
                        if nLeft < minKeep:
                            # we should keep some in fromSEs, too bad
                            targetSEs = randomize(targetSEs)[0 : minKeep - nLeft]
                            self.util.logInfo(
                                "Found %d files that could only be deleted in %d of the requested SEs"
                                % (len(lfns), minKeep - nLeft)
                            )
                            self.util.logVerbose("Target SEs, 2nd level: %s" % targetSEs)
                    elif fromSEs:
                        # Here the fromSEs are only a preference (we want to keep only exactly minKeep replicas)
                        targetSEs = randomize(list(existingSet & fromSet)) + randomize(list(existingSet - fromSet))
                        targetSEs = targetSEs[0:-minKeep]
                    else:
                        # remove all replicas and keep only minKeep
                        targetSEs = randomize(existingSEs)[0:-minKeep]
                    targetSEs.sort()
                    self.util.logVerbose("Remove %d replicas from %s" % (len(lfns), ",".join(targetSEs)))
                elif not reduceSEs and (existingSet & fromSet):
                    nLeft = len(existingSet - fromSet)
                    self.util.logInfo(
                        "Found %d files at %s with not enough replicas (%d left, %d requested), set Problematic"
                        % (len(lfns), ",".join(existingSEs), nLeft, minKeep)
                    )
                    self.transClient.setFileStatusForTransformation(self.transID, "Problematic", lfns)
                    continue

            if targetSEs:
                toRemove = len(lfns)
                # Throttle if needed
                if throttleLimit:
                    for se in targetSEs:
                        toRemove = min(toRemove, max(0, throttleLimit - self.pendingTasksPerSE[se]))
                        if toRemove != len(lfns):
                            self.util.logVerbose("Throttle files", "for %s" % se)
                            self.throttledFilesPerSE[se] += len(lfns) - toRemove
                            break
                if toRemove:
                    stringTargetSEs = ",".join(targetSEs)
                    storageElementGroups.setdefault(stringTargetSEs, []).extend(lfns[:toRemove])
                    # Count files as pending
                    if throttleLimit:
                        for se in targetSEs:
                            self.pendingTasksPerSE[se] += toRemove
            else:
                self.util.logInfo("Found %s files that don't need any replica deletion, set Processed" % len(lfns))
                self.transClient.setFileStatusForTransformation(self.transID, "Processed", lfns)

        if notInKeepSEs:
            self.util.logInfo(
                "Found %d files not in at least one keepSE, no removal done, set Problematic" % len(notInKeepSEs)
            )
            self.transClient.setFileStatusForTransformation(self.transID, "Problematic", notInKeepSEs)

        if (
            throttleLimit
            and self.throttledFilesPerSE
            and self.plugin not in ("ReduceReplicasKeepDestination", "RemoveReplicasKeepDestination")
        ):
            self.util.logInfo("Throttled removal of files", str(dict(self.throttledFilesPerSE)))

        if self.pluginCallback:
            self.pluginCallback(self.transID, invalidateCache=True)
        return S_OK(self.util.createTasks(storageElementGroups))

    def _RemoveReplicasWhenProcessed(self, maxFiles=None):
        """This plugin considers files and checks whether they were processed for a
        list of processing passes For files that were processed, it sets replica
        removal tasks from a set of SEs."""
        keepSEs = resolveSEGroup(self.util.getPluginParam("KeepSEs", []))
        fromSEs = set(resolveSEGroup(self.util.getPluginParam("FromSEs", []))) - set(keepSEs)
        # Ignore files that are at a banned SE
        bannedSEs = set(se for se in fromSEs if not StorageElement(se).status()["Remove"])
        if not fromSEs:
            self.util.logError("No SEs where to delete from, check overlap with %s" % keepSEs)
            return S_OK([])
        processingPasses = self.util.getPluginParam("ProcessingPasses", [])

        transStatus = self.params["Status"]
        self.util.readCacheFile(self.workDirectory)

        if not processingPasses:
            self.util.logWarn("No processing pass(es)")
            return S_OK([])

        maxTime = self.util.getPluginParam("MaxTimeAllowed", 0)
        pluginStartTime = time.time()

        self.util.setCachedTimeExceeded(False)
        try:
            # Now we must find out whether the input files have a descendant in the processing passes
            result = self.util.getProductions(processingPasses, transStatus)
            if not result["OK"]:
                return result
            if not result["Value"]:
                return S_OK([])
            bkPathList, productions = result["Value"]
            if productions is None or not productions.get("List"):
                return S_OK([])

            # Group files per StorageElement
            replicaGroups = getFileGroups(self.transReplicas)
            self.util.logVerbose("Using %d input files, in %d groups" % (len(self.transReplicas), len(replicaGroups)))
            storageElementGroups = {}
            newGroups = {}
            for stringSEs, lfns in replicaGroups.items():  # can be an iterator
                replicaSEs = set(stringSEs.split(","))
                if replicaSEs & bannedSEs:
                    # Ignore these files
                    continue
                targetSEs = fromSEs & replicaSEs
                if not targetSEs:
                    # This is a fake to have a placeholder for the replica location... Later it is not used
                    self.util.logVerbose(
                        "%d files are not in required list (only at %s)" % (len(lfns), ",".join(sorted(replicaSEs)))
                    )
                    newGroups.setdefault(",".join(sorted(replicaSEs)), []).extend(lfns)
                elif not replicaSEs - fromSEs:
                    self.util.logInfo(
                        "%d files are only in required list (only at %s), don't remove (yet)"
                        % (len(lfns), ",".join(sorted(replicaSEs)))
                    )
                else:
                    self.util.logVerbose(
                        "%d files are in required list (also at %s)"
                        % (len(lfns), ",".join(sorted(replicaSEs - fromSEs)))
                    )
                    newGroups.setdefault(",".join(sorted(targetSEs)), []).extend(lfns)

            # Restrict the query to the BK to the interesting productions
            #####################
            # Loop on storages  #
            #####################
            for stringTargetSEs in randomize(newGroups):
                # if enough time already spent, exit
                # this is better placed at the beginning of the loop in case timeout in last item
                timeSpent = time.time() - pluginStartTime
                if maxTime and timeSpent > maxTime:
                    # We break the loop here and set a flag in the cached file to execute next time
                    self.util.setCachedTimeExceeded(True)
                    self.util.logInfo("Enough time spent in plugin (%.1f seconds), exit" % (timeSpent))
                    break

                lfns = set(newGroups[stringTargetSEs])
                # Use the cached information if any
                bkPathsToCheck = dict(
                    (lfn, set(self.util.cachedLFNProcessedPath.get(lfn, bkPathList)) & set(bkPathList)) for lfn in lfns
                )
                # Only check files that are not fully processed (cache contains processing passes still not done)
                lfnsToCheck = set(lfn for lfn in bkPathsToCheck if bkPathsToCheck[lfn])
                self.util.logInfo("Checking descendants for %d files at %s" % (len(lfnsToCheck), stringTargetSEs))
                # Update with the cached information
                remaining = len(bkPathList)
                for bkPath in bkPathList:
                    # How many iterations are left?
                    remaining -= 1
                    prods = productions["List"][bkPath]
                    # If there is nothing left to do, exit
                    if not prods or not lfnsToCheck:
                        break
                    lfnsToCheckForPath = set(lfn for lfn in lfnsToCheck if bkPath in bkPathsToCheck[lfn])
                    if not lfnsToCheckForPath:
                        continue
                    startTime = time.time()
                    res = self.util.checkForDescendants(lfnsToCheckForPath, prods)
                    if not res["OK"]:
                        self.util.logError("Error checking descendants using utility", res["Message"])
                    processedLfns = res.get("Value", set())
                    self.util.logVerbose(
                        "Found %s processed files in %.1f seconds"
                        % (len(processedLfns) if processedLfns else "no", time.time() - startTime)
                    )
                    # Remove bkPath from processing passes to check for lLFNs found processed
                    for lfn in processedLfns:
                        if bkPath not in bkPathsToCheck[lfn]:
                            self.util.logWarn("LFN not in list: %s" % lfn, str(bkPathsToCheck[lfn]))
                        else:
                            bkPathsToCheck[lfn].remove(bkPath)
                    lfnsToCheckForPath -= processedLfns
                    # Only worth checking if not the last processing pass
                    if remaining:
                        notProcessed = set(lfn for lfn in lfnsToCheckForPath if bkPath in bkPathsToCheck[lfn])
                        if notProcessed:
                            self.util.logVerbose(
                                "%d files not processed by processing pass %s, don't check further"
                                % (len(notProcessed), bkPathList[bkPath])
                            )
                            lfnsToCheck -= notProcessed

                lfnsProcessed = [lfn for lfn in lfns if not bkPathsToCheck[lfn]]
                self.util.cachedLFNProcessedPath.update(bkPathsToCheck)
                # print lfnsProcessed, bkPathsToCheck
                self.util.logInfo(
                    "Found %d / %d files that are processed (/ not) at %s"
                    % (len(lfnsProcessed), len([lfn for lfn in lfns if bkPathsToCheck[lfn]]), stringTargetSEs)
                )
                if lfnsProcessed:
                    targetSEs = set(stringTargetSEs.split(","))
                    if not targetSEs & fromSEs:
                        # Files are processed but are no longer at the requested SEs, set them Processed
                        self._alreadyProcessedLFNs.setdefault(",".join(fromSEs), []).extend(lfnsProcessed)
                        self.util.logInfo(
                            "%d processed files are no longer in required SE list: set them Processed"
                            % len(lfnsProcessed)
                        )
                        self.transClient.setFileStatusForTransformation(self.transID, "Processed", lfnsProcessed)
                    else:
                        storageElementGroups.setdefault(stringTargetSEs, []).extend(lfnsProcessed)

                ###############
                # End of loop #
                ###############
            if not storageElementGroups:
                return S_OK([])
        except Exception as e:  # pylint: disable=broad-except
            self.util.logException("Exception while executing the plugin", "", lException=e)
            return S_ERROR(e)
        finally:
            self.util.writeCacheFile()
            if self.pluginCallback:
                self.pluginCallback(self.transID, invalidateCache=True)
        return S_OK(self.util.createTasks(storageElementGroups, chunkSize=maxFiles))

    def _RemoveReplicasWithAncestors(self):
        """Same as _RemoveReplicasWhenProcessed but also remove parents This plugin
        is useful for removing at once RDST and RAW files after stripping."""
        return self.__addAncestors(pluginMethod=self._RemoveReplicasWhenProcessed)

    def __getAncestorLFNs(self, lfns):
        ancestors = self.util.getFileAncestors(lfns, depth=1)
        if not ancestors["OK"]:
            self.util.logError("Error getting ancestors", ancestors["Message"])
            return ancestors
        ancestors = [
            anc["FileName"] for ancList in ancestors["Value"]["Successful"].values() for anc in ancList
        ]  # can be an iterator
        return S_OK(ancestors)

    def __addAncestors(self, pluginMethod=None):
        """Call a standard plugin and then add ancestors to tasks."""
        maxFiles = self.util.getPluginParam("MaxFilesPerTask", 100) // 2
        tasks = pluginMethod(maxFiles=maxFiles)
        if not tasks["OK"]:
            return tasks
        newTasks = []
        addedAncestors = []
        for targetSE, lfns in tasks["Value"]:
            ancestors = self.__getAncestorLFNs(lfns)
            if not ancestors["OK"]:
                return ancestors
            ancestors = ancestors["Value"]
            # It is not possible to create a task with files that are not in the transformation!
            # therefore add them...
            if ancestors:
                res = self.transClient.addFilesToTransformation(self.transID, ancestors)
                if not res["OK"]:
                    self.util.logError("Failed to add files to transformation", res["Message"])
                    return res
                # Only put added files in tasks
                addedLfns = [
                    lfn for (lfn, status) in res["Value"]["Successful"].items() if status == "Added"
                ]  # can be an iterator
                addedAncestors += addedLfns
            else:
                addedLfns = []
            newTasks.append((targetSE, lfns + addedLfns))
        # This dict is those files already processed by the initial plugin (i.e. no need to process them)
        for targetSE, lfns in self._alreadyProcessedLFNs.items():  # can be an iterator
            ancestors = self.__getAncestorLFNs(lfns)
            if not ancestors["OK"]:
                return ancestors
            ancestors = ancestors["Value"]
            if ancestors:
                res = self.transClient.addFilesToTransformation(self.transID, ancestors)
                if not res["OK"]:
                    self.util.logError("Failed to add files to transformation", res["Message"])
                    return res
                addedLfns = [
                    lfn for (lfn, status) in res["Value"]["Successful"].items() if status == "Added"
                ]  # can be an iterator
                self.util.logVerbose("Found %d ancestors of Processed files: add them to tasks" % len(addedLfns))
                addedAncestors += addedLfns
                for ancChunk in breakListIntoChunks(addedLfns, 2 * maxFiles):
                    newTasks.append((targetSE, ancChunk))
        if addedAncestors:
            self.util.logInfo("Added %d ancestors to tasks" % len(addedAncestors))
        return S_OK(newTasks)

    def _ReplicateToLocalSE(self, maxFiles=None):
        """Used for example to replicate from a buffer to a tape SE on the same
        site."""
        res = self.util.getMaxFilesToReplicate(self.workDirectory)
        if not res["OK"]:
            return res
        watermark, maxFilesAtSE = res["Value"]
        # This is a convention, to skip the loop or to stop replicating
        if watermark is None:
            return S_OK([])
        destSEs = set(maxFilesAtSE)

        # Read the cached information from disk
        self.util.readCacheFile(self.workDirectory)
        # Is throttling on pending transfers requested?
        throttleLimit = self.util.getPluginParam("ThrottlePendingTasks", 0)
        if throttleLimit:
            # Get the number of not yet running jobs for this trans type at each SE
            res = self.util.getPendingTasks(self.params["Type"])
            if not res["OK"]:
                self.util.logError("Error getting number of pending tasks", res["Message"])
                return res
            if res["Value"] is None:
                return S_OK([])
            self.pendingTasksPerSE = res["Value"]

        overflowSEs = set(resolveSEGroup(self.util.getPluginParam("OverflowSEs", [])))
        storageElementGroups = {}

        for replicaSE, lfns in getFileGroups(self.transReplicas).items():  # can be an iterator
            replicaSEs = set(se for se in replicaSE.split(",") if not self.util.dmsHelper.isSEFailover(se))
            if not replicaSEs:
                continue
            okSEs = replicaSEs & destSEs
            if okSEs:
                # We have to choose only one SE to replicate to...
                #  There should in principle not be more but to be safe, take one only
                self._alreadyProcessedLFNs.setdefault(list(okSEs)[0], []).extend(lfns)
                self.util.logInfo(
                    "Found %d files that are already present in the destination SEs (status set Processed)" % len(lfns)
                )
                res = self.transClient.setFileStatusForTransformation(self.transID, "Processed", lfns)
                if not res["OK"]:
                    self.util.logError("Can't set files to Processed", "(%d files): %s" % (len(lfns), res["Message"]))
                    return res
                continue
            targetSEs = destSEs - replicaSEs
            candidateSEs = self.util.closerSEs(replicaSEs, targetSEs, local=True)
            if candidateSEs:
                # If the max number of files to copy is negative, stop
                shortSEs = [se for se in candidateSEs if maxFilesAtSE.get(se, sys.maxsize) == 0]
                candidateSEs = [se for se in candidateSEs if se not in shortSEs]
                if not candidateSEs:
                    self.util.logInfo(
                        "No candidate SE where more files are accepted (%s not allowed)" % ",".join(shortSEs)
                    )
                else:
                    # Check if enough free space
                    freeSpace = self.util.getStorageFreeSpace(candidateSEs + list(overflowSEs))
                    shortSEs = [se for se in candidateSEs if freeSpace[se] < watermark]
                    candidateSEs = [se for se in candidateSEs if se not in shortSEs]
                    if not candidateSEs:
                        if overflowSEs:
                            # Use some overflow SE to replicate files
                            candidateSEs = [
                                se
                                for se in self.util.rankSEs(overflowSEs)
                                if freeSpace[se] >= watermark and maxFilesAtSE.get(se, sys.maxsize) > 0
                            ]
                        if candidateSEs:
                            self.util.logInfo(
                                "No enough space (%s TB) found at %s, use %s instead"
                                % (watermark, ",".join(shortSEs), candidateSEs[0])
                            )
                        else:
                            self.util.logInfo("No enough space (%s TB) found at %s" % (watermark, ",".join(shortSEs)))
                    if candidateSEs:
                        # Select a single SE out of candidates; in most cases there is one only
                        candidateSE = candidateSEs[0]
                        maxToReplicate = maxFilesAtSE.get(candidateSE, sys.maxsize)
                        reason = "(Max files reached)"
                        # If throttling is requested, limit the number of files
                        if throttleLimit:
                            # Limit the number of files to replicate
                            maxToReplicate = min(len(lfns), max(0, throttleLimit - self.pendingTasksPerSE[candidateSE]))
                            reason = "(Throttling)"
                        if maxToReplicate < len(lfns):
                            self.util.logInfo(
                                "Limit number of files %s for %s to %d (out of %d)"
                                % (reason, candidateSE, maxToReplicate, len(lfns))
                            )
                        else:
                            maxToReplicate = len(lfns)
                            self.util.logVerbose("Number of files for %s: %d" % (candidateSE, len(lfns)))
                        # Count new files at candidateSE
                        if throttleLimit:
                            self.pendingTasksPerSE[candidateSE] += maxToReplicate
                        storageElementGroups.setdefault(candidateSE, []).extend(lfns[:maxToReplicate])
            else:
                self.util.logWarn("Could not find a local SE for %d files, set them Problematic" % len(lfns))
                res = self.transClient.setFileStatusForTransformation(self.transID, "Problematic", lfns)
                if not res["OK"]:
                    self.util.logError("Can't set files to Problematic", "(%d files): %s" % (len(lfns), res["Message"]))
                    return res

        return S_OK(self.util.createTasks(storageElementGroups, chunkSize=maxFiles))

    def _ReplicateWithAncestors(self):
        """Same as _ReplicateToLocalSE but also replicate parents If only one SE is
        given, use _ReplicateDataset This plugin is useful for prestaging at once
        RDST and RAW files before stripping."""
        destSEs = set(resolveSEGroup(self.util.getPluginParam("DestinationSEs", [])))
        if len(destSEs) == 1:
            return self.__addAncestors(pluginMethod=self._ReplicateDataset)
        return self.__addAncestors(pluginMethod=self._ReplicateToLocalSE)

    def _Healing(self):
        """Plugin that creates task for replicating files to the same SE where they
        are declared problematic."""
        self.util.cleanFiles(self.transFiles, self.transReplicas)
        storageElementGroups = {}

        for replicaSE, lfns in getFileGroups(self.transReplicas).items():  # can be an iterator
            replicaSE = set(se for se in replicaSE.split(",") if not self.util.dmsHelper.isSEFailover(se))
            if not replicaSE:
                self.util.logInfo(
                    "Found %d files that don't have a suitable source replica. Set Problematic" % len(lfns)
                )
                res = self.transClient.setFileStatusForTransformation(self.transID, "Problematic", lfns)
                continue
            # get no problematic replicas only
            res = self.fileCatalog.getReplicas(lfns, allStatus=False)
            if not res["OK"]:
                self.util.logError("Error getting catalog replicas", res["Message"])
                continue
            replicas = res["Value"]["Successful"]
            noMissingSE = []
            noOtherReplica = []
            for lfn in lfns:
                if lfn not in replicas:
                    # This file has no active replicas, problematic
                    noOtherReplica.append(lfn)
                else:
                    targetSEs = replicaSE - set(replicas[lfn])
                    if targetSEs:
                        storageElementGroups.setdefault(",".join(sorted(targetSEs)), []).append(lfn)
                    else:
                        # print lfn, sorted( replicas[lfn] ), sorted( replicaSE )
                        noMissingSE.append(lfn)
            if noOtherReplica:
                self.util.logInfo(
                    "Found %d files that have no other active replica (set Problematic)" % len(noOtherReplica)
                )
                res = self.transClient.setFileStatusForTransformation(self.transID, "Problematic", noOtherReplica)
                if not res["OK"]:
                    self.util.logError(
                        "Can't set %d files of transformation %s to 'Problematic': %s"
                        % (len(noOtherReplica), str(self.transID), res["Message"])
                    )
            if noMissingSE:
                self.util.logInfo(
                    "Found %d files that are already present in the destination SEs (set Processed)" % len(noMissingSE)
                )
                res = self.transClient.setFileStatusForTransformation(self.transID, "Processed", noMissingSE)
                if not res["OK"]:
                    self.util.logError(
                        "Can't set %d files of transformation %s to 'Processed': %s"
                        % (len(noMissingSE), str(self.transID), res["Message"])
                    )
                    return res

        return S_OK(self.util.createTasks(storageElementGroups))

    def _DataChallengeReplication(self):
        """Plugin for replicating RAW data during the data challenges.
        What it does will change every time, but the idea is to be as
        close as possible to the RAWReplication, but without really
        caring about runs."""
        self.util.logInfo("Starting execution of plugin")

        res = self.util.getPluginShares(section="DataChallenge")
        if not res["OK"]:
            self.util.logError("Section DataChallenge in Shares not available")
            return res

        _, targetShares = res["Value"]

        sites = list(targetShares.keys())
        weights = list(targetShares.values())
        # Now group all of the files by their target SEs
        storageElementGroups = defaultdict(list)

        for lfn in self.transReplicas:  # can be an iterator
            # Choose from the site
            rndSite = random.choices(sites, weights=weights)[0]
            stringTargetSEs = f"{rndSite}-DC-BUFFER,{rndSite}-DC-RAW"
            storageElementGroups[stringTargetSEs].append(lfn)

        return S_OK(self.util.createTasks(storageElementGroups))
