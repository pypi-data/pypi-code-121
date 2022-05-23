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
:mod: RAWIntegrityAgent

.. module: RAWIntegrityAgent

:synopsis: RAWIntegrityAgent determines whether RAW files in CASTOR were migrated correctly.
"""

# # imports
import datetime

# # from DIRAC
from DIRAC import S_OK

# # from Core
from DIRAC.Core.Base.AgentModule import AgentModule
from DIRAC.ConfigurationSystem.Client.ConfigurationData import gConfigurationData
from DIRAC.FrameworkSystem.Client.MonitoringClient import gMonitor

# # from DMS
from DIRAC.Resources.Catalog.FileCatalog import FileCatalog
from DIRAC.Resources.Storage.StorageElement import StorageElement
from LHCbDIRAC.DataManagementSystem.DB.RAWIntegrityDB import RAWIntegrityDB
from DIRAC.Core.Utilities.List import breakListIntoChunks

AGENT_NAME = "DataManagement/RAWIntegrityAgent"


class RAWIntegrityAgent(AgentModule):
    """.. class:: RAWIntegirtyAgent.

    :param RAWIntegrityDB rawIntegrityDB: RAWIntegrityDB instance
    :param str gatewayUrl: URL to online RequestClient
    """

    def __init__(self, *args, **kwargs):
        """c'tor."""

        AgentModule.__init__(self, *args, **kwargs)

        self.rawIntegrityDB = None
        self.fileCatalog = None
        self.onlineRequestMgr = None

    def initialize(self):
        """agent initialisation."""

        self.rawIntegrityDB = RAWIntegrityDB()

        # The file catalog is used to register file once it has been transfered
        # But we want to register it in all the catalogs except the RAWIntegrityDB
        # otherwise it is register twice
        # We also remove the BK catalog because some files are not registered there
        # (detector calibration files for example). The real data are registered in
        # the bookeeping by the DataMover
        self.fileCatalog = FileCatalog(catalogs="FileCatalog")

        gMonitor.registerActivity("Iteration", "Agent Loops/min", "RAWIntegriryAgent", "Loops", gMonitor.OP_SUM)
        gMonitor.registerActivity(
            "WaitingFiles", "Files waiting for migration", "RAWIntegriryAgent", "Files", gMonitor.OP_MEAN
        )
        gMonitor.registerActivity("WaitSize", "Size of migration buffer", "RAWIntegrityAgent", "GB", gMonitor.OP_MEAN)

        gMonitor.registerActivity(
            "NewlyMigrated", "Newly migrated files", "RAWIntegriryAgent", "Files", gMonitor.OP_SUM
        )
        gMonitor.registerActivity("TotMigrated", "Total migrated files", "RAWIntegriryAgent", "Files", gMonitor.OP_ACUM)
        gMonitor.registerActivity(
            "TotMigratedSize", "Total migrated file size", "RAWIntegriryAgent", "GB", gMonitor.OP_ACUM
        )

        gMonitor.registerActivity("BadChecksum", "Checksums mismatch", "RAWIntegriryAgent", "Files", gMonitor.OP_SUM)
        gMonitor.registerActivity(
            "ErrorMetadata", "Error when getting files metadata", "RAWIntegriryAgent", "Files", gMonitor.OP_SUM
        )
        gMonitor.registerActivity(
            "ErrorRegister", "Error when registering files", "RAWIntegriryAgent", "Files", gMonitor.OP_SUM
        )
        gMonitor.registerActivity(
            "ErrorRemove", "Error when removing files", "RAWIntegriryAgent", "Files", gMonitor.OP_SUM
        )

        gMonitor.registerActivity(
            "FailedMigrated",
            "Number of files encountering error during migration",
            "RAWIntegriryAgent",
            "Files",
            gMonitor.OP_SUM,
        )
        gMonitor.registerActivity(
            "TotFailMigrated",
            "Total number of files encountering error during migration",
            "RAWIntegriryAgent",
            "Files",
            gMonitor.OP_ACUM,
        )

        gMonitor.registerActivity(
            "MigrationTime", "Average migration time", "RAWIntegriryAgent", "Seconds", gMonitor.OP_MEAN
        )
        # gMonitor.registerActivity("TimeInQueue", "Average current wait for migration",
        #                           "RAWIntegriryAgent", "Minutes", gMonitor.OP_MEAN)
        gMonitor.registerActivity(
            "MigrationRate", "Observed migration rate", "RAWIntegriryAgent", "MB/s", gMonitor.OP_MEAN
        )

        # This sets the Default Proxy to used as that defined under
        # /Operations/Shifter/DataManager
        # the shifterProxy option in the Configuration can be used to change this default.
        self.am_setOption("shifterProxy", "DataProcessing")

        return S_OK()

    def _checkMigrationStatus(self, filesMetadata, lfnsMetadata):
        """Check that the lfns in parameters are properly migrated, and compares
        the checksum between castor and the RAWIntegrityDB.

        :param filesMetadata: dict {lfn: se metadata}
        :param lfnsMetadata: dict {lfn: metadata in RAWIntegrityDB}

        :returns: True/False in successful, Failed in case of problem
        """
        ############################################################
        #
        # Determine the files that have been newly migrated and their success
        #

        successful = {}
        failed = {}
        for lfn, seMetadata in filesMetadata.items():
            isMigrated = seMetadata.get("Migrated", False)
            # If it is not migrated, go to the next one
            if not isMigrated:
                successful[lfn] = False
                continue
            else:
                self.log.info("%s is copied." % lfn)
                castorChecksum = seMetadata["Checksum"]
                onlineChecksum = lfnsMetadata[lfn]["Checksum"]
                if castorChecksum.lower().lstrip("0") == onlineChecksum.lower().lstrip("0").lstrip("x"):
                    self.log.info("%s migrated checksum match." % lfn)
                    successful[lfn] = True
                else:
                    errStr = "Migrated checksum mis-match.", "%s %s %s" % (
                        lfn,
                        castorChecksum.lstrip("0"),
                        onlineChecksum.lstrip("0").lstrip("x"),
                    )
                    self.log.error(errStr)
                    failed[lfn] = errStr

        return S_OK({"Successful": successful, "Failed": failed})

    def getNewlyCopiedFiles(self, activeFiles):
        """Get the list of files newly copied and those not yet copied.

        :param activeFiles: dict {lfn:RawIntegrityDB metadata} for files in Active status

        :return: tuple filesNewlyCopied, filesNotYetCopied (lfns lists)
        """
        # This is a list of all the lfns that we will have newly copied
        filesNewlyCopied = []
        # This are the lfns that are not yet copied
        filesNotYetCopied = []

        self.log.info("Obtaining physical file metadata.")
        # Group the lfns by SEs
        seLfns = {}
        for lfn, metadataDict in activeFiles.items():
            se = metadataDict["SE"]
            seLfns.setdefault(se, []).append(lfn)

        for se in sorted(seLfns):
            lfnList = seLfns[se]
            failedMetadata = {}
            successfulMetadata = {}
            res = StorageElement(se).getFileMetadata(lfnList)
            if not res["OK"]:
                errStr = "Failed to obtain physical file metadata."
                self.log.error(errStr, res["Message"])
                failedMetadata = dict((lfn, errStr) for lfn in lfnList)
            else:
                successfulMetadata = res["Value"]["Successful"]
                failedMetadata = res["Value"]["Failed"]

            if failedMetadata:
                self.log.info("Failed to obtain physical file metadata for %s files." % len(failedMetadata))
                gMonitor.addMark("ErrorMetadata", len(failedMetadata))

            if successfulMetadata:
                self.log.info("Obtained physical file metadata for %s files." % len(successfulMetadata))

                ############################################################
                #
                # Determine the files that have been newly migrated and their success
                #
                res = self._checkMigrationStatus(successfulMetadata, activeFiles)
                if not res["OK"]:
                    self.log.error("Error when checking migration status", res)
                    gMonitor.addMark("BadChecksum", len(successfulMetadata))
                else:
                    succCompare = res["Value"]["Successful"]
                    failedCompare = res["Value"]["Failed"]
                    seFilesCopied = []
                    seFilesNotCopied = []
                    # The copied files are those in True in the successful dictionary
                    for lfn, isCopied in succCompare.items():
                        if isCopied:
                            seFilesCopied.append(lfn)
                        else:
                            seFilesNotCopied.append(lfn)

                    filesNewlyCopied.extend(seFilesCopied)
                    filesNotYetCopied.extend(seFilesNotCopied)

                    gMonitor.addMark("BadChecksum", len(failedCompare))

                    self.log.info("%s files newly copied at %s." % (len(seFilesCopied), se))
                    self.log.info("Found %s checksum mis-matches at %s." % (len(failedCompare), se))

        return filesNewlyCopied, filesNotYetCopied

    def registerCopiedFiles(self, filesNewlyCopied, copiedFiles, allUnmigratedFilesMeta):
        """Register successfuly copied files (newly, or in Copied status in the DB)
        in the DFC.

        :param filesNewlyCopied: [lfns] of files newly copied
        :param copiedFiles: {lfn:RIDb metadata} of files that were in Copied state.
        :param allUnmigratedFilesMeta: {lfn:RI Db metadata} for all lfns non migrated at
                                      the beginning of the loop.

        :return: {lfn:True} for successfuly registered lfns
        """
        if filesNewlyCopied or copiedFiles:
            self.log.info(
                "Attempting to register %s newly copied and %s previously copied files"
                % (len(filesNewlyCopied), len(copiedFiles))
            )
        else:
            self.log.info("No files to be registered")

        # Update copiedFiles to also contain the newly copied files
        copiedFiles.update(dict((lfn, allUnmigratedFilesMeta[lfn]) for lfn in filesNewlyCopied))

        successfulRegister = {}
        failedRegister = {}

        # Try to register them by batch
        for lfnChunk in breakListIntoChunks(copiedFiles, 100):
            # Add the metadata
            lfnDictChuck = dict((lfn, copiedFiles[lfn]) for lfn in lfnChunk)
            res = self.fileCatalog.addFile(lfnDictChuck)

            if not res["OK"]:
                self.log.error("Completely failed to register some successfully copied file.", res["Message"])
                failedRegister.update(dict((lfn, res["Message"]) for lfn in lfnDictChuck))
            else:
                successfulRegister.update(res["Value"]["Successful"])
                failedRegister.update(res["Value"]["Failed"])

        gMonitor.addMark("ErrorRegister", len(failedRegister))
        for lfn, reason in failedRegister.items():
            self.log.error("Failed to register lfn. Setting to Copied", "%s: %s" % (lfn, reason))
            res = self.rawIntegrityDB.setFileStatus(lfn, "Copied")
            if not res["OK"]:
                self.log.error("Error setting file status to Copied", "%s: %s" % (lfn, res["Message"]))

        for lfn in successfulRegister:
            self.log.info("Successfully registered %s in the File Catalog." % lfn)

        return successfulRegister

    def removeRegisteredFiles(self, filesNewlyRegistered, registeredFiles, allUnmigratedFilesMeta):
        """Remove successfuly registered files (newly, or in Registered status in
        the DB) from the OnlineStorage.

        :param filesNewlyCopied: [lfns] of files newly copied
        :param copiedFiles: {lfn:RIDb metadata} of files that were in Copied state.
        :param allUnmigratedFilesMeta: {lfn:RI Db metadata} for all lfns non migrated at
                                      the beginning of the loop.

        :return: {lfn:True} for successfuly registered lfns
        """
        if filesNewlyRegistered or registeredFiles:
            self.log.info(
                "Attempting to remove %s newly registered and %s previously registered files"
                % (len(filesNewlyRegistered), len(registeredFiles))
            )
        else:
            self.log.info("No files to be removed")

        # Update registeredFiles to also contain the newly registered files
        registeredFiles.update(dict((lfn, allUnmigratedFilesMeta[lfn]) for lfn in filesNewlyRegistered))

        onlineSE = StorageElement("OnlineRunDB")

        # Try to them them all
        res = onlineSE.removeFile(registeredFiles)

        filesNewlyRemoved = {}
        failedRemove = {}
        if not res["OK"]:
            self.log.error("Completely failed to remove successfully registered files.", res["Message"])
            failedRemove = dict((lfn, res["Message"]) for lfn in registeredFiles)
        else:
            filesNewlyRemoved = res["Value"]["Successful"]
            failedRemove = res["Value"]["Failed"]

        gMonitor.addMark("ErrorRemove", len(failedRemove))
        for lfn, reason in failedRemove.items():
            self.log.error("Failed to remove lfn. Setting to Registered", "%s: %s" % (lfn, reason))
            res = self.rawIntegrityDB.setFileStatus(lfn, "Registered")
            if not res["OK"]:
                self.log.error("Error setting file status to Registered", "%s: %s" % (lfn, res["Message"]))

        now = datetime.datetime.utcnow()
        for lfn in filesNewlyRemoved:
            self.log.info("Successfully removed %s from the Online storage. Setting it to Done" % lfn)
            res = self.rawIntegrityDB.setFileStatus(lfn, "Done")
            if not res["OK"]:
                self.log.error("Error setting file status to Done", "%s: %s" % (lfn, res["Message"]))
            else:
                # SubmitTime is ALREADY a datetime since it is declared as such in the DB.
                submitTime = allUnmigratedFilesMeta[lfn]["SubmitTime"]
                migrationTime = (now - submitTime).total_seconds()
                gMonitor.addMark("MigrationTime", migrationTime)
                fileSizeMB = allUnmigratedFilesMeta[lfn]["Size"] / (1024 * 1024.0)
                gMonitor.addMark("MigrationRate", fileSizeMB / migrationTime)

        return filesNewlyRemoved

    def execute(self):
        """execution in one cycle."""

        # Don't use the server certificate otherwise the DFC wont let us write
        gConfigurationData.setOptionInCFG("/DIRAC/Security/UseServerCertificate", "false")

        gMonitor.addMark("Iteration", 1)

        ############################################################
        #
        # Obtain the files which have not yet been migrated
        #
        self.log.info("Obtaining un-migrated files.")
        res = self.rawIntegrityDB.getUnmigratedFiles()
        if not res["OK"]:
            errStr = "Failed to obtain un-migrated files."
            self.log.error(errStr, res["Message"])
            return S_OK()

        # allUnmigratedFilesMeta contain all the files that are not yet
        # migrated (not copied, not registered, not removed), as well as their metadata
        allUnmigratedFilesMeta = res["Value"]
        self.log.info("Obtained %s un-migrated files." % len(allUnmigratedFilesMeta))
        if not allUnmigratedFilesMeta:
            return S_OK()

        # activeFiles contains the files that are not yet copied
        activeFiles = {}
        # copiedFiles contains files that are copied but not yet registered
        copiedFiles = {}
        # registeredFiles contains files that are copied, registered, but not removed from source
        registeredFiles = {}

        # Assign them
        for lfn, lfnMetadata in allUnmigratedFilesMeta.items():
            status = lfnMetadata.pop("Status")
            if status == "Active":
                activeFiles[lfn] = lfnMetadata
            elif status == "Copied":
                copiedFiles[lfn] = lfnMetadata
            elif status == "Registered":
                registeredFiles[lfn] = lfnMetadata

        gMonitor.addMark("WaitingFiles", len(activeFiles))
        totalSize = 0
        for lfn, fileDict in activeFiles.items():
            totalSize += int(fileDict["Size"])
            # gMonitor.addMark("TimeInQueue", (fileDict['WaitTime'] / 60))
        gMonitor.addMark("WaitSize", (totalSize / (1024 * 1024 * 1024.0)))

        ############################################################
        #
        # Checking newly copied files
        #

        # Get the list of lfns properly copied and not copied
        filesNewlyCopied, filesNotYetCopied = self.getNewlyCopiedFiles(activeFiles)

        ####################################################
        #
        # Registering copied files
        #
        ####################################################

        filesNewlyRegistered = self.registerCopiedFiles(filesNewlyCopied, copiedFiles, allUnmigratedFilesMeta)

        ####################################################
        #
        # Performing the removal from the online storage
        #
        ####################################################
        filesNewlyRemoved = self.removeRegisteredFiles(filesNewlyRegistered, registeredFiles, allUnmigratedFilesMeta)

        # Doing some accounting

        migratedSize = sum(allUnmigratedFilesMeta[lfn]["Size"] for lfn in filesNewlyRemoved)

        # The number of files that we failed at migrating
        # is the number of files at the beginning, minus the one we processed completely
        # minus those that are not yet copied
        failedMigrated = len(allUnmigratedFilesMeta) - len(filesNewlyRemoved) - len(filesNotYetCopied)

        res = self.rawIntegrityDB.setLastMonitorTime()
        migratedSizeGB = migratedSize / (1024 * 1024 * 1024.0)
        gMonitor.addMark("TotMigratedSize", migratedSizeGB)
        gMonitor.addMark("NewlyMigrated", len(filesNewlyRemoved))
        gMonitor.addMark("TotMigrated", len(filesNewlyRemoved))
        gMonitor.addMark("FailedMigrated", failedMigrated)
        gMonitor.addMark("TotFailMigrated", failedMigrated)

        return S_OK()
