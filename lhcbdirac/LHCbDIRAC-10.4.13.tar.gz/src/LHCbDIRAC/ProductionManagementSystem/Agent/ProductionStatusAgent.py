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
"""The ProductionStatusAgent monitors productions for active requests and takes
care to update their status. Initially this is just to handle simulation
requests.

Allowed production status transitions performed by this agent include:

Idle -> ValidatingInput
Idle -> ValidatingOutput

ValidatedOutput -> Completed

ValidatingInput -> RemovingFiles

RemovedFiles -> Completed

Active -> Idle

Testing -> Idle

In addition this also updates request status from Active to Done.

To do: review usage of production API(s) and re-factor into Production Client

AZ 10.14: merged with a part from RequestTrackingAgent to avoid race conditions
"""
import time
import os
import sqlite3
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, wait

import DIRAC
from DIRAC import S_OK, S_ERROR, gLogger
from DIRAC.Core.Base.AgentModule import AgentModule
from DIRAC.Core.Utilities.Time import timeThis
from DIRAC.Interfaces.API.Dirac import Dirac
from DIRAC.ConfigurationSystem.Client.Helpers.Operations import Operations

from LHCbDIRAC.TransformationSystem.Client.TransformationClient import TransformationClient
from LHCbDIRAC.Interfaces.API.DiracProduction import DiracProduction
from LHCbDIRAC.BookkeepingSystem.Client.BookkeepingClient import BookkeepingClient
from LHCbDIRAC.ProductionManagementSystem.Client.ProductionRequestClient import ProductionRequestClient

#############################################################################
# The following is used for StandAlone debugging only (outside Agent)
gStandAlone = False  # work in command line without Agent
# gSimulate = gStandAlone and True  # real clients are replaced with simulation
gSimulate = False
gDoRealUpdate = True  # call status updates
gDoRealTracking = True  # update requests progress

KNOWN_TASK_STATES = [
    "Checking",
    "Completed",
    "Created",
    "Matched",
    "Received",
    "Reserved",
    "Rescheduled",
    "Running",
    "Submitted",
    "Waiting",
]


class ProductionStatusAgent(AgentModule):
    """Usual DIRAC agent."""

    def __init__(self, *args, **kwargs):
        """c'tor.

        :param self: self reference
        :param str agentName: name of agent
        :param str loadName: load name of agent
        :param bool baseAgentName: whatever
        :param dict properties: whatever else
        """
        if not gStandAlone:
            AgentModule.__init__(self, *args, **kwargs)
        else:
            self.log = gLogger

        self.dProd = None
        self.dirac = None
        self.prClient = None
        self.tClient = None

        self.simulationTypes = Operations().getValue(
            "Transformations/ExtendableTransfTypes",
            ["MCSimulation", "Simulation"],
        )

        self.allKnownStates = (
            "RemovedFiles",
            "RemovingFiles",
            "ValidatedOutput",
            "ValidatingInput",
            "Testing",
            "Active",
            "Idle",
        )

        self.notify = True
        self.cacheFile = os.path.join(DIRAC.rootPath, "work/ProductionManagement/cache.db")

        # For processing transformations, it can happen that there are some Unused files
        # with which no tasks can be created. The number of such files can be different depending
        # from the module and distribution between centres.
        # So we declare such transformations isIdle() once there is no jobs, no files in other
        # pending states and the number of Unused files was not changed last cyclesTillIdle times
        self.cyclesTillIdle = 1
        self.filesUnused = {}  # <tID: { 'Number': x, 'NotChanged': n }

        self.prMasters = {}  # [ prID: [<subrequests> ...] ]
        self.prSummary = {}
        self.prProds = {}  # <prID>, map production to known request, from _getProductionRequestsProgress
        self.notPrTrans = defaultdict(list)  # transformation without PR, from _getTransformationsState
        self.toUpdate = []

    #############################################################################
    def initialize(self):
        """Sets default values."""
        # shifter
        self.am_setOption("shifterProxy", "ProductionManager")

        if not gStandAlone:
            self.notify = eval(self.am_getOption("NotifyProdManager", "True"))

        # Set the clients
        self.dProd = DiracProduction()
        self.dirac = Dirac()
        if gSimulate:
            raise NotImplementedError()
        self.prClient = ProductionRequestClient()
        self.tClient = TransformationClient()

        return S_OK()

    #############################################################################
    def execute(self):
        """The execution method, track requests progress and implement a part of
        Production SM."""
        updatedT = {}  # updated transformations
        updatedPr = []  # updated production requests (excluding tracking updates)

        # Distinguish between leafs and master requests
        # Masters should not appear in the prodReqSummary and they should have no
        # associated productions.
        self.prMasters = {}  # [ prID: [<subrequests> ...] ]
        self.prSummary = {}
        # { <reqID> :
        #     'type', 'master', 'bkTotal', 'prTotal',  - from _getActiveProductionRequests()
        #     'isDone', 'prods': [ <prodIf> : { 'Used', 'Events' } ] - from __getProductionRequestsProgress
        #     'state' for each production - from _getTransformationsState()
        #     'isIdle', 'isProcIdle' for each 'Active' or 'Idle' production,
        #     'isSimulation' - from _getIdleProductionRequestProductions()
        #     'isFinished' - from _applyProductionRequestsLogic()
        #     'filesTotal' - from _getIdleProductionRequestProductions()
        #     'filesProcessed' - from _getIdleProductionRequestProductions()
        #     'filesUnused' - from _getIdleProductionRequestProductions()
        #     'filesMaxReset' - from _getIdleProductionRequestProductions()
        #     'inputIDs' - from _getExtraInfo()
        #     'hasActiveInput' - from _trackProductionRequests()
        # }
        self.prProds = {}  # <prID>, map production to known request, from _getProductionRequestsProgress

        self.notPrTrans = defaultdict(list)  # transformation without PR, from _getTransformationsState

        self.log.info("******************************")
        self.log.info("Collecting required information")
        self.log.info("******************************")

        result = self._getActiveProductionRequests()
        if not result["OK"]:
            self.log.error("Aborting cycle", result["Message"])
            return S_OK()
        if len(self.prProds) < len(self.prSummary):
            self.log.fatal(
                "Aborting cycle, as the number of sub-requests can't be larger than the number of productions"
            )
            return S_OK()

        self._getTransformationsState()
        result = self._getIdleProductionRequestProductions()
        if not result["OK"]:
            self.log.error("Aborting cycle", result["Message"])
            return S_OK()

        # That is IMPORTANT to do that after we have the transformation status,
        # since Validation can (really???) update BK, rendering MC incomplete
        result = self._trackProductionRequests()  # also updates PR DB
        if not result["OK"]:
            self.log.error("Aborting cycle", result["Message"])
            return S_OK()

        self.log.info("******************************")
        self.log.info("Updating Production Requests and related transformations")
        self.log.info("******************************")

        self._applyProductionRequestsLogic(updatedT, updatedPr)

        self.log.info("******************************")
        self.log.info("Updating Production Request for unrelated transformations (replication, etc.)")
        self.log.info("******************************")

        self._applyOtherTransformationsLogic(updatedT)

        self.log.info("*********")
        self.log.info("Reporting")
        self.log.info("*********")

        if updatedT:
            self.log.info("Transformations updated this cycle:")
            for name, value in updatedT.items():
                self.log.info("Transformations %s: %s => %s" % (name, value["from"], value["to"]))

        if updatedPr:
            self.log.info("Production Requests updated to Done status:", "%s" % (", ".join(str(i) for i in updatedPr)))

        if gDoRealUpdate and not gSimulate:
            self._mailProdManager(updatedT, updatedPr)

        self._cleanFilesUnused()

        if gSimulate:
            self.tClient.animate(self.prClient)

        return S_OK()

    #############################################################################

    @timeThis
    def __getProductionRequestsProgress(self):
        """get known progress for Active requests related productions Failures
        there are critical and can enforce wrong logic."""
        self.log.verbose("Collecting old Production Request Progress...")
        result = self.prClient.getAllProductionProgress()
        if not result["OK"]:
            return S_ERROR("Could not retrieve production progress summary: %s" % result["Message"])
        progressSummary = result["Value"]  # { <prID> : [ <prodId> : { 'Used', 'Events' } ] }

        for prID, summary in self.prSummary.items():
            # Setting it before updating will give grace period before SM ops
            summary["isDone"] = summary["bkTotal"] >= summary["prTotal"]
            summary["prods"] = progressSummary.get(prID, {})
            for tID in summary["prods"]:
                self.prProds[tID] = prID
        self.log.verbose("Done with old Production Request Progress")
        return S_OK()

    @timeThis
    def _getActiveProductionRequests(self):
        """get 'Active' requests.

        Failures there are critical and can enforce wrong logic
        Note: this method can be moved to the service
        """
        self.log.info("Collecting active production requests...")
        result = self.prClient.getProductionRequestList(0, "", "ASC", 0, 0, {"RequestState": "Active"})
        if not result["OK"]:
            return S_ERROR("Could not retrieve active production requests: %s" % result["Message"])
        activeMasters = result["Value"]["Rows"]
        for pr in activeMasters:
            prID = pr["RequestID"]
            if pr["HasSubrequest"]:
                self.prMasters[prID] = []
                result = self.prClient.getProductionRequestList(prID, "", "ASC", 0, 0, {})
                if not result["OK"]:
                    return S_ERROR(
                        "Could not get subrequests for production request %s: %s" % (prID, result["Message"])
                    )
                for subPr in result["Value"]["Rows"]:
                    subPrID = subPr["RequestID"]
                    self.prSummary[subPrID] = {
                        "type": pr["RequestType"],
                        "master": prID,
                        "bkTotal": subPr["bkTotal"],
                        "prTotal": subPr["rqTotal"],
                    }
                    self.prMasters[prID].append(subPrID)
            else:
                self.prSummary[prID] = {
                    "type": pr["RequestType"],
                    "master": 0,
                    "bkTotal": pr["bkTotal"],
                    "prTotal": pr["rqTotal"],
                }

        result = self.__getProductionRequestsProgress()
        if not result["OK"]:
            return result

        self.log.info(
            "Will work with %s productions from %s Active (sub)requests" % (len(self.prProds), len(self.prSummary))
        )
        self.log.verbose("Done with collecting Active production requests")
        return S_OK()

    @timeThis
    def __getTransformations(self, status):
        """dev function.

        Get the transformations (print info in the meanwhile)
        """
        res = self.tClient.getTransformationWithStatus(status)
        if not res["OK"]:
            self.log.error("Failed to get transformations", "%s: %s" % (status, res["Message"]))
            raise RuntimeError("Failed to get %s transformations: %s" % (status, res["Message"]))
        if not res["Value"]:
            self.log.debug("No transformations in %s status" % status)
            return []
        if len(res["Value"]) > 20:
            self.log.verbose(
                "The following number of transformations are in %s status: %u" % (status, len(res["Value"]))
            )
        else:
            valOutStr = ", ".join(str(i) for i in res["Value"])
            self.log.verbose("The following transformations are in %s status: %s" % (status, valOutStr))
        return res["Value"]

    @timeThis
    def _getTransformationsState(self):
        """get Transformations state (set 'Other' for not interesting states)
        failures to get something are not critical since there is no reaction on
        'Other' state."""
        self.log.info("Collecting transformations state...")
        try:
            # We put 'Finished' for both
            tListCompleted = self.__getTransformations("Completed")
            tListArchived = self.__getTransformations("Archived")
            tListFinished = tListCompleted + tListArchived
            for tID in tListFinished:
                prID = self.prProds.get(tID, None)
                if prID:
                    self.prSummary[prID]["prods"][tID]["state"] = "Finished"

            for state in self.allKnownStates:
                tList = self.__getTransformations(state)
                for tID in tList:
                    prID = self.prProds.get(tID, None)
                    if prID:
                        self.prSummary[prID]["prods"][tID]["state"] = state
                    else:
                        self.notPrTrans[state].append(tID)
        except RuntimeError as error:
            self.log.error(error)

        for tID, prID in self.prProds.items():
            if "state" not in self.prSummary[prID]["prods"][tID]:
                self.prSummary[prID]["prods"][tID]["state"] = "Other"

        self.log.verbose("Done with collecting transformations states")

    def _getStatusCountersBulk(self, tableName, statusKey, transformationIDs):
        """Get the counter named ``statusKey`` for many transformations

        Wrapper around ``TransformationClient.getCounters`` that returns a nested
        dictionary of:
        ``{transformationID: {state1: X, state2: Y, ..., "TotalCreated": X+Y+...}}``

        :param str tableName: Table in the TransformationDB to use
        :param str statusKey: Name of the status column to consider
        :param list transformationIDs: List of transformation IDs to inspect
        :returns: ``dict`` of ``dict`` of ``int``
        """
        # This is for compatibility with TransformationClient.getTransformationStats
        # and TransformationClient.getTransformationTaskStats
        if tableName == "TransformationTasks":
            totalColumnName = "TotalCreated"
        elif tableName == "TransformationFiles":
            totalColumnName = "Total"
        else:
            raise NotImplementedError(tableName)
        self.log.verbose("Getting counters from for", "%s transformations" % len(transformationIDs))
        res = self.tClient.getCounters(
            tableName,
            ["TransformationID", statusKey],
            {"TransformationID": transformationIDs},
        )
        if not res["OK"]:
            raise RuntimeError(res)
        # Ensure totalColumnName is always included in the output
        statusDict = defaultdict(lambda: defaultdict(int, **{totalColumnName: 0}))
        for attrDict, count in res["Value"]:
            tID = attrDict["TransformationID"]
            status = attrDict[statusKey]
            statusDict[tID][status] = count
            statusDict[tID][totalColumnName] += count
        # Loop over transformationIDs to ensure all IDs are included in the output
        return {int(tID): dict(statusDict[int(tID)]) for tID in transformationIDs}

    def _isIdleCache(self, transIDs):
        """Get the cache dictionaries that need to be passed to __isIdle

        This method is used with __isIdle to minimise the number of RPC calls required::

          transformations, taskStatuses, fileStatuses = self._isIdleCache(tIDs)
          for tID in tIDs:
            isIdle, isProcIdle, isSimulation = self.__isIdle(
                tID, transformations[tID], taskStatuses[tID], fileStatuses[tID]
            )

        :param list of str tIDs: The IDs to get cached data for
        :returns: transformations, taskStatuses, fileStatuses
        """
        self.log.verbose("Filling _isIdleCache caches for", "%s transformations" % len(transIDs))
        result = self.tClient.getTransformations(condDict={"TransformationID": transIDs}, limit=1000)
        if not result["OK"]:
            self.log.error("Could not get transformations", result["Message"])
            raise RuntimeError("Could not get transformations")
        transformations = {x["TransformationID"]: x for x in result["Value"]}
        taskStatuses = self._getStatusCountersBulk("TransformationTasks", "ExternalStatus", transIDs)
        fileStatuses = self._getStatusCountersBulk("TransformationFiles", "Status", transIDs)
        return transformations, taskStatuses, fileStatuses

    def __isIdle(self, tID, tInfo, tStats, filesStats):
        """Checks if a transformation is idle, is procIdle and either the
        transformation is simulation.

        The ``tInfo``, ``tStats``, ``filesStats`` parameters are passed to improve
        performance by avoiding 3 round trips to the transformation service. See
        ``_isIdleCache`` for more details.

        :param str tID: ID of the transformation to check
        :param dict tInfo: Result of ``TransformationClient.getTransformations``
        :param dict tStats: Result of ``self._getStatusCountersBulk`` for the
                            ``ExternalStatus`` column in the ``TransformationTasks`` table
        :param dict filesStats: Result of ``self._getStatusCountersBulk`` for the
                                ``Status`` column in the ``TransformationFiles`` table
        :returns: ``dict`` of ``dict`` of ``int``
        """
        self.log.debug("Checking if transformation is idle", str(tID))
        if tInfo.get("Type", None) in self.simulationTypes:
            isSimulation = True
            # simulation : go to Idle if
            # only failed and done tasks
            # AND number of tasks created in total == number of tasks submitted
            self.log.verbose("Tasks Stats for %d: %s" % (tID, str(tStats)))
            isIdle = (tStats.get("TotalCreated", 0) > 0) and all(
                tStats.get(status, 0) == 0 for status in KNOWN_TASK_STATES
            )
            isProcIdle = isIdle
        else:
            isSimulation = False
            # other transformation type : go to Idle if
            # 0 assigned files, unused files number was not changing during the last cyclesTillIdle time
            # AND only failed and done tasks
            self.log.debug("Files stats: %s" % str(filesStats))
            unused = filesStats.get("Unused", 0)
            unusedInherited = filesStats.get("Unused-inherited", 0)
            oldUnused = self.filesUnused.setdefault(tID, {"Number": -1, "NotChanged": 0})
            if oldUnused["Number"] == unused:
                oldUnused["NotChanged"] += 1
            else:
                oldUnused["NotChanged"] = 0
                oldUnused["Number"] = unused
            assigned = filesStats.get("Assigned", 0)
            isProcIdle = (assigned == 0) and ((unused == 0) or (oldUnused["NotChanged"] >= self.cyclesTillIdle))
            if isProcIdle:
                self.log.debug("Tasks Stats: %s" % str(tStats))
                isProcIdle = all(tStats.get(status, 0) == 0 for status in KNOWN_TASK_STATES)
            isIdle = isProcIdle and (unused == 0) and (unusedInherited == 0)
        return (isIdle, isProcIdle, isSimulation)

    def _getIdleProductionRequestProductions(self):
        """evaluate isIdle and isProcIdle status for all productions we need.

        failures are remembered and are taken into account later
        """
        self.log.verbose("Filling caches for _getIdleProductionRequestProductions...")
        transIDs = [
            str(tID)
            for tID, prID in self.prProds.items()
            if self.prSummary[prID]["prods"][tID]["state"] in ("Active", "Idle")
        ]
        try:
            transformations, taskStatuses, fileStatuses = self._isIdleCache(transIDs)
        except RuntimeError:
            return S_ERROR("Failed to get _isIdleCache in _getIdleProductionRequestProductions")

        self.log.verbose("Checking idle productions...")
        for tID, prID in self.prProds.items():
            tInfo = self.prSummary[prID]["prods"][tID]
            if tInfo["state"] in ("Active", "Idle"):
                isIdle, isProcIdle, isSimulation = self.__isIdle(
                    tID, transformations[tID], taskStatuses[tID], fileStatuses[tID]
                )
                tInfo["isIdle"] = "Yes" if isIdle else "No"
                tInfo["isProcIdle"] = "Yes" if isProcIdle else "No"
                tInfo["isSimulation"] = isSimulation
                tInfo["filesTotal"] = fileStatuses[tID]["Total"]
                tInfo["filesProcessed"] = fileStatuses[tID].get("Processed", 0)
                tInfo["filesUnused"] = fileStatuses[tID].get("Unused", 0)
                tInfo["filesMaxReset"] = fileStatuses[tID].get("MaxReset", 0)
            else:
                tInfo["isIdle"] = "Unknown"
                tInfo["isProcIdle"] = "Unknown"
                tInfo["isSimulation"] = False
                tInfo["filesTotal"] = None
                tInfo["filesProcessed"] = 0
                tInfo["filesUnused"] = 0
                tInfo["filesMaxReset"] = 0
        self.log.verbose("Checking idle done")
        return S_OK()

    def _trackProductionRequests(self):
        """contact BK for the current number of processed events failures are
        critical."""
        self.log.info("Updating production requests progress...")

        # Using 10 threads, and waiting for the results before continuing
        futureThreads = []
        with ThreadPoolExecutor(10) as threadPool:
            for tID, prID in self.prProds.items():
                futureThreads.append(threadPool.submit(self._getExtraInfo, tID, prID))
            wait(futureThreads)

        # Update the Production request DB with the number of bookkeeping events
        if self.toUpdate:
            if gDoRealTracking:
                result = self.prClient.updateTrackedProductions(self.toUpdate)
            else:
                result = S_OK()
            if not result["OK"]:
                self.log.error(
                    "Could not send update to the Production Request System", result["Message"]
                )  # that is not critical
            else:
                self.log.verbose("The progress of %s Production Requests is updated" % len(self.toUpdate))
        self.log.info("Production requests progress update is finished")

        # Get the status of the Analysis Productions input transformations
        inputTransformIDs = set()
        for summary in self.prSummary.values():
            for tID, tInfo in summary["prods"].items():
                inputTransformIDs = inputTransformIDs.union(
                    x for x in tInfo.get("inputIDs", []) if x not in summary["prods"]
                )
        inputTransformStatuses = {}
        if inputTransformIDs:
            retVal = self.tClient.getTransformations(
                condDict={"TransformationID": list(inputTransformIDs)},
                limit=10000,
                columns=["TransformationID", "Status"],
            )
            if not retVal["OK"]:
                self.log.error("Failed to call getTransformations", retVal["Message"])
                return S_ERROR("Too dangerous to continue")
            inputTransformStatuses = {d["TransformationID"]: d["Status"] for d in retVal["Value"]}
        for prID, summary in self.prSummary.items():
            for tID, tInfo in summary["prods"].items():
                if "inputIDs" not in tInfo:
                    continue
                tInfo["hasActiveInput"] = False
                for inputID in tInfo["inputIDs"]:
                    if inputID in summary["prods"]:
                        inputState = summary["prods"][inputID]["state"]
                    else:
                        inputState = inputTransformStatuses.get(inputID, "Unknown")
                    if inputState not in ["Archived", "Completed", "Finished"]:
                        self.log.info(
                            "Marking hasActiveInput=True for",
                            "%s (%s) as input %s has status %s" % (tID, prID, inputID, inputState),
                        )
                        tInfo["hasActiveInput"] = True

        return S_OK()

    def _getExtraInfo(self, tID, prID):
        tInfo = self.prSummary[prID]["prods"][tID]
        # Get the number of bookkeeping events
        self.log.verbose("Getting BK production progress", "Transformation ID = %d" % tID)
        result = BookkeepingClient().getProductionProducedEvents(tID)
        if result["OK"]:
            nEvents = result["Value"]
            if nEvents and nEvents != tInfo["Events"]:
                self.log.verbose("Updating production %d, with BkEvents %d" % (int(tID), int(nEvents)))
                self.toUpdate.append({"ProductionID": tID, "BkEvents": nEvents})
                tInfo["Events"] = nEvents
        else:
            self.log.error("Progress is not updated", "%s : %s" % (tID, result["Message"]))
            return S_ERROR("Too dangerous to continue")
        # Find the transfromation ID for the input to each Analysis Production
        if self.prSummary[prID]["type"] == "AnalysisProduction":
            retVal = TransformationClient().getBookkeepingQuery(tID)
            if not retVal["OK"]:
                self.log.error("Failed to call getBookkeepingQuery", "%s %s" % (tID, retVal["Message"]))
                return S_ERROR("Too dangerous to continue")
            inputBkQuery = retVal["Value"]
            if "ProductionID" in inputBkQuery:
                tInfo["inputIDs"] = [inputBkQuery["ProductionID"]]
            else:
                # FIXME: Just why?!
                if "DataTakingConditions" in inputBkQuery:
                    inputBkQuery["ConditionDescription"] = inputBkQuery["DataTakingConditions"]
                retVal = BookkeepingClient().getProductions(inputBkQuery)
                if not retVal["OK"]:
                    self.log.error("Failed to call getProductions", "%s %s" % (tID, retVal["Message"]))
                    return S_ERROR("Too dangerous to continue")
                tInfo["inputIDs"] = [x[0] for x in retVal["Value"]["Records"]]

    def _cleanFilesUnused(self):
        """remove old transformations from filesUnused."""
        oldIDs = []
        for tID in self.filesUnused:
            if tID in self.prProds:
                continue
            if all(tID not in IDs for _status, IDs in self.notPrTrans.items()):
                oldIDs.append(tID)
        for tID in oldIDs:
            del self.filesUnused[tID]

    def __updateTransformationStatus(self, tID, origStatus, status, updatedT):
        """This method updates the transformation status and logs the changes for
        each iteration of the agent.

        Most importantly this method only allows status transitions based on
        what the original status should be.
        """
        self.log.info("Changing status for transformation %s to %s" % (tID, status))

        if not gDoRealUpdate:
            updatedT[tID] = {"to": status, "from": origStatus}
            return

        result = self.tClient.setTransformationParameter(tID, "Status", status, currentStatus=origStatus)
        if not result["OK"]:
            self.log.error("Failed to update status of transformation", "%s from %s to %s" % (tID, origStatus, status))
        else:
            updatedT[tID] = {"to": status, "from": origStatus}

    def _mailProdManager(self, updatedT, updatedPr):
        """Notify the production manager of the changes as productions should be
        manually extended in some cases."""
        if not updatedT and not updatedPr:
            self.log.verbose("No changes this cycle, mail will not be sent")
            return

        if self.notify:

            with sqlite3.connect(self.cacheFile) as conn:

                try:
                    conn.execute(
                        """CREATE TABLE IF NOT EXISTS ProductionStatusAgentCache(
                        production VARCHAR(64) NOT NULL DEFAULT "",
                        from_status VARCHAR(64) NOT NULL DEFAULT "",
                        to_status VARCHAR(64) NOT NULL DEFAULT "",
                        time VARCHAR(64) NOT NULL DEFAULT ""
                       );"""
                    )

                    conn.execute(
                        """CREATE TABLE IF NOT EXISTS ProductionStatusAgentReqCache(
                        prod_requests VARCHAR(64) NOT NULL DEFAULT "",
                        time VARCHAR(64) NOT NULL DEFAULT ""
                       );"""
                    )

                except sqlite3.OperationalError:
                    self.log.error("Could not queue mail")

                for tID, val in updatedT.items():
                    conn.execute(
                        "INSERT INTO ProductionStatusAgentCache (production, from_status, to_status, time)"
                        " VALUES (?, ?, ?, ?)",
                        (tID, val["from"], val["to"], time.asctime()),
                    )

                for prod_request in updatedPr:
                    conn.execute(
                        "INSERT INTO ProductionStatusAgentReqCache (prod_requests, time) VALUES (?, ?)",
                        (prod_request, time.asctime()),
                    )

                conn.commit()

                self.log.info("Mail summary queued for sending")

    def __updateProductionRequestStatus(self, prID, status, updatedPr):
        """This method updates the production request status."""
        self.log.info("Marking Production Request %s as %s" % (prID, status))

        if not gDoRealUpdate:
            updatedPr.append(prID)
            return

        reqClient = ProductionRequestClient(useCertificates=False, timeout=120)
        result = reqClient.updateProductionRequest(int(prID), {"RequestState": status})
        if not result["OK"]:
            self.log.error(result)
        else:
            updatedPr.append(prID)

    def _applyOtherTransformationsLogic(self, updatedT):
        """animate not Production Requests related transformations failures are not
        critical."""
        self.log.verbose("Updating requests unrelated transformations...")

        self.log.info(
            'Processing %s requests unrelated transformations in "RemovedFiles" state'
            % len(self.notPrTrans["RemovedFiles"])
        )
        for tID in self.notPrTrans["RemovedFiles"]:
            self.__updateTransformationStatus(tID, "RemovedFiles", "Completed", updatedT)

        self.log.info(
            'Processing %s requests unrelated transformations in "Active" state' % len(self.notPrTrans["Active"])
        )
        try:
            transformations, taskStatuses, fileStatuses = self._isIdleCache(self.notPrTrans["Active"])
        except RuntimeError:
            self.log.error('Failed to get _isIdleCache for monitoring "Active" requests')
        else:
            for tID in self.notPrTrans["Active"]:
                isIdle, _isProcIdle, _isSimulation = self.__isIdle(
                    tID, transformations[tID], taskStatuses[tID], fileStatuses[tID]
                )
                if isIdle:
                    self.__updateTransformationStatus(tID, "Active", "Idle", updatedT)

        self.log.info('Processing %s requests unrelated transformations in "Idle" state' % len(self.notPrTrans["Idle"]))
        try:
            transformations, taskStatuses, fileStatuses = self._isIdleCache(self.notPrTrans["Idle"])
        except RuntimeError:
            self.log.error('Failed to get _isIdleCache for monitoring "Idle" requests')
        else:
            for tID in self.notPrTrans["Idle"]:
                isIdle, _isProcIdle, _isSimulation = self.__isIdle(
                    tID, transformations[tID], taskStatuses[tID], fileStatuses[tID]
                )
                if not isIdle:
                    self.__updateTransformationStatus(tID, "Idle", "Active", updatedT)

        self.log.verbose("Requests unrelated transformations update is finished")

    def _isReallyDone(self, summary):
        """Evaluate 'isDone' from current update cycle."""
        # Other production types rely on the number of bookkeeping events
        bkTotal = sum(t["Events"] for t in summary["prods"].values() if t["Used"])
        return bkTotal >= summary["prTotal"]

    def _producersAreIdle(self, summary):
        """Return True in case all producers (not 'Used') transformations are Idle,
        Finished or not exist."""
        for _tID, tInfo in summary["prods"].items():
            if tInfo["Used"]:
                continue
            if tInfo["isIdle"] != "Yes" and tInfo["state"] != "Finished":
                return False
        return True

    def _producersAreProcIdle(self, summary):
        """Return True in case all producers (not 'Used') transformations are
        procIdle or finished or not exist."""
        for _tID, tInfo in summary["prods"].items():
            if tInfo["Used"]:
                continue
            if tInfo["isProcIdle"] != "Yes" and tInfo["state"] != "Finished":
                return False
        return True

    def _processorsAreProcIdle(self, summary):
        """Return True in case all processors ('Used' or not Sim) transformations
        are procIdle or finished or not exist."""
        for _tID, tInfo in summary["prods"].items():
            if not tInfo["Used"] and tInfo["isSimulation"]:
                continue
            if tInfo["isProcIdle"] != "Yes" and tInfo["state"] != "Finished":
                return False
        return True

    def _mergersAreDone(self, summary):
        """Return True in case all mergers ('Used') transformations are finished or
        not exist."""
        for _tID, tInfo in summary["prods"].items():
            if not tInfo["Used"]:
                continue
            if tInfo["state"] != "Finished":
                return False
        return True

    def _mergersAreProcIdle(self, summary):
        """Return True in case all mergers ('Used') transformations are procIdle or
        finished or not exist."""
        for _tID, tInfo in summary["prods"].items():
            if not tInfo["Used"]:
                continue
            if tInfo["isProcIdle"] != "Yes" and tInfo["state"] != "Finished":
                return False
        return True

    def _requestedMoreThenProduced(self, tID, summary):
        """Check that this transformation has registered less events than it was
        requested."""
        if summary["prods"][tID]["Events"] < summary["prTotal"]:
            self.log.verbose(" Transformation %s has produced less events, asking for extention " % tID)
            return True
        return False

    def _applyProductionRequestsLogic(self, updatedT, updatedPr):
        """Apply known logic to transformations related to production requests
        NOTE: we make decision based on BK statistic collected in the PREVIOUS cycle (except isReallyDone)
              and transformation status in THIS cycle BEFORE the Logic is started
        """
        self.log.verbose("Production Requests logic...")

        for prID, summary in self.prSummary.items():
            countFinished = 0
            for tID, tInfo in summary["prods"].items():
                if tInfo["state"] == "Finished":
                    countFinished += 1
                elif tInfo["state"] == "Idle":
                    self._handleStateIdle(tID, tInfo, summary, updatedT)
                elif tInfo["state"] == "RemovedFiles":
                    self._handleStateRemovedFiles(tID, tInfo, summary, updatedT)
                elif tInfo["state"] == "Active":
                    self._handleStateActive(tID, tInfo, summary, updatedT)
                elif tInfo["state"] == "ValidatedOutput":
                    self._handleStateValidatedOutput(tID, tInfo, summary, updatedT)
                elif tInfo["state"] == "ValidatingInput":
                    self._handleStateValidatingInput(tID, tInfo, summary, updatedT)
                elif tInfo["state"] == "Testing":
                    self._handleStateTesting(tID, tInfo, summary, updatedT)

            summary["isFinished"] = countFinished == len(summary["prods"])
            if (
                summary["isFinished"]
                and not summary["master"]
                and summary["type"] in ["Simulation", "AnalysisProduction"]
            ):
                self.__updateProductionRequestStatus(prID, "Done", updatedPr)

        for masterID, prList in self.prMasters.items():
            countFinished = sum(1 for prID in prList if self.prSummary[prID]["isFinished"])
            if countFinished == len(prList):
                self.__updateProductionRequestStatus(masterID, "Done", updatedPr)

        self.log.verbose("Done with Production Requests logic")

    def _handleStateIdle(self, tID, tInfo, summary, updatedT):
        """Used by _applyProductionRequestsLogic"""
        if tInfo["isIdle"] == "No":
            # 'Idle' && !isIdle() --> 'Active'
            self.__updateTransformationStatus(tID, "Idle", "Active", updatedT)
        elif tInfo["isIdle"] != "Yes":
            return

        if summary["type"] == "Simulation":
            if self._isReallyDone(summary):
                # 'Idle' && isIdle() && isDone for MC logic
                if tInfo["Used"]:  # for standard sim requests, only the merge will go to ValidatingOutput
                    if self._producersAreIdle(summary):
                        self.__updateTransformationStatus(tID, "Idle", "ValidatingOutput", updatedT)
                    # else
                    #  it can happened that MC is !isIdle()
                else:  # for standard sim requests, all but the merge will go to ValidatingInput
                    if self._mergersAreProcIdle(summary):
                        # Note: 'isSimulation' should not be there (it should stay in 'Active')
                        self.__updateTransformationStatus(tID, "Idle", "ValidatingInput", updatedT)
                    # else:
                    #   We wait till mergers finish the job

        elif summary["type"] == "AnalysisProduction":
            if not tInfo["hasActiveInput"]:
                # The number of bookkeeping events is not well defined for Analysis Productions
                allFilesProcessed = tInfo["filesTotal"] and tInfo["filesTotal"] == tInfo["filesProcessed"]
                if allFilesProcessed:
                    if tInfo["Used"]:
                        self.__updateTransformationStatus(tID, "Idle", "ValidatingOutput", updatedT)
                    else:
                        self.__updateTransformationStatus(tID, "Idle", "Completed", updatedT)
                elif tInfo["filesTotal"] == tInfo["filesProcessed"] + tInfo["filesMaxReset"]:
                    self.log.warn(
                        "Transformation has files in MaxReset", "ID=%s count=%s" % (tID, tInfo["filesMaxReset"])
                    )

    def _handleStateRemovedFiles(self, tID, tInfo, summary, updatedT):
        """Used by _applyProductionRequestsLogic"""
        self.__updateTransformationStatus(tID, "RemovedFiles", "Completed", updatedT)

    def _handleStateActive(self, tID, tInfo, summary, updatedT):
        """Used by _applyProductionRequestsLogic"""
        if tInfo["isIdle"] == "Yes":
            if summary["type"] == "Simulation":
                # 'Active' && isIdle() for MC logic
                if tInfo["Used"] or not tInfo["isSimulation"]:
                    # The merger will either wait for MC extention (if !isDone)
                    # or will start validation once producers are isIdle()
                    self.__updateTransformationStatus(tID, "Active", "Idle", updatedT)
                # 'Active' && isIdle() && !Used && isSimulation
                elif self._isReallyDone(summary):
                    if self._mergersAreProcIdle(summary):
                        self.__updateTransformationStatus(tID, "Active", "ValidatingInput", updatedT)
                elif self._processorsAreProcIdle(summary) or self._requestedMoreThenProduced(tID, summary):
                    # we are not done yet, extend production
                    self.__updateTransformationStatus(tID, "Active", "Idle", updatedT)
                # else:
                #  we wait till the situation with mergers is clear
            else:
                # for not MC, use reasonable default
                self.__updateTransformationStatus(tID, "Active", "Idle", updatedT)
        elif summary["type"] == "AnalysisProduction" and not tInfo["hasActiveInput"]:
            if tInfo["filesUnused"] and tInfo["filesTotal"] == tInfo["filesProcessed"] + tInfo["filesUnused"]:
                self.__updateTransformationStatus(tID, "Active", "Flush", updatedT)

    def _handleStateValidatedOutput(self, tID, tInfo, summary, updatedT):
        """Used by _applyProductionRequestsLogic"""
        if summary["type"] == "Simulation" and summary["isDone"] and tInfo["Used"]:
            # for standard sim requests, only the merge
            self.__updateTransformationStatus(tID, "ValidatedOutput", "Completed", updatedT)
        elif summary["type"] == "AnalysisProduction" and tInfo["Used"]:
            # isDone only uses the bookkeeping and therefore isn't useful
            self.__updateTransformationStatus(tID, "ValidatedOutput", "Completed", updatedT)
        else:
            self.log.warn("Logical bug: transformation %s unexpectedly has 'ValidatedOutput'" % tID)

    def _handleStateValidatingInput(self, tID, tInfo, summary, updatedT):
        """Used by _applyProductionRequestsLogic"""
        if summary["type"] == "Simulation" and summary["isDone"] and not tInfo["Used"]:
            # for standard sim requests, all but the merge
            self.__updateTransformationStatus(tID, "ValidatingInput", "RemovingFiles", updatedT)
        else:
            self.log.warn("Logical bug: transformation %s is unexpectedly 'ValidatingInput'" % tID)

    def _handleStateTesting(self, tID, tInfo, summary, updatedT):
        """Used by _applyProductionRequestsLogic"""
        try:
            # TODO This should ideally be moved out of the loop
            transformations, taskStatuses, fileStatuses = self._isIdleCache([str(tID)])
        except RuntimeError:
            self.log.error("Failed to get _isIdleCache for", str(tID))
            return
        isIdle, isProcIdle, isSimulation = self.__isIdle(
            tID, transformations[tID], taskStatuses[tID], fileStatuses[tID]
        )
        self.log.verbose("TransID %d, %s, %s, %s" % (tID, isIdle, isProcIdle, isSimulation))
        if isIdle:
            self.__updateTransformationStatus(tID, "Testing", "Idle", updatedT)
