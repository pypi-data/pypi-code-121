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
:mod: RAWIntegrityHandler

.. module: RAWIntegrityHandler

:synopsis: DISET interface to the RAWIntegrityDB.
"""
# imports
import six

# from DIRAC
from DIRAC import gLogger, S_OK, S_ERROR
from DIRAC.Core.DISET.RequestHandler import RequestHandler

# from LHCbDIRAC
from LHCbDIRAC.DataManagementSystem.DB.RAWIntegrityDB import RAWIntegrityDB

# global instance of the RAWIntegrityDB
gRAWIntegrityDB = False


def initializeRAWIntegrityHandler(_serviceInfo):
    """handler initialisation."""

    global gRAWIntegrityDB
    gRAWIntegrityDB = RAWIntegrityDB()

    # Create DB tables if needed
    return gRAWIntegrityDB._checkTable()


class RAWIntegrityHandler(RequestHandler):
    """
    .. class:: RAWIntegrityHandler
    """

    types_addFile = [
        six.string_types,
        six.string_types,
        six.integer_types,
        six.string_types,
        six.string_types,
        six.string_types,
    ]

    @staticmethod
    def export_addFile(lfn, pfn, size, se, guid, checksum):
        """Add a file to the RAW integrity DB."""
        try:
            gLogger.info("RAWIntegrityHandler.addFile: Attempting to add %s to the gRAWIntegrityDB." % lfn)
            res = gRAWIntegrityDB.addFile(lfn, pfn, size, se, guid, checksum)
            return res
        except Exception as x:
            errStr = "RAWIntegrityHandler.addFile: Exception while adding file to gRAWIntegrityDB."
            gLogger.exception(errStr, lException=x)
            return S_ERROR(errStr)

    types_getGlobalStatistics = []

    @staticmethod
    def export_getGlobalStatistics():
        """Get global file statistics."""
        try:
            gLogger.info("Attempting to get global statistics.")
            res = gRAWIntegrityDB.getGlobalStatistics()
            if not res["OK"]:
                gLogger.error("getGlobalStatistics: Failed to get global statistics", res["Message"])
            else:
                gLogger.info("getGlobalStatistics: Obtained global statistics")
            return res
        except Exception as x:
            errStr = "getGlobalStatistics: Exception while getting global statistics."
            gLogger.exception(errStr, lException=x)
            return S_ERROR(errStr)

    types_getFileSelections = []

    @staticmethod
    def export_getFileSelections():
        """Get the possible selections available."""
        try:
            gLogger.info("Attempting to get selections.")
            res = gRAWIntegrityDB.getFileSelections()
            if not res["OK"]:
                gLogger.error("getFileSelections: Failed to get file selections", res["Message"])
            else:
                gLogger.info("getFileSelections: Obtained file selections")
            return res
        except Exception as x:
            errStr = "getFileSelections: Exception while getting file selections."
            gLogger.exception(errStr, lException=x)
            return S_ERROR(errStr)

    types_getFilesSummaryWeb = [dict, list, six.integer_types, six.integer_types]

    @staticmethod
    def export_getFilesSummaryWeb(selectDict, sortList, startItem, maxItems):
        """Get the file information according to conventions."""
        resultDict = {}
        startDate = selectDict.get("FromDate", None)
        if startDate:
            del selectDict["FromDate"]
        endDate = selectDict.get("ToDate", None)
        if endDate:
            del selectDict["ToDate"]
        # Sorting instructions. Only one for the moment.
        if sortList:
            orderAttribute = sortList[0][0] + ":" + sortList[0][1]
        else:
            orderAttribute = None
        res = gRAWIntegrityDB.selectFiles(selectDict, orderAttribute=orderAttribute, newer=startDate, older=endDate)
        if not res["OK"]:
            return S_ERROR("Failed to select jobs: " + res["Message"])
        # Get the files and the counters correctly
        fileList = res["Value"]
        nFiles = len(fileList)
        resultDict["TotalRecords"] = nFiles
        if nFiles == 0:
            return S_OK(resultDict)
        iniFile = startItem
        lastFile = iniFile + maxItems
        if iniFile >= nFiles:
            return S_ERROR("Item number out of range")
        if lastFile > nFiles:
            lastFile = nFiles
        summaryFileList = fileList[iniFile:lastFile]
        # Prepare the standard format
        resultDict["ParameterNames"] = [
            "lfn",
            "pfn",
            "size",
            "storageelement",
            "guid",
            "checksum",
            "startTime",
            "endTime",
            "status",
        ]
        records = []
        statusCountDict = {}
        for lfn, pfn, size, se, guid, checksum, submit, complete, status in fileList:
            if status not in statusCountDict:
                statusCountDict[status] = 0
            statusCountDict[status] += 1
        for fileTuple in summaryFileList:
            lfn, pfn, size, se, guid, checksum, submit, complete, status = fileTuple
            startTime = str(submit)
            endTime = str(complete)
            records.append((lfn, pfn, size, se, guid, checksum, startTime, endTime, status))
        resultDict["Records"] = records
        resultDict["Extras"] = statusCountDict
        return S_OK(resultDict)

    types_getStatistics = [six.string_types, dict]

    @staticmethod
    def export_getStatistics(attribute, selectDict):
        """Get job statistics distribution per attribute value with a given
        selection."""
        startDate = selectDict.get("FromDate", None)
        if startDate:
            del selectDict["FromDate"]
        # For backward compatibility
        if startDate is None:
            startDate = selectDict.get("LastUpdate", None)
            if startDate:
                del selectDict["LastUpdate"]
        endDate = selectDict.get("ToDate", None)
        if endDate:
            del selectDict["ToDate"]

        result = gRAWIntegrityDB.getCounters("Files", [attribute], selectDict, newer=startDate, older=endDate)

        resultDict = {}
        if result["OK"]:
            for cDict, count in result["Value"]:
                resultDict[cDict[attribute]] = count

        return S_OK(resultDict)
