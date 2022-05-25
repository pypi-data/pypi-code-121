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
"""DISET request handler for the LHCbDIRAC/TransformationDB."""
import six

from DIRAC import S_OK, S_ERROR
from DIRAC.TransformationSystem.Service.TransformationManagerHandler import TransformationManagerHandler as TManagerBase
from LHCbDIRAC.TransformationSystem.DB.TransformationDB import TransformationDB


class TransformationManagerHandlerMixin:
    types_deleteTransformation = [six.integer_types]

    def export_deleteTransformation(self, transID):
        rc = self.getRemoteCredentials()
        author = rc.get("DN", rc.get("CN"))
        return self.transformationDB.deleteTransformation(transID, author=author)

    types_setHotFlag = [six.integer_types, bool]

    def export_setHotFlag(self, transID, hotFlag):
        return self.transformationDB.setHotFlag(transID, hotFlag)

    #############################################################################
    #
    # Managing the BkQueries table
    #

    types_addBookkeepingQuery = [six.integer_types, dict]

    @classmethod
    def export_addBookkeepingQuery(self, transID, queryDict):
        return self.transformationDB.addBookkeepingQuery(transID, queryDict)

    types_deleteBookkeepingQuery = [six.integer_types]

    @classmethod
    def export_deleteBookkeepingQuery(self, transID):
        return self.transformationDB.deleteBookkeepingQuery(transID)

    types_getBookkeepingQuery = [six.integer_types]

    @classmethod
    def export_getBookkeepingQuery(self, transID):
        return self.transformationDB.getBookkeepingQuery(transID)

    types_getTransformationsWithBkQueries = [list]

    @classmethod
    def export_getTransformationsWithBkQueries(self, transIDs):
        return self.transformationDB.getTransformationsWithBkQueries(transIDs)

    types_setBookkeepingQueryEndRun = [six.integer_types, six.integer_types]

    @classmethod
    def export_setBookkeepingQueryEndRun(self, transID, runNumber):
        return self.transformationDB.setBookkeepingQueryEndRun(transID, runNumber)

    types_setBookkeepingQueryStartRun = [six.integer_types, six.integer_types]

    @classmethod
    def export_setBookkeepingQueryStartRun(self, transID, runNumber):
        return self.transformationDB.setBookkeepingQueryStartRun(transID, runNumber)

    types_addBookkeepingQueryRunList = [six.integer_types, [list]]

    @classmethod
    def export_addBookkeepingQueryRunList(self, transID, runList):
        return self.transformationDB.addBookkeepingQueryRunList(transID, runList)

    #############################################################################
    #
    # Managing the TransformationRuns table
    #

    types_getTransformationRuns = []

    @classmethod
    def export_getTransformationRuns(self, condDict={}, orderAttribute=None, limit=None):
        return self.transformationDB.getTransformationRuns(condDict, orderAttribute=orderAttribute, limit=limit)

    types_insertTransformationRun = [six.integer_types, six.integer_types, six.string_types]

    @classmethod
    def export_insertTransformationRun(self, transID, runID, selectedSite=""):
        return self.transformationDB.insertTransformationRun(transID, runID, selectedSite="")

    types_getTransformationRunStats = [[six.integer_types, list]]

    @classmethod
    def export_getTransformationRunStats(self, transIDs):
        if isinstance(transIDs, six.integer_types):
            transIDs = [transIDs]
        return self.transformationDB.getTransformationRunStats(transIDs)

    types_addTransformationRunFiles = [six.integer_types, six.integer_types, list]

    @classmethod
    def export_addTransformationRunFiles(self, transID, runID, lfns):
        return self.transformationDB.addTransformationRunFiles(transID, runID, lfns)

    types_setParameterToTransformationFiles = [six.integer_types, dict]

    @classmethod
    def export_setParameterToTransformationFiles(self, transID, lfnsDict):
        return self.transformationDB.setParameterToTransformationFiles(transID, lfnsDict)

    types_setTransformationRunStatus = [six.integer_types, [six.integer_types, list], six.string_types]

    @classmethod
    def export_setTransformationRunStatus(self, transID, runID, status):
        return self.transformationDB.setTransformationRunStatus(transID, runID, status)

    types_setTransformationRunsSite = [six.integer_types, six.integer_types, six.string_types]

    @classmethod
    def export_setTransformationRunsSite(self, transID, runID, assignedSE):
        return self.transformationDB.setTransformationRunsSite(transID, runID, assignedSE)

    types_getTransformationRunsSummaryWeb = [dict, list, int, int]

    def export_getTransformationRunsSummaryWeb(self, selectDict, sortList, startItem, maxItems):
        """Get the summary of the transformation run information for a given page
        in the generic format."""

        # Obtain the timing information from the selectDict
        last_update = selectDict.get("LastUpdate", None)
        if last_update:
            del selectDict["LastUpdate"]
        fromDate = selectDict.get("FromDate", None)
        if fromDate:
            del selectDict["FromDate"]
        if not fromDate:
            fromDate = last_update
        toDate = selectDict.get("ToDate", None)
        if toDate:
            del selectDict["ToDate"]
        # Sorting instructions. Only one for the moment.
        if sortList:
            orderAttribute = sortList[0][0] + ":" + sortList[0][1]
        else:
            orderAttribute = None

        # Get the transformations that match the selection
        res = self.transformationDB.getTransformationRuns(
            condDict=selectDict, older=toDate, newer=fromDate, orderAttribute=orderAttribute
        )
        if not res["OK"]:
            self.log.error("TransformationManager.getTransformationRuns()", res["Message"])
            return res

        # Prepare the standard structure now within the resultDict dictionary
        resultDict = {}
        trList = res["Records"]
        # Create the total records entry
        nTrans = len(trList)
        resultDict["TotalRecords"] = nTrans
        # Create the ParameterNames entry
        paramNames = res["ParameterNames"]
        resultDict["ParameterNames"] = list(paramNames)

        # Add the job states to the ParameterNames entry
        # taskStateNames   = ['Created','Running','Submitted','Failed','Waiting','Done','Stalled']
        # resultDict['ParameterNames'] += ['Jobs_'+x for x in taskStateNames]
        # Add the file states to the ParameterNames entry
        fileStateNames = [
            "PercentProcessed",
            "Processed",
            "Unused",
            "Assigned",
            "Total",
            "Problematic",
            "ApplicationCrash",
            "MaxReset",
        ]
        resultDict["ParameterNames"] += ["Files_" + x for x in fileStateNames]

        # Get the transformations which are within the selected window
        if nTrans == 0:
            return S_OK(resultDict)
        ini = startItem
        last = ini + maxItems
        if ini >= nTrans:
            return S_ERROR("Item number out of range")
        if last > nTrans:
            last = nTrans
        transList = trList[ini:last]
        if not transList:
            return S_OK(resultDict)

        # Obtain the run statistics for the requested transformations
        transIDs = []
        for transRun in transList:
            transRunDict = dict(zip(paramNames, transRun))
            transID = int(transRunDict["TransformationID"])
            if transID not in transIDs:
                transIDs.append(transID)
        res = self.transformationDB.getTransformationRunStats(transIDs)
        if not res["OK"]:
            return res
        transRunStatusDict = res["Value"]

        statusDict = {}
        # Add specific information for each selected transformation/run
        for transRun in transList:
            transRunDict = dict(zip(paramNames, transRun))
            transID = transRunDict["TransformationID"]
            runID = transRunDict["RunNumber"]
            if transID not in transRunStatusDict or runID not in transRunStatusDict[transID]:
                for state in fileStateNames:
                    transRun.append(0)
                continue
            # Update the status counters
            status = transRunDict["Status"]
            statusDict[status] = statusDict.setdefault(status, 0) + 1

            # Populate the run file statistics
            fileDict = transRunStatusDict[transID][runID]
            if fileDict["Total"] == 0:
                fileDict["PercentProcessed"] = 0
            else:
                processed = fileDict.get("Processed", 0)
                fileDict["PercentProcessed"] = "%.1f" % (int(processed * 1000.0 / fileDict["Total"]) / 10.0)
            for state in fileStateNames:
                if fileDict and state in fileDict:
                    transRun.append(fileDict[state])
                else:
                    transRun.append(0)

            # Get the statistics on the number of jobs for the transformation
            # res = database.getTransformationTaskRunStats(transID)
            # taskDict = {}
            # if res['OK'] and res['Value']:
            #  taskDict = res['Value']
            # for state in taskStateNames:
            #  if taskDict and taskDict.has_key(state):
            #    trans.append(taskDict[state])
            #  else:
            #    trans.append(0)

        resultDict["Records"] = transList
        resultDict["Extras"] = statusDict
        return S_OK(resultDict)

    #############################################################################
    #
    # Managing the RunsMetadata table
    #

    types_addRunsMetadata = [six.integer_types, dict]

    @classmethod
    def export_addRunsMetadata(self, runID, metadataDict):
        """insert run metadata."""
        return self.transformationDB.setRunsMetadata(runID, metadataDict)

    types_updateRunsMetadata = [six.integer_types, dict]

    @classmethod
    def export_updateRunsMetadata(self, runID, metadataDict):
        """insert run metadata."""
        return self.transformationDB.updateRunsMetadata(runID, metadataDict)

    types_getRunsMetadata = [[list, six.integer_types]]

    @classmethod
    def export_getRunsMetadata(self, runID):
        """retrieve run metadata."""
        return self.transformationDB.getRunsMetadata(runID)

    types_deleteRunsMetadata = [six.integer_types]

    @classmethod
    def export_deleteRunsMetadata(self, runID):
        """delete run metadata."""
        return self.transformationDB.deleteRunsMetadata(runID)

    types_getRunsInCache = [dict]

    @classmethod
    def export_getRunsInCache(self, condDict):
        """gets what's in."""
        return self.transformationDB.getRunsInCache(condDict)

    #############################################################################
    #
    # Managing the RunDestination table
    #

    types_getDestinationForRun = [[six.integer_types, six.string_types, list]]

    @classmethod
    def export_getDestinationForRun(self, runIDs):
        """retrieve run destination for a single run or a list of runs."""
        if isinstance(runIDs, six.integer_types):
            runIDs = [runIDs]
        if isinstance(runIDs, str):
            runIDs = [int(runIDs)]
        # expecting a list of long integers
        return self.transformationDB.getDestinationForRun(runIDs)

    types_setDestinationForRun = [six.integer_types, six.string_types]

    @classmethod
    def export_setDestinationForRun(self, runID, destination):
        """set run destination."""
        return self.transformationDB.setDestinationForRun(runID, destination)

    #############################################################################
    #
    # Managing the StoredJobDescription table
    #

    types_addStoredJobDescription = [six.integer_types, six.string_types]

    @classmethod
    def export_addStoredJobDescription(self, transformationID, jobDescription):
        return self.transformationDB.addStoredJobDescription(transformationID, jobDescription)

    types_getStoredJobDescription = [six.integer_types]

    @classmethod
    def export_getStoredJobDescription(self, transformationID):
        return self.transformationDB.getStoredJobDescription(transformationID)

    types_removeStoredJobDescription = [six.integer_types]

    @classmethod
    def export_removeStoredJobDescription(self, transformationID):
        return self.transformationDB.removeStoredJobDescription(transformationID)

    types_getStoredJobDescriptionIDs = []

    @classmethod
    def export_getStoredJobDescriptionIDs(self):
        return self.transformationDB.getStoredJobDescriptionIDs()


class TransformationManagerHandler(TransformationManagerHandlerMixin, TManagerBase):
    pass
