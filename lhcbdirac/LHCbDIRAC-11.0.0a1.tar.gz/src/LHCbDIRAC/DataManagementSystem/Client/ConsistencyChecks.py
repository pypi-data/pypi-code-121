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
    LHCb class for doing consistency checks, between files in:
    - Bookkeeping
    - Transformation
    - File Catalog
"""
import time
import ast
import os
import copy
import six

import DIRAC

from DIRAC import gLogger

from DIRAC.DataManagementSystem.Utilities.DMSHelpers import DMSHelpers, resolveSEGroup
from DIRAC.DataManagementSystem.Client.ConsistencyInspector import ConsistencyInspector as DiracConsistencyChecks
from DIRAC.ConfigurationSystem.Client.Helpers.Operations import Operations
from DIRAC.Core.Utilities.List import breakListIntoChunks
from DIRAC.Resources.Storage.StorageElement import StorageElement
from DIRAC.Core.Utilities.Adler import compareAdler

from LHCbDIRAC.BookkeepingSystem.Client.BKQuery import BKQuery
from LHCbDIRAC.BookkeepingSystem.Client.BookkeepingClient import BookkeepingClient
from LHCbDIRAC.DataManagementSystem.Client.DMScript import ProgressBar
from LHCbDIRAC.TransformationSystem.Client.TransformationClient import TransformationClient

# FIXME: this is quite dirty, what should be checked is exactly what it is done
prodsWithMerge = ("MCSimulation", "MCFastSimulation", "DataStripping", "MCStripping", "DataSwimming", "WGProduction")


def getFileDescendants(transID, lfns, transClient=None, dm=None, bkClient=None, descendantsDepth=None):
    """Function that returns the list of descendants from BKK

    Args:
        transID (str, int): transformationID
        lfns (str, list, dict): a string for a single lfn, a list of strings, or a dict with lfns as keys

    Returns:
        dict: a dictionary of files with descendants (lfn as key)

    Examples:
        >>> getFileDescendants(55032, ['/lhcb/LHCb/anLFN_1.dst', '/lhcb/LHCb/anLFN_2.dst',
                                       '/lhcb/LHCb/anLFN_3_NODESCENDANTS.dst'])
        {'/lhcb/LHCb/anLFN_1.dst': ['/lhcb/validation/desc_1.PIDCALIB.mdst',
                                    '/lhcb/validation/desc_1.pidcalib.root'],
        {'/lhcb/LHCb/anLFN_2.dst': ['/lhcb/validation/desc_2.PIDCALIB.mdst',
                                    '/lhcb/validation/desc_2.pidcalib.root'],

    """
    cc = ConsistencyChecks(interactive=False, transClient=transClient, dm=dm, bkClient=bkClient)
    if descendantsDepth is not None:
        cc.descendantsDepth = descendantsDepth
    else:
        cc.descendantsDepth = 1
    cc.prod = transID
    cc.fileType = []
    cc.fileTypesExcluded = Operations().getValue("DataConsistency/IgnoreDescendantsOfType", [])
    savedLevel = gLogger.getLevel()
    gLogger.setLevel("FATAL")
    result = cc.getDescendants(lfns)
    # Files with descendants
    descendants = result[0]
    # Add files with multiple descendants
    descendants.update(result[2])
    gLogger.setLevel(savedLevel)
    return descendants


class ConsistencyChecks(DiracConsistencyChecks):
    """LHCb extension to ConsistencyInspector"""

    def __init__(self, interactive=True, transClient=None, dm=None, bkClient=None, fc=None):
        """c'tor"""
        super(ConsistencyChecks, self).__init__(interactive, transClient, dm, fc)

        self.dmsHelpers = DMSHelpers()
        self.bkClient = BookkeepingClient() if bkClient is None else bkClient
        self.transClient = TransformationClient() if transClient is None else transClient

        # Base elements from which to start the consistency checks
        self._prod = 0
        self._bkQuery = None
        self._fileType = []
        self._fileTypesExcluded = []
        self._lfns = []
        self._status = None
        self._seList = []
        self._verbose = False
        self.noFC = False
        self.directories = []
        self.descendantsDepth = 10
        self.ancestorsDepth = 10

        # Results of the checks
        self.existLFNsBKRepNo = {}
        self.absentLFNsBKRepNo = []
        self.existLFNsBKRepYes = []
        self.absentLFNsBKRepYes = []
        self.existLFNsNotInBK = []
        self.absentLFNsNotInBK = []
        self.filesInBKNotInTS = []

        self.inBKNotInFC = []
        self.inFCNotInBK = []

        self.removedFiles = []
        self.inFailover = []

        self.absentLFNsInFC = []
        self.inSEbutNotInFC = {}
        self.notRegisteredAtSE = {}
        self.existLFNsNoSE = {}
        self.existLFNsBadReplicas = {}
        self.existLFNsBadFiles = {}
        self.existLFNsNotExisting = {}
        self.commonAncestors = {}
        self.multipleDescendants = {}
        self.ancestors = {}

        self._verbose = False
        self._seList = None

    def __logVerbose(self, msg, msg1=""):
        if self._verbose:
            newMsg = "[ConsistencyChecks] " + ("[%s] " % str(self.prod)) if self.prod else ""
            # Add that prefix to all lines of the message
            newMsg1 = msg1.replace("\n", "\n" + newMsg)
            newMsg += msg.replace("\n", "\n" + newMsg)
            gLogger.notice(newMsg, newMsg1)
        else:
            gLogger.verbose(msg, msg1)

    ################################################################################

    def __getLFNsFromBK(self, checkAll=False):
        """
        Get list of LFNs with gotReplica No and Yes
        """
        lfnsReplicaNo, lfnsReplicaYes = (0, 0)
        if self.lfns:
            lfnsNotInBK, lfnsReplicaNo, lfnsReplicaYes = self._getBKMetadata(self.lfns)
            lfnsReplicaNo = list(lfnsReplicaNo) + lfnsNotInBK
        else:
            bkQuery = self.__getBKQuery()
            gLogger.notice("Getting files for BK query %s..." % str(bkQuery))
            if checkAll:
                lfnsReplicaNo = self._getBKFiles(bkQuery, "No")
            lfnsReplicaYes = self._getBKFiles(bkQuery, "Yes")
        return lfnsReplicaNo, lfnsReplicaYes

    def checkBK2FC(self, checkAll):
        """Starting from the BK, check if the FileCatalog has consistent information (BK -> FileCatalog)

        Works either when the bkQuery is free, or when it is made using a transformation ID
        """
        lfnsReplicaNo, lfnsReplicaYes = self.__getLFNsFromBK(checkAll)

        if self.lfns:
            self.__logVerbose("Checking the File Catalog for those files with BK ReplicaFlag = No")
            self.existLFNsBKRepNo, self.absentLFNsBKRepNo = self.getReplicasPresence(lfnsReplicaNo)
            self.__logVerbose("Checking the File Catalog for those files with BK ReplicaFlag = Yes")
            self.existLFNsBKRepYes, self.absentLFNsBKRepYes = self.getReplicasPresence(lfnsReplicaYes)
        elif self.transType not in prodsWithMerge:
            # Merging and Reconstruction
            # In principle few files without replica flag, check them in FC
            if checkAll:
                self.__logVerbose("Checking the File Catalog for those files with BK ReplicaFlag = No")
                self.existLFNsBKRepNo, self.absentLFNsBKRepNo = self.getReplicasPresence(lfnsReplicaNo)
            self.__logVerbose("Checking the File Catalog for those files with BK ReplicaFlag = Yes")
            self.existLFNsBKRepYes, self.absentLFNsBKRepYes = self.getReplicasPresenceFromDirectoryScan(lfnsReplicaYes)

        else:
            # prodsWithMerge
            # In principle most files have no replica flag, start from the File Catalog files with replicas
            if checkAll:
                self.__logVerbose("Checking the File Catalog for those files with BK ReplicaFlag = No")
                self.existLFNsBKRepNo, self.absentLFNsNotInBK = self.getReplicasPresenceFromDirectoryScan(lfnsReplicaNo)
            self.__logVerbose("Checking the File Catalog for those files with BK ReplicaFlag = Yes")
            self.existLFNsBKRepYes, self.absentLFNsBKRepYes = self.getReplicasPresence(lfnsReplicaYes)

        if checkAll and self.existLFNsBKRepNo:
            msg = "%d files have ReplicaFlag = No, but %d are in the FC" % (
                len(lfnsReplicaNo),
                len(self.existLFNsBKRepNo),
            )
            if self.transType:
                msg = "For prod %s of type %s, " % (self.prod, self.transType) + msg
            gLogger.info(msg)

        if self.absentLFNsBKRepYes:
            msg = "%d files have ReplicaFlag = Yes, but %d are not in the FC" % (
                len(lfnsReplicaYes),
                len(self.absentLFNsBKRepYes),
            )
            if self.transType:
                msg = "For prod %s of type %s, " % (self.prod, self.transType) + msg
            gLogger.info(msg)

        ################################################################################

    def _getBKFiles(self, bkQuery, replicaFlag="Yes"):
        """Helper function - get files from BK, first constructing the bkQuery"""
        visibility = bkQuery.isVisible()
        if self.transType:
            visibility = "Yes" if self.transType not in prodsWithMerge else "All"
        bkQuery.setVisible("All")
        bkQueryRes = BKQuery(bkQuery, visible=visibility)
        bkQueryRes.setOption("ReplicaFlag", replicaFlag)
        startTime = time.time()
        lfnsRes = bkQueryRes.getLFNs(printOutput=False)
        if not lfnsRes:
            gLogger.info("No files found with replica flag = %s" % replicaFlag)
        else:
            gLogger.info(
                "Found %d files with replica flag = %s (%.1f seconds)"
                % (len(lfnsRes), replicaFlag, time.time() - startTime)
            )

        return lfnsRes

    def __getBKQuery(self, fromTS=False):
        """get the bkQuery to be used"""
        bkQuery = None
        if fromTS:
            res = self.transClient.getBookkeepingQuery(self.prod)
            if not res["OK"]:
                raise ValueError(res["Message"])
            bkQuery = BKQuery(res["Value"])
        else:
            if self.bkQuery:
                bkQuery = self.bkQuery
            if self.prod:
                # If production is specificed, the visibility flag is ignored
                if not self.bkQuery:
                    bkQuery = BKQuery(prods=self.prod, fileTypes=self.fileType, visible=None)
                else:
                    bkQuery = BKQuery(self.bkQuery.setOption("Production", self.prod), visible=None)
            if not bkQuery:
                raise ValueError("Need to specify either the bkQuery or a production id")

        return bkQuery

    ################################################################################

    def getReplicasPresence(self, lfns, ignoreFailover=False, typeStr="files"):
        """get the replicas using the standard DataManager.getReplicas()"""
        present = set()
        notPresent = set()
        if not lfns:
            return [], []
        lfns = set(lfns)

        chunkSize = 100
        if not ignoreFailover:
            progressBar = ProgressBar(
                len(lfns),
                title="Checking replicas for %d %s" % (len(lfns), typeStr),
                chunk=chunkSize,
                interactive=self.interactive,
            )
        else:
            progressBar = None
        for chunk in breakListIntoChunks(lfns, chunkSize):
            if progressBar:
                progressBar.loop()
            for _ in range(1, 10):
                res = self.dataManager.getReplicas(chunk, getUrl=False)
                if res["OK"]:
                    success = res["Value"]["Successful"]
                    if ignoreFailover:
                        present.update(
                            lfn
                            for lfn, seList in success.items()
                            for se in seList
                            if not self.dmsHelpers.isSEFailover(se)
                        )
                    else:
                        present.update(success)
                    self.cachedReplicas.update(success)
                    notPresent.update(res["Value"]["Failed"])
                    break
                else:
                    time.sleep(0.1)
        if progressBar:
            progressBar.endLoop("found %d files with replicas and %d without" % (len(present), len(notPresent)))

        if notPresent:
            self.__logVerbose("Files without replicas:", "\n".join([""] + sorted(notPresent)))
        return list(present), list(notPresent)

    ################################################################################

    def getReplicasPresenceFromDirectoryScan(self, lfns, typeStr="files"):
        """Get replicas scanning the directories. Might be faster."""

        dirs = {}
        present = []
        notPresent = []
        compare = True

        for lfn in lfns:
            dirN = os.path.dirname(lfn)
            if lfn == dirN + "/":
                compare = False
            dirs.setdefault(dirN, []).append(lfn)

        if compare:
            title = "Checking File Catalog for %d %s from %d directories " % (len(lfns), typeStr, len(dirs))
        else:
            title = "Getting files from %d directories " % len(dirs)
        progressBar = ProgressBar(len(dirs), title=title)

        for dirN in sorted(dirs):
            progressBar.loop()
            startTime1 = time.time()
            lfnsFound = self._getFilesFromDirectoryScan(dirN)
            self.__logVerbose("Obtained %d files in %.1f seconds" % (len(lfnsFound), time.time() - startTime1))
            if compare:
                pr, notPr = self.__compareLFNLists(dirs[dirN], lfnsFound)
                notPresent += notPr
                present += pr
            else:
                present += lfnsFound

        progressBar.endLoop("found %d files with replicas and %d without" % (len(present), len(notPresent)))
        return present, notPresent

    ################################################################################

    def __compareLFNLists(self, lfns, lfnsFound):
        """return files in both lists and files in lfns and not in lfnsFound"""
        present = []
        notPresent = lfns
        startTime = time.time()
        self.__logVerbose("Comparing list of %d LFNs with second list of %d" % (len(lfns), len(lfnsFound)))
        if lfnsFound:
            # print sorted( lfns )
            # print sorted( lfnsFound )
            setLfns = set(lfns)
            setLfnsFound = set(lfnsFound)
            present = list(setLfns & setLfnsFound)
            notPresent = list(setLfns - setLfnsFound)
            # print sorted( present )
            # print sorted( notPresent )
        self.__logVerbose("End of comparison: %.1f seconds" % (time.time() - startTime))
        return present, notPresent

    def _getFilesFromDirectoryScan(self, dirs):
        """calls dm.getFilesFromDirectory"""

        level = gLogger.getLevel()
        gLogger.setLevel("FATAL")
        res = self.dataManager.getFilesFromDirectory(dirs)
        gLogger.setLevel(level)
        if not res["OK"]:
            if "No such file or directory" not in res["Message"]:
                gLogger.error("Error getting files from directories %s:" % dirs, res["Message"])
            return []
        if res["Value"]:
            lfnsFound = res["Value"]
        else:
            lfnsFound = []

        return lfnsFound

    ################################################################################

    def checkTS2BK(self):
        """Check if lfns has descendants (TransformationFiles -> BK)"""
        if not self.prod:
            raise ValueError("You need a transformationID")

        gLogger.notice("Getting files from the TransformationSystem...")
        startTime = time.time()
        processedLFNs, nonProcessedLFNs, statuses = self._getTSFiles()
        gLogger.notice(
            "Found %d processed files and %d non processed%s files (%.1f seconds)"
            % (
                len(processedLFNs),
                len(nonProcessedLFNs),
                " (%s)" % ",".join(statuses) if statuses else "",
                (time.time() - startTime),
            )
        )

        res = self.getDescendants(processedLFNs, status="processed")
        self.prcdWithDesc = res[0]
        self.prcdWithoutDesc = res[1]
        self.prcdWithMultDesc = res[2]
        self.descForPrcdLFNs = res[3]
        self.inFCNotInBK = res[4]
        self.inBKNotInFC = res[5]
        self.removedFiles = res[6]
        self.inFailover = res[7]

        res = self.getDescendants(nonProcessedLFNs, status="non-processed")
        self.nonPrcdWithDesc = res[0]
        self.nonPrcdWithoutDesc = res[1]
        self.nonPrcdWithMultDesc = res[2]
        self.descForNonPrcdLFNs = res[3]
        self.inFCNotInBK += res[4]
        self.inBKNotInFC += res[5]
        self.inFailover += res[7]

        prTuple = (self.prod, self.transType, len(processedLFNs))
        if self.prcdWithoutDesc:
            self.__logVerbose(
                "For prod %s of type %s, %d files are processed," % prTuple,
                "and %d of those do not have descendants" % len(self.prcdWithoutDesc),
            )

        if self.prcdWithMultDesc:
            self.__logVerbose(
                "For prod %s of type %s, %d files are processed," % prTuple,
                "and %d of those have multiple descendants: " % len(self.prcdWithMultDesc),
            )

        prTuple = (self.prod, self.transType, len(nonProcessedLFNs))
        if self.nonPrcdWithDesc:
            self.__logVerbose(
                "For prod %s of type %s, %d files are not processed," % prTuple,
                "but %d of those have descendants" % len(self.nonPrcdWithDesc),
            )

        if self.nonPrcdWithMultDesc:
            self.__logVerbose(
                "For prod %s of type %s, %d files are not processed," % prTuple,
                "but %d of those have multiple descendants: " % len(self.nonPrcdWithMultDesc),
            )

    ################################################################################

    def checkAncestors(self):
        """Check if a set of files don't share a common ancestor"""
        if self.lfns:
            files = self.lfns
            bkQuery = None
            fileType = []
        else:
            bkQuery = self.__getBKQuery()
            gLogger.notice("Getting files for BK query: %s" % bkQuery)
            fileType = bkQuery.getFileTypeList()
            files = self._getBKFiles(bkQuery)

        if len(fileType) == 1:
            fileTypes = {fileType[0]: set(files)}
            getFileType = False
        else:
            fileTypes = {}
            getFileType = True

        chunkSize = 10
        ancestors = {}
        listAncestors = []
        progressBar = ProgressBar(
            len(files),
            title="Getting ancestors for %d files" % len(files),
            chunk=chunkSize,
            interactive=self.interactive,
        )
        for lfnChunk in breakListIntoChunks(files, chunkSize):
            progressBar.loop()
            if getFileType:
                res = self.bkClient.getFileMetadata(lfnChunk)
                if not res["OK"]:
                    gLogger.fatal("Error getting files metadata", res["Message"])
                    DIRAC.exit(2)
                for lfn, metadata in res["Value"]["Successful"].items():
                    fileType = metadata.get("FileType")
                    if fileType is None:
                        gLogger.notice("File type unavailable for %s" % lfn, str(metadata))
                    fileTypes.setdefault(fileType, set()).add(lfn)
            res = self.bkClient.getFileAncestors(
                lfnChunk, depth=self.ancestorsDepth, replica=(self.ancestorsDepth == 10)
            )
            if not res["OK"]:
                gLogger.fatal("Error getting file ancestors", res["Message"])
                DIRAC.exit(2)
            for lfn, anc in res["Value"]["Successful"].items():
                ancestors[lfn] = [ancDict["FileName"] for ancDict in anc]
                if not getFileType:
                    listAncestors += ancestors[lfn]
        progressBar.endLoop()

        self.ancestors = ancestors
        self.commonAncestors = {}
        self.multipleDescendants = {}
        if not getFileType and len(listAncestors) == len(set(listAncestors)):
            gLogger.notice("Found %d ancestors, no common one" % len(listAncestors))
            return

        gLogger.notice("Found files with %d file types" % len(fileTypes))
        for fileType in fileTypes:
            lfns = fileTypes[fileType] & set(ancestors)
            gLogger.notice("File type %s, checking %d files" % (fileType, len(lfns)))
            listAncestors = []
            for lfn in lfns:
                listAncestors += ancestors[lfn]
            setAncestors = set(listAncestors)
            if len(listAncestors) == len(setAncestors):
                gLogger.notice("Found %d ancestors for file type %s, no common one" % (len(listAncestors), fileType))
                continue
            # There are common ancestors
            descendants = {}
            # Reverse the list of ancestors
            for lfn in lfns:
                for anc in ancestors[lfn]:
                    descendants.setdefault(anc, []).append(lfn)
            # Check if ancestor has more than one descendant
            for anc in sorted(descendants):
                if len(descendants[anc]) > 1:
                    desc = sorted(descendants[anc])
                    gLogger.notice("For ancestor %s, found %d descendants: %s" % (anc, len(desc), desc))
                    self.multipleDescendants[anc] = desc
                    self.commonAncestors.setdefault(",".join(sorted(desc)), []).append(anc)

    ################################################################################

    def _getTSFiles(self):
        """Helper function - get files from the TS"""

        selectDict = {"TransformationID": self.prod}
        if self._lfns:
            selectDict["LFN"] = self._lfns
        elif self._status:
            selectDict["Status"] = self._status
        elif self.runStatus and self.fromProd:
            res = self.transClient.getTransformationRuns({"TransformationID": self.fromProd, "Status": self.runStatus})
            if not res["OK"]:
                gLogger.error("Failed to get runs for transformation %d" % self.prod)
            else:
                if res["Value"]:
                    self.runsList.extend(
                        run["RunNumber"] for run in res["Value"] if run["RunNumber"] not in self.runsList
                    )
                    gLogger.notice(
                        "%d runs selected:" % len(res["Value"]), ",".join(str(run["RunNumber"]) for run in res["Value"])
                    )
                elif not self.runsList:
                    gLogger.notice("No runs selected, check completed")
                    DIRAC.exit(0)
        if not self._lfns and self.runsList:
            selectDict["RunNumber"] = self.runsList

        res = self.transClient.getTransformation(self.prod)
        if not res["OK"]:
            gLogger.error("Failed to find transformation %s" % self.prod)
            return [], [], []
        status = res["Value"]["Status"]
        if status not in ("Active", "Stopped", "Completed", "Idle"):
            gLogger.notice(
                "Transformation %s in status %s, will not check if files are processed" % (self.prod, status)
            )
            processedLFNs = []
            nonProcessedLFNs = []
            nonProcessedStatuses = []
            if self._lfns:
                processedLFNs = self._lfns
        else:
            res = self.transClient.getTransformationFiles(selectDict)
            if not res["OK"]:
                gLogger.error("Failed to get files for transformation %d" % self.prod, res["Message"])
                return [], [], []
            else:
                processedLFNs = [item["LFN"] for item in res["Value"] if item["Status"] == "Processed"]
                nonProcessedLFNs = [item["LFN"] for item in res["Value"] if item["Status"] != "Processed"]
                nonProcessedStatuses = list(
                    set(item["Status"] for item in res["Value"] if item["Status"] != "Processed")
                )

        return processedLFNs, nonProcessedLFNs, nonProcessedStatuses

    ################################################################################

    def __getDaughtersInfo(
        self, lfns, status, filesWithDescendants, filesWithoutDescendants, filesWithMultipleDescendants
    ):
        """Get BK information about daughers of lfns"""
        chunkSize = 20
        lfns = set(lfns)
        progressBar = ProgressBar(
            len(lfns),
            title="Now getting all daughters for %d %s mothers in production %d (depth %d)"
            % (len(lfns), status, self.prod, self.descendantsDepth),
            chunk=chunkSize,
            interactive=self.interactive,
        )
        daughtersBKInfo = {}
        for lfnChunk in breakListIntoChunks(lfns, chunkSize):
            progressBar.loop()
            while True:
                resChunk = self.bkClient.getFileDescendants(
                    lfnChunk, depth=self.descendantsDepth, production=self.prod, checkreplica=False
                )
                # If error, global or for some files, retry
                if resChunk["OK"] and not resChunk["Value"]["Failed"]:
                    # Key is ancestor, value is metadata dictionary of daughters
                    descDict = self._selectByFileType(resChunk["Value"]["WithMetadata"])
                    # Do the daughters have a replica flag in BK? Store file type as well... Key is daughter
                    daughtersBKInfo.update(
                        dict(
                            (lfn, (desc[lfn]["GotReplica"] == "Yes", desc[lfn]["FileType"]))
                            for desc in descDict.values()
                            for lfn in desc
                        )
                    )
                    # Count the daughters per file type (key is ancestor)
                    ft_count = self._getFileTypesCount(descDict)
                    for lfn in lfnChunk:
                        # Check if file has a daughter and how many per file type
                        if lfn in descDict:
                            # Assign the daughters list to the initial LFN
                            filesWithDescendants[lfn] = list(descDict[lfn])
                            # Is there a file type with more than one daughter of a given file type?
                            multi = dict((ft, ftc) for ft, ftc in ft_count[lfn].items() if ftc > 1)
                            if multi:
                                filesWithMultipleDescendants[lfn] = multi
                        else:
                            # No daughter, easy case!
                            filesWithoutDescendants[lfn] = None
                    break
                else:
                    progressBar.comment(
                        "Error getting daughters for %d files, retry" % len(lfnChunk), resChunk["Message"]
                    )
        prStr = ""
        if filesWithDescendants:
            nb = sum(len(desc) for desc in filesWithDescendants.values())
            prStr += "found %d descendants (%d unique) for %d files" % (
                nb,
                len(daughtersBKInfo),
                len(filesWithDescendants),
            )
        if filesWithoutDescendants:
            if not prStr:
                prStr = "found"
            else:
                prStr += " and"
            prStr += " no descendants for %d files" % len(filesWithoutDescendants)
        progressBar.endLoop(message=prStr)
        return daughtersBKInfo

    def getDescendants(self, lfns, status=""):
        """get the descendants of a list of LFN (for the production)

        Args:
            lfns (str, list, dict): a string for a single lfn, a list of strings, or a dict with lfns as keys
        """
        if isinstance(lfns, six.string_types):
            lfns = [lfns]
        elif isinstance(lfns, dict):
            lfns = list(lfns)
        filesWithDescendants = {}
        filesWithoutDescendants = {}
        filesWithMultipleDescendants = {}
        fileTypesExcluded = Operations().getValue("DataConsistency/IgnoreDescendantsOfType", [])
        if self.fileType:
            fileTypesExcluded = list(set(fileTypesExcluded) - set(self.fileType))
        inFCNotInBK = []
        inBKNotInFC = []
        allDaughters = []
        removedFiles = []
        inFailover = []
        if not lfns:
            return (
                filesWithDescendants,
                filesWithoutDescendants,
                filesWithMultipleDescendants,
                allDaughters,
                inFCNotInBK,
                inBKNotInFC,
                removedFiles,
                inFailover,
            )

        daughtersBKInfo = self.__getDaughtersInfo(
            lfns, status, filesWithDescendants, filesWithoutDescendants, filesWithMultipleDescendants
        )
        for daughter in list(daughtersBKInfo):
            # Ignore the daughters that have a type to ignore
            if daughtersBKInfo[daughter][1] in fileTypesExcluded:
                daughtersBKInfo.pop(daughter)

        # This is the list of all daughters, sets will contain unique entries
        setAllDaughters = set(daughtersBKInfo)
        allDaughters = list(setAllDaughters)
        inBK = set(lfn for lfn in setAllDaughters if daughtersBKInfo[lfn][0])
        setRealDaughters = set()
        # Now check whether these daughters files have replicas or have descendants that have replicas
        chunkSize = 100 if self.transType == "DataStripping" and len(self.fileType) > 1 else 500
        if filesWithDescendants:
            # First check in LFC the presence of daughters
            if not self.noFC:
                present, notPresent = (
                    self.getReplicasPresenceFromDirectoryScan(allDaughters, typeStr="daughters")
                    if len(allDaughters) > 10 * chunkSize and len(inBK) < len(allDaughters) / 2
                    else self.getReplicasPresence(allDaughters, typeStr="daughters")
                )
                setPresent = set(present)
                setNotPresent = set(notPresent)
            else:
                setPresent = inBK
                setNotPresent = setAllDaughters - inBK

            setRealDaughters = setPresent
            # Now check consistency between BK and FC for daughters
            inBKNotInFC = list(inBK & setNotPresent)
            inFCNotInBK = list(setPresent - inBK)

            # Now check whether the daughters without replica have a descendant
            if setNotPresent:
                chunkSize = 20 if self.transType == "DataStripping" and len(self.fileType) > 1 else 50
                progressBar = ProgressBar(
                    len(setNotPresent),
                    title="Now getting descendants from %d daughters without replicas" % len(setNotPresent),
                    chunk=chunkSize,
                    interactive=self.interactive,
                )
                # Get existing descendants of notPresent daughters
                notPresentDescendants = {}
                for lfnChunk in breakListIntoChunks(setNotPresent, chunkSize):
                    progressBar.loop()
                    while True:
                        res = self.bkClient.getFileDescendants(lfnChunk, depth=99, checkreplica=True)
                        if res["OK"]:
                            # Exclude ignored file types, but select any other file type, key is daughters
                            notPresentDescendants.update(res["Value"]["WithMetadata"])
                            break
                        else:
                            progressBar.comment(
                                "Error getting descendants for %d files, retry" % len(lfnChunk), res["Message"]
                            )
                uniqueDescendants = set(lfn for desc in notPresentDescendants.values() for lfn in desc)
                progressBar.endLoop(
                    message="found %d descendants of %d daughters"
                    % (len(uniqueDescendants), len(notPresentDescendants))
                )
                # Check if descendants have a replica in the FC
                setDaughtersWithDesc = set()
                if uniqueDescendants:
                    _, notPresent = self.getReplicasPresence(uniqueDescendants)
                    inBKNotInFC += notPresent
                    # Remove descendants that are not in FC, and if no descendants remove ancestor as well
                    for anc in list(notPresentDescendants):
                        for desc in list(notPresentDescendants[anc]):
                            if desc in notPresent:
                                notPresentDescendants[anc].pop(desc)
                        if not notPresentDescendants[anc]:
                            notPresentDescendants.pop(anc)
                    if notPresentDescendants:
                        setDaughtersWithDesc = set(
                            self._selectByFileType(
                                notPresentDescendants, fileTypes=[""], fileTypesExcluded=fileTypesExcluded
                            )
                        )

                progressBar = ProgressBar(
                    len(filesWithDescendants),
                    title="Now establishing final list of existing descendants for %d mothers"
                    % len(filesWithDescendants),
                    step=chunkSize,
                    interactive=self.interactive,
                )
                for lfn in set(filesWithDescendants):
                    setDaughters = set(filesWithDescendants[lfn])
                    progressBar.loop()
                    # If all daughters are present, all is easy...
                    daughtersNotPresent = setDaughters & setNotPresent
                    if not daughtersNotPresent:
                        continue
                    self.__logVerbose("Mother file:", lfn)
                    self.__logVerbose("Daughters:\n", "\n".join(sorted(filesWithDescendants[lfn])))
                    self.__logVerbose("Not present daughters:\n", "\n".join(sorted(daughtersNotPresent)))
                    notPresentWithDesc = daughtersNotPresent & setDaughtersWithDesc
                    if notPresentWithDesc:
                        self.__logVerbose(" but with descendants:\n", "\n".join(sorted(notPresentWithDesc)))
                    else:
                        self.__logVerbose(" none of them has descendants")
                    # Some daughters may have a replica though, take them into account
                    daughtersWithReplica = setDaughters & setPresent
                    # and add those without a replica but that have  a descendant with replica
                    realDaughters = daughtersWithReplica | notPresentWithDesc
                    if realDaughters:
                        self.__logVerbose("Real Daughters:\n", "\n".join(sorted(realDaughters)))
                    else:
                        self.__logVerbose("No real daughters found")
                    # descToCheck: dictionary with key = daughter and value = dictionary of file type counts
                    daughtersDict = dict(
                        (daughter, {daughter: {"FileType": daughtersBKInfo[daughter][1]}}) for daughter in realDaughters
                    )
                    descToCheck = self._getFileTypesCount(daughtersDict)

                    # Update the result dictionaries according to the final set of descendants
                    if not descToCheck:
                        # Mother has no descendant
                        self.__logVerbose("%s has no real descendants" % lfn)
                        filesWithMultipleDescendants.pop(lfn, None)
                        filesWithDescendants.pop(lfn, None)
                        filesWithoutDescendants[lfn] = None
                    else:
                        self.__logVerbose("Descendants to check:\n", "\n".join(sorted(descToCheck)))
                        filesWithDescendants[lfn] = sorted(realDaughters)
                        setRealDaughters.update(realDaughters)
                        # Count the descendants by file type
                        ft_count = {}
                        for counts in descToCheck.values():
                            for ft in counts:
                                ft_count[ft] = ft_count.setdefault(ft, 0) + counts.get(ft, 0)
                        multi = dict((ft, ftc) for ft, ftc in ft_count.items() if ftc > 1)
                        # Mother has at least one real descendant
                        # Now check whether there are more than one descendant of the same file type
                        if not multi:
                            filesWithMultipleDescendants.pop(lfn, None)
                            prStr = "single"
                        else:
                            filesWithMultipleDescendants[lfn] = multi
                            prStr = "multiple"
                        self.__logVerbose("Found %s descendants" % prStr)
                progressBar.endLoop(message="found %d files with existing descendants" % len(filesWithDescendants))
        # print 'Final multiple descendants', filesWithMultipleDescendants

        # File files without descendants don't exist, not important
        if filesWithoutDescendants:
            present, removedFiles = self.getReplicasPresence(list(filesWithoutDescendants), ignoreFailover=True)
            filesWithoutDescendants = dict.fromkeys(present)
        else:
            removedFiles = []

        # Remove files with multiple descendants from files with descendants
        for lfn in filesWithMultipleDescendants:
            filesWithDescendants.pop(lfn, None)
        # For files in FC and not in BK, ignore if they are not active
        if inFCNotInBK:
            progressBar = ProgressBar(
                len(inFCNotInBK),
                title="Checking Failover for %d descendants found in FC and not in BK" % len(inFCNotInBK),
                step=1,
                interactive=self.interactive,
            )
            notInFailover, _notFound = self.getReplicasPresence(inFCNotInBK, ignoreFailover=True)
            inFailover = list(set(inFCNotInBK) - set(notInFailover))
            progressBar.endLoop(message="found %d in Failover" % len(inFailover))
            inFCNotInBK = notInFailover
        return (
            filesWithDescendants,
            filesWithoutDescendants,
            filesWithMultipleDescendants,
            list(setRealDaughters),
            inFCNotInBK,
            inBKNotInFC,
            removedFiles,
            inFailover,
        )

    ################################################################################

    def _selectByFileType(self, lfnDict, fileTypes=None, fileTypesExcluded=None):
        """Select only those files from the values of lfnDict that have a certain type"""
        if not lfnDict:
            return {}
        if not fileTypes:
            fileTypes = self.fileType
        if not fileTypesExcluded:
            fileTypesExcluded = self.fileTypesExcluded
        else:
            fileTypesExcluded += [ft for ft in self.fileTypesExcluded if ft not in fileTypesExcluded]
        # lfnDict is a dictionary of dictionaries including the metadata, create a deep copy to get modified
        ancDict = copy.deepcopy(lfnDict)
        if fileTypes == [""]:
            fileTypes = []
        if fileTypes:
            fileTypesExcluded = list(set(fileTypesExcluded) - set(fileTypes))
        # and loop on the original dictionaries
        for ancestor in lfnDict:
            for desc in lfnDict[ancestor]:
                ft = lfnDict[ancestor][desc]["FileType"]
                if ft in fileTypesExcluded or (fileTypes and ft not in fileTypes):
                    ancDict[ancestor].pop(desc)
            if len(ancDict[ancestor]) == 0:
                ancDict.pop(ancestor)
        return ancDict

    @staticmethod
    def _getFileTypesCount(lfnDict):
        """return file types count"""
        ft_dict = {}
        for ancestor in lfnDict:
            t_dict = {}
            for desc in lfnDict[ancestor]:
                ft = lfnDict[ancestor][desc]["FileType"]
                t_dict[ft] = t_dict.setdefault(ft, 0) + 1
            ft_dict[ancestor] = t_dict

        return ft_dict

    def __getLFNsFromFC(self):
        if not self.lfns:
            directories = []
            for dirName in self.__getDirectories():
                if not dirName.endswith("/"):
                    dirName += "/"
                directories.append(dirName)
            present, notPresent = self.getReplicasPresenceFromDirectoryScan(directories)
        else:
            present, notPresent = self.getReplicasPresence(self.lfns)
        return present, notPresent

    def _checkFilesInSE(self, notPresent, seList):
        foundInSE = {}
        for se in seList:
            seObj = StorageElement(se)
            res = seObj.exists(notPresent)
            if not res["OK"]:
                gLogger.error("Error checking file in SE", res["Message"])
            else:
                for lfn, ex in res["Value"]["Successful"].items():
                    if ex:
                        foundInSE.setdefault(lfn, []).append(se)
        return foundInSE

    def checkFC2BK(self, bkCheck=True):
        """check that files present in the FC are also in the BK"""
        present, notPresent = self.__getLFNsFromFC()
        foundInSE = {}
        if not self.lfns:
            prStr = " are in the FC but"
        else:
            if notPresent and self._seList:
                gLogger.notice("Found %d files not in FC, check if they are in specified SEs" % len(notPresent))
                foundInSE = self._checkFilesInSE(notPresent, self._seList)
                if foundInSE:
                    self.inSEbutNotInFC = foundInSE
            elif not present:
                if bkCheck:
                    gLogger.notice("No files are in the FC, no check in the BK. Use dirac-dms-check-bkk2fc instead")
                return
            prStr = ""

        if bkCheck and (present or foundInSE):
            res = self._getBKMetadata(present + list(foundInSE))
            self.existLFNsNotInBK = res[0]
            self.existLFNsBKRepNo = res[1]
            self.existLFNsBKRepYes = res[2]
            msg = ""
            if self.transType:
                msg = "For prod %s of type %s, " % (self.prod, self.transType)
            if self.existLFNsBKRepNo:
                gLogger.warn("%s %d files%s have replica = NO in BK" % (msg, len(self.existLFNsBKRepNo), prStr))
            if self.existLFNsNotInBK:
                gLogger.warn("%s %d files%s not in BK" % (msg, len(self.existLFNsNotInBK), prStr))
        else:
            self.existLFNsBKRepYes = present

        ########################################################################

    def __getDirectories(self):
        """get the directories where to look into (they are either given, or taken from the transformation ID"""
        if self.directories:
            directories = []
            printout = False
            for directory in self.directories:
                if not directory.endswith("..."):
                    directories.append(directory)
                else:
                    printout = True
                    topDir = os.path.dirname(directory)
                    res = self.fileCatalog.listDirectory(topDir)
                    if not res["OK"]:
                        raise RuntimeError("Error listing directory: " + res["Message"])
                    else:
                        matchDir = directory.split("...")[0]
                        directories += [
                            d
                            for d in res["Value"]["Successful"].get(topDir, {}).get("SubDirs", [])
                            if d.startswith(matchDir)
                        ]
            if printout:
                gLogger.notice("Expanded list of %d directories:\n%s" % (len(directories), "\n".join(directories)))
            return directories
        try:
            bkQuery = self.__getBKQuery()
        except ValueError:
            bkQuery = None
        if bkQuery and set(bkQuery.getQueryDict()) - {"Visible", "Production", "FileType"}:
            return bkQuery.getDirs()
        if self.prod:
            if bkQuery:
                fileType = bkQuery.getFileTypeList()
            else:
                fileType = []
            res = self.transClient.getTransformationParameters(self.prod, ["OutputDirectories"])
            if not res["OK"]:
                raise RuntimeError("Error getting transformation parameters: " + res["Message"])
            else:
                directories = []
                dirList = res["Value"]
                if isinstance(dirList, six.string_types) and dirList[0] == "[" and dirList[-1] == "]":
                    dirList = ast.literal_eval(dirList)
                for dirName in dirList:
                    # There is a shortcut when multiple streams are used, only the stream name is repeated!
                    if ";" in dirName:
                        items = dirName.split(";")
                        baseDir = os.path.dirname(items[0])
                        items[0] = os.path.basename(items[0])
                        lastItems = items[-1].split("/")
                        items[-1] = lastItems[0]
                        if len(lastItems) > 1:
                            suffix = "/".join(lastItems[1:])
                        else:
                            suffix = ""
                        for it in items:
                            directories.append(os.path.join(baseDir, it, suffix))
                    else:
                        if dirName.endswith("/0"):
                            dirName = dirName.replace("/0", "/%08d" % int(self.prod))
                        ftOK = True if not fileType else False
                        for ft in fileType:
                            if ft in dirName:
                                ftOK = True
                                break
                        if ftOK:
                            directories.append(dirName)
                return directories
        else:
            raise RuntimeError("No files found: you need to specify either the directories or a production ID")

        ########################################################################

    def _getBKMetadata(self, lfns):
        """get metadata (i.e. replica flag) of a list of LFNs"""
        missingLFNs = []
        noFlagLFNs = {}
        okLFNs = []
        chunkSize = 1000
        progressBar = ProgressBar(
            len(lfns),
            title="Getting %d files metadata from BK" % len(lfns),
            chunk=chunkSize,
            interactive=self.interactive,
        )
        for lfnChunk in breakListIntoChunks(lfns, chunkSize):
            progressBar.loop()
            while True:
                res = self.bkClient.getFileMetadata(lfnChunk)
                if not res["OK"]:
                    gLogger.error("\nCan't get the BK metadata, retry: ", res["Message"])
                else:
                    metadata = res["Value"]["Successful"]
                    missingLFNs += [lfn for lfn in lfnChunk if lfn not in metadata]
                    noFlagLFNs.update(
                        dict(
                            (lfn, metadata[lfn]["RunNumber"]) for lfn in metadata if metadata[lfn]["GotReplica"] == "No"
                        )
                    )
                    okLFNs += [lfn for lfn in metadata if metadata[lfn]["GotReplica"] == "Yes"]
                    break
        progressBar.endLoop()
        return missingLFNs, noFlagLFNs, okLFNs

    ################################################################################

    def checkBK2TS(self):
        """check that files present in the BK are also in the FC (re-check of BKWatchAgent)"""
        bkQuery = self.__getBKQuery(fromTS=True)
        lfnsReplicaYes = self._getBKFiles(bkQuery)
        proc, nonProc, _statuses = self._getTSFiles()
        self.filesInBKNotInTS = list(set(lfnsReplicaYes) - set(proc + nonProc))
        if self.filesInBKNotInTS:
            gLogger.error(
                "There are %d files in BK that are not in TS: %s"
                % (len(self.filesInBKNotInTS), str(self.filesInBKNotInTS))
            )

    ################################################################################

    def checkFC2SE(self, bkCheck=True):  # pylint: disable=arguments-differ
        self.checkFC2BK(bkCheck=bkCheck)
        if self.existLFNsBKRepYes or self.existLFNsBKRepNo:
            repDict = self.compareChecksum(self.existLFNsBKRepYes + list(self.existLFNsBKRepNo))
            self.existLFNsNoSE = repDict["MissingReplica"]
            self.existLFNsNotExisting = repDict["MissingAllReplicas"]
            self.existLFNsBadReplicas = repDict["SomeReplicasCorrupted"]
            self.existLFNsBadFiles = repDict["AllReplicasCorrupted"]
            self.notRegisteredAtSE = repDict["NotRegisteredAtSE"]

    def checkSE(self, seList):
        """
        Check if the provided files are registered in the FC in a given list of SEs
        """
        lfnsReplicaNo, lfnsReplicaYes = self.__getLFNsFromBK()
        if not lfnsReplicaNo and not lfnsReplicaYes:
            lfns, notPresent = self.__getLFNsFromFC()
        else:
            lfns = lfnsReplicaYes
            notPresent = []
        gLogger.notice("Checking presence of %d files at %s" % (len(lfns), ", ".join(seList)))
        replicaRes = self.dataManager.getReplicas(lfns)
        if not replicaRes["OK"]:
            gLogger.error("Error getting replicas", replicaRes["Message"])
            return
        seSet = set(seList)
        success = replicaRes["Value"]["Successful"]
        self.absentLFNsInFC = sorted(set(notPresent) | set(replicaRes["Value"]["Failed"]))
        self.existLFNsNoSE = [lfn for lfn in success if not seSet & set(success[lfn])]

    def compareChecksum(self, lfns):
        """compare the checksum of the file in the FC and the checksum of the physical replicas.
        Returns a dictionary containing 3 sub-dictionaries: one with files with missing PFN, one with
        files with all replicas corrupted, and one with files with some replicas corrupted and at least
        one good replica
        """
        retDict = {
            "AllReplicasCorrupted": {},
            "SomeReplicasCorrupted": {},
            "MissingReplica": {},
            "MissingAllReplicas": {},
            "NoReplicas": {},
            "NotRegisteredAtSE": {},
        }

        chunkSize = 100
        replicas = {}
        setLfns = set(lfns)
        cachedLfns = setLfns & set(self.cachedReplicas)
        for lfn in cachedLfns:
            replicas[lfn] = self.cachedReplicas[lfn]
        lfnsLeft = setLfns - cachedLfns
        if lfnsLeft:
            progressBar = ProgressBar(
                len(lfnsLeft),
                title="Get replicas for %d files" % len(lfnsLeft),
                chunk=chunkSize,
                interactive=self.interactive,
            )
            for lfnChunk in breakListIntoChunks(lfnsLeft, chunkSize):
                progressBar.loop()
                replicasRes = self.dataManager.getReplicas(lfnChunk, getUrl=False)
                if not replicasRes["OK"]:
                    raise RuntimeError("Error getting replicas:  " + replicasRes["Message"])
                replicasRes = replicasRes["Value"]
                if replicasRes["Failed"]:
                    retDict["NoReplicas"].update(replicasRes["Failed"])
                replicas.update(replicasRes["Successful"])
            progressBar.endLoop()

        # Reduce the set of files to those at requested SEs if specified
        otherReplicas = []
        if self._seList:
            notAtSE = []
            for lfn, ses in replicas.items():
                if set(ses) - self._seList:
                    otherReplicas.append(lfn)
                replicas[lfn] = set(ses) & self._seList
                if not replicas[lfn]:
                    notAtSE.append(lfn)
            if notAtSE:
                gLogger.notice(
                    "%d files are not registered at requested SEs, check if they exist in SE..." % len(notAtSE)
                )
                foundInSE = self._checkFilesInSE(notAtSE, self._seList)
                if foundInSE:
                    gLogger.notice(
                        "Of these, %d files were found at requested SEs but are not registered" % len(foundInSE)
                    )
                    retDict["NotRegisteredAtSE"] = foundInSE
                else:
                    gLogger.notice("None of them were found at requested SEs, ignore them")
                for lfn in [lfn for lfn in notAtSE if lfn not in foundInSE]:
                    del replicas[lfn]

        if not replicas:
            return retDict
        progressBar = ProgressBar(
            len(replicas),
            title="Get FC metadata for %d files to be checked: " % len(replicas),
            chunk=chunkSize,
            interactive=self.interactive,
        )
        metadata = {}
        for lfnChunk in breakListIntoChunks(replicas, chunkSize):
            progressBar.loop()
            res = self.fileCatalog.getFileMetadata(lfnChunk)
            if not res["OK"]:
                raise RuntimeError("Error getting file metadata: " + res["Message"])
            metadata.update(res["Value"]["Successful"])
        progressBar.endLoop()

        gLogger.notice("Check existence and compare checksum file by file...")
        csDict = {}
        seFiles = {}
        # Reverse the LFN->SE dictionary
        nReps = 0
        for lfn in replicas:
            csDict.setdefault(lfn, {})["LFCChecksum"] = metadata.get(lfn, {}).get("Checksum")
            for se in replicas[lfn]:
                seFiles.setdefault(se, []).append(lfn)
                nReps += 1

        gLogger.notice("Getting checksum of %d replicas in %d SEs" % (nReps, len(seFiles)))
        checkSum = {}
        lfnNotExisting = {}
        lfnNoInfo = {}
        logLevel = gLogger.getLevel()
        gLogger.setLevel("FATAL")
        for num, se in enumerate(sorted(seFiles)):
            progressBar = ProgressBar(
                len(seFiles[se]),
                title="%d. At %s (%d files)" % (num, se, len(seFiles[se])),
                chunk=chunkSize,
                interactive=self.interactive,
            )
            oSe = StorageElement(se)
            errMsg = None
            notFound = 0
            for surlChunk in breakListIntoChunks(seFiles[se], chunkSize):
                progressBar.loop()
                metadata = oSe.getFileMetadata(surlChunk)
                if not metadata["OK"]:
                    errMsg = "Error: getFileMetadata returns %s. Ignore those replicas" % (metadata["Message"])
                    progressBar.comment(errMsg)
                    # Remove from list of replicas as we don't know whether it is OK or not
                    for lfn in seFiles[se]:
                        lfnNoInfo.setdefault(lfn, []).append(se)
                else:
                    metadata = metadata["Value"]
                    # print metadata
                    notFound += len(metadata["Failed"])
                    for lfn in metadata["Failed"]:
                        lfnNotExisting.setdefault(lfn, []).append(se)
                    for lfn in metadata["Successful"]:
                        checkSum.setdefault(lfn, {})[se] = metadata["Successful"][lfn]["Checksum"]
            if notFound:
                errMsg = "%d files not found" % notFound
            progressBar.endLoop(errMsg)
        gLogger.setLevel(logLevel)

        gLogger.notice("Verifying checksum of %d files" % len(replicas))
        for lfn in replicas:
            # get the lfn checksum from the LFC
            replicaDict = replicas[lfn]
            oneGoodReplica = False if lfn not in otherReplicas else True
            allGoodReplicas = True
            lfcChecksum = csDict[lfn].pop("LFCChecksum")
            for se in replicaDict:
                # If replica doesn't exist skip check
                if se in lfnNotExisting.get(lfn, []):
                    allGoodReplicas = False
                    continue
                if se in lfnNoInfo.get(lfn, []):
                    # If there is no info, a priori it could be good
                    oneGoodReplica = True
                    continue
                # get the surls metadata and compare the checksum
                surlChecksum = checkSum.get(lfn, {}).get(se, "")
                if not surlChecksum or not compareAdler(lfcChecksum, surlChecksum):
                    # if lfcChecksum does not match surlChecksum
                    csDict[lfn][se] = {"PFNChecksum": surlChecksum}
                    gLogger.info(
                        "ERROR!! checksum mismatch at %s for LFN %s:  LFC checksum: %s , PFN checksum : %s "
                        % (se, lfn, lfcChecksum, surlChecksum)
                    )
                    allGoodReplicas = False
                else:
                    oneGoodReplica = True
            if not oneGoodReplica:
                if lfn in lfnNotExisting:
                    gLogger.info("=> All replicas are missing", lfn)
                    retDict["MissingAllReplicas"][lfn] = "All"
                else:
                    gLogger.info("=> All replicas have bad checksum", lfn)
                    retDict["AllReplicasCorrupted"][lfn] = csDict[lfn]
            elif not allGoodReplicas:
                if lfn in lfnNotExisting:
                    gLogger.info("=> At least one replica missing", lfn)
                    retDict["MissingReplica"][lfn] = lfnNotExisting[lfn]
                else:
                    gLogger.info("=> At least one replica with good Checksum", lfn)
                    retDict["SomeReplicasCorrupted"][lfn] = csDict[lfn]

        return retDict

    ################################################################################
    # properties

    def set_prod(self, value):
        """Setter"""
        if value:
            value = int(value)
            res = self.transClient.getTransformation(value, extraParams=False)
            if not res["OK"]:
                raise RuntimeError("Couldn't find transformation %d: %s" % (value, res["Message"]))
            else:
                self.transType = res["Value"]["Type"]
            if self.interactive:
                gLogger.info("Production %d has type %s" % (value, self.transType))
        else:
            value = 0
        self._prod = value

    def get_prod(self):
        """Getter"""
        return self._prod

    prod = property(get_prod, set_prod)

    def set_fileType(self, value):
        """Setter"""
        fts = [ft.upper() for ft in value]
        self._fileType = fts

    def get_fileType(self):
        """Getter"""
        return self._fileType

    fileType = property(get_fileType, set_fileType)

    def set_fileTypesExcluded(self, value):
        """Setter"""
        fts = [ft.upper() for ft in value]
        self._fileTypesExcluded = fts

    def get_fileTypesExcluded(self):
        """Getter"""
        return self._fileTypesExcluded

    fileTypesExcluded = property(get_fileTypesExcluded, set_fileTypesExcluded)

    def set_bkQuery(self, value):
        """Setter"""
        if isinstance(value, six.string_types):
            self._bkQuery = ast.literal_eval(value)
        else:
            self._bkQuery = value

    def get_bkQuery(self):
        """Getter"""
        return self._bkQuery

    bkQuery = property(get_bkQuery, set_bkQuery)

    def set_lfns(self, value):
        """Setter"""
        if isinstance(value, six.string_types):
            value = [value]
        value = [v.replace(" ", "").replace("//", "/") for v in value]
        self._lfns = value

    def get_lfns(self):
        """Getter"""
        return self._lfns

    lfns = property(get_lfns, set_lfns)

    def set_status(self, value):
        """Setter"""
        self._status = value

    def get_status(self):
        """Getter"""
        return self._status

    status = property(get_status, set_status)

    def set_verbose(self, value):
        """Setter"""
        self._verbose = bool(value)

    def get_verbose(self):
        """Getter"""
        return self._verbose

    verbose = property(get_verbose, set_verbose)

    def set_seList(self, value):
        """Setter"""
        self._seList = set(resolveSEGroup(value))

    def get_seList(self):
        """Getter"""
        return self._seList

    seList = property(get_seList, set_seList)

    def _findNextProduction(self):
        """
        Find in the next productions one that uses the current production as input in the BK query
        Returns its number and its type
        """
        for nextProd in range(self.prod + 1, self.prod + 6):
            res = self.transClient.getBookkeepingQuery(nextProd)
            if res["OK"] and res["Value"].get("ProductionID") == self.prod:
                res = self.transClient.getTransformation(nextProd)
                if not res["OK"]:
                    return None, None
                return (nextProd, res["Value"]["Type"])
        return None, None
