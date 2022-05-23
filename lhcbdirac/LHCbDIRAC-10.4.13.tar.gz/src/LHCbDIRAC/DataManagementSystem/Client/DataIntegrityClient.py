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
"""This is the Data Integrity Client which allows the simple reporting of
problematic file and replicas to the IntegrityDB and their status correctly
updated in the FileCatalog."""
import re
import six

from DIRAC import S_OK, gLogger
from DIRAC.Core.Utilities.Adler import compareAdler
from DIRAC.Core.Utilities.ReturnValues import returnSingleResult
from DIRAC.Resources.Catalog.FileCatalog import FileCatalog
from DIRAC.Resources.Storage.StorageElement import StorageElement
from DIRAC.DataManagementSystem.Client.DataIntegrityClient import DataIntegrityClient as DIRACDataIntegrityClient
from LHCbDIRAC.BookkeepingSystem.Client.BookkeepingClient import BookkeepingClient
from LHCbDIRAC.DataManagementSystem.Client.ConsistencyChecks import ConsistencyChecks


class DataIntegrityClient(DIRACDataIntegrityClient):
    def __init__(self):
        """Extending DIRAC's DIRACDataIntegrityClient init."""
        super(DataIntegrityClient, self).__init__()

        self.cc = ConsistencyChecks()

    ##########################################################################
    #
    # This section contains the specific methods for BK->FC checks
    #

    def productionToCatalog(self, productionID):
        """This obtains the file information from the BK and checks these files are
        present in the FC."""
        gLogger.info("-" * 40)
        gLogger.info("Performing the BK->FC check")
        gLogger.info("-" * 40)
        res = self.__getProductionFiles(productionID)
        if not res["OK"]:
            return res
        noReplicaFiles = res["Value"]["GotReplicaNo"]
        yesReplicaFiles = res["Value"]["GotReplicaYes"]
        # For the files marked as existing we perfom catalog check
        res = self.cc._getCatalogMetadata(yesReplicaFiles)
        if not res["OK"]:
            return res
        catalogMetadata, missingCatalogFiles, zeroSizeFiles = res["Value"]
        if missingCatalogFiles:
            self._reportProblematicFiles(missingCatalogFiles, "LFNCatalogMissing")
        if zeroSizeFiles:
            self._reportProblematicFiles(zeroSizeFiles, "LFNZeroSize")

        # Try and get the metadata for files that shouldn't exist in the catalog
        if noReplicaFiles:
            res = self.__checkCatalogForBKNoReplicas(noReplicaFiles)
            if not res["OK"]:
                return res
            catalogMetadata.update(res["Value"])
        # Get the replicas for the files found to exist in the catalog
        res = self.cc._getCatalogReplicas(list(catalogMetadata))
        if not res["OK"]:
            return res
        replicas, zeroReplicaFiles = res["Value"]
        if zeroReplicaFiles:
            self._reportProblematicFiles(zeroReplicaFiles, "LFNZeroReplicas")
        resDict = {"CatalogMetadata": catalogMetadata, "CatalogReplicas": replicas}
        return S_OK(resDict)

    def __checkCatalogForBKNoReplicas(self, lfns):
        """Checks the catalog existence for given files."""
        gLogger.info("Checking the catalog existence of %s files" % len(lfns))

        res = self.fc.getFileMetadata(lfns)
        if not res["OK"]:
            gLogger.error("Failed to get catalog metadata", res["Message"])
            return res
        allMetadata = res["Value"]["Successful"]
        existingCatalogFiles = list(allMetadata)
        if existingCatalogFiles:
            self._reportProblematicFiles(existingCatalogFiles, "BKReplicaNo")
        gLogger.info("Checking the catalog existence of files complete")
        return S_OK(allMetadata)

    def __getProductionFiles(self, productionID):
        """This method queries the bookkeeping and obtains the file metadata for
        the given production."""
        gLogger.info("Attempting to get files for production %s" % productionID)
        res = BookkeepingClient().getProductionFiles(productionID, "ALL")
        if not res["OK"]:
            return res
        yesReplicaFiles = []
        noReplicaFiles = []
        badReplicaFiles = []
        badBKFileSize = []
        badBKGUID = []
        allMetadata = res["Value"]
        gLogger.info("Obtained at total of %s files" % len(allMetadata))
        totalSize = 0
        for lfn, bkMetadata in allMetadata.items():
            if bkMetadata["FileType"] != "LOG":
                if bkMetadata["GotReplica"] == "Yes":
                    yesReplicaFiles.append(lfn)
                    if bkMetadata["FileSize"]:
                        totalSize += int(bkMetadata["FileSize"])
                elif bkMetadata["GotReplica"] == "No":
                    noReplicaFiles.append(lfn)
                else:
                    badReplicaFiles.append(lfn)
                if not bkMetadata["FileSize"]:
                    badBKFileSize.append(lfn)
                if not bkMetadata["GUID"]:
                    badBKGUID.append(lfn)
        if badReplicaFiles:
            self._reportProblematicFiles(badReplicaFiles, "BKReplicaBad")
        if badBKFileSize:
            self._reportProblematicFiles(badBKFileSize, "BKSizeBad")
        if badBKGUID:
            self._reportProblematicFiles(badBKGUID, "BKGUIDBad")
        gLogger.info("%s files marked with replicas with total size %s bytes" % (len(yesReplicaFiles), totalSize))
        gLogger.info("%s files marked without replicas" % len(noReplicaFiles))
        resDict = {"BKMetadata": allMetadata, "GotReplicaYes": yesReplicaFiles, "GotReplicaNo": noReplicaFiles}
        return S_OK(resDict)

    ##########################################################################
    #
    # This section contains the specific methods for FC->BK checks
    #

    def catalogDirectoryToBK(self, lfnDir):
        """This obtains the replica and metadata information from the catalog for
        the supplied directory and checks against the BK."""
        gLogger.info("-" * 40)
        gLogger.info("Performing the FC->BK check")
        gLogger.info("-" * 40)
        if isinstance(lfnDir, six.string_types):
            lfnDir = [lfnDir]
        res = self.__getCatalogDirectoryContents(lfnDir)
        if not res["OK"]:
            return res
        replicas = res["Value"]["Replicas"]
        catalogMetadata = res["Value"]["Metadata"]
        resDict = {"CatalogMetadata": catalogMetadata, "CatalogReplicas": replicas}
        if not catalogMetadata:
            gLogger.warn("No files found in directory %s" % lfnDir)
            return S_OK(resDict)
        lfns = []
        for repDict in replicas:
            lfns.append(repDict)
        missingLFNs, noFlagLFNs, _okLFNs = self.cc._getBKMetadata(lfns)
        if missingLFNs:
            self._reportProblematicFiles(missingLFNs, "LFNBKMissing")
        if noFlagLFNs:
            self._reportProblematicFiles(noFlagLFNs, "BKReplicaNo")
        return S_OK(resDict)

    def catalogFileToBK(self, lfns):
        """This obtains the replica and metadata information from the catalog and
        checks against the storage elements."""
        gLogger.info("-" * 40)
        gLogger.info("Performing the FC->BK check")
        gLogger.info("-" * 40)
        if isinstance(lfns, six.string_types):
            lfns = [lfns]

        res = self.cc._getCatalogMetadata(lfns)
        if not res["OK"]:
            return res
        catalogMetadata, missingCatalogFiles, zeroSizeFiles = res["Value"]
        if missingCatalogFiles:
            self._reportProblematicFiles(missingCatalogFiles, "LFNCatalogMissing")
        if zeroSizeFiles:
            self._reportProblematicFiles(zeroSizeFiles, "LFNZeroSize")

        res = self.cc._getCatalogReplicas(list(catalogMetadata))
        if not res["OK"]:
            return res
        replicas, _zeroReplicaFiles = res["Value"]

        lfns = []
        for repDict in replicas:
            lfns.append(repDict)
        missingLFNs, noFlagLFNs, _okLFNs = self.cc._getBKMetadata(lfns)
        if missingLFNs:
            self._reportProblematicFiles(missingLFNs, "LFNBKMissing")
        if noFlagLFNs:
            self._reportProblematicFiles(noFlagLFNs, "BKReplicaNo")

        resDict = {"CatalogMetadata": catalogMetadata, "CatalogReplicas": replicas}
        return S_OK(resDict)

    ##########################################################################
    #
    # This section contains the resolution methods for various prognoses
    #

    def resolveBKReplicaYes(self, problematicDict):
        """This takes the problematic dictionary returned by the integrity DB and
        resolved the BKReplicaYes prognosis."""
        lfn = problematicDict["LFN"]
        fileID = problematicDict["FileID"]

        res = returnSingleResult(self.fc.exists(lfn))
        if not res["OK"]:
            return self.__returnProblematicError(fileID, res)
        removeBKFile = False
        # If the file does not exist in the catalog
        if not res["Value"]:
            gLogger.info("BKReplicaYes file (%d) does not exist in the catalog. Removing..." % fileID)
            removeBKFile = True
        else:
            gLogger.info("BKReplicaYes file (%d) found to exist in the catalog" % fileID)
            # If the file has no replicas in the catalog
            res = returnSingleResult(self.fc.getReplicas(lfn))
            if (not res["OK"]) and (res["Message"] == "File has zero replicas"):
                gLogger.info("BKReplicaYes file (%d) found to exist without replicas. Removing..." % fileID)
                removeBKFile = True
        if removeBKFile:
            # Remove the file from the BK because it does not exist
            res = returnSingleResult(FileCatalog(catalogs=["BookkeepingDB"]).removeFile(lfn))
            if not res["OK"]:
                return self.__returnProblematicError(fileID, res)
            gLogger.info("BKReplicaYes file (%d) removed from bookkeeping" % fileID)
        return self.__updateCompletedFiles("BKReplicaYes", fileID)

    def resolveBKReplicaNo(self, problematicDict):
        """This takes the problematic dictionary returned by the integrity DB and
        resolved the BKReplicaNo prognosis."""
        lfn = problematicDict["LFN"]
        fileID = problematicDict["FileID"]

        res = returnSingleResult(self.fc.exists(lfn))
        if not res["OK"]:
            return self.__returnProblematicError(fileID, res)
        # If the file exists in the catalog
        if not res["Value"]:
            return self.__updateCompletedFiles("BKReplicaNo", fileID)
        gLogger.info("BKReplicaNo file (%d) found to exist in the catalog" % fileID)
        # and has available replicas
        res = returnSingleResult(self.fc.getCatalogReplicas(lfn))
        if not res["OK"]:
            return self.__returnProblematicError(fileID, res)
        if not res["Value"]:
            gLogger.info("BKReplicaNo file (%d) found to have no replicas" % fileID)
            return self.changeProblematicPrognosis(fileID, "LFNZeroReplicas")
        gLogger.info("BKReplicaNo file (%d) found to have replicas" % fileID)
        res = returnSingleResult(FileCatalog(catalogs=["BookkeepingDB"]).addFile(lfn))
        if not res["OK"]:
            return self.__returnProblematicError(fileID, res)
        return self.__updateCompletedFiles("BKReplicaNo", fileID)

    def checkPhysicalFiles(self, replicas, catalogMetadata, ses=[], fixIt=False):
        """This obtains takes the supplied replica and metadata information
        obtained from the catalog and checks against the storage elements."""
        gLogger.info("-" * 40)
        gLogger.info("Performing the FC->SE check")
        gLogger.info("-" * 40)

        seLfns = {}
        for lfn, replicaDict in replicas.items():
            for se in replicaDict:
                if (ses) and (se not in ses):
                    continue
                seLfns.setdefault(se, []).append(lfn)
        gLogger.info("%s %s" % ("Storage Element".ljust(20), "Replicas".rjust(20)))

        for se in seLfns:
            res = StorageElement(se).isValid("Check")
            if not res["OK"]:
                gLogger.error("Unable to checkPhysicalFiles at", "%s: %s" % (se, res["Message"]))
                return res

        for se, lfns in sorted(seLfns.items()):
            sizeMismatch = []
            checksumMismatch = []
            checksumBadInFC = []
            res = self.__checkPhysicalFileMetadata(lfns, se)
            if not res["OK"]:
                gLogger.error("Failed to get physical file metadata.", res["Message"])
                return res
            for lfn, metadata in res["Value"].items():
                if lfn in catalogMetadata:
                    if (metadata["Size"] != catalogMetadata[lfn]["Size"]) and (metadata["Size"] != 0):
                        sizeMismatch.append((lfn, "deprecatedUrl", se, "CatalogPFNSizeMismatch"))
                    if not compareAdler(metadata["Checksum"], catalogMetadata[lfn]["Checksum"]):
                        if compareAdler(
                            metadata["Checksum"].replace("x", "0"), catalogMetadata[lfn]["Checksum"].replace("x", "0")
                        ):
                            checksumBadInFC.append(
                                (
                                    lfn,
                                    "deprecatedUrl",
                                    se,
                                    "%s %s" % (metadata["Checksum"], catalogMetadata[lfn]["Checksum"]),
                                )
                            )
                        else:
                            checksumMismatch.append(
                                (
                                    lfn,
                                    "deprecatedUrl",
                                    se,
                                    "%s %s" % (metadata["Checksum"], catalogMetadata[lfn]["Checksum"]),
                                )
                            )
            if sizeMismatch:
                self.reportProblematicReplicas(sizeMismatch, se, "CatalogPFNSizeMismatch", fixIt=fixIt)
            if checksumMismatch:
                self.reportProblematicReplicas(checksumMismatch, se, "CatalogChecksumMismatch", fixIt=fixIt)
            if checksumBadInFC:
                self.reportProblematicReplicas(checksumBadInFC, se, "CatalogChecksumToBeFixed", fixIt=fixIt)
        return S_OK()

    def __checkPhysicalFileMetadata(self, lfns, se):
        """Check obtain the physical file metadata and check the files are
        available."""
        gLogger.info("Checking the integrity of %s physical files at %s" % (len(lfns), se))

        res = StorageElement(se).getFileMetadata(lfns)
        if not res["OK"]:
            gLogger.error("Failed to get metadata for lfns.", res["Message"])
            return res
        pfnMetadataDict = res["Value"]["Successful"]
        # If the replicas are completely missing
        missingReplicas = []
        for lfn, reason in res["Value"]["Failed"].items():
            if re.search("File does not exist", reason):
                missingReplicas.append((lfn, "deprecatedUrl", se, "PFNMissing"))
        if missingReplicas:
            self.reportProblematicReplicas(missingReplicas, se, "PFNMissing")
        lostReplicas = []
        unavailableReplicas = []
        zeroSizeReplicas = []
        # If the files are not accessible
        for lfn, metadata in pfnMetadataDict.items():
            if metadata.get("Lost", False):
                lostReplicas.append((lfn, se, "PFNLost"))
            if metadata.get("Unavailable", not metadata["Accessible"]):
                unavailableReplicas.append((lfn, "deprecatedUrl", se, "PFNUnavailable"))
            if metadata["Size"] == 0:
                zeroSizeReplicas.append((lfn, "deprecatedUrl", se, "PFNZeroSize"))
        if lostReplicas:
            self.reportProblematicReplicas(lostReplicas, se, "PFNLost")
        if unavailableReplicas:
            self.reportProblematicReplicas(unavailableReplicas, se, "PFNUnavailable")
        if zeroSizeReplicas:
            self.reportProblematicReplicas(zeroSizeReplicas, se, "PFNZeroSize")
        gLogger.info("Checking the integrity of physical files at %s complete" % se)
        return S_OK(pfnMetadataDict)

    def reportProblematicReplicas(self, replicaTuple, se, reason, fixIt=False):
        """Simple wrapper function around setReplicaProblematic."""
        gLogger.info("The following %s files had %s at %s" % (len(replicaTuple), reason, se))
        for lfn, pfn, se, reason1 in sorted(replicaTuple):
            if reason1 == reason:
                reason1 = ""
            if lfn:
                gLogger.info(lfn, reason1)
            else:
                gLogger.info(pfn, reason1)
        if fixIt:
            res = self.setReplicaProblematic(replicaTuple, sourceComponent="DataIntegrityClient")
            if not res["OK"]:
                gLogger.info("Failed to update integrity DB with replicas", res["Message"])
            else:
                gLogger.info("Successfully updated integrity DB with replicas")

    ##########################################################################
    #
    # This section contains the specific methods for obtaining replica and metadata information from the catalog
    #

    def __getCatalogDirectoryContents(self, lfnDir):
        """Obtain the contents of the supplied directory."""
        gLogger.info("Obtaining the catalog contents for %s directories" % len(lfnDir))

        activeDirs = list(lfnDir)
        allFiles = {}
        while len(activeDirs) > 0:
            currentDir = activeDirs[0]
            res = self.fc.listDirectory(currentDir, verbose=True)
            activeDirs.remove(currentDir)
            if not res["OK"]:
                gLogger.error("Failed to get directory contents", res["Message"])
                return res
            elif currentDir in res["Value"]["Failed"]:
                gLogger.error(
                    "Failed to get directory contents", "%s %s" % (currentDir, res["Value"]["Failed"][currentDir])
                )
            else:
                dirContents = res["Value"]["Successful"][currentDir]
                activeDirs.extend(dirContents["SubDirs"])
                allFiles.update(dirContents["Files"])

        zeroReplicaFiles = []
        zeroSizeFiles = []
        allReplicaDict = {}
        allMetadataDict = {}
        for lfn, lfnDict in allFiles.items():
            lfnReplicas = {}
            for se, replicaDict in lfnDict["Replicas"].items():
                lfnReplicas[se] = replicaDict["PFN"]
            if not lfnReplicas:
                zeroReplicaFiles.append(lfn)
            allReplicaDict[lfn] = lfnReplicas
            allMetadataDict[lfn] = lfnDict["MetaData"]
            if lfnDict["MetaData"]["Size"] == 0:
                zeroSizeFiles.append(lfn)
        if zeroReplicaFiles:
            self._reportProblematicFiles(zeroReplicaFiles, "LFNZeroReplicas")
        if zeroSizeFiles:
            self._reportProblematicFiles(zeroSizeFiles, "LFNZeroSize")
        gLogger.info("Obtained at total of %s files for the supplied directories" % len(allMetadataDict))
        resDict = {"Metadata": allMetadataDict, "Replicas": allReplicaDict}
        return S_OK(resDict)
