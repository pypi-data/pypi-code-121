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
:mod: TransformationCleaningAgent

.. module: TransformationCleaningAgent

:synopsis: clean up of finalised transformations
"""
import ast

import six

# # from DIRAC
from DIRAC import S_OK, S_ERROR
from DIRAC.ConfigurationSystem.Client.Helpers.Operations import Operations
from DIRAC.ConfigurationSystem.Client.ConfigurationData import gConfigurationData
from DIRAC.DataManagementSystem.Client.DataManager import DataManager
from DIRAC.Resources.Catalog.FileCatalog import FileCatalog
from DIRAC.TransformationSystem.Agent.TransformationCleaningAgent import TransformationCleaningAgent as DiracTCAgent

# # from LHCbDIRAC
from LHCbDIRAC.TransformationSystem.Client.TransformationClient import TransformationClient
from LHCbDIRAC.BookkeepingSystem.Client.BookkeepingClient import BookkeepingClient
from LHCbDIRAC.DataManagementSystem.Client.StorageUsageClient import StorageUsageClient

# # agent's name
AGENT_NAME = "Transformation/TransformationCleaningAgent"


class TransformationCleaningAgent(DiracTCAgent):
    """.. class:: TransformationCleaningAgent"""

    def __init__(self, *args, **kwargs):
        """c'tor."""
        DiracTCAgent.__init__(self, *args, **kwargs)

        self.directoryLocations = ["TransformationDB", "StorageUsage"]
        self.archiveAfter = 7
        self.fileTypesToKeep = ["GAUSSHIST"]

        self.bkClient = None
        self.transClient = None
        self.storageUsageClient = None

    #############################################################################

    def initialize(self):
        """Standard initialize method for agents."""
        DiracTCAgent.initialize(self)

        self.directoryLocations = sorted(self.am_getOption("DirectoryLocations", self.directoryLocations))
        self.archiveAfter = self.am_getOption("ArchiveAfter", self.archiveAfter)  # days

        self.fileTypesToKeep = Operations().getValue("Transformations/FileTypesToKeep", self.fileTypesToKeep)

        self.bkClient = BookkeepingClient()
        self.transClient = TransformationClient()
        self.storageUsageClient = StorageUsageClient()

        return S_OK()

    def cleanMetadataCatalogFiles(self, transID):
        """clean the metadata using BKK and Data Manager. This method is a
        replacement of the one from base class.

        :param self: self reference
        :param int transID: transformation ID
        """
        res = self.bkClient.getProductionFiles(transID, "ALL", "Yes")
        if not res["OK"]:
            return res
        bkMetadata = res["Value"]
        fileToRemove = []
        yesReplica = []
        self.log.info("Found a total of %d files in the BK for transformation %d" % (len(bkMetadata), transID))
        for lfn, metadata in bkMetadata.items():
            if metadata["FileType"] != "LOG":
                fileToRemove.append(lfn)
                if metadata["GotReplica"] == "Yes":
                    yesReplica.append(lfn)
        if fileToRemove:
            self.log.info("Attempting to remove %d possible remnants from the catalog and storage" % len(fileToRemove))
            # Executing with shifter proxy
            gConfigurationData.setOptionInCFG("/DIRAC/Security/UseServerCertificate", "false")
            res = DataManager().removeFile(fileToRemove, force=True)
            gConfigurationData.setOptionInCFG("/DIRAC/Security/UseServerCertificate", "true")
            if not res["OK"]:
                return res
            for lfn, reason in res["Value"]["Failed"].items():
                self.log.error("Failed to remove file found in BK", "%s %s" % (lfn, reason))
            if res["Value"]["Failed"]:
                return S_ERROR("Failed to remove all files found in the BK")
            if yesReplica:
                self.log.info("Ensuring that %d files are removed from the BK" % (len(yesReplica)))
                res = FileCatalog(catalogs=["BookkeepingDB"]).removeFile(yesReplica)
                if not res["OK"]:
                    return res
                for lfn, reason in res["Value"]["Failed"].items():
                    self.log.error("Failed to remove file from BK", "%s %s" % (lfn, reason))
                if res["Value"]["Failed"]:
                    return S_ERROR("Failed to remove all files from the BK")
        self.log.info("Successfully removed all files found in the BK")
        return S_OK()

    def getTransformationDirectories(self, transID):
        """get the directories for the supplied transformation from the
        transformation system.

        :param self: self reference
        :param int transID: transformation ID
        """

        res = DiracTCAgent.getTransformationDirectories(self, transID)

        if not res["OK"]:
            return res

        directories = res["Value"]
        if isinstance(directories, six.string_types):  # Check for (stupid) formats
            directories = ast.literal_eval(directories)
            if not isinstance(directories, list):
                return S_ERROR("Wrong format of output directories")

        if "StorageUsage" in self.directoryLocations:
            res = self.storageUsageClient.getStorageDirectories("", "", transID, [])
            if not res["OK"]:
                self.log.error("Failed to obtain storage usage directories", res["Message"])
                return res
            transDirectories = res["Value"]
            directories = self._addDirs(transID, transDirectories, directories)

        if not directories:
            self.log.info("No output directories found")

        # We should be removing from the list of directories
        # those directories created for file types that are part of those:
        # - uploaded (as output files)
        # - not merged by subsequent steps
        # but this is pretty difficult to identify at run time, so we better remove the "RemovingFiles" production status
        # and replace it with a flush (this applies only to MC).
        # So we just have a created list.
        fileTypesToKeepDirs = []
        for fileTypeToKeep in self.fileTypesToKeep:
            fileTypesToKeepDirs.extend([x for x in directories if fileTypeToKeep in x])
        directories = list(set(directories).difference(set(fileTypesToKeepDirs)))

        directories = sorted(directories)
        return S_OK(directories)
