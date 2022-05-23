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
Actual executor methods of the dirac-transformation-debug script
"""
import sys
import os
import datetime
import gzip
import ssl
import tarfile
import tempfile

from collections import defaultdict
from fnmatch import fnmatch
import six
from six.moves.urllib.request import FancyURLopener

import DIRAC
from DIRAC.Core.Utilities.File import mkDir
from DIRAC import gLogger
from DIRAC.Core.Base import Script
from DIRAC.Core.Utilities.List import breakListIntoChunks
from DIRAC.Core.Security.Locations import getCAsLocation, getProxyLocation
from DIRAC.DataManagementSystem.Client.DataManager import DataManager
from DIRAC.Resources.Catalog.FileCatalog import FileCatalog
from DIRAC.RequestManagementSystem.Client.ReqClient import ReqClient, printOperation
from DIRAC.WorkloadManagementSystem.Client.JobMonitoringClient import JobMonitoringClient
from DIRAC.ConfigurationSystem.Client.Helpers.Operations import Operations

from LHCbDIRAC.TransformationSystem.Client.TransformationClient import TransformationClient
from LHCbDIRAC.BookkeepingSystem.Client.BookkeepingClient import BookkeepingClient
from LHCbDIRAC.TransformationSystem.Utilities.PluginUtilities import PluginUtilities
from LHCbDIRAC.TransformationSystem.Utilities.ScriptUtilities import getTransformations


def _checkReplicasForProblematic(lfns, replicas, nbReplicasProblematic, problematicReplicas):
    """
    Check replicas of Problematic files

    :param lfns: list of LFNs
    :type lfns: list
    :param replicas: replica dict
    :type replicas:dict
    :param nbReplicasProblematic: dict to be filled with stat per number of SE
    :type nbReplicasProblematic: dict
    :param problematicReplicas: dict of LFNs per SE
    :type problematicReplicas: dict
    """
    for lfn in lfns:
        # Problematic files, let's see why
        realSEs = [se for se in replicas.get(lfn, []) if not se.endswith("-ARCHIVE")]
        nbSEs = len(realSEs)
        nbReplicasProblematic[nbSEs] += 1
        if not nbSEs:
            problematicReplicas[None].append(lfn)
        for se in realSEs:
            problematicReplicas[se].append(lfn)


def _genericLfn(lfn, lfnList):
    """
    From a file name, replace the job number with <jobNumber>
    """
    if lfn not in lfnList and os.path.dirname(lfn) == "":
        spl = lfn.split("_")
        if len(spl) == 3:
            spl[1] = "<jobNumber>"
        lfn = "_".join(spl)
    return lfn


def __buildURL(urlBase, ref):
    """Build URL from a base, checking whether the ref file is an absolute or relative path"""
    # If absolute path, get the hostas base
    if os.path.isabs(ref):
        urlBase = os.path.sep.join(urlBase.split(os.path.sep)[:3])
        ref = ref[1:]
    return os.path.join(urlBase, ref)


def _getLog(urlBase, logFile, debug=False):
    """
    Get a logfile and return its content
    """
    # if logFile == "" it is assumed the file is directly the urlBase
    # Otherwise it can either be referenced within urlBase or contained (.tar.gz)

    # In order to use https with the correct CA, use the FancyURLOpener and the user proxy as certificate
    context = ssl.create_default_context(capath=getCAsLocation())
    proxyFile = getProxyLocation()
    urlOpener = FancyURLopener(cert_file=proxyFile, context=context)
    if os.path.basename(urlBase) == "":
        url = os.path.join(urlBase, "index.html")
    else:
        url = urlBase
    if debug:
        print("Entering getLog", url, logFile)
    cc = None
    if logFile and ".tgz" not in url:
        # Try first with index.html and then try and list the directory
        while True:
            try:
                fd = None
                if debug:
                    print("Try opening URL ", url)
                fd = urlOpener.open(url)
                if debug:
                    print("Open")
                cc = fd.read()
                # Check if the page was not found
                if (
                    "404 - Not Found" in cc
                    or "was not found on this server." in cc
                    or "There was an error loading the page you requested" in cc
                ):
                    if debug:
                        print("File not found")
                    # If the file is not found, try with the urlBase
                    if url == urlBase:
                        return ""
                    if debug:
                        print("Try with urlBase", urlBase)
                    url = urlBase
                else:
                    if debug:
                        print("File read")
                    break
            except (IOError, ValueError) as e:
                print("Exception opening %s: %s" % (url, repr(e)))
                break
            finally:
                if fd:
                    fd.close()
        logURL = None
        if cc:
            cc = cc.split("\n")
            for line in cc:
                # Look for an html reference
                try:
                    ll = line.split("href=")[1].split('"')[1]
                except IndexError:
                    continue
                # Find the URL
                if fnmatch(ll, "*" + logFile + "*"):
                    if debug:
                        print("Match found:", ll)
                    logURL = __buildURL(urlBase, ll)
                elif fnmatch(ll, "*.tgz") or fnmatch(ll, "*.tar"):
                    if debug:
                        print("Match found with tgz or tar file:", ll)
                    # If a tgz file is found, it could help, but still continue!
                    logURL = __buildURL(urlBase, ll)
                if logURL:
                    break
        if not logURL:
            if debug:
                print("No match found")
            return ""
        if debug:
            print("URL found:", logURL)
    tmp = None
    tmp1 = None
    tf = None
    if ".tgz" in logURL or ".gz" in logURL or ".tar" in logURL:
        if debug:
            print("Opening tar file ", logURL)
        # retrieve the zipped file
        tmp = os.path.join(tempfile.gettempdir(), "logFile.tmp")
        if debug:
            print("Retrieve the file in ", tmp)
        if os.path.exists(tmp):
            os.remove(tmp)
        urlOpener.retrieve(logURL, tmp)
        with open(tmp, "rt") as fd:
            cc = fd.read()
        if "404 Not Found" in cc:
            return ""
            # unpack the tarfile
        if debug:
            print("Open tarfile ", tmp)
        if ".tar" in logURL:
            tf = tarfile.open(tmp, "r")
        else:
            tf = tarfile.open(tmp, "r:gz")
        mn = tf.getnames()
        fd = None
        if debug:
            print("Found those members", mn, ", looking for", logFile)
        for fileName in mn:
            if fnmatch(fileName, logFile + "*"):
                if debug:
                    print("Found ", logFile, " in tar object ", fileName)
                if ".gz" in fileName:
                    # file is again a gzip file!!
                    tmp1 = os.path.join(tempfile.gettempdir(), "logFile-1.tmp")
                    if debug:
                        print("Extract", fileName, "into", tmp1, "and open it")
                    tf.extract(fileName, tmp1)
                    tmp1 = os.path.join(tmp1, fileName)
                    fd = gzip.GzipFile(tmp1, "r")
                else:
                    fd = tf.extractfile(fileName)
                break
    else:
        try:
            fd = urlOpener.open(logURL)
        except IOError as e:
            if debug:
                print("Exception opening %s: %s" % (logURL, repr(e)))
    # read the actual file...
    if not fd:
        if debug:
            print("Couldn't open file...")
        cc = ""
    else:
        if debug:
            print("File successfully open")
        cc = fd.read()
        fd.close()
        if "was not found on this server." not in cc:
            cc = cc.split("\n")
            if debug:
                print("Reading the file now... %d lines" % len(cc))
        else:
            cc = ""
    if tf:
        tf.close()
    if tmp:
        os.remove(tmp)
    if tmp1:
        os.remove(tmp1)
    return cc


def _getSandbox(job, logFile, debug=False):
    """
    Get a sandox and return its content
    """
    fd = None
    files = []
    try:
        tmpDir = os.path.join(tempfile.gettempdir(), "sandBoxes/")
        mkDir(tmpDir)
        if debug:
            print("Job", job, ": sandbox being retrieved in", tmpDir)
        from DIRAC.WorkloadManagementSystem.Client.SandboxStoreClient import SandboxStoreClient

        res = SandboxStoreClient(smdb=False).downloadSandboxForJob(job, "Output", tmpDir)
        if res["OK"]:
            if debug:
                print("Sandbox successfully retrieved")
            files = os.listdir(tmpDir)
            if debug:
                print("Files:", files)
            for lf in files:
                if fnmatch(lf, logFile):
                    if debug:
                        print(lf, "matched", logFile)
                    with open(os.path.join(tmpDir, lf), "rt") as fd:
                        return fd.readlines()
            return ""
    except IOError as e:
        gLogger.exception("Exception while getting sandbox", lException=e)
        return ""
    finally:
        for lf in files:
            os.remove(os.path.join(tmpDir, lf))
        os.rmdir(tmpDir)


def _checkXMLSummary(job, logURL):
    """
    Look in an XMLSummary file for partly processed files of failed files
    Return the list of bad LFNs
    """
    debug = False
    try:
        xmlFile = _getLog(logURL, "summary*.xml*", debug=debug)
        if not xmlFile:
            if debug:
                print("XML not found in logs")
            xmlFile = _getSandbox(job, "summary*.xml*", debug=debug)
            if xmlFile and debug:
                print("XML from SB")
        elif debug:
            print("XML from logs")
        lfns = {}
        if xmlFile:
            for line in xmlFile:
                if 'status="part"' in line and "LFN:" in line:
                    event = line.split(">")[1].split("<")[0]
                    lfns.update({line.split("LFN:")[1].split('"')[0]: "Partial (last event %s)" % event})
                elif 'status="fail"' in line and "LFN:" in line:
                    lfns.update({line.split("LFN:")[1].split('"')[0]: "Failed"})
            if not lfns:
                lfns = {None: "No errors found in XML summary"}
        return lfns
    except tarfile.ReadError as e:
        gLogger.exception("Exception while checking XML summary", lException=e)
        return {None: "Could not open XML summary"}


def _checkLog(logURL):
    """
    Find ERROR string, core dump or "stalled events" in a logfile
    """
    for i in range(5, 0, -1):
        logFile = _getLog(logURL, "*_%d.log" % i, debug=False)
        if logFile:
            break
    logDump = []
    if logFile:
        space = False
        for line in logFile:
            if " ERROR " in line or "*** Break ***" in line:
                if space:
                    logDump.append("....")
                    space = False
                logDump.append(line)
            else:
                space = True
            if "Stalled event" in line:
                logDump = ["Stalled Event"]
                break
    else:
        logDump = ["Couldn't find log file in %s" % logURL]
    return logDump[-10:]


class TransformationDebug(object):
    """
    This class houses all methods for debugging transformations
    """

    def __init__(self):

        self.transClient = TransformationClient()
        self.reqClient = ReqClient()
        self.bkClient = BookkeepingClient()
        self.dataManager = DataManager()
        self.fileCatalog = FileCatalog()
        self.monitoring = None
        self.dataManagerTransTypes = ("Replication", "Removal")
        self.transID = None
        self.transType = None
        self.fixIt = False
        self.kickRequests = False
        self.cancelRequests = False
        self.pluginUtil = None
        self.listOfAssignedRequests = {}
        self.transPlugin = None

    def __getFilesForRun(self, runID=None, status=None, lfnList=None, seList=None, taskList=None, transID=None):
        """
        Get a lit of TS files fulfilling criteria

        :param runList: list of run numbers
        :type runList: list
        :param seList: list of UsedSE
        :type seList: list
        :param status: file TS status
        :type status: string or list
        :param taskList: list of task IDs
        :type taskList: list
        :param lfnList: list of LFNs
        :type lfnList: list
        :param transID: transformation ID
        :type transID: int

        :return : list of TS files (i.e. dictionaries) fulfilling the criteria
        """
        if transID is None:
            transID = self.transID
        # print transID, runID, status, lfnList
        selectDict = {"TransformationID": transID}
        if runID is not None:
            if runID:
                selectDict["RunNumber"] = runID
            else:
                selectDict["RunNumber"] = str(runID)
        if status:
            selectDict["Status"] = status
        if lfnList:
            selectDict["LFN"] = lfnList
        if seList:
            selectDict["UsedSE"] = seList
        taskFiles = defaultdict(set)
        if taskList:
            # First get fileID per task as the task may no longer be in the TransformationFiles table
            for taskID in taskList:
                res = self.transClient.getTableDistinctAttributeValues(
                    "TransformationFileTasks", ["FileID"], {"TransformationID": transID, "TaskID": taskID}
                )
                if res["OK"]:
                    # Keep track of which file corresponds to which task
                    if res["Value"]["FileID"]:
                        for fileID in res["Value"]["FileID"]:
                            taskFiles[fileID].add(taskID)
                            selectDict.setdefault("FileID", []).append(fileID)
                else:
                    gLogger.error("Error getting Transformation tasks:", res["Message"])
                    return []
        res = self.transClient.getTransformationFiles(selectDict)
        if res["OK"]:
            if taskFiles:
                # Set the correct taskID as it may have changed
                fileDictList = []
                for fileDict in res["Value"]:
                    for taskID in taskFiles[fileDict["FileID"]]:
                        newFile = fileDict.copy()
                        newFile["TaskID"] = taskID
                        fileDictList.append(newFile)
            else:
                fileDictList = res["Value"]
            return fileDictList
        else:
            gLogger.error("Error getting Transformation files:", res["Message"])
            return []

    def __filesProcessed(self, runID):
        """
        Get the number of files and number of processed files in a run

        :param runID: run number
        :type runID: int, long
        :return : tuple (nb of files, nb of files Processed)
        """
        transFilesList = self.__getFilesForRun(runID, None)
        files = len(transFilesList)
        processed = sum(fileDict["Status"] == "Processed" for fileDict in transFilesList)
        return (files, processed)

    def __getRuns(self, runList=None, byRuns=True, seList=None, status=None, taskList=None, transID=None):
        """
        Get a list of TS runs fulfilling criteria

        :param runList: list of run numbers
        :type runList: list
        :param byRuns: if True, get a list of runs, else just None
        :type byRuns: boolean
        :param seList: list of UsedSE
        :type seList: list
        :param status: file TS status
        :type status: string or list
        :param taskList: list of task IDs
        :type taskList: list

        :return : list of dictionaries (one per run) fulfilling the criteria
        """
        runs = []
        if status and byRuns and not runList:
            files = self.__getFilesForRun(status=status, taskList=taskList, transID=transID)
            runList = set(str(fileDict["RunNumber"]) for fileDict in files)

        if runList:
            for runRange in runList:
                runRange = runRange.split(":")
                if len(runRange) == 1:
                    runs.append(int(runRange[0]))
                else:
                    for run in range(int(runRange[0]), int(runRange[1]) + 1):
                        runs.append(run)
            selectDict = {"TransformationID": self.transID, "RunNumber": runs}
            if runs == [0]:
                runs = [{"RunNumber": 0}]
            else:
                if seList:
                    selectDict["SelectedSite"] = seList
                res = self.transClient.getTransformationRuns(selectDict)
                if res["OK"]:
                    if not len(res["Value"]):
                        gLogger.notice("No runs found, set to None")
                        runs = [{"RunNumber": None}]
                    else:
                        runs = res["Value"]
        elif not byRuns:
            # No run selection
            runs = [{"RunNumber": None}]
        elif not status:
            # All runs selected explicitly
            selectDict = {"TransformationID": self.transID}
            if seList:
                selectDict["SelectedSite"] = seList
            res = self.transClient.getTransformationRuns(selectDict)
            if res["OK"]:
                if not len(res["Value"]):
                    gLogger.notice("No runs found, set to None")
                    runs = [{"RunNumber": None}]
                else:
                    runs = res["Value"]
        return runs

    def __justStats(self, status, seList):
        """
        Print out statistics per usedSE about TS files in a given status targeting some sites

        :param status: (list of) status
        :type status: list or string
        :param seList: list of usedSE
        :type seList: list or string

        :return : list of jobIDs that are not in a proper status w.r.t. status
        """
        improperJobs = []
        if not status:
            status = "Assigned"
        transFilesList = self.__getFilesForRun(status=status, seList=seList)
        if not transFilesList:
            return improperJobs
        statsPerSE = {}
        # print transFilesList
        statusList = {"Received", "Checking", "Staging", "Waiting", "Running", "Stalled"}
        if status == "Processed":
            statusList.update({"Done", "Completed", "Failed"})
        taskList = [fileDict["TaskID"] for fileDict in transFilesList]
        res = self.transClient.getTransformationTasks({"TransformationID": self.transID, "TaskID": taskList})
        if not res["OK"]:
            gLogger.notice("Could not get the list of tasks...", res["Message"])
            DIRAC.exit(2)
        for task in res["Value"]:
            # print task
            targetSE = task["TargetSE"]
            stat = task["ExternalStatus"]
            statusList.add(stat)
            statsPerSE[targetSE][stat] = (
                statsPerSE.setdefault(targetSE, dict.fromkeys(statusList, 0)).setdefault(stat, 0) + 1
            )
            if status == "Processed" and stat not in ("Done", "Completed", "Stalled", "Failed", "Killed", "Running"):
                improperJobs.append(task["ExternalID"])

        shift = 0
        for se in statsPerSE:
            shift = max(shift, len(se) + 2)
        prString = "SE".ljust(shift)
        for stat in statusList:
            prString += stat.ljust(10)
        gLogger.notice(prString)
        for se in sorted(statsPerSE):
            prString = se.ljust(shift)
            for stat in statusList:
                prString += str(statsPerSE[se].get(stat, 0)).ljust(10)
            gLogger.notice(prString)
        return improperJobs

    def __getTransformationInfo(self, transSep):
        """
        Print out information about a given transformation

        :param transSep: separator to print out before info
        :type transSep: string

        :return : tuple ("Job"|"Request", file type in BK query)
        """
        res = self.transClient.getTransformation(self.transID, extraParams=False)
        if not res["OK"]:
            gLogger.notice("Couldn't find transformation", self.transID)
            return None, None
        else:
            transStatus = res["Value"]["Status"]
            self.transType = res["Value"]["Type"]
            transBody = res["Value"]["Body"]
            self.transPlugin = res["Value"]["Plugin"]
            strPlugin = self.transPlugin
            if self.transType in ("Merge", "MCMerge", "DataStripping", "MCStripping"):
                strPlugin += ", GroupSize: %s" % str(res["Value"]["GroupSize"])
            if self.transType in self.dataManagerTransTypes:
                taskType = "Request"
            else:
                taskType = "Job"
            transGroup = res["Value"]["TransformationGroup"]
        gLogger.notice(
            "%s Transformation %d (%s) of type %s (plugin %s) in %s"
            % (transSep, self.transID, transStatus, self.transType, strPlugin, transGroup)
        )
        if self.transType == "Removal":
            gLogger.notice("Transformation body:", transBody)
        res = self.transClient.getBookkeepingQuery(self.transID)
        if res["OK"] and res["Value"]:
            gLogger.notice("BKQuery:", res["Value"])
            queryFileTypes = res["Value"].get("FileType")
        else:
            gLogger.notice("No BKQuery for this transformation")
            queryFileTypes = None
        gLogger.notice("")
        return taskType, queryFileTypes

    def __fixRunNumber(self, filesToFix, fixRun, noTable=False):
        """
        Fix run information in TS

        :param filesToFix: list of TS files to get fixed
        :type filesToFix: list
        :param fixRun: if set, fix run, else print out number of files
        :type fixRun: boolean
        :param noTable: if True, the run is absent, else it is 0
        :type noTable: boolean
        """
        if not fixRun:
            if noTable:
                gLogger.notice(
                    "%d files have run number not in run table, use --FixRun to get this fixed" % len(filesToFix)
                )
            else:
                gLogger.notice("%d files have run number 0, use --FixRun to get this fixed" % len(filesToFix))
        else:
            fixedFiles = 0
            res = self.bkClient.getFileMetadata(filesToFix)
            if res["OK"]:
                runFiles = defaultdict(list)
                for lfn, metadata in res["Value"]["Successful"].items():  # can be an iterator
                    runFiles[metadata["RunNumber"]].append(lfn)
                for run in runFiles:
                    if not run:
                        gLogger.notice(
                            "%d files found in BK with run '%s': %s"
                            % (len(runFiles[run]), str(run), str(runFiles[run]))
                        )
                        continue
                    res = self.transClient.addTransformationRunFiles(self.transID, run, runFiles[run])
                    # print run, runFiles[run], res
                    if not res["OK"]:
                        gLogger.notice(
                            "***ERROR*** setting %d files to run %d in transformation %d"
                            % (len(runFiles[run]), run, self.transID),
                            res["Message"],
                        )
                    else:
                        fixedFiles += len(runFiles[run])
                if fixedFiles:
                    gLogger.notice("Successfully fixed run number for %d files" % fixedFiles)
                else:
                    gLogger.notice("There were no files for which to fix the run number")
            else:
                gLogger.notice("***ERROR*** getting metadata for %d files:" % len(filesToFix), res["Message"])

    def __checkFilesMissingInFC(self, transFilesList, status):
        """
        Check a list of files that are missing in FC and print information

        :param transFilesList: list of TS files
        :type transFilesList: list
        :param status: (list of) status
        :type status: list or string
        """
        lfns = [fileDict["LFN"] for fileDict in transFilesList if fileDict["Status"] == "MissingInFC"]
        if lfns:
            res = self.dataManager.getReplicas(lfns)
            if res["OK"]:
                replicas = res["Value"]["Successful"]
                notMissing = len(replicas)
                if notMissing:
                    if not self.kickRequests:
                        gLogger.notice(
                            "%d files are %s but indeed are in the FC - \
              Use --KickRequests to reset them Unused"
                            % (notMissing, status)
                        )
                    else:
                        res = self.transClient.setFileStatusForTransformation(
                            self.transID, "Unused", list(replicas), force=True
                        )
                        if res["OK"]:
                            gLogger.notice(
                                "%d files were %s but indeed are in the FC - Reset to Unused" % (notMissing, status)
                            )
                        else:
                            gLogger.notice("Error resetting %d files Unused" % notMissing, res["Message"])
                else:
                    res = self.bkClient.getFileMetadata(lfns)
                    if not res["OK"]:
                        gLogger.notice("ERROR getting metadata from BK", res["Message"])
                    else:
                        metadata = res["Value"]["Successful"]
                        lfnsWithReplicaFlag = [lfn for lfn in metadata if metadata[lfn]["GotReplica"] == "Yes"]
                        if lfnsWithReplicaFlag:
                            gLogger.notice("All files are really missing in FC")
                            if not self.fixIt:
                                gLogger.notice(
                                    "%d files are not in the FC but have a replica flag in BK, use --FixIt to fix"
                                    % len(lfnsWithReplicaFlag)
                                )
                            else:
                                res = self.bkClient.removeFiles(lfnsWithReplicaFlag)
                                if not res["OK"]:
                                    gLogger.notice("ERROR removing replica flag:", res["Message"])
                                else:
                                    gLogger.notice("Replica flag removed from %d files" % len(lfnsWithReplicaFlag))
                        else:
                            gLogger.notice("All files are really missing in FC and BK")

    def __getReplicas(self, lfns):
        """
        Get replicas of a list of LFNs

        :param lfns: list of LFNs
        :type lfns: list
        """
        replicas = {}
        for lfnChunk in breakListIntoChunks(lfns, 200):
            res = self.dataManager.getReplicas(lfnChunk, getUrl=False)
            if res["OK"]:
                replicas.update(res["Value"]["Successful"])
            else:
                gLogger.notice("Error getting replicas", res["Message"])
        return replicas

    def __getTask(self, taskID):
        """
        Get a TS task

        :param taskID: task ID
        :type taskID: int
        """
        res = self.transClient.getTransformationTasks({"TransformationID": self.transID, "TaskID": taskID})
        if not res["OK"] or not res["Value"]:
            return None
        return res["Value"][0]

    def __fillStatsPerSE(self, seStat, rep, listSEs):
        """
        Fill statistics per SE for a set of replicas and a list of SEs
        Depending whether the transformation is replication or removal, give the stat of missing or still present SEs

        :param seStat: returned dictionary (number per SE)
        :type seStat: dictionary
        :param rep: list of replicas
        :type rep: list or dict
        :param listSEs: list of SEs to give statistics about
        :type listSEs: list
        """
        seStat["Total"] += 1
        completed = True
        if not rep:
            seStat[None] += 1
        if not listSEs:
            listSEs = ["Some"]
        for se in listSEs:
            if self.transType == "Replication":
                if se == "Some" or se not in rep:
                    seStat[se] += 1
                    completed = False
            elif self.transType == "Removal":
                if se == "Some" or se in rep:
                    seStat[se] += 1
                    completed = False
            else:
                if se not in rep:
                    seStat[se] += 1
        return completed

    def __getRequestName(self, requestID):
        """
        Return request name from ID

        :param requestID: request ID
        :type requestID: int
        """
        level = gLogger.getLevel()
        gLogger.setLevel("FATAL")
        try:
            if not requestID:
                return None
            res = self.reqClient.getRequestInfo(requestID)
            if res["OK"]:
                return res["Value"][2]
            gLogger.notice("No such request found: %s" % requestID)
            return None
        except IndexError:
            return None
        finally:
            gLogger.setLevel(level)

    def __getAssignedRequests(self):
        """
        Set member variable to the list of Assigned requests
        """
        if not self.listOfAssignedRequests:
            res = self.reqClient.getRequestIDsList(["Assigned"], limit=10000)
            if res["OK"]:
                self.listOfAssignedRequests = [reqID for reqID, _x, _y in res["Value"]]

    def __printRequestInfo(self, task, lfnsInTask, taskCompleted, status, dmFileStatusComment):
        """
        Print information about a request for a given task

        :param task: TS task
        :type task: dictionary
        :param lfnsInTask: List of LFNs in that task
        :type lfnsInTask: list
        :param taskCompleted: flag telling whether task is supposed to be completed or not
        :type taskCompleted: boolean
        :param status: status of TS files
        :type status: string
        :param dmFileStatusComment: comment
        :type dmFileStatusComment: string
        """
        requestID = int(task["ExternalID"])
        taskID = task["TaskID"]
        taskName = "%08d_%08d" % (self.transID, taskID)
        if taskCompleted and (
            task["ExternalStatus"] not in ("Done", "Failed") or set(status) & {"Assigned", "Problematic"}
        ):
            # If the task is completed but files are not set Processed, wand or fix it
            #   note that this may just be to a delay of the RequestTaskAgent, but it wouldn't harm anyway
            prString = "\tTask %s is completed: no %s replicas" % (taskName, dmFileStatusComment)
            if self.kickRequests:
                res = self.transClient.setFileStatusForTransformation(self.transID, "Processed", lfnsInTask, force=True)
                if res["OK"]:
                    prString += " - %d files set Processed" % len(lfnsInTask)
                else:
                    prString += " - Failed to set %d files Processed (%s)" % (len(lfnsInTask), res["Message"])
            else:
                prString += " - To mark files Processed, use option --KickRequests"
            gLogger.notice(prString)

        if not requestID:
            if task["ExternalStatus"] == "Submitted":
                # This should not happen: a Submitted task should have an associated request: warn or fix
                prString = "\tTask %s is Submitted but has no external ID" % taskName
                if taskCompleted:
                    newStatus = "Done"
                else:
                    newStatus = "Created"
                if self.kickRequests:
                    res = self.transClient.setTaskStatus(self.transID, taskID, newStatus)
                    if res["OK"]:
                        prString += " - Task reset %s" % newStatus
                    else:
                        prString += " - Failed to set task %s (%s)" % (newStatus, res["Message"])
                else:
                    prString += " - To reset task %s, use option --KickRequests" % newStatus
                gLogger.notice(prString)
            return 0
        # This method updates self.listOfAssignedRequests
        self.__getAssignedRequests()
        request = None
        res = self.reqClient.peekRequest(requestID)
        if res["OK"]:
            if res["Value"] is not None:
                request = res["Value"]
                requestStatus = request.Status if request.RequestID not in self.listOfAssignedRequests else "Assigned"
                if requestStatus != task["ExternalStatus"]:
                    gLogger.notice(
                        "\tRequest %d status: %s updated last %s" % (requestID, requestStatus, request.LastUpdate)
                    )
                if task["ExternalStatus"] == "Failed":
                    # Find out why this task is failed
                    for i, op in enumerate(request):
                        if op.Status == "Failed":
                            printOperation((i, op), onlyFailed=True)
            else:
                requestStatus = "NotExisting"
        else:
            gLogger.notice("Failed to peek request:", res["Message"])
            requestStatus = "Unknown"

        res = self.reqClient.getRequestFileStatus(requestID, lfnsInTask)
        if res["OK"]:
            reqFiles = res["Value"]
            statFiles = defaultdict(int)
            for stat in reqFiles.values():
                statFiles[stat] += 1
            for stat in sorted(statFiles):
                gLogger.notice("\t%s: %d files" % (stat, statFiles[stat]))
            # If all files failed, set the request as failed
            if requestStatus != "Failed" and statFiles.get("Failed", -1) == len(reqFiles):
                prString = "\tAll transfers failed for that request"
                if not self.kickRequests:
                    prString += ": it should be marked as Failed, use --KickRequests"
                else:
                    request.Status = "Failed"
                    res = self.reqClient.putRequest(request)
                    if res["OK"]:
                        prString += ": request set to Failed"
                    else:
                        prString += ": error setting to Failed: %s" % res["Message"]
                gLogger.notice(prString)
            # If some files are Scheduled, try and get information about the FTS jobs
            if statFiles.get("Scheduled", 0) and request:
                try:
                    from DIRAC.DataManagementSystem.Client.FTS3Client import FTS3Client

                    fts3Client = FTS3Client()
                    # We take all the operationIDs
                    rmsOpIDs = [o.OperationID for o in request if o.Type == "ReplicateAndRegister"]
                    fts3Ops = []
                    for rmsOpID in rmsOpIDs:

                        res = fts3Client.getOperationsFromRMSOpID(rmsOpID)
                        if not res["OK"]:
                            gLogger.warn(
                                "Could not get FTS operations associated to RMS Operation %s: %s" % (rmsOpID, res)
                            )
                            continue
                        fts3Ops.extend(res["Value"])

                    fts3FileStatusCount = defaultdict(int)
                    for fts3Op in fts3Ops:
                        for fts3File in fts3Op.ftsFiles:
                            fts3FileStatusCount[fts3File.status] += 1

                    prStr = []
                    for stat, statusCount in fts3FileStatusCount.items():  # can be an iterator
                        prStr.append("%s:%d" % (stat, statusCount))
                    gLogger.notice("\tFTS files statuses: %s" % ", ".join(prStr))

                    # Get FTS jobs that are still active
                    activeFtsGUID = set()
                    for fts3Op in fts3Ops:
                        for fts3File in fts3Op.ftsFiles:
                            if fts3File.status != "Finished":
                                activeFtsGUID.add(fts3File.ftsGUID)
                                # If asking for Assigned or Problematic  files, list those that are not yet replicated
                                if set(status) & {"Assigned", "Problematic"}:
                                    gLogger.notice("\t%s : %s" % (fts3File.status, fts3File.lfn))

                    fts3Jobs = []
                    for fts3Op in fts3Ops:
                        for job in fts3Op.ftsJobs:
                            if job.ftsGUID in activeFtsGUID:
                                fts3Jobs.append(job)

                    if not fts3Jobs:
                        gLogger.notice("\tNo active FTS jobs found for that request")
                    else:
                        gLogger.notice("\tActive associated FTS jobs:")
                        for job in fts3Jobs:
                            gLogger.notice(
                                "\t\t%s/fts3/ftsmon/#/job/%s (%s, completed at %s %%)"
                                % (
                                    job.ftsServer.replace(
                                        ":8446", ":8449"
                                    ),  # Submission port is 8446, web port is 8449
                                    job.ftsGUID,
                                    job.status,
                                    job.completeness,
                                )
                            )
                except ImportError as e:
                    gLogger.notice("\tNo FTS information:", repr(e))

        # Kicking stuck requests in status Assigned
        toBeKicked = 0
        assignedReqLimit = datetime.datetime.utcnow() - datetime.timedelta(hours=2)
        if request:
            if request.RequestID in self.listOfAssignedRequests and request.LastUpdate < assignedReqLimit:
                gLogger.notice("\tRequest stuck: %d Updated %s" % (request.RequestID, request.LastUpdate))
                toBeKicked += 1
                if self.kickRequests:
                    res = self.reqClient.putRequest(request)
                    if res["OK"]:
                        gLogger.notice("\tRequest %d is reset" % requestID)
                    else:
                        gLogger.notice("\tError resetting request", res["Message"])
                elif self.cancelRequests:
                    res = self.reqClient.cancelRequest(request)
                    if res["OK"]:
                        gLogger.notice("\tRequest %d is canceled" % requestID)
                    else:
                        gLogger.notice("\tError canceling request", res["Message"])
        else:
            selectDict = {"RequestID": requestID}
            res = self.reqClient.getRequestSummaryWeb(selectDict, [], 0, 100000)
            if res["OK"]:
                params = res["Value"]["ParameterNames"]
                records = res["Value"]["Records"]
                for rec in records:
                    subReqDict = {}
                    subReqStr = ""
                    conj = ""
                    for i, param in enumerate(params):
                        subReqDict.update({param: rec[i]})
                        subReqStr += conj + param + ": " + rec[i]
                        conj = ", "

                    if subReqDict["Status"] == "Assigned" and subReqDict["LastUpdateTime"] < str(assignedReqLimit):
                        gLogger.notice(subReqStr)
                        toBeKicked += 1
                        if self.kickRequests:
                            res = self.reqClient.setRequestStatus(requestID, "Waiting")
                            if res["OK"]:
                                gLogger.notice("\tRequest %d reset Waiting" % requestID)
                            else:
                                gLogger.notice("\tError resetting request %d" % requestID, res["Message"])
        return toBeKicked

    def __checkProblematicFiles(self, nbReplicasProblematic, problematicReplicas, failedFiles):
        """
        Check files found Problematic in TS

        :param nbReplicasProblematic: dict of frequency of nb of replicas
        :type nbReplicasProblematic: dict
        :param problematicReplicas: problematic replicas by SE
        :type problematicReplicas: dict {SE:list of LFNs}
        :param failedFiles: list of files in Failed status
        :type failedFiles: list
        """
        from DIRAC.Core.Utilities.Adler import compareAdler

        gLogger.notice("\nStatistics for Problematic files in FC:")
        existingReplicas = defaultdict(list)
        lfns = set()
        lfnsInFC = set()
        for nb in sorted(nbReplicasProblematic):
            gLogger.notice("   %d replicas in FC: %d files" % (nb, nbReplicasProblematic[nb]))
        # level = gLogger.getLevel()
        # gLogger.setLevel( 'FATAL' )
        lfnCheckSum = {}
        badChecksum = defaultdict(list)
        error = {}
        for se in problematicReplicas:
            lfns.update(problematicReplicas[se])
            if se:
                lfnsInFC.update(problematicReplicas[se])
                res = self.fileCatalog.getFileMetadata(
                    [lfn for lfn in problematicReplicas[se] if lfn not in lfnCheckSum]
                )
                if res["OK"]:
                    success = res["Value"]["Successful"]
                    lfnCheckSum.update(dict((lfn, success[lfn]["Checksum"]) for lfn in success))
                res = self.dataManager.getReplicaMetadata(problematicReplicas[se], se)
                if res["OK"]:
                    for lfn in res["Value"]["Successful"]:
                        existingReplicas[lfn].append(se)
                        # Compare checksums
                        checkSum = res["Value"]["Successful"][lfn]["Checksum"]
                        if not checkSum or not compareAdler(checkSum, lfnCheckSum[lfn]):
                            badChecksum[lfn].append(se)
                else:
                    error[se] = res["Message"]
        nbProblematic = len(lfns) - len(existingReplicas)
        nbExistingReplicas = defaultdict(int)
        for lfn in existingReplicas:
            nbReplicas = len(existingReplicas[lfn])
            nbExistingReplicas[nbReplicas] += 1
        nonExistingReplicas = defaultdict(list)
        if error:
            gLogger.notice("Could not get information for some problematic files from SEs:")
            for se, err in error.items():  # can be an iterator
                gLogger.notice("\t%s: %s" % (se, err))
            gLogger.notice("This check may be totally meaningless, thus no report is made")
            return
        elif nbProblematic == len(lfns):
            gLogger.notice("None of the %d problematic files actually have an active replica" % len(lfns))
        else:
            strMsg = "Out of %d problematic files" % len(lfns)
            if nbProblematic:
                strMsg += ", only %d have an active replica" % (len(lfns) - nbProblematic)
            else:
                strMsg += ", all have an active replica"
            gLogger.notice(strMsg)
            for nb in sorted(nbExistingReplicas):
                gLogger.notice("   %d active replicas: %d files" % (nb, nbExistingReplicas[nb]))
            for se in problematicReplicas:
                lfns = [
                    lfn
                    for lfn in problematicReplicas[se]
                    if lfn not in existingReplicas or se not in existingReplicas[lfn]
                ]
                str2Msg = ""
                if len(lfns):
                    nonExistingReplicas[se].extend(lfns)
                    if not self.fixIt:
                        str2Msg = " Use --FixIt to remove them"
                    else:
                        str2Msg = " Will be removed from FC"
                    strMsg = "%d" % len(lfns)
                else:
                    strMsg = "none"
                if se:
                    gLogger.notice(
                        "   %s : %d replicas of problematic files in FC, %s physically missing.%s"
                        % (str(se).ljust(15), len(problematicReplicas[se]), strMsg, str2Msg)
                    )
                else:
                    gLogger.notice(
                        "   %s : %d files are not in self.fileCatalog." % ("".ljust(15), len(problematicReplicas[se]))
                    )
            lfns = [lfn for lfn in existingReplicas if lfn in failedFiles]
            if lfns:
                prString = "Failed transfers but existing replicas"
                if self.fixIt:
                    prString += ". Use --FixIt to fix it"
                else:
                    for lfn in lfns:
                        res = self.transClient.setFileStatusForTransformation(self.transID, "Unused", lfns, force=True)
                        if res["OK"]:
                            prString += " - %d files reset Unused" % len(lfns)
                gLogger.notice(prString)
        filesInFCNotExisting = list(lfnsInFC - set(existingReplicas))
        if filesInFCNotExisting:
            prString = "%d files are in the FC but are not physically existing. " % len(filesInFCNotExisting)
            if self.fixIt:
                prString += "Removing them now from self.fileCatalog..."
            else:
                prString += "Use --FixIt to remove them"
            gLogger.notice(prString)
            if self.fixIt:
                self.__removeFiles(filesInFCNotExisting)
        if badChecksum:
            prString = "%d files have a checksum mismatch:" % len(badChecksum)
            replicasToRemove = {}
            filesToRemove = []
            for lfn in badChecksum:
                if badChecksum[lfn] == existingReplicas[lfn]:
                    filesToRemove.append(lfn)
                else:
                    replicasToRemove[lfn] = badChecksum[lfn]
            if filesToRemove:
                prString += " %d files have no correct replica;" % len(filesToRemove)
            if replicasToRemove:
                prString += " %d files have at least an incorrect replica" % len(replicasToRemove)
            if not self.fixIt:
                prString += " Use --FixIt to remove them"
            else:
                prString += " Removing them now..."
            gLogger.notice(prString)
            if self.fixIt:
                if filesToRemove:
                    self.__removeFiles(filesToRemove)
                if replicasToRemove:
                    seFiles = defaultdict(list)
                    for lfn in replicasToRemove:
                        for se in replicasToRemove[lfn]:
                            seFiles[se].append(lfn)
                    for se in seFiles:
                        res = self.dataManager.removeReplica(se, seFiles[se])
                        if not res["OK"]:
                            gLogger.notice("ERROR: error removing replicas", res["Message"])
                        else:
                            gLogger.notice("Successfully removed %d replicas from %s" % (len(seFiles[se], se)))
        elif existingReplicas:
            gLogger.notice("All existing replicas have a good checksum")
        if self.fixIt and nonExistingReplicas:
            nRemoved = 0
            failures = defaultdict(list)
            # If SE == None, the file is not in the FC
            notInFC = nonExistingReplicas.get(None)
            if notInFC:
                nonExistingReplicas.pop(None)
                nRemoved, transRemoved = self.__removeFilesFromTS(notInFC)
                if nRemoved:
                    gLogger.notice(
                        "Successfully removed %d files from transformations %s" % (nRemoved, ",".join(transRemoved))
                    )
            for se in nonExistingReplicas:
                lfns = [lfn for lfn in nonExistingReplicas[se] if lfn not in filesInFCNotExisting]
                res = self.dataManager.removeReplica(se, lfns)
                if not res["OK"]:
                    gLogger.notice("ERROR when removing replicas from FC at %s" % se, res["Message"])
                else:
                    failed = res["Value"]["Failed"]
                    if failed:
                        gLogger.notice("Failed to remove %d replicas at %s" % (len(failed), se))
                        gLogger.notice("\n".join(sorted(failed)))
                        for lfn in failed:
                            failures[failed[lfn]].append(lfn)
                    nRemoved += len(res["Value"]["Successful"])
            if nRemoved:
                gLogger.notice("Successfully removed %s replicas from FC" % nRemoved)
            if failures:
                gLogger.notice("Failures:")
                for error in failures:
                    gLogger.notice("%s: %d replicas" % (error, len(failures[error])))
        gLogger.notice("")

    def __removeFilesFromTS(self, lfns):
        """
        Set a list of files in status Removed

        :param lfns: list of LFNs
        :type lfns: list

        :return : (nb of removed files, list of removed LFNs)
        """
        res = self.transClient.getTransformationFiles({"LFN": lfns})
        if not res["OK"]:
            gLogger.notice("Error getting %d files in the TS" % len(lfns), res["Message"])
            return (None, None)
        transFiles = defaultdict(list)
        removed = 0
        for fd in res["Value"]:
            transFiles[fd["TransformationID"]].append(fd["LFN"])
        for transID, lfns in transFiles.items():  # can be an iterator
            res = self.transClient.setFileStatusForTransformation(transID, "Removed", lfns, force=True)
            if not res["OK"]:
                gLogger.notice("Error setting %d files Removed" % len(lfns), res["Message"])
            else:
                removed += len(lfns)
        return removed, [str(tr) for tr in transFiles]

    def __removeFiles(self, lfns):
        """
        Remove files from FC and TS

        :param lfns: list of LFNs
        :type lfns: list
        """
        res = self.dataManager.removeFile(lfns)
        if res["OK"]:
            gLogger.notice("Successfully removed %d files from FC" % len(lfns))
            nRemoved, transRemoved = self.__removeFilesFromTS(lfns)
            if nRemoved:
                gLogger.notice(
                    "Successfully removed %d files from transformations %s" % (nRemoved, ",".join(transRemoved))
                )
        else:
            gLogger.notice("ERROR when removing files from FC:", res["Message"])

    def __getJobStatus(self, job):
        """
        Get the status of a (list of) job, return it formated <major>;<minor>;<application>
        """
        if isinstance(job, six.string_types):
            jobs = [int(job)]
        elif isinstance(job, six.integer_types):
            jobs = [job]
        else:
            jobs = list(int(jid) for jid in job)
        if not self.monitoring:
            self.monitoring = JobMonitoringClient()
        res = self.monitoring.getJobsStatus(jobs)
        if res["OK"]:
            jobStatus = res["Value"]
            res = self.monitoring.getJobsMinorStatus(jobs)
            if res["OK"]:
                jobMinorStatus = res["Value"]
                res = self.monitoring.getJobsApplicationStatus(jobs)
                if res["OK"]:
                    jobApplicationStatus = res["Value"]
        if not res["OK"]:
            return {}
        return dict(
            (
                job,
                "%s; %s; %s"
                % (
                    jobStatus.get(job, {}).get("Status", "Unknown"),
                    jobMinorStatus.get(job, {}).get("MinorStatus", "Unknown"),
                    jobApplicationStatus.get(job, {}).get("ApplicationStatus", "Unknown"),
                ),
            )
            for job in jobs
        )

    def __getJobSites(self, job):
        """
        Get the status of a (list of) job, return it formated <major>;<minor>;<application>
        """
        if isinstance(job, six.string_types):
            jobs = [int(job)]
        elif isinstance(job, six.integer_types):
            jobs = [job]
        else:
            jobs = list(int(jid) for jid in job)
        if not self.monitoring:
            self.monitoring = JobMonitoringClient()
        res = self.monitoring.getJobsSites(jobs)
        if res["OK"]:
            jobSites = res["Value"]
        else:
            return {}
        return dict((job, jobSites.get(job, {}).get("Site", "Unknown")) for job in jobs)

    def __getJobCPU(self, job):
        """
        Get the status of a (list of) job, return it formated <major>;<minor>;<application>
        """
        if isinstance(job, six.string_types):
            jobs = [int(job)]
        elif isinstance(job, six.integer_types):
            jobs = [job]
        else:
            jobs = list(int(jid) for jid in job)
        if not self.monitoring:
            self.monitoring = JobMonitoringClient()
        jobCPU = {}
        stdoutTag = " (h:m:s)"
        for job in jobs:
            param = "TotalCPUTime(s)"
            res = self.monitoring.getJobParameter(job, param)
            if res["OK"] and param in res["Value"]:
                jobCPU[job] = res["Value"][param] + " s"
            else:
                # Try and get the stdout
                param = "StandardOutput"
                res = self.monitoring.getJobParameter(job, param)
                if res["OK"]:
                    try:
                        for line in res["Value"].get(param, "").splitlines():
                            if stdoutTag in line:
                                cpu = line.split(stdoutTag)[0].split()[-1].split(":")
                                cpu = 3600 * int(cpu[0]) + 60 * int(cpu[1]) + int(cpu[2])
                                jobCPU[job] = "%d s" % cpu
                                break
                    except (IndexError, ValueError):
                        pass
        return jobCPU

    def __checkJobs(self, jobsForLfn, byFiles=False, checkLogs=False):
        """
        Extract all information about jobs referring to list of LFNs

        :param jobsForLfn: dict { lfnString : [jobs] }
        :type jobsForLfn: dict
        :param byFiles: print file information
        :type byFiles: boolean
        :param checkLogs: check also logfiles of jobs
        :type checkLogs: boolean
        """
        if not self.monitoring:
            self.monitoring = JobMonitoringClient()
        failedLfns = defaultdict(list)
        idrLfns = defaultdict(list)
        jobLogURL = {}
        jobSites = {}
        jobCPU = {}
        for lfnStr, allJobs in jobsForLfn.items():  # can be an iterator
            lfnList = lfnStr.split(",")
            exitedJobs = {}
            allJobs.sort()
            allStatus = self.__getJobStatus(allJobs)
            if "Message" in allStatus:
                gLogger.notice("Error getting jobs statuses:", allStatus["Message"])
                return
            if byFiles or len(lfnList) < 3:
                gLogger.notice(
                    "\n %d LFNs: %s : Status of corresponding %d jobs (sorted):" % (len(lfnList), lfnList, len(allJobs))
                )
            else:
                gLogger.notice("\n %d LFNs: Status of corresponding %d jobs (sorted):" % (len(lfnList), len(allJobs)))
            # Get the sites
            jobSites.update(self.__getJobSites(allJobs))
            jobCPU.update(self.__getJobCPU(allJobs))
            gLogger.notice("Jobs:", ", ".join(allJobs))
            gLogger.notice(
                "Sites (CPU):",
                ", ".join(
                    "%s (%s)" % (jobSites.get(int(job), "Site unknown"), jobCPU.get(int(job), "CPU unknown"))
                    for job in allJobs
                ),
            )
            prevStatus = None
            allStatus[sys.maxsize] = ""
            jobs = []
            # print '*** AllStatus', allStatus
            for job in sorted(allStatus):
                status = allStatus[job]
                job = int(job)
                # print '*** job, prevStatus, status', job, prevStatus, status
                if status == prevStatus:
                    jobs.append(job)
                    continue
                elif not prevStatus:
                    prevStatus = status
                    jobs = [job]
                    continue
                # print '*** Jobs', jobs
                prStr = "%3d jobs" % len(jobs)
                if "Failed" in prevStatus or "Done" in prevStatus or "Completed" in prevStatus:
                    prStr += " terminated with status:"
                else:
                    prStr += " in status:"
                gLogger.notice(prStr, prevStatus)
                majorStatus, minorStatus, applicationStatus = prevStatus.split("; ")
                if majorStatus == "Failed" and (
                    "exited with status" in applicationStatus.lower()
                    or "non-zero exit status" in applicationStatus.lower()
                    or "problem executing application" in applicationStatus.lower()
                ):
                    exitedJobs.update(dict.fromkeys(jobs, applicationStatus))
                elif majorStatus == "Failed" and applicationStatus == "Failed Input Data Resolution ":
                    # Try and find out which file was faulty
                    for job1 in jobs:
                        res = self.monitoring.getJobParameter(job1, "DownloadInputData")
                        if res["OK"] and "Failed to download" in res["Value"].get("DownloadInputData", ""):
                            lfns = (
                                res["Value"]["DownloadInputData"].split("Failed to download")[1].split(":")[1].split()
                            )
                            for lfn in lfns:
                                idrLfns[lfn].append(job1)
                elif minorStatus in ("Job stalled: pilot not running", "Watchdog identified this job as stalled"):
                    lastLine = ""
                    # Now get last lines
                    for job1 in sorted(jobs) + [0]:
                        if job1:
                            res = self.monitoring.getJobParameter(job1, "StandardOutput")
                            if res["OK"]:
                                line = (
                                    "(%s) " % jobSites.get(job1, "Unknown")
                                    + res["Value"]
                                    .get("StandardOutput", "stdout not available\n")
                                    .splitlines()[-1]
                                    .split("UTC ")[-1]
                                )
                        else:
                            line = ""
                        if not lastLine:
                            lastLine = line
                            jobs = [job1]
                            continue
                        elif line == lastLine:
                            jobs.append(job)
                            continue
                        maxLineLength = 120
                        gLogger.notice(
                            "\t%3d jobs stalled with last line: %s%s"
                            % (len(jobs), lastLine[:maxLineLength], " [...]" if len(lastLine) > maxLineLength else "")
                        )
                        lastLine = line
                        jobs = [job1]
                jobs = [job]
                prevStatus = status
                if exitedJobs:
                    # print '*** exitedJobs', exitedJobs
                    badLfns = {}
                    for lastJob in sorted(exitedJobs, reverse=True)[0:10]:
                        res = self.monitoring.getJobParameter(lastJob, "Log URL")
                        if res["OK"] and "Log URL" in res["Value"]:
                            logURL = res["Value"]["Log URL"].split('"')[1] + "/"
                            jobLogURL[lastJob] = logURL
                            lfns = _checkXMLSummary(str(lastJob), logURL)
                            lfns = dict((_genericLfn(lfn, lfnList), lfns[lfn]) for lfn in lfns if lfn)
                            if lfns:
                                badLfns.update({lastJob: lfns})
                        # break
                    # print '*** badLfns', badLfns
                    if not badLfns:
                        gLogger.notice("\tNo error was found in XML summary files")
                    else:
                        # lfnsFound is an AND of files found bad in all jobs
                        lfnsFound = set(badLfns[sorted(badLfns, reverse=True)[0]])
                        for lfns in badLfns.values():
                            lfnsFound &= set(lfns)
                        if lfnsFound:
                            for lfn, job, reason in [
                                (x, job, badLfns[job][x])
                                for job, lfns in badLfns.items()
                                for x in set(lfns) & lfnsFound
                            ]:  # can be an iterator
                                if job in exitedJobs:
                                    exitStatus = exitedJobs[job].split("status ")
                                    if len(exitStatus) == 2:
                                        reason = "(exit code %s) was " % exitStatus[1] + reason
                                failedLfns[(lfn, reason)].append(job)
                        else:
                            gLogger.notice("No common error was found in all XML summary files")
                    exitedJobs = {}
        if idrLfns:
            gLogger.notice("\nSummary of failures due to Input Data Resolution")
            for (lfn, jobs) in idrLfns.items():  # can be an iterator
                jobs = sorted(set(jobs))
                js = set(jobSites.get(job, "Unknown") for job in jobs)
                if len(js) == 1:
                    gLogger.notice(
                        "\nERROR ==> %s could not be downloaded by jobs: %s (%s)"
                        % (lfn, ", ".join(str(job) for job in jobs), list(js)[0])
                    )
                else:
                    gLogger.notice(
                        "\nERROR ==> %s could not be downloaded by jobs: %s"
                        % (lfn, ", ".join("%d (%s)" % (job, jobSites.get(job, "Unknown")) for job in jobs))
                    )

        # print '*** failedLfns', failedLfns
        if failedLfns:
            gLogger.notice("\nSummary of failures due to: Application Exited with non-zero status")
            lfnDict = {}
            partial = "Partial (last event "
            for (lfn, reason), jobs in list(failedLfns.items()):
                if partial not in reason:
                    continue
                failedLfns.pop((lfn, reason))
                otherReasons = lfnDict.get(lfn)
                if not otherReasons:
                    lfnDict[lfn] = (reason, jobs)
                else:
                    lastEvent = int(reason.split(partial)[1][:-1])
                    lfnDict[lfn] = (otherReasons[0][:-1] + ",%d)" % lastEvent, otherReasons[1] + jobs)
            for lfn, (reason, jobs) in lfnDict.items():  # can be an iterator
                failedLfns[(lfn, reason)] = jobs

            for (lfn, reason), jobs in failedLfns.items():  # can be an iterator
                js = set(jobSites.get(job, "Unknown") for job in jobs)
                # If only one site, print it once only
                if len(js) == 1:
                    gLogger.notice(
                        "\nERROR ==> %s %s during processing from jobs: %s (%s)"
                        % (lfn, reason, ", ".join(str(job) for job in jobs), list(js)[0])
                    )
                else:
                    gLogger.notice(
                        "\nERROR ==> %s %s during processing from jobs: %s"
                        % (lfn, reason, ", ".join("%d (%s)" % (job, jobSites.get(job, "Unknown")) for job in jobs))
                    )
                # Get an example log if possible
                if checkLogs:
                    logDump = _checkLog(jobLogURL[jobs[0]])
                    prStr = "\tFrom logfile of job %s: " % jobs[0]
                    if len(logDump) == 1:
                        prStr += logDump[0]
                    else:
                        prStr += "\n\t".join([""] + logDump)
                    gLogger.notice(prStr)
        gLogger.notice("")

    def __checkRunsToFlush(self, runID, transFilesList, runStatus, evtType=90000000, fileTypes=None):
        """
        Check whether the run is flushed and if not, why it was not

        :param runID: run number
        :type runID: int
        :param transFilesList: list of TS files
        :type transFilesList: list
        :param runStatus: current status of run
        :type runStatus: string
        :param evtType: event type
        :type evtType: int
        :param fileTypes: file types
        :type fileTypes: list
        """
        if not runID:
            gLogger.notice("Cannot check flush status for run", runID)
            return
        rawFiles = self.pluginUtil.getNbRAWInRun(runID, evtType)
        if not rawFiles:
            gLogger.notice("Run %s is not finished..." % runID)
            return
        if "FileType" in self.transPlugin:
            param = "FileType"
        elif "EventType" in self.transPlugin:
            param = "EventType"
        else:
            param = ""
            paramValues = [""]
        if param:
            res = self.bkClient.getFileMetadata([fileDict["LFN"] for fileDict in transFilesList])
            if not res["OK"]:
                gLogger.notice("Error getting files metadata", res["Message"])
                DIRAC.exit(2)
            evtType = list(res["Value"]["Successful"].values())[0]["EventType"]
            if isinstance(fileTypes, (list, set)) and param == "FileType":
                paramValues = sorted(fileTypes)
            elif evtType and param == "EventType":
                paramValues = [evtType]
            else:
                paramValues = sorted(set(meta[param] for meta in res["Value"]["Successful"].values() if param in meta))
        ancestors = defaultdict(list)
        # print "*** Param values", ','.join( paramValues )
        for paramValue in paramValues:
            try:
                nbAnc = self.pluginUtil.getRAWAncestorsForRun(runID, param, paramValue)
                # print '*** For %s = %s: %d ancestors' % ( param, paramValue, nbAnc )
                ancestors[nbAnc].append(paramValue)
            except Exception as e:  # pylint: disable=broad-except
                gLogger.exception("Exception calling pluginUtilities:", lException=e)
        prStr = ""
        for anc in sorted(ancestors):
            ft = ancestors[anc]
            if ft and ft != [""]:
                prStr += "%d ancestors found for %s; " % (anc, ",".join(ft))
            else:
                prStr = "%d ancestors found" % anc
        toFlush = False
        flushError = False
        for ancestorRawFiles in ancestors:
            if rawFiles == ancestorRawFiles:
                toFlush = True
            elif ancestorRawFiles > rawFiles:
                flushError = True

        # Missing ancestors, find out which ones
        if not toFlush and not flushError:
            gLogger.notice(
                "Run %s flushed: %s while %d RAW files"
                % ("should not be" if runStatus == "Flush" else "not", prStr, rawFiles)
            )
            # Find out which ones are missing
            res = self.bkClient.getRunFiles(int(runID))
            if not res["OK"]:
                gLogger.notice("Error getting run files", res["Message"])
            else:
                res = self.bkClient.getFileMetadata(sorted(res["Value"]))
                if not res["OK"]:
                    gLogger.notice("Error getting files metadata", res["Message"])
                else:
                    metadata = res["Value"]["Successful"]
                    runRAWFiles = set(
                        lfn
                        for lfn, meta in metadata.items()  # can be an iterator
                        if meta["EventType"] == evtType and meta["GotReplica"] == "Yes"
                    )
                    badRAWFiles = (
                        set(lfn for lfn, meta in metadata.items() if meta["EventType"] == evtType)  # can be an iterator
                        - runRAWFiles
                    )
                    # print len( runRAWFiles ), 'RAW files'
                    allAncestors = set()
                    for paramValue in paramValues:
                        # This call returns only the base name of LFNs as they are unique
                        ancFiles = self.pluginUtil.getRAWAncestorsForRun(runID, param, paramValue, getFiles=True)
                        allAncestors.update(ancFiles)
                    # Remove ancestors from their basename in a list of LFNs
                    missingFiles = set(lfn for lfn in runRAWFiles if os.path.basename(lfn) not in allAncestors)
                    if missingFiles:
                        gLogger.notice("Missing RAW files:\n\t%s" % "\n\t".join(sorted(missingFiles)))
                    else:
                        if badRAWFiles:
                            gLogger.notice("Indeed %d RAW files have no replicas and therefore..." % len(badRAWFiles))
                        else:
                            gLogger.notice("No RAW files are missing in the end and therefore...")
                        rawFiles = len(runRAWFiles)
                        toFlush = True
        if toFlush:
            gLogger.notice(
                "Run %s flushed: %d RAW files and ancestors found"
                % ("correctly" if runStatus == "Flush" else "should be", rawFiles)
            )
            if runStatus != "Flush":
                if self.fixIt:
                    res = self.transClient.setTransformationRunStatus(self.transID, runID, "Flush")
                    if res["OK"]:
                        gLogger.notice("Run %d successfully flushed" % runID)
                    else:
                        gLogger.notice("Error flushing run %d" % runID, res["Message"])
                else:
                    gLogger.notice("Use --FixIt to flush the run")
        if flushError:
            gLogger.notice(
                "More ancestors than RAW files (%d) for run %d ==> Problem!\n\t%s"
                % (rawFiles, runID, prStr.replace("; ", "\n\t"))
            )

    def __checkWaitingTasks(self):
        """
        Check waiting tasks:
        They can be really waiting (assigned files), Failed, Done or just orphan (no files)
        """
        res = self.transClient.getTransformationTasks({"TransformationID": self.transID, "ExternalStatus": "Waiting"})
        if not res["OK"]:
            gLogger.notice("Error getting waiting tasks:", res["Message"])
            return
        tasks = res["Value"]
        taskStatuses = defaultdict(list)
        gLogger.notice("Found %d waiting tasks" % len(tasks))
        for task in tasks:
            fileDicts = self.transClient.getTransformationFiles(
                {"TransformationID": self.transID, "TaskID": task["TaskID"]}
            ).get("Value", [])
            if not fileDicts:
                status = "Orphan"
            else:
                statuses = sorted(set(fileName["Status"] for fileName in fileDicts))
                if statuses == ["Processed"]:
                    status = "Done"
                elif statuses == ["Failed"]:
                    status = "Failed"
                else:
                    status = None
            if status:
                taskStatuses[status].append((task["TaskID"], int(task["ExternalID"])))
        if not taskStatuses:
            gLogger.notice("All tasks look OK")
            return
        for status in taskStatuses:
            gLogger.notice("%d tasks are indeed %s" % (len(taskStatuses[status]), status))
            if self.kickRequests:
                fixed = 0
                ids = taskStatuses[status]
                if status == "Orphan":
                    status = "Failed"
                for taskID, requestID in ids:
                    requestName = self.__getRequestName(requestID)
                    if requestName:
                        res = self.transClient.setTaskStatus(self.transID, taskID, status)
                        if not res["OK"]:
                            gLogger.notice("Error setting task %s to %s" % (requestID, status), res["Message"])
                        res = self.reqClient.peekRequest(requestID)
                        if res["OK"]:
                            request = res["Value"]
                            request.Status = status
                            res = self.reqClient.putRequest(request)
                            if res["OK"]:
                                fixed += 1
                        if not res["OK"]:
                            gLogger.notice("Error setting %s to %s" % (requestID, status), res["Message"])
                gLogger.notice("\t%d requests set to status %s" % (fixed, status))
        if not self.kickRequests:
            gLogger.notice("Use --KickRequests to fix them")

    def __getRunsForFiles(self, lfnList):
        """
        Get run list for a set of files
        """
        transFiles = self.__getFilesForRun(lfnList=lfnList)
        return list(set([str(f["RunNumber"]) for f in transFiles]))

    def debugTransformation(self, dmScript, infoList, statusList):
        """
        Actual script execution code: parses arguments and implements the checking logic

        :param dmScript: DMScript object to be parsed
        :type dmScript: DMScript
        :param infoList: list of possible information
        :type infoList: tuple
        :param statusList: list of possible statuses
        :type statusList: tuple
        """

        verbose = False
        byFiles = False
        byRuns = False
        byTasks = False
        byJobs = False
        dumpFiles = False
        status = []
        taskList = []
        seList = []
        runList = None
        justStats = False
        fixRun = False
        allTasks = False
        checkFlush = False
        checkWaitingTasks = False
        checkSubmittedTasks = False
        checkLogs = False
        jobList = []
        exceptProd = None

        switches = Script.getUnprocessedSwitches()
        for opt, val in switches:
            if opt == "Info":
                infos = val.split(",")
                for val in infos:
                    val = val.lower()
                    if val not in infoList:
                        gLogger.notice("Unknown information... Select in %s" % str(infoList))
                        DIRAC.exit(0)
                    elif val == "files":
                        byFiles = True
                    elif val == "runs":
                        byRuns = True
                    elif val == "tasks":
                        byTasks = True
                    elif val == "jobs":
                        byJobs = True
                    elif val == "alltasks":
                        allTasks = True
                    elif val == "flush":
                        byRuns = True
                        checkFlush = True
                    elif val == "log":
                        checkLogs = True
            elif opt == "Status":
                status = val.split(",")
                val = set(status) - set(statusList)
                if val:
                    gLogger.notice("Unknown status %s... Select in %s" % (sorted(val), str(statusList)))
                    DIRAC.exit(1)
            elif opt == "Runs":
                runList = val.split(",")
            elif opt == "SEs":
                seList = val.split(",")
            elif opt in ("v", "Verbose"):
                verbose = True
            elif opt == "Tasks":
                taskList = [int(x) for x in val.split(",")]
            elif opt == "KickRequests":
                self.kickRequests = True
            elif opt == "CancelRequests":
                self.cancelRequests = True
            elif opt == "DumpFiles":
                dumpFiles = True
            elif opt == "Statistics":
                justStats = True
            elif opt == "FixIt":
                self.fixIt = True
            elif opt == "FixRun":
                fixRun = True
                runList = ["0"]
            elif opt == "CheckWaitingTasks":
                checkWaitingTasks = True
            elif opt == "CheckSubmittedTasks":
                checkSubmittedTasks = True
                byTasks = True
            elif opt == "Jobs":
                # in TransformationTasks job is a string
                jobList = [job for job in val.split(",") if job.isdigit()]
            elif opt == "ExceptActiveRunsFromProduction":
                exceptProd = int(val)

        lfnList = dmScript.getOption("LFNs", [])
        if lfnList:
            byFiles = True
        if dumpFiles:
            byFiles = True
        if allTasks:
            byTasks = True
        if byJobs:
            allTasks = True
            byTasks = False
        if fixRun and not status:
            status = "Unused"

        transList = getTransformations(Script.getPositionalArgs()) if not jobList and not checkSubmittedTasks else []

        improperJobs = []
        # gLogger.setLevel( 'INFO' )

        # If looking for MaxReset files, and no transformation is specified, get the list
        if status in (["MaxReset"], ["Problematic"]) and not transList:
            res = self.transClient.getTransformationFiles({"Status": status})
            if not res["OK"]:
                gLogger.notice("Failed getting MaxReset files", res["Message"])
                DIRAC.exit(1)
            transList = getTransformations([",".join(set(str(fd["TransformationID"]) for fd in res["Value"]))])
            if transList:
                gLogger.notice(
                    "Transformations to be debugged", ": %s\n" % ",".join(str(trans) for trans in sorted(transList))
                )

        # Get list of transformations from the list of jobs
        if jobList:
            # Check first which JobGroup jobs come from
            transJobs = defaultdict(list)
            badJobs = []
            if not self.monitoring:
                self.monitoring = JobMonitoringClient()
            for job in jobList:
                trans = self.monitoring.getJobAttribute(int(job), "JobGroup").get("Value")
                if trans.isdigit() and (not transList or int(trans) in transList):
                    transJobs[int(trans)].append(job)
                else:
                    badJobs.append(job)
            if badJobs:
                gLogger.notice("Jobs are not production jobs", ",".join(badJobs))
            transList = defaultdict(list)
            for trans, jobs in transJobs.items():
                res = self.transClient.getTransformationTasks({"TransformationID": trans, "ExternalID": jobs})
                if not res["OK"]:
                    gLogger.notice("Error getting jobs:", res["Message"])
                else:
                    for task in res["Value"]:
                        transList[trans].append(task["TaskID"])
            if transList:
                gLogger.notice(
                    "Transformations to be debugged", ": %s\n" % ",".join(str(trans) for trans in sorted(transList))
                )

        # Get list of transformations that have tasks in status Submitted
        if checkSubmittedTasks:
            res = self.transClient.getTransformationTasks({"ExternalStatus": "Submitted", "ExternalID": "0"})
            if not res["OK"]:
                gLogger.notice("Error getting submitted tasks:", res["Message"])
            elif not res["Value"]:
                gLogger.notice("No tasks submitted with no task ID")
            else:
                transList = defaultdict(list)
                for task in res["Value"]:
                    transList[task["TransformationID"]].append(task["TaskID"])

        # At this point we should have a list of transformations, othewise stop
        if not transList:
            gLogger.notice("No valid transformation found...")
            DIRAC.exit(0)

        transSep = ""
        for transID in sorted(transList):
            self.transID = transID
            if isinstance(transList, dict):
                taskList = transList[transID]
            problematicReplicas = defaultdict(list)
            failedFiles = []
            nbReplicasProblematic = defaultdict(int)
            taskType, queryFileTypes = self.__getTransformationInfo(transSep)
            if taskType is None:
                continue
            transSep = "==============================\n"
            dmFileStatusComment = {"Replication": "missing", "Removal": "remaining"}.get(self.transType, "absent")
            if not transID:
                continue
            #####################
            # If just statistics are requested
            if justStats:
                improperJobs += self.__justStats(status, seList)
                continue
            #####################
            # If only checking waiting tasks
            if checkWaitingTasks:
                self.__checkWaitingTasks()
                continue

            self.pluginUtil = PluginUtilities(
                self.transPlugin,
                transClient=self.transClient,
                dataManager=self.dataManager,
                bkClient=self.bkClient,
                debug=verbose,
                transID=transID,
            )
            # Select runs, or all
            # If byRuns is requested but LFNs are provided, get the list of runs
            if byRuns and lfnList:
                runList = self.__getRunsForFiles(lfnList)
                gLogger.notice("Files are from runs %s" % ",".join(runList))
            runsDictList = self.__getRuns(runList=runList, byRuns=byRuns, seList=seList, status=status)
            # If some runs must be excluded, remove them
            if status and byRuns and exceptProd:
                exceptRunsDict = self.__getRuns(
                    runList=[],
                    byRuns=byRuns,
                    seList=seList,
                    status=["Assigned", "Problematic", "Unused", "MaxReset"],
                    transID=exceptProd,
                )
                exceptRuns = [run["RunNumber"] for run in exceptRunsDict]
                for run in list(runsDictList):
                    if run["RunNumber"] in exceptRuns:
                        runsDictList.remove(run)
            else:
                exceptRuns = []
            if runList and [run["RunNumber"] for run in runsDictList] == [None]:
                gLogger.notice("None of the requested runs was found, exit")
                DIRAC.exit(0)
            if status and byRuns and not runList:
                if not runsDictList:
                    if exceptRuns:
                        gLogger.notice(
                            "No runs left, runs %s have non-processed files in production %d"
                            % (",".join([str(r) for r in exceptRuns]), exceptProd)
                        )
                    else:
                        gLogger.notice("No runs found...")
                else:
                    gLogger.notice(
                        "%d runs found: %s"
                        % (len(runsDictList), ",".join(str(runDict["RunNumber"]) for runDict in runsDictList))
                    )
                    if exceptRuns:
                        gLogger.notice(
                            "Runs %s excluded: they have non-processed files in production %d"
                            % (",".join([str(r) for r in exceptRuns]), exceptProd)
                        )
            seStat = defaultdict(int)
            allFiles = []
            toBeKicked = 0

            # Loop over all requested runs or just all in one go (runID == None)
            runsInTable = {}
            for runDict in runsDictList:
                runID = runDict["RunNumber"]
                selectedSEs = runDict.get("SelectedSite", "None").split(",")
                runStatus = runDict.get("Status")

                # Get all files from TransformationDB
                transFilesList = sorted(
                    self.__getFilesForRun(
                        runID=runID, status=status, lfnList=lfnList, seList=seList, taskList=taskList
                    ),
                    key=lambda d: (d["TaskID"] if d["TaskID"] is not None else 0, d["LFN"]),
                )
                if jobList and allTasks:
                    taskList = []
                if lfnList:
                    notFoundFiles = [
                        lfn for lfn in lfnList if lfn not in [fileDict["LFN"] for fileDict in transFilesList]
                    ]
                    if notFoundFiles:
                        gLogger.notice(
                            "Some requested files were not found in transformation (%d):" % len(notFoundFiles)
                        )
                        gLogger.notice("\n\t".join(notFoundFiles))

                # No files found in transDB
                if not transFilesList:
                    if not byRuns:
                        gLogger.notice("No files found with given criteria")
                    continue

                # Run display
                if byRuns and runID:
                    files, processed = self.__filesProcessed(runID)
                    if runID:
                        prString = "Run: %d" % runID
                    else:
                        prString = "No run"
                    if runStatus:
                        prString += " (%s)" % runStatus
                    tasks = set()
                    nFilesNoTask = 0
                    for fileDict in transFilesList:
                        if fileDict["TaskID"]:
                            tasks.add(fileDict["TaskID"])
                        else:
                            nFilesNoTask += 1
                    prString += " - %d files (" % files
                    if nFilesNoTask:
                        prString += "%d files in no task, " % nFilesNoTask
                    prString += "%d tasks, SelectedSite: %s), %d processed, status: %s" % (
                        len(tasks),
                        selectedSEs,
                        processed,
                        runStatus,
                    )
                    gLogger.notice(prString)

                if checkFlush or ((byRuns and runID) and status == "Unused" and "WithFlush" in self.transPlugin):
                    if runStatus != "Flush":
                        # Check if the run should be flushed
                        lfn = transFilesList[0]["LFN"]
                        evtType = self.pluginUtil.getMetadataFromTSorBK(lfn, "EventType").get(lfn, 90000000)
                        self.__checkRunsToFlush(
                            runID, transFilesList, runStatus, evtType=evtType, fileTypes=queryFileTypes
                        )
                    else:
                        gLogger.notice("Run %d is already flushed" % runID)

                prString = "%d files found" % len(transFilesList)
                nbUniqueFiles = len(set(t["LFN"] for t in transFilesList))
                if nbUniqueFiles != len(transFilesList):
                    prString += " (%d unique LFNs)" % nbUniqueFiles
                if status:
                    prString += " with status %s" % status
                if runID:
                    prString += " in run %d" % runID
                gLogger.notice(prString + "\n")

                # Extract task list
                filesWithRunZero = []
                filesWithNoRunTable = []
                problematicFiles = []
                taskDict = defaultdict(list)
                for fileDict in transFilesList:
                    if not allTasks:
                        taskID = fileDict["TaskID"] if fileDict["TaskID"] is not None else 0
                        taskDict[taskID].append(fileDict["LFN"])
                        if "Problematic" in status and not fileDict["TaskID"]:
                            problematicFiles.append(fileDict["LFN"])
                    else:
                        # Get all tasks associated to that file
                        res = self.transClient.getTableDistinctAttributeValues(
                            "TransformationFileTasks",
                            ["TaskID"],
                            {"TransformationID": transID, "FileID": fileDict["FileID"]},
                        )
                        if not res["OK"]:
                            gLogger.notice("Error when getting tasks for file %s" % fileDict["LFN"])
                        else:
                            for taskID in res["Value"]["TaskID"]:
                                if taskID is None:
                                    taskID = 0
                                taskDict[taskID].append(fileDict["LFN"])
                    fileRun = fileDict.get("RunNumber")
                    fileLfn = fileDict["LFN"]
                    if byFiles:
                        gLogger.notice(
                            "%s - Run: %s - Status: %s - UsedSE: %s - ErrorCount %s"
                            % (fileLfn, fileRun, fileDict["Status"], fileDict["UsedSE"], fileDict["ErrorCount"])
                        )
                    if not fileRun and "/MC" not in fileLfn:
                        filesWithRunZero.append(fileLfn)
                    if fileRun:
                        runInTable = runsInTable.get(fileRun)
                        if not runInTable:
                            runInTable = self.__getRuns(runList=[str(fileRun)], byRuns=True)[0].get("RunNumber")
                            runsInTable[fileRun] = runInTable
                        if not runInTable:
                            filesWithNoRunTable.append(fileLfn)

                # Files with run# == 0
                transWithRun = self.transPlugin in Operations().getValue("TransformationPlugins/PluginsWithRunInfo", [])
                if filesWithRunZero and transWithRun:
                    self.__fixRunNumber(filesWithRunZero, fixRun)
                if filesWithNoRunTable and transWithRun:
                    self.__fixRunNumber(filesWithNoRunTable, fixRun, noTable=True)

                # Problematic files
                if problematicFiles and not byFiles:
                    _checkReplicasForProblematic(
                        problematicFiles,
                        self.__getReplicas(problematicFiles),
                        nbReplicasProblematic,
                        problematicReplicas,
                    )

                # Check files with missing FC
                if status:
                    self.__checkFilesMissingInFC(transFilesList, status)

                ####################
                # Now loop on all tasks
                jobsForLfn = defaultdict(list)
                if verbose:
                    gLogger.notice("Tasks:", ",".join(str(taskID) for taskID in sorted(taskDict)))
                if allTasks:
                    # Sort tasks by LFNs in order to print them together
                    lfnTask = defaultdict(list)
                    for taskID in sorted(taskDict):
                        for lfn in taskDict[taskID]:
                            lfnTask[lfn].append(taskID)
                    sortedTasks = []
                    for lfn in sorted(lfnTask):
                        for taskID in lfnTask[lfn]:
                            if taskID not in sortedTasks:
                                sortedTasks.append(taskID)
                else:
                    sortedTasks = sorted(taskDict)
                lfnsInTask = []
                for taskID in sorted(taskList) if taskList else sortedTasks:
                    if allTasks and not byJobs and taskDict[taskID] != lfnsInTask:
                        gLogger.notice("")
                    if taskID not in taskDict:
                        gLogger.notice("Task %s not found in the transformation files table" % taskID)
                        lfnsInTask = []
                    else:
                        lfnsInTask = taskDict[taskID]
                    task = self.__getTask(taskID)
                    if not task:
                        continue
                    # Analyse jobs
                    if byJobs and taskType == "Job":
                        job = task["ExternalID"]
                        lfns = set(lfnsInTask if lfnsInTask else [""]) & set(
                            fileDict["LFN"] for fileDict in transFilesList
                        )
                        if not jobList or job in jobList:
                            jobsForLfn[",".join(sorted(lfns))].append(job)
                        if not byFiles and not byTasks:
                            continue
                    nfiles = len(lfnsInTask)
                    allFiles += lfnsInTask
                    replicas = self.__getReplicas(lfnsInTask)
                    targetSE = task.get("TargetSE")
                    if targetSE == "None":
                        targetSE = "Some"
                    # Accounting per SE
                    listSEs = targetSE.split(",")
                    # If a list of LFNs is provided, we may not have all files in the task, set to False
                    taskCompleted = not lfnList

                    # Check problematic files
                    if "Problematic" in status:
                        _checkReplicasForProblematic(lfnsInTask, replicas, nbReplicasProblematic, problematicReplicas)

                    # Collect statistics per SE
                    for lfn in replicas:
                        taskCompleted = self.__fillStatsPerSE(seStat, replicas[lfn], listSEs) and taskCompleted

                    # Print out task's information
                    if byTasks:
                        # print task
                        prString = "TaskID: %s (created %s, updated %s) - %d files" % (
                            taskID,
                            task["CreationTime"],
                            task["LastUpdateTime"],
                            nfiles,
                        )
                        if byFiles and lfnsInTask:
                            sep = ","  # if sys.stdout.isatty() else '\n'
                            prString += " (" + sep.join(lfnsInTask) + ")"
                        prString += "- %s: %s - Status: %s" % (taskType, task["ExternalID"], task["ExternalStatus"])
                        if targetSE:
                            prString += " - TargetSE: %s" % targetSE
                        gLogger.notice(prString)

                        # More information from Request tasks
                        if taskType == "Request":
                            toBeKicked += self.__printRequestInfo(
                                task, lfnsInTask, taskCompleted, status, dmFileStatusComment
                            )
                        elif task["ExternalStatus"] in ("Failed", "Done", "Completed"):
                            # Get job statuses
                            jobID = int(task["ExternalID"])
                            jobStatus = self.__getJobStatus(jobID)
                            jobSite = self.__getJobSites(jobID)
                            gLogger.notice("Job status at %s:" % jobSite[int(jobID)], jobStatus[jobID])
                        if not allTasks:
                            gLogger.notice("")
                if byJobs and jobsForLfn:
                    self.__checkJobs(jobsForLfn, byFiles, checkLogs)
            if "Problematic" in status and nbReplicasProblematic and not byFiles:
                self.__checkProblematicFiles(nbReplicasProblematic, problematicReplicas, failedFiles)
            if toBeKicked:
                if self.kickRequests:
                    gLogger.notice("%d requests have been kicked" % toBeKicked)
                else:
                    gLogger.notice(
                        "%d requests are eligible to be kicked or canceled (use option --KickRequests or --CancelRequests)"
                        % toBeKicked
                    )

            ###########
            # Print out statistics of SEs if relevant (DMS)
            if seStat["Total"] and self.transType in self.dataManagerTransTypes and not checkSubmittedTasks:
                gLogger.notice("%d files found in tasks" % seStat["Total"])
                seStat.pop("Total")
                if None in seStat:
                    gLogger.notice("Found without replicas: %d files" % seStat[None])
                    seStat.pop(None)
                gLogger.notice("Statistics per %s SE:" % dmFileStatusComment)
                selectedSEs = sorted(seStat)
                found = False
                for se in selectedSEs:
                    gLogger.notice("%s %d files" % (se, seStat[se]))
                    found = True
                if not found:
                    gLogger.notice("... None ...")
            elif self.transType == "Removal" and (not status or "MissingInFC" not in status):
                gLogger.notice("All files have been successfully removed!")

            # All files?
            if dumpFiles and allFiles:
                gLogger.notice("List of files found:")
                gLogger.notice("\n".join(allFiles))

        if improperJobs:
            gLogger.notice("List of %d jobs in improper status:" % len(improperJobs))
            gLogger.notice(" ".join(str(j) for j in sorted(improperJobs)))
