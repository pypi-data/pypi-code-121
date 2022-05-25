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
:mod: StorageUsageHandler

.. module: StorageUsageHandler

:synopsis: Implementation of the Storage Usage service in the DISET framework.
"""
# imports
import six

# from DIRAC
from DIRAC import gLogger, S_OK, S_ERROR
from DIRAC.Core.DISET.RequestHandler import RequestHandler

# from LHCbDIRAC
from LHCbDIRAC.DataManagementSystem.DB.StorageUsageDB import StorageUsageDB

gStorageUsageDB = False


def initializeStorageUsageHandler(_serviceInfo):
    """handlre initialisation."""
    global gStorageUsageDB
    gStorageUsageDB = StorageUsageDB()
    return S_OK()


class StorageUsageHandler(RequestHandler):
    """
    .. class:: StorageUsageHandler
    """

    types_publishDirectories = [dict]

    @staticmethod
    def export_publishDirectories(directoryDict):
        """export of publishDirectories."""
        return gStorageUsageDB.publishDirectories(directoryDict)

    types_removeDirectory = [[six.string_types, list, tuple]]

    @staticmethod
    def export_removeDirectory(dirPaths):
        """export of removeDirectory."""
        if isinstance(dirPaths, six.string_types):
            dirPaths = (dirPaths,)
        for dirPath in dirPaths:
            result = gStorageUsageDB.removeDirectory(dirPath)
            if not result["OK"]:
                gLogger.error("Could not delete directory", "%s : %s" % (dirPath, result["Message"]))
                return result
        return S_OK()

    types_removeDirFromSe_Usage = []

    @staticmethod
    def export_removeDirFromSe_Usage(dirPaths):
        """Exports the method to remove entries from the se_Usage table."""
        return gStorageUsageDB.removeDirFromSe_Usage(dirPaths)

    types_removeDirFromProblematicDirs = []

    @staticmethod
    def export_removeDirFromProblematicDirs(dirPaths):
        """Exports the method to remove entries from the problematicDirs table."""
        return gStorageUsageDB.removeDirFromProblematicDirs(dirPaths)

    ##################################################################
    #
    # These are the methods for monitoring the usage
    #

    types_getStorageSummary = []

    @staticmethod
    def export_getStorageSummary(directory="", filetype="", production="", sites=None):
        """Retieve a summary for the storage usage."""
        sites = sites if sites else []
        return gStorageUsageDB.getStorageSummary(directory, filetype, production, sites)

    types_getStorageDirectorySummary = []

    @staticmethod
    def export_getStorageDirectorySummary(directory="", filetype="", production="", sites=None):
        """Retieve a directory summary for the storage usage."""
        sites = sites if sites else []
        result = gStorageUsageDB.getStorageDirectorySummary(directory, filetype, production, sites)
        if not result["OK"]:
            return result
        dl = []
        for dirPath in result["Value"]:
            dl.append((dirPath, result["Value"][dirPath]["Size"], result["Value"][dirPath]["Files"]))
        return S_OK(dl)

    types_getStorageDirectoryData = []

    @staticmethod
    def export_getStorageDirectoryData(directory="", filetype="", production="", sites=None):
        """Retrieve a directory summary for the storage usage."""
        sites = sites if sites else []
        return gStorageUsageDB.getStorageDirectorySummary(directory, filetype, production, sites)

    types_getStorageDirectories = []

    @staticmethod
    def export_getStorageDirectories(directory="", filetype="", production="", sites=None):
        """Retrieve the directories for the supplied selection."""
        sites = sites if sites else []
        return gStorageUsageDB.getStorageDirectories(directory, filetype, production, sites)

    types_getStorageDirectorySummaryWeb = []

    @staticmethod
    def export_getStorageDirectorySummaryWeb(selectDict, sortList, startItem, maxItems):
        """Get the summary of the directory storage summary."""
        resultDict = {}
        # Sorting instructions. Only one for the moment.
        directory = ""
        if "Directory" in selectDict:
            directory = selectDict["Directory"]
        filetype = ""
        if "FileType" in selectDict:
            filetype = selectDict["FileType"]
        production = ""
        if "Production" in selectDict:
            production = selectDict["Production"]
        ses = []
        if "SEs" in selectDict:
            ses = selectDict["SEs"]

        res = gStorageUsageDB.getStorageDirectorySummary(directory, filetype, production, ses)
        if not res["OK"]:
            gLogger.error(
                "StorageUsageHandler.getStorageDirectorySummaryWeb: Failed to obtain directory summary.", res["Message"]
            )
            return res
        dirList = res["Value"]
        dirList = [(path, dirList[path]["Size"], dirList[path]["Files"]) for path in dirList]

        nDirs = len(dirList)
        resultDict["TotalRecords"] = nDirs
        if nDirs == 0:
            return S_OK(resultDict)
        iniDir = startItem
        lastDir = iniDir + maxItems
        if iniDir >= nDirs:
            return S_ERROR("Item number out of range")
        if lastDir > nDirs:
            lastDir = nDirs

        # prepare the extras count
        res = gStorageUsageDB.getStorageSummary(directory, filetype, production, ses)
        if not res["OK"]:
            gLogger.error(
                "StorageUsageHandler.getStorageDirectorySummaryWeb: Failed to obtain usage summary.", res["Message"]
            )
            return res
        resultDict["Extras"] = res["Value"]

        # prepare the standard structure now
        resultDict["ParameterNames"] = ["Directory Path", "Size", "Files"]
        resultDict["Records"] = dirList[iniDir:lastDir]
        return S_OK(resultDict)

    types_getStorageElementSelection = []

    @staticmethod
    def export_getStorageElementSelection():
        """Retrieve the possible selections."""
        return gStorageUsageDB.getStorageElementSelection()

    types_getUserStorageUsage = []

    @staticmethod
    def export_getUserStorageUsage(userName=False):
        """Retrieve a summary of the user usage."""
        return gStorageUsageDB.getUserStorageUsage(userName)

    types_getUserSummaryPerSE = []

    @staticmethod
    def export_getUserSummaryPerSE(userName=False):
        """Retrieve a summary of the user usage per SE."""
        return gStorageUsageDB.getUserSummaryPerSE(userName)

    types_getDirectorySummaryPerSE = []

    @staticmethod
    def export_getDirectorySummaryPerSE(directory):
        """Retrieve a summary (total files and total size) for a given directory,
        grouped by storage element."""
        return gStorageUsageDB.getDirectorySummaryPerSE(directory)

    types_getRunSummaryPerSE = []

    @staticmethod
    def export_getRunSummaryPerSE(run):
        """Retrieve a summary (total files and total size) for a given run, grouped
        by storage element."""
        return gStorageUsageDB.getRunSummaryPerSE(run)

    types_getIDs = []

    @staticmethod
    def export_getIDs(dirList):
        """Check if the directories exist in the su_Directory table and if yes
        returns the IDs."""
        return gStorageUsageDB.getIDs(dirList)

    types_getAllReplicasInFC = []

    @staticmethod
    def export_getAllReplicasInFC(path):
        """Export the DB method to query the su_seUsage table to get all the
        entries relative to a given path registered in the FC.

        Returns for every replica the SE, the update, the files and the size
        """
        return gStorageUsageDB.getAllReplicasInFC(path)

    ####
    # Catalog
    ####

    types_getSummary = [six.string_types]

    @staticmethod
    def export_getSummary(path, fileType=False, production=False):
        """export of getSummary."""
        return gStorageUsageDB.getSummary(path, fileType, production)

    types_getUserSummary = []

    @staticmethod
    def export_getUserSummary(userName=False):
        """export of getUserSummary."""
        return gStorageUsageDB.getUserSummary(userName)

    ####
    # Purge
    ####

    types_purgeOutdatedEntries = [six.string_types, int]

    @staticmethod
    def export_purgeOutdatedEntries(rootDir, outdatedSeconds, preserveDirsList=None):
        """Purge entries that haven't been updated in the last outdated seconds."""
        preserveDirsList = preserveDirsList if preserveDirsList else []
        return gStorageUsageDB.purgeOutdatedEntries(rootDir, outdatedSeconds, preserveDirsList)

    ###
    # methods to deal with problematicDirs directory: problematicDirs
    ###
    types_publishToProblematicDirs = []

    @staticmethod
    def export_publishToProblematicDirs(directoryDict):
        """Export the publishToProblematicDirs DB method, which inserts/updates row
        into the  problematicDirs."""
        return gStorageUsageDB.publishToProblematicDirs(directoryDict)

    types_getProblematicDirsSummary = []

    @staticmethod
    def export_getProblematicDirsSummary(site, problem=False):
        """Exports the getProblematicDirsSummary method: returns a list of
        directories from the problematicDirs table, that have some inconsistency
        between the SE dumps and the LFC."""
        return gStorageUsageDB.getProblematicDirsSummary(site, problem)

    types_removeAllFromProblematicDirs = []

    @staticmethod
    def export_removeAllFromProblematicDirs(site=False):
        """Exports the removeAllFromProblematicDirs method: delete all entries from
        problematicDirs table for a give site (optional argument)"""
        return gStorageUsageDB.removeAllFromProblematicDirs(site)

    ###
    # methods to deal with se_Usage table
    ###
    types_publishToSEReplicas = []

    @staticmethod
    def export_publishToSEReplicas(directoryDict):
        """Export the publishToSEReplicas DB method, which inserts/updates replicas
        on the SE to the se_Usage table."""
        return gStorageUsageDB.publishToSEReplicas(directoryDict)

    ###
    # methods to deal with se_STSummary table
    ###

    types_publishTose_STSummary = []

    @staticmethod
    def export_publishTose_STSummary(site, spaceToken, totalSize, totalFiles, StorageDumpUpdate):
        """Export the publishTose_STSummary DB method, which inserts/updates the
        reports of total files and total size from the storage dumps to the
        se_STSummary table."""
        return gStorageUsageDB.publishTose_STSummary(site, spaceToken, totalSize, totalFiles, StorageDumpUpdate)

    types_getSTSummary = []

    @staticmethod
    def export_getSTSummary(site, spaceToken=False):
        """Exports getSTSummary method: returns a summary of the used space for the
        given site, based on the storage dumps provided by sites."""
        return gStorageUsageDB.getSTSummary(site, spaceToken)

    types_removeSTSummary = []

    @staticmethod
    def export_removeSTSummary(site, spaceToken=False):
        """Exports removeSTSummary method: removes from the se_STSummary table all
        entries relative to the given site and (optionally ) space token."""
        return gStorageUsageDB.removeSTSummary(site, spaceToken)
