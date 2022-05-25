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
"""This LHCbDIRAC agent takes BkQueries from the TranformationDB, and issue a
query to the BKK, for populating a table in the Transformation DB, with all the
files in input to a transformation.

A pickle file is used as a cache.
"""
import os
import time
import datetime
import pickle
from six.moves import queue as Queue
import six

from DIRAC import S_OK
from DIRAC.Core.Base.AgentModule import AgentModule
from DIRAC.Core.Utilities.ThreadPool import ThreadPool
from DIRAC.Core.Utilities.ThreadSafe import Synchronizer
from DIRAC.Core.Utilities.List import breakListIntoChunks
from DIRAC.TransformationSystem.Agent.TransformationAgentsUtilities import TransformationAgentsUtilities
from DIRAC.ConfigurationSystem.Client.Helpers.Operations import Operations
from LHCbDIRAC.BookkeepingSystem.Client.BookkeepingClient import BookkeepingClient
from LHCbDIRAC.TransformationSystem.Client.TransformationClient import TransformationClient

AGENT_NAME = "Transformation/BookkeepingWatchAgent"
gSynchro = Synchronizer()


class BookkeepingWatchAgent(AgentModule, TransformationAgentsUtilities):
    """LHCbDIRAC only agent.

    A threaded agent.
    """

    def __init__(self, *args, **kwargs):
        """c'tor."""
        AgentModule.__init__(self, *args, **kwargs)
        TransformationAgentsUtilities.__init__(self)

        self.bkQueriesToBeChecked = Queue.Queue()
        self.bkQueriesInCheck = []

        self.fullUpdatePeriod = 86400
        self.bkUpdateLatency = 7200
        self.debug = False

        self.transInThread = {}

        self.pickleFile = "BookkeepingWatchAgent.pkl"
        self.chunkSize = 1000

        # No need to give full list as it is in the CS anyway
        self.pluginsWithRunInfo = []

        self.timeLog = {}
        self.fullTimeLog = {}
        self.bkQueries = {}

        self.transClient = None
        self.bkClient = None

    def initialize(self):
        """Make the necessary initializations.

        The ThreadPool is created here, the _execute() method is what each
        thread will execute.
        """

        self.fullUpdatePeriod = self.am_getOption("FullUpdatePeriod", self.fullUpdatePeriod)
        self.bkUpdateLatency = self.am_getOption("BKUpdateLatency", self.bkUpdateLatency)
        self.debug = self.am_getOption("verbose", self.debug)

        self.pickleFile = os.path.join(self.am_getWorkDirectory(), self.pickleFile)
        self.chunkSize = self.am_getOption("maxFilesPerChunk", self.chunkSize)

        self.pluginsWithRunInfo = Operations().getValue(
            "TransformationPlugins/PluginsWithRunInfo", self.pluginsWithRunInfo
        )

        self._logInfo("Full Update Period: %d seconds" % self.fullUpdatePeriod)
        self._logInfo("BK update latency : %d seconds" % self.bkUpdateLatency)
        self._logInfo("Plugins with run info: %s" % ", ".join(self.pluginsWithRunInfo))

        self.transClient = TransformationClient()
        self.bkClient = BookkeepingClient()

        try:
            with open(self.pickleFile, "rb") as pf:
                self.timeLog = pickle.load(pf)
                self.fullTimeLog = pickle.load(pf)
                self.bkQueries = pickle.load(pf)
            self._logInfo("successfully loaded Log from", self.pickleFile, "initialize")
        except (EOFError, IOError):
            self._logInfo("failed loading Log from", self.pickleFile, "initialize")
            self.timeLog = {}
            self.fullTimeLog = {}
            self.bkQueries = {}

        maxNumberOfThreads = self.am_getOption("maxThreadsInPool", 1)
        threadPool = ThreadPool(maxNumberOfThreads, maxNumberOfThreads)

        for i in range(maxNumberOfThreads):
            threadPool.generateJobAndQueueIt(self._execute, [i])

        return S_OK()

    @gSynchro
    def __dumpLog(self):
        """dump the log in the pickle file."""
        if self.pickleFile:
            try:
                with open(self.pickleFile, "wb") as pf:
                    pickle.dump(self.timeLog, pf)
                    pickle.dump(self.fullTimeLog, pf)
                    pickle.dump(self.bkQueries, pf)
                self._logVerbose("successfully dumped Log into %s" % self.pickleFile)
            except IOError as e:
                self._logError("fail to open %s: %s" % (self.pickleFile, e))
            except pickle.PickleError as e:
                self._logError("fail to dump %s: %s" % (self.pickleFile, e))
            except ValueError as e:
                self._logError("fail to close %s: %s" % (self.pickleFile, e))

    ################################################################################

    def execute(self):
        """Main execution method.

        Just fills a list, and a queue, with BKKQueries ID.
        """

        # Get all the transformations
        result = self.transClient.getTransformations(condDict={"Status": ["Active", "Idle"]})
        if not result["OK"]:
            self._logError("Failed to get transformations.", result["Message"])
            return S_OK()
        transIDsList = [int(transDict["TransformationID"]) for transDict in result["Value"]]
        res = self.transClient.getTransformationsWithBkQueries(transIDsList)
        if not res["OK"]:
            self._logError("Failed to get transformations with Bk Queries.", res["Message"])
            return S_OK()
        transIDsWithBkQueriesList = res["Value"]

        _count = 0
        # Process each transformation
        for transID in transIDsWithBkQueriesList:
            if transID in self.bkQueriesInCheck:
                continue
            self.bkQueriesInCheck.append(transID)
            self.bkQueriesToBeChecked.put(transID)
            _count += 1

        self._logInfo("Out of %d transformations, %d put in thread queue" % (len(result["Value"]), _count))

        self.__dumpLog()
        return S_OK()

    def _execute(self, threadID):
        """Real executor.

        This is what is executed by the single threads - so do not return here! Just continue
        """

        while True:  # not self.bkQueriesToBeChecked.empty():

            transID = None

            try:

                transID = self.bkQueriesToBeChecked.get()
                self.transInThread[transID] = " [Thread%d] [%s] " % (threadID, str(transID))

                startTime = time.time()
                self._logInfo("Processing transformation %s." % transID, transID=transID)

                res = self.transClient.getTransformation(transID, extraParams=False)
                if not res["OK"]:
                    self._logError("Failed to get transformation", res["Message"], transID=transID)
                    continue
                transPlugin = res["Value"]["Plugin"]

                res = self.transClient.getBookkeepingQuery(transID)
                if not res["OK"]:
                    self._logError("Failed to get BkQuery", res["Message"], transID=transID)
                    continue
                bkQuery = res["Value"]

                # Determine the correct time stamp to use for this transformation
                now = datetime.datetime.utcnow()
                self.__timeStampForTransformation(transID, bkQuery, now)

                try:
                    files = self.__getFiles(transID, bkQuery, now)
                except RuntimeError as e:
                    # In case we failed a full query, we should retry full query until successful
                    if "StartDate" not in bkQuery:
                        self.bkQueries.pop(transID, None)
                    self._logError("Failed to get response from the Bookkeeping: %s" % e, "", "__getFiles", transID)
                    continue

                runDict = {}
                filesMetadata = {}
                # get the files metadata
                for lfnChunk in breakListIntoChunks(files, self.chunkSize):
                    start = time.time()
                    res = self.bkClient.getFileMetadata(lfnChunk)
                    self._logVerbose(
                        "Got metadata from BK for %d files" % len(lfnChunk), transID=transID, reftime=start
                    )
                    if not res["OK"]:
                        self._logError(
                            "Failed to get BK metadata for %d files" % len(lfnChunk), res["Message"], transID=transID
                        )
                        # No need to return as we only consider files that are successful...
                    else:
                        success = res["Value"]["Successful"]
                        # Test if the list of returned LFNs is within the supplied chunk
                        invalid = set(success) - set(lfnChunk)
                        if invalid:
                            self._logError(
                                "Invalid LFNs returned by getFileMetadata", ",".join(sorted(invalid)), transID=transID
                            )
                            for inv in invalid:
                                success.pop(inv)
                        filesMetadata.update(success)

                # There is no need to add the run information for a transformation that doesn't need it
                if transPlugin in self.pluginsWithRunInfo:
                    for lfn, metadata in filesMetadata.items():  # can be an iterator
                        runID = metadata.get("RunNumber", None)
                        if isinstance(runID, (six.string_types, six.integer_types)):
                            runDict.setdefault(int(runID), []).append(lfn)
                    try:
                        self.__addRunsMetadata(transID, list(runDict))
                    except RuntimeError as e:
                        self._logException(
                            "Failure adding runs metadata", method="__addRunsMetadata", lException=e, transID=transID
                        )
                else:
                    runDict[None] = list(filesMetadata)

                # Add all new files to the transformation
                for runID in sorted(runDict):
                    lfnList = runDict[runID]
                    # We enter all files of a run at once, otherwise do it by chunks
                    lfnChunks = [lfnList] if runID else breakListIntoChunks(lfnList, self.chunkSize)
                    for lfnChunk in lfnChunks:
                        # Add the files to the transformation
                        self._logVerbose("Adding %d lfns for transformation" % len(lfnChunk), transID=transID)
                        result = self.transClient.addFilesToTransformation(transID, lfnChunk)
                        if not result["OK"]:
                            self._logError(
                                "Failed to add %d lfns to transformation" % len(lfnChunk),
                                result["Message"],
                                transID=transID,
                            )
                            continue
                        else:
                            # Handle errors
                            errors = {}
                            for lfn, error in result["Value"]["Failed"].items():  # can be an iterator
                                errors.setdefault(error, []).append(lfn)
                            for error, lfns in errors.items():  # can be an iterator
                                self._logWarn("Failed to add files to transformation", error, transID=transID)
                                self._logVerbose("\n\t".join([""] + lfns))
                            # Add the metadata and RunNumber to the newly inserted files
                            addedLfns = [
                                lfn for (lfn, status) in result["Value"]["Successful"].items() if status == "Added"
                            ]  # can be an iterator
                            if addedLfns:
                                # Add files metadata: size and file type
                                lfnDict = dict(
                                    (
                                        lfn,
                                        {
                                            "Size": filesMetadata[lfn]["FileSize"],
                                            "FileType": filesMetadata[lfn]["FileType"],
                                        },
                                    )
                                    for lfn in addedLfns
                                )
                                res = self.transClient.setParameterToTransformationFiles(transID, lfnDict)
                                if not res["OK"]:
                                    self._logError(
                                        "Failed to set transformation files metadata", res["Message"], transID=transID
                                    )
                                    continue
                                # Add run information if it exists
                                if runID:
                                    self._logInfo(
                                        "Added %d files to transformation for run %d, now including run information"
                                        % (len(addedLfns), runID),
                                        transID=transID,
                                    )
                                    self._logVerbose(
                                        "Associating %d files to run %d" % (len(addedLfns), runID), transID=transID
                                    )
                                    res = self.transClient.addTransformationRunFiles(transID, runID, addedLfns)
                                    if not res["OK"]:
                                        self._logError(
                                            "Failed to associate %d files to run %d" % (len(addedLfns), runID),
                                            res["Message"],
                                            transID=transID,
                                        )
                                        continue
                                else:
                                    self._logInfo("Added %d files to transformation" % len(addedLfns), transID=transID)

            except Exception as x:  # pylint: disable=broad-except
                self._logException(
                    "Exception while adding files to transformation", lException=x, method="_execute", transID=transID
                )
            finally:
                self._logInfo("Processed transformation", transID=transID, reftime=startTime)
                if transID in self.bkQueriesInCheck:
                    self.bkQueriesInCheck.remove(transID)
                self.transInThread.pop(transID, None)

        return S_OK()

    @gSynchro
    def __timeStampForTransformation(self, transID, bkQuery, now):
        """Determine the correct time stamp to use for this transformation."""

        fullTimeLog = self.fullTimeLog.setdefault(transID, now)
        bkQueryLog = self.bkQueries.setdefault(transID, {})

        bkQueryLog.pop("StartDate", None)
        self.bkQueries[transID] = bkQuery.copy()
        if (
            transID in self.timeLog
            and bkQueryLog == bkQuery
            and (now - fullTimeLog) < datetime.timedelta(seconds=self.fullUpdatePeriod)
        ):
            # If it is more than a day since the last reduced query, make a full query just in case
            timeStamp = self.timeLog[transID]
            delta = datetime.timedelta(seconds=self.bkUpdateLatency)
            bkQuery["StartDate"] = (timeStamp - delta).strftime("%Y-%m-%d %H:%M:%S")
        if "StartDate" not in bkQuery:
            self.fullTimeLog[transID] = now

    def __getFiles(self, transID, bkQuery, now):
        """Perform the query to the Bookkeeping."""
        self._logInfo("Using BK query for transformation: %s" % str(bkQuery), transID=transID)
        start = time.time()
        result = self.bkClient.getFiles(bkQuery)
        self._logVerbose("BK query time: %.2f seconds." % (time.time() - start), transID=transID)
        if not result["OK"]:
            raise RuntimeError(result["Message"])
        else:
            self.__updateTimeStamp(transID, now)
            if result["Value"]:
                self._logInfo("Obtained %d files from BK" % len(result["Value"]), transID=transID)
            return result["Value"]

    @gSynchro
    def __updateTimeStamp(self, transID, now):
        """Update time stamp for current transformation to now."""
        self.timeLog[transID] = now

    def __addRunsMetadata(self, transID, runsList):
        """Add the run metadata."""
        runsInCache = self.transClient.getRunsInCache({"Name": ["TCK", "CondDb", "DDDB"]})
        if not runsInCache["OK"]:
            raise RuntimeError(runsInCache["Message"])
        newRuns = list(set(runsList) - set(runsInCache["Value"]))
        if newRuns:
            self._logVerbose("Associating run metadata to %d runs" % len(newRuns), transID=transID)
            res = self.bkClient.getRunInformation({"RunNumber": newRuns, "Fields": ["TCK", "CondDb", "DDDB"]})
            if not res["OK"]:
                raise RuntimeError(res["Message"])
            else:
                for run, runMeta in res["Value"].items():  # can be an iterator
                    res = self.transClient.addRunsMetadata(run, runMeta)
                    if not res["OK"]:
                        raise RuntimeError(res["Message"])
        # Add run duration to the metadata
        runsInCache = self.transClient.getRunsInCache({"Name": ["Duration"]})
        if not runsInCache["OK"]:
            raise RuntimeError(runsInCache["Message"])
        newRuns = list(set(runsList) - set(runsInCache["Value"]))
        if newRuns:
            self._logVerbose("Associating run duration to %d runs" % len(newRuns), transID=transID)
            res = self.bkClient.getRunInformation({"RunNumber": newRuns, "Fields": ["JobStart", "JobEnd"]})
            if not res["OK"]:
                raise RuntimeError(res["Message"])
            else:
                for run, runMeta in res["Value"].items():  # can be an iterator
                    duration = (runMeta["JobEnd"] - runMeta["JobStart"]).seconds
                    res = self.transClient.addRunsMetadata(run, {"Duration": duration})
                    if not res["OK"]:
                        raise RuntimeError(res["Message"])

    def finalize(self):
        """Gracious finalization."""
        if self.bkQueriesInCheck:
            self._logInfo(
                "Wait for queue to get empty before terminating the agent (%d tasks)" % len(self.transInThread)
            )
            self.bkQueriesInCheck = []
            while self.transInThread:
                time.sleep(2)
            self.log.info("Threads are empty, terminating the agent...")
        return S_OK()
