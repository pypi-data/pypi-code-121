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
:mod: StorageUsageAgent

.. module: StorageUsageAgent

:synopsis: StorageUsageAgent takes the FC as the primary source of information to
  determine storage usage.
"""
# # imports
import time
import random
import os
import re
import threading

# # from DIRAC
from DIRAC import S_OK, S_ERROR
from DIRAC.Core.Base.AgentModule import AgentModule
from DIRAC.ConfigurationSystem.Client.Helpers import Registry
from DIRAC.Core.Utilities.DirectoryExplorer import DirectoryExplorer
from DIRAC.Core.Utilities.File import mkDir
from DIRAC.FrameworkSystem.Client.ProxyManagerClient import gProxyManager
from DIRAC.FrameworkSystem.Client.MonitoringClient import gMonitor
from DIRAC.Resources.Catalog.FileCatalog import FileCatalog
from DIRAC.Core.Utilities.ReturnValues import returnSingleResult
from DIRAC.Core.Utilities import List
from DIRAC.Core.Utilities.Time import timeInterval, dateTime, week
from DIRAC.Core.Utilities.DictCache import DictCache
from DIRAC.Core.Utilities.List import breakListIntoChunks
from DIRAC.ConfigurationSystem.Client.Helpers.Operations import Operations

# # from LHCbDIRAC
from LHCbDIRAC.DataManagementSystem.DB.StorageUsageDB import StorageUsageDB
from LHCbDIRAC.DataManagementSystem.Client.StorageUsageClient import StorageUsageClient

AGENT_NAME = "DataManagement/StorageUsageAgent"


def removeProxy(proxyFile):
    if os.path.exists(proxyFile):
        os.remove(proxyFile)


class StorageUsageAgent(AgentModule):
    """.. class:: StorageUsageAgent.

    :param FileCatalog catalog: FileCatalog instance
    :parma mixed storageUsage: StorageUsageDB instance or its rpc client
    :param int pollingTime: polling time
    :param int activePeriod: active period on weeks
    :param threading.Lock dataLock: data lock
    :param threading.Lock replicaListLock: replica list lock
    :param DictCache proxyCache: creds cache
    """

    catalog = None
    storageUsage = None
    pollingTime = 43200
    activePeriod = 0
    dataLock = None  # threading.Lock()
    replicaListLock = None  # threading.Lock()
    proxyCache = None  # DictCache()
    enableStartupSleep = True  # Enable a random sleep so not all the user agents start together

    def __init__(self, *args, **kwargs):
        """c'tor."""
        AgentModule.__init__(self, *args, **kwargs)

        self.__baseDir = "/lhcb"
        self.__baseDirLabel = "_".join(List.fromChar(self.__baseDir, "/"))
        self.__ignoreDirsList = []
        self.__keepDirLevels = 4

        self.__startExecutionTime = int(time.time())
        self.__dirExplorer = DirectoryExplorer(reverse=True)
        self.__processedDirs = 0
        self.__directoryOwners = {}
        self.catalog = FileCatalog()
        self.__maxToPublish = self.am_getOption("MaxDirectories", 5000)
        if self.am_getOption("DirectDB", False):
            self.storageUsage = StorageUsageDB()
        else:
            # Set a timeout of 0.1 seconds per directory (factor 5 margin)
            self.storageUsage = StorageUsageClient(timeout=self.am_getOption("Timeout", int(self.__maxToPublish * 0.1)))
        self.activePeriod = self.am_getOption("ActivePeriod", self.activePeriod)
        self.dataLock = threading.Lock()
        self.replicaListLock = threading.Lock()
        self.proxyCache = DictCache(removeProxy)
        self.__noProxy = set()
        self.__catalogType = None
        self.__recalculateUsage = Operations().getValue("DataManagement/RecalculateDirSize", False)
        self.enableStartupSleep = self.am_getOption("EnableStartupSleep", self.enableStartupSleep)
        self.__publishDirQueue = {}
        self.__dirsToPublish = {}
        self.__replicaFilesUsed = set()
        self.__replicaListFilesDir = ""

    def initialize(self):
        """agent initialisation."""

        self.am_setOption("PollingTime", self.pollingTime)

        if self.enableStartupSleep:
            rndSleep = random.randint(1, self.pollingTime)
            self.log.info("Sleeping for %s seconds" % rndSleep)
            time.sleep(rndSleep)

        # This sets the Default Proxy to used as that defined under
        # /Operations/Shifter/DataManager
        # the shifterProxy option in the Configsorteduration can be used to change this default.
        self.am_setOption("shifterProxy", "DataManager")

        return S_OK()

    def __writeReplicasListFiles(self, dirPathList):
        """dump replicas list to files."""
        self.replicaListLock.acquire()
        try:
            self.log.info("Dumping replicas for %s dirs" % len(dirPathList))
            result = self.catalog.getDirectoryReplicas(dirPathList)
            if not result["OK"]:
                self.log.error("Could not get directory replicas", "%s -> %s" % (dirPathList, result["Message"]))
                return result
            resData = result["Value"]
            filesOpened = {}
            for dirPath in dirPathList:
                if dirPath in result["Value"]["Failed"]:
                    self.log.error(
                        "Could not get directory replicas", "%s -> %s" % (dirPath, resData["Failed"][dirPath])
                    )
                    continue
                dirData = resData["Successful"][dirPath]
                for lfn in dirData:
                    for seName in dirData[lfn]:
                        if seName not in filesOpened:
                            filePath = os.path.join(
                                self.__replicaListFilesDir, "replicas.%s.%s.filling" % (seName, self.__baseDirLabel)
                            )
                            # Check if file is opened and if not open it
                            if seName not in filesOpened:
                                if seName not in self.__replicaFilesUsed:
                                    self.__replicaFilesUsed.add(seName)
                                    filesOpened[seName] = open(filePath, "w")
                                else:
                                    filesOpened[seName] = open(filePath, "a")
                        # seName file is opened. Write
                        filesOpened[seName].write("%s -> %s\n" % (lfn, dirData[lfn][seName]))
            # Close the files
            for seName in filesOpened:
                filesOpened[seName].close()
            return S_OK()
        finally:
            self.replicaListLock.release()

    def __resetReplicaListFiles(self):
        """prepare directories for replica list files."""
        self.__replicaFilesUsed = set()
        self.__replicaListFilesDir = os.path.join(self.am_getOption("WorkDirectory"), "replicaLists")
        mkDir(self.__replicaListFilesDir)
        self.log.info("Replica Lists directory is %s" % self.__replicaListFilesDir)

    def __replicaListFilesDone(self):
        """rotate replicas list files."""
        self.replicaListLock.acquire()
        try:
            old = re.compile(r"^replicas\.([a-zA-Z0-9\-_]*)\.%s\.old$" % self.__baseDirLabel)
            current = re.compile(r"^replicas\.([a-zA-Z0-9\-_]*)\.%s$" % self.__baseDirLabel)
            filling = re.compile(r"^replicas\.([a-zA-Z0-9\-_]*)\.%s\.filling$" % self.__baseDirLabel)
            # Delete old
            for fileName in os.listdir(self.__replicaListFilesDir):
                match = old.match(fileName)
                if match:
                    os.unlink(os.path.join(self.__replicaListFilesDir, fileName))
            # Current -> old
            for fileName in os.listdir(self.__replicaListFilesDir):
                match = current.match(fileName)
                if match:
                    newFileName = "replicas.%s.%s.old" % (match.group(1), self.__baseDirLabel)
                    self.log.info(
                        "Moving \n %s\n to \n %s"
                        % (
                            os.path.join(self.__replicaListFilesDir, fileName),
                            os.path.join(self.__replicaListFilesDir, newFileName),
                        )
                    )
                    os.rename(
                        os.path.join(self.__replicaListFilesDir, fileName),
                        os.path.join(self.__replicaListFilesDir, newFileName),
                    )
            # filling to current
            for fileName in os.listdir(self.__replicaListFilesDir):
                match = filling.match(fileName)
                if match:
                    newFileName = "replicas.%s.%s" % (match.group(1), self.__baseDirLabel)
                    self.log.info(
                        "Moving \n %s\n to \n %s"
                        % (
                            os.path.join(self.__replicaListFilesDir, fileName),
                            os.path.join(self.__replicaListFilesDir, newFileName),
                        )
                    )
                    os.rename(
                        os.path.join(self.__replicaListFilesDir, fileName),
                        os.path.join(self.__replicaListFilesDir, newFileName),
                    )

            return S_OK()
        finally:
            self.replicaListLock.release()

    def __printSummary(self):
        """pretty print summary."""
        res = self.storageUsage.getStorageSummary()
        if res["OK"]:
            self.log.notice("Storage Usage Summary")
            self.log.notice("============================================================")
            self.log.notice("%-40s %20s %20s" % ("Storage Element", "Number of files", "Total size"))

            for se in sorted(res["Value"]):
                site = se.split("_")[0].split("-")[0]
                gMonitor.registerActivity(
                    "%s-used" % se,
                    "%s usage" % se,
                    "StorageUsage/%s usage" % site,
                    "",
                    gMonitor.OP_MEAN,
                    bucketLength=600,
                )
                gMonitor.registerActivity(
                    "%s-files" % se,
                    "%s files" % se,
                    "StorageUsage/%s files" % site,
                    "Files",
                    gMonitor.OP_MEAN,
                    bucketLength=600,
                )

            time.sleep(2)

            for se in sorted(res["Value"]):
                usage = res["Value"][se]["Size"]
                files = res["Value"][se]["Files"]
                self.log.notice("%-40s %20s %20s" % (se, str(files), str(usage)))
                gMonitor.addMark("%s-used" % se, usage)
                gMonitor.addMark("%s-files" % se, files)

    def execute(self):
        """execution in one cycle."""
        self.__publishDirQueue = {}
        self.__dirsToPublish = {}
        self.__baseDir = self.am_getOption("BaseDirectory", "/lhcb")
        self.__baseDirLabel = "_".join(List.fromChar(self.__baseDir, "/"))
        self.__ignoreDirsList = self.am_getOption("Ignore", [])
        self.__keepDirLevels = self.am_getOption("KeepDirLevels", 4)

        self.__startExecutionTime = int(time.time())
        self.__dirExplorer = DirectoryExplorer(reverse=True)
        self.__resetReplicaListFiles()
        self.__noProxy = set()
        self.__processedDirs = 0
        self.__directoryOwners = {}

        self.__printSummary()

        self.__dirExplorer.addDir(self.__baseDir)
        self.log.notice("Initiating with %s as base directory." % self.__baseDir)
        # Loop over all the directories and sub-directories
        totalIterTime = 0.0
        numIterations = 0.0
        iterMaxDirs = 100
        while self.__dirExplorer.isActive():
            startT = time.time()
            d2E = [self.__dirExplorer.getNextDir() for _i in range(iterMaxDirs) if self.__dirExplorer.isActive()]
            self.__exploreDirList(d2E)
            iterTime = time.time() - startT
            totalIterTime += iterTime
            numIterations += len(d2E)
            self.log.verbose("Query took %.2f seconds for %s dirs" % (iterTime, len(d2E)))
        self.log.verbose("Average query time: %2.f secs/dir" % (totalIterTime / numIterations))

        # Publish remaining directories
        self.__publishData(background=False)

        # Move replica list files
        self.__replicaListFilesDone()

        # Clean records older than 1 day
        self.log.info("Finished recursive directory search.")

        if self.am_getOption("PurgeOutdatedRecords", True):
            elapsedTime = time.time() - self.__startExecutionTime
            outdatedSeconds = max(max(self.am_getOption("PollingTime"), elapsedTime) * 2, 86400)
            result = self.storageUsage.purgeOutdatedEntries(self.__baseDir, int(outdatedSeconds), self.__ignoreDirsList)
            if not result["OK"]:
                return result
            self.log.notice("Purged %s outdated records" % result["Value"])
        return S_OK()

    def __exploreDirList(self, dirList):
        """collect directory size for directory in :dirList:"""
        # Normalise dirList first
        dirList = [os.path.realpath(d) for d in dirList]
        self.log.notice("Retrieving info for %s dirs" % len(dirList))
        # For top directories, no files anyway, hence no need to get full size
        dirContents = {}
        failed = {}
        successfull = {}
        startTime = time.time()
        nbDirs = len(dirList)
        chunkSize = 10
        if self.__catalogType == "DFC" or dirList == [self.__baseDir]:
            # Get the content of the directory as anyway this is needed
            for dirChunk in breakListIntoChunks(dirList, chunkSize):
                res = self.catalog.listDirectory(dirChunk, True, timeout=600)
                if not res["OK"]:
                    failed.update(dict.fromkeys(dirChunk, res["Message"]))
                else:
                    failed.update(res["Value"]["Failed"])
                    dirContents.update(res["Value"]["Successful"])
            self.log.info(
                "Time to retrieve content of %d directories: %.1f seconds" % (nbDirs, time.time() - startTime)
            )
            for dirPath in failed:
                dirList.remove(dirPath)
        # We don't need to get the storage usage if there are no files...
        dirListSize = [d for d in dirList if dirContents.get(d, {}).get("Files")]

        startTime1 = time.time()
        # __recalculateUsage enables to recompute the directory usage in case the internal table is wrong
        for args in [(d, True, self.__recalculateUsage) for d in breakListIntoChunks(dirListSize, chunkSize)]:
            res = self.catalog.getDirectorySize(*args, timeout=600)
            if not res["OK"]:
                failed.update(dict.fromkeys(args[0], res["Message"]))
            else:
                failed.update(res["Value"]["Failed"])
                successfull.update(res["Value"]["Successful"])
        errorReason = {}
        for dirPath in failed:
            error = str(failed[dirPath])
            errorReason.setdefault(error, []).append(dirPath)
        for error in errorReason:
            self.log.error("Failed to get directory info", "- %s for:\n\t%s" % (error, "\n\t".join(errorReason[error])))
        self.log.info(
            "Time to retrieve size of %d directories: %.1f seconds" % (len(dirListSize), time.time() - startTime1)
        )
        for dirPath in [d for d in dirList if d not in failed]:
            metadata = successfull.get(dirPath, {})
            if "SubDirs" in metadata:
                self.__processDir(dirPath, metadata)
            else:
                if not self.__catalogType:
                    self.log.info("Catalog type determined to be DFC")
                    self.__catalogType = "DFC"
                self.__processDirDFC(dirPath, metadata, dirContents[dirPath])
        self.log.info("Time to process %d directories: %.1f seconds" % (nbDirs, time.time() - startTime))
        notCommited = len(self.__publishDirQueue) + len(self.__dirsToPublish)
        self.log.notice(
            "%d dirs to be explored, %d done. %d not yet committed."
            % (self.__dirExplorer.getNumRemainingDirs(), self.__processedDirs, notCommited)
        )

    def __processDirDFC(self, dirPath, metadata, subDirectories):
        """gets the list of subdirs that the DFC doesn't return, set the metadata
        like the FC and then call the same method as for the FC.
        """
        if "SubDirs" not in subDirectories:
            self.log.error("No subdirectory item for directory", dirPath)
            return
        dirMetadata = {"Files": 0, "TotalSize": 0, "ClosedDirs": [], "SiteUsage": {}}
        if "PhysicalSize" in metadata:
            dirMetadata["Files"] = metadata["LogicalFiles"]
            dirMetadata["TotalSize"] = metadata["LogicalSize"]
            dirMetadata["SiteUsage"] = metadata["PhysicalSize"].copy()
            dirMetadata["SiteUsage"].pop("TotalFiles", None)
            dirMetadata["SiteUsage"].pop("TotalSize", None)
        subDirs = subDirectories["SubDirs"].copy()
        dirMetadata["SubDirs"] = subDirs
        dirUsage = dirMetadata["SiteUsage"]
        errorReason = {}
        for subDir in subDirs:
            self.__directoryOwners.setdefault(subDir, (subDirs[subDir]["Owner"], subDirs[subDir]["OwnerGroup"]))
            subDirs[subDir] = subDirs[subDir].get("CreationTime", dateTime())
            if dirUsage:
                # This part here is for removing the recursivity introduced by the DFC
                args = [subDir]
                if len(subDir.split("/")) > self.__keepDirLevels:
                    args += [True, self.__recalculateUsage]
                result = self.catalog.getDirectorySize(*args)
                if not result["OK"]:
                    errorReason.setdefault(str(result["Message"]), []).append(subDir)
                    continue
                else:
                    metadata = result["Value"]["Successful"].get(subDir)
                    if metadata:
                        dirMetadata["Files"] -= metadata["LogicalFiles"]
                        dirMetadata["TotalSize"] -= metadata["LogicalSize"]
                    else:
                        errorReason.setdefault(str(result["Value"]["Failed"][subDir], [])).append(subDir)
                        continue
                if "PhysicalSize" in metadata and dirUsage:
                    seUsage = metadata["PhysicalSize"]
                    seUsage.pop("TotalFiles", None)
                    seUsage.pop("TotalSize", None)
                    for se in seUsage:
                        if se not in dirUsage:
                            self.log.error("SE used in subdir but not in dir", se)
                        else:
                            dirUsage[se]["Files"] -= seUsage[se]["Files"]
                            dirUsage[se]["Size"] -= seUsage[se]["Size"]
        for error in errorReason:
            self.log.error("Failed to get directory info", "- %s for:\n\t%s" % (error, "\n\t".join(errorReason[error])))
        for se, usage in list(dirUsage.items()):
            # Both info should be 0 or #0
            if not usage["Files"] and not usage["Size"]:
                dirUsage.pop(se)
            elif not usage["Files"] * usage["Size"]:
                self.log.error("Directory inconsistent", "%s @ %s: %s" % (dirPath, se, str(usage)))
        return self.__processDir(dirPath, dirMetadata)

    def __processDir(self, dirPath, dirMetadata):
        """calculate nb of files and size of :dirPath:, remove it if it's empty."""
        subDirs = dirMetadata["SubDirs"]
        closedDirs = dirMetadata["ClosedDirs"]
        ##############################
        # FIXME: Until we understand while closed dirs are not working...
        ##############################
        closedDirs = []
        prStr = "%s: found %s sub-directories" % (dirPath, len(subDirs) if subDirs else "no")
        if closedDirs:
            prStr += ", %s are closed (ignored)" % len(closedDirs)
        for rmDir in closedDirs + self.__ignoreDirsList:
            subDirs.pop(rmDir, None)
        numberOfFiles = int(dirMetadata["Files"])
        totalSize = int(dirMetadata["TotalSize"])
        if numberOfFiles:
            prStr += " and %s files (%s bytes)" % (numberOfFiles, totalSize)
        else:
            prStr += " and no files"
        self.log.notice(prStr)
        if closedDirs:
            self.log.verbose("Closed dirs:\n %s" % "\n".join(closedDirs))
        siteUsage = dirMetadata["SiteUsage"]
        if numberOfFiles > 0:
            dirData = {"Files": numberOfFiles, "TotalSize": totalSize, "SEUsage": siteUsage}
            self.__addDirToPublishQueue(dirPath, dirData)
            # Print statistics
            self.log.verbose("%-40s %20s %20s" % ("Storage Element", "Number of files", "Total size"))
            for storageElement in sorted(siteUsage):
                usageDict = siteUsage[storageElement]
                self.log.verbose("%-40s %20s %20s" % (storageElement, str(usageDict["Files"]), str(usageDict["Size"])))
        # If it's empty delete it
        elif len(subDirs) == 0 and len(closedDirs) == 0:
            if dirPath != self.__baseDir:
                self.removeEmptyDir(dirPath)
                return
        # We don't need the cached information about owner
        self.__directoryOwners.pop(dirPath, None)
        rightNow = dateTime()
        chosenDirs = [
            subDir
            for subDir in subDirs
            if not self.activePeriod or timeInterval(subDirs[subDir], self.activePeriod * week).includes(rightNow)
        ]

        self.__dirExplorer.addDirList(chosenDirs)
        self.__processedDirs += 1

    def __getOwnerProxy(self, dirPath):
        """get owner creds for :dirPath:"""
        self.log.verbose("Retrieving dir metadata...")
        # get owner form the cached information, if not, try getDirectoryMetadata
        ownerName, ownerGroup = self.__directoryOwners.pop(dirPath, (None, None))
        if not ownerName or not ownerGroup:
            result = returnSingleResult(self.catalog.getDirectoryMetadata(dirPath))
            if not result["OK"] or "OwnerRole" not in result["Value"]:
                self.log.error("Could not get metadata info", result["Message"])
                return result
            ownerRole = result["Value"]["OwnerRole"]
            ownerDN = result["Value"]["OwnerDN"]
            if ownerRole[0] != "/":
                ownerRole = "/%s" % ownerRole
            cacheKey = (ownerDN, ownerRole)
            ownerName = "unknown"
            byGroup = False
        else:
            ownerDN = Registry.getDNForUsername(ownerName)
            if not ownerDN["OK"]:
                self.log.error("Could not get DN from user name", ownerDN["Message"])
                return ownerDN
            ownerDN = ownerDN["Value"][0]
            # This bloody method returns directly a string!!!!
            ownerRole = Registry.getVOMSAttributeForGroup(ownerGroup)
            byGroup = True
            # Get all groups for that VOMS Role, and add lhcb_user as in DFC this is a safe value
        ownerGroups = Registry.getGroupsWithVOMSAttribute(ownerRole) + ["lhcb_user"]

        downErrors = []
        for ownerGroup in ownerGroups:
            if byGroup:
                ownerRole = None
                cacheKey = (ownerDN, ownerGroup)
            if cacheKey in self.__noProxy:
                return S_ERROR("Proxy not available")
                # Getting the proxy...
            upFile = self.proxyCache.get(cacheKey, 3600)
            if upFile and os.path.exists(upFile):
                self.log.verbose(
                    "Returning cached proxy for %s %s@%s [%s] in %s"
                    % (ownerName, ownerDN, ownerGroup, ownerRole, upFile)
                )
                return S_OK(upFile)
            if ownerRole:
                result = gProxyManager.downloadVOMSProxy(
                    ownerDN, ownerGroup, limited=False, requiredVOMSAttribute=ownerRole
                )
            else:
                result = gProxyManager.downloadProxy(ownerDN, ownerGroup, limited=False)
            if not result["OK"]:
                downErrors.append("%s : %s" % (cacheKey, result["Message"]))
                continue
            userProxy = result["Value"]
            secsLeft = max(0, userProxy.getRemainingSecs()["Value"])
            upFile = userProxy.dumpAllToFile()
            if upFile["OK"]:
                upFile = upFile["Value"]
            else:
                return upFile
            self.proxyCache.add(cacheKey, secsLeft, upFile)
            self.log.info("Got proxy for %s %s@%s [%s]" % (ownerName, ownerDN, ownerGroup, ownerRole))
            return S_OK(upFile)
        self.__noProxy.add(cacheKey)
        return S_ERROR(
            "Could not download proxy for user (%s, %s):\n%s " % (ownerDN, ownerRole, "\n ".join(downErrors))
        )

    def removeEmptyDir(self, dirPath):
        self.log.notice("Deleting empty directory %s" % dirPath)
        for useOwnerProxy in (False, True):
            result = self.__removeEmptyDir(dirPath, useOwnerProxy=useOwnerProxy)
            if result["OK"]:
                self.log.info("Successfully removed empty directory from File Catalog and StorageUsageDB")
                break
        return result

    def __removeEmptyDir(self, dirPath, useOwnerProxy=True):
        """unlink empty folder :dirPath:"""
        from DIRAC.ConfigurationSystem.Client.ConfigurationData import gConfigurationData

        if len(List.fromChar(dirPath, "/")) < self.__keepDirLevels:
            return S_OK()

        if useOwnerProxy:
            result = self.__getOwnerProxy(dirPath)
            if not result["OK"]:
                if "Proxy not available" not in result["Message"]:
                    self.log.error(result["Message"])
                return result

            upFile = result["Value"]
            prevProxyEnv = os.environ["X509_USER_PROXY"]
            os.environ["X509_USER_PROXY"] = upFile
        try:
            gConfigurationData.setOptionInCFG("/DIRAC/Security/UseServerCertificate", "false")
            # res = self.catalog.removeDirectory( dirPath )
            res = self.catalog.writeCatalogs[0][1].removeDirectory(dirPath)
            if not res["OK"]:
                self.log.error("Error removing empty directory from File Catalog.", res["Message"])
                return res
            elif dirPath in res["Value"]["Failed"]:
                self.log.error("Failed to remove empty directory from File Catalog.", res["Value"]["Failed"][dirPath])
                self.log.debug(str(res))
                return S_ERROR(res["Value"]["Failed"][dirPath])
            res = self.storageUsage.removeDirectory(dirPath)
            if not res["OK"]:
                self.log.error("Failed to remove empty directory from Storage Usage database.", res["Message"])
                return res
            return S_OK()
        finally:
            gConfigurationData.setOptionInCFG("/DIRAC/Security/UseServerCertificate", "true")
            if useOwnerProxy:
                os.environ["X509_USER_PROXY"] = prevProxyEnv

    def __addDirToPublishQueue(self, dirName, dirData):
        """enqueue :dirName: and :dirData: for publishing."""
        self.__publishDirQueue[dirName] = dirData
        numDirsToPublish = len(self.__publishDirQueue)
        if numDirsToPublish and numDirsToPublish % self.am_getOption("PublishClusterSize", 100) == 0:
            self.__publishData(background=True)

    def __publishData(self, background=True):
        """publish data in a separate deamon thread."""
        self.dataLock.acquire()
        try:
            # Dump to file
            if self.am_getOption("DumpReplicasToFile", False):
                pass
                # repThread = threading.Thread( target = self.__writeReplicasListFiles,
                #                              args = ( list( self.__publishDirQueue ), ) )
            self.__dirsToPublish.update(self.__publishDirQueue)
            self.__publishDirQueue = {}
        finally:
            self.dataLock.release()
        if background:
            pubThread = threading.Thread(target=self.__executePublishData)
            pubThread.setDaemon(1)
            pubThread.start()
        else:
            self.__executePublishData()

    def __executePublishData(self):
        """publication thread target."""
        self.dataLock.acquire()
        try:
            if not self.__dirsToPublish:
                self.log.info("No data to be published")
                return
            if len(self.__dirsToPublish) > self.__maxToPublish:
                toPublish = {}
                for dirName in sorted(self.__dirsToPublish)[: self.__maxToPublish]:
                    toPublish[dirName] = self.__dirsToPublish.pop(dirName)
            else:
                toPublish = self.__dirsToPublish
            self.log.info("Publishing usage for %d directories" % len(toPublish))
            res = self.storageUsage.publishDirectories(toPublish)
            if res["OK"]:
                # All is OK, reset the dictionary, even if data member!
                toPublish.clear()
            else:
                # Put back dirs to be published, due to the error
                self.__dirsToPublish.update(toPublish)
                self.log.error("Failed to publish directories", res["Message"])
            return res
        finally:
            self.dataLock.release()
