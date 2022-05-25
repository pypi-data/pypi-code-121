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
:mod: DataUsageHandler

.. module: DataUsageHandler

:synopsis: Implementation of the Data Usage service in the DISET framework.
"""
import six

# # from DIRAC
from DIRAC import S_OK
from DIRAC.Core.DISET.RequestHandler import RequestHandler

# # from LHCbDIRAC
from LHCbDIRAC.DataManagementSystem.DB.StorageUsageDB import StorageUsageDB

# # RCSID
# global instance of the StorageUsageDB class
gStorageUsageDB = False


def initializeDataUsageHandler(_serviceInfo):
    """service initalisation."""
    global gStorageUsageDB
    gStorageUsageDB = StorageUsageDB()
    return S_OK()


class DataUsageHandler(RequestHandler):
    """
    .. class:: DataUsageHandler
    """

    types_sendDataUsageReport = [six.string_types, dict]

    @staticmethod
    def export_sendDataUsageReport(site, directoryDict, status="New"):
        """export of sendDataUsageReport."""
        return gStorageUsageDB.sendDataUsageReport(site, directoryDict, status)

    types_getDataUsageSummary = [six.string_types, six.string_types, six.string_types]

    @staticmethod
    def export_getDataUsageSummary(startTime, endTime, status):
        """export of getDataUsageSummary."""
        return gStorageUsageDB.getDataUsageSummary(startTime, endTime, status)

    types_getDataUsageForDirectory = [six.string_types]

    @staticmethod
    def export_getDataUsageForDirectory(path):
        """export of getDataUsageForDirectory."""
        return gStorageUsageDB.getDataUsageForDirectory(path)

    types_sendDataUsageReport_2 = [(dict)]

    @staticmethod
    def export_sendDataUsageReport_2(directoryDict):
        """export of sendDataUsageReport (new version)"""
        return gStorageUsageDB.sendDataUsageReport_2(directoryDict)

    types_updatePopEntryStatus = [list, six.string_types]

    @staticmethod
    def export_updatePopEntryStatus(idList, newStatus):
        """export of updatePopEntryStatus."""
        return gStorageUsageDB.updatePopEntryStatus(idList, newStatus)

    types_insertToDirMetadata = [dict]

    @staticmethod
    def export_insertToDirMetadata(directoryDict):
        """export of insertToDirMetadata."""
        return gStorageUsageDB.insertToDirMetadata(directoryDict)

    types_getDirMetadata = [list]

    @staticmethod
    def export_getDirMetadata(directoryList):
        """export of getDirMetadata."""
        return gStorageUsageDB.getDirMetadata(directoryList)
