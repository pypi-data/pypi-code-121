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
"""BKQuery is a class that decodes BK paths, queries the BK at a high level."""
import os
import sys
import six
from fnmatch import fnmatch
from DIRAC import gLogger
from LHCbDIRAC.BookkeepingSystem.Client.BookkeepingClient import BookkeepingClient
from LHCbDIRAC.DataManagementSystem.Client.StorageUsageClient import StorageUsageClient
from LHCbDIRAC.TransformationSystem.Client.TransformationClient import TransformationClient


def getProcessingPasses(bkQuery, depth=None):
    """Get the list of processing passes for a given BK query The processing pass
    in the initial query may contain "..." or a '*', in which case this acts as a
    wildcard character The search for processing passes may be limited to a
    certain depth (default: all)

    :param bkQuery: BK query dictionary
    :type bkQuery: dict
    :param depth: depth to which look for the processing pass
    :type depth: int
    """
    processingPass = bkQuery.getProcessingPass().replace("...", "*")
    if "*" not in processingPass:
        return [processingPass]
    ind = processingPass.index("*")
    basePass = os.path.dirname(processingPass[:ind])
    bkQuery.setProcessingPass(basePass)
    return sorted(
        pp for pp in bkQuery.getBKProcessingPasses(depth=depth) if fnmatch(pp, processingPass) and pp != basePass
    )


def makeBKPath(bkDict):
    """Builds a path from the dictionary.

    :param bkDict: BK query dictionary
    :type bkDict: dict
    """
    fileType = bkDict.get("FileType", ".")
    if isinstance(fileType, list):
        fileType = ",".join(fileType)
    path = os.path.join(
        "/",
        bkDict.get("ConfigName", ""),
        bkDict.get("ConfigVersion", ""),
        bkDict.get("ConditionDescription", bkDict.get("DataTakingConditions", bkDict.get("SimulationConditions", "."))),
        bkDict.get("ProcessingPass", ".")[1:],
        str(bkDict.get("EventType", ".")).replace("90000000", "."),
        fileType,
    ).replace("/.", "/")
    while path.endswith("/"):
        path = path[:-1]
    return path.replace("RealData", "Real Data")


class BadRunRange(Exception):
    """Exception class for bad run range."""

    pass


def parseRuns(bkQuery, runs):
    """Parse the parameter "Runs" and set it in the dictionary.

    :param bkQuery: BK dictionary
    :type bkQuery: dict
    :param runs: a string, an int, or a list,dict,tuple of run numbers
    :type runs: string or int/long, iterable
    """
    if isinstance(runs, six.string_types):
        runs = runs.split(",")
    elif isinstance(runs, (dict, tuple)):
        runs = list(runs)
    elif isinstance(runs, six.integer_types):
        runs = [str(runs)]
    if len(runs) > 1:
        runList = []
        for run in runs:
            if run.isdigit():
                runList.append(int(run))
            else:
                runRange = run.split(":")
                if len(runRange) == 2 and runRange[0].isdigit() and runRange[1].isdigit():
                    runList += range(int(runRange[0]), int(runRange[1]) + 1)
                else:
                    gLogger.error("Run numbers must be numbers...")
                    raise BadRunRange
        bkQuery["RunNumber"] = runList
    else:
        runs = runs[0].split(":")
        if len(runs) == 1:
            runs = runs[0].split("-")
            if len(runs) == 1:
                bkQuery["RunNumber"] = int(runs[0])
    if "RunNumber" not in bkQuery:
        try:
            if runs[0] and runs[1] and int(runs[0]) > int(runs[1]):
                gLogger.error("Warning: End run should be larger than start run: %d, %d" % (int(runs[0]), int(runs[1])))
                raise BadRunRange
            if runs[0].isdigit():
                bkQuery["StartRun"] = int(runs[0])
            if runs[1].isdigit():
                bkQuery["EndRun"] = int(runs[1])
        except IndexError as ex:  # The runs must be a list
            gLogger.exception("Invalid run range", runs, lException=ex)
            raise BadRunRange
    else:
        if "StartRun" in bkQuery:
            bkQuery.pop("StartRun")
        if "EndRun" in bkQuery:
            bkQuery.pop("EndRun")
    return bkQuery


class BKQuery:
    """It used to build a dictionary using a given Bookkeeping path which is used
    to query the Bookkeeping database."""

    def __init__(self, bkQuery=None, prods=None, runs=None, fileTypes=None, visible=True, eventTypes=None):
        prods = prods if prods is not None else []
        runs = runs if runs is not None else []
        fileTypes = fileTypes if fileTypes is not None else []

        self.extraBKitems = ("StartRun", "EndRun", "Production", "RunNumber")
        self.__bkClient = BookkeepingClient()
        bkPath = ""
        bkQueryDict = {}
        self.__bkFileTypes = set()
        self.__exceptFileTypes = set()
        self.__fakeAllDST = "ZZZZZZZZALL.DST"
        self.__alreadyWarned = False
        if isinstance(bkQuery, BKQuery):
            bkQueryDict = bkQuery.getQueryDict().copy()
        elif isinstance(bkQuery, dict):
            bkQueryDict = bkQuery.copy()
        elif isinstance(bkQuery, six.string_types):
            bkPath = bkQuery
        bkQueryDict = self.buildBKQuery(
            bkPath=bkPath,
            bkQueryDict=bkQueryDict,
            prods=prods,
            runs=runs,
            fileTypes=fileTypes,
            eventTypes=eventTypes,
            visible=visible,
        )
        self.__bkPath = bkPath
        self.__bkQueryDict = bkQueryDict
        if not bkQueryDict.get("Visible"):
            self.setVisible(visible)

    def __str__(self):
        return str(self.__bkQueryDict)

    def buildBKQuery(
        self, bkPath="", bkQueryDict=None, prods=None, runs=None, fileTypes=None, visible=True, eventTypes=None
    ):
        """it builds a dictionary using a path."""
        bkQueryDict = bkQueryDict if bkQueryDict is not None else {}
        prods = prods if prods is not None else []
        if not isinstance(prods, list):
            prods = [prods]
        runs = runs if runs is not None else []
        fileTypes = fileTypes if fileTypes is not None else []

        gLogger.verbose(
            "BKQUERY.buildBKQuery: Path %s, Dict %s, \
      Prods %s, Runs %s, FileTypes %s, EventTypes %s, Visible %s"
            % (bkPath, str(bkQueryDict), str(prods), str(runs), str(fileTypes), str(eventTypes), visible)
        )
        self.__bkQueryDict = {}
        if not bkPath and not prods and not bkQueryDict and not runs:
            return {}
        if bkQueryDict:
            bkQuery = bkQueryDict.copy()
        else:
            bkQuery = {}

        # Query given as a path /ConfigName/ConfigVersion/ConditionDescription/ProcessingPass/EventType/FileType
        # or if prefixed with evt: /ConfigName/ConfigVersion/EventType/ConditionDescription/ProcessingPass/FileType
        if bkPath:
            self.__getAllBKFileTypes()
            bkFields = (
                "ConfigName",
                "ConfigVersion",
                "ConditionDescription",
                "ProcessingPass",
                "EventType",
                "FileType",
            )
            url = bkPath.split(":", 1)
            if len(url) == 1:
                bkPath = url[0]
            else:
                if url[0] in ("evt", "evt+std"):
                    bkFields = (
                        "ConfigName",
                        "ConfigVersion",
                        "EventType",
                        "ConditionDescription",
                        "ProcessingPass",
                        "FileType",
                    )
                elif url[0] == "pp":
                    bkFields = ("ProcessingPass", "EventType", "FileType")
                elif url[0] == "prod":
                    bkFields = ("Production", "ProcessingPass", "EventType", "FileType")
                elif url[0] == "runs":
                    bkFields = ("Runs", "ProcessingPass", "EventType", "FileType")
                elif url[0] not in ("sim", "daq", "cond"):
                    gLogger.error("Invalid BK path:%s" % bkPath)
                    return self.__bkQueryDict
                bkPath = url[1]
            if bkPath[0] != "/":
                bkPath = "/" + bkPath
            if bkPath[0:2] == "//":
                bkPath = bkPath[1:]
            bkPath = bkPath.replace("RealData", "Real Data")
            i = 0
            processingPass = "/"
            defaultPP = False
            bk = bkPath.split("/")[1:] + len(bkFields) * [""]
            for bpath in bk:
                gLogger.verbose(
                    "buildBKQuery.1. Item #%d, Field %s, From Path %s, ProcessingPass %s"
                    % (i, bkFields[i], bpath, processingPass)
                )
                if bkFields[i] == "ProcessingPass":
                    if (
                        bpath != ""
                        and bpath.upper() != "ALL"
                        and not bpath.split(",")[0].split(" ")[0].isdigit()
                        and not bpath.upper() in self.__bkFileTypes
                    ):
                        processingPass = os.path.join(processingPass, bpath)
                        continue
                    # Set the PP
                    if processingPass != "/":
                        bkQuery["ProcessingPass"] = processingPass
                    else:
                        defaultPP = True
                    i += 1
                gLogger.verbose(
                    "buildBKQuery.2. Item #%d, Field %s, From Path %s, ProcessingPass %s"
                    % (i, bkFields[i], bpath, processingPass)
                )
                if bkFields[i] == "EventType" and bpath:
                    eventTypeList = []
                    # print b
                    if bpath.upper() == "ALL":
                        bpath = "ALL"
                    else:
                        for et in bpath.split(","):
                            try:
                                eventType = int(et.split(" ")[0])
                                eventTypeList.append(eventType)
                            except ValueError:
                                pass
                        if len(eventTypeList) == 1:
                            eventTypeList = eventTypeList[0]
                        bpath = eventTypeList
                        gLogger.verbose("buildBKQuery. Event types %s" % eventTypeList)
                # Set the BK dictionary item
                if bpath != "":
                    bkQuery[bkFields[i]] = bpath
                if defaultPP:
                    # PP was empty, try once more to get the Event Type
                    defaultPP = False
                else:
                    # Go to next item
                    i += 1
                if i == len(bkFields):
                    break

            gLogger.verbose("buildBKQuery. Query dict %s" % str(bkQuery))
            # Set default event type to real data
            if bkQuery.get("ConfigName") != "MC" and not bkQuery.get("EventType"):
                bkQuery["EventType"] = "90000000"
            if bkQuery.get("EventType") == "ALL":
                bkQuery.pop("EventType")

        # Run limits are given
        runs = bkQuery.pop("Runs", runs)
        if runs:
            try:
                bkQuery = parseRuns(bkQuery, runs)
            except BadRunRange:
                return self.__bkQueryDict

        # Query given as a list of production
        if prods and str(prods[0]).upper() != "ALL":
            try:
                bkQuery.setdefault("Production", []).extend([int(prod) for prod in prods])
            except ValueError as ex:  # The prods list does not contains numbers
                gLogger.warn(ex)
                gLogger.error("Invalid production list", str(prods))
                return self.__bkQueryDict

        # If an event type is specified
        if eventTypes:
            bkQuery["EventType"] = eventTypes

        # Set the file type(s) taking into account excludes file types
        fileTypes = bkQuery.get("FileType", fileTypes)
        bkQuery.pop("FileType", None)
        self.__bkQueryDict = bkQuery.copy()
        fileType = self.__fileType(fileTypes)
        # print fileType
        if fileType:
            bkQuery["FileType"] = fileType

        # Remove all "ALL"'s in the dict, if any
        for i in self.__bkQueryDict:
            if isinstance(bkQuery[i], six.string_types) and bkQuery[i] == "ALL":
                bkQuery.pop(i)

        # If there is only one production, make it faster with a single value rather than a list
        prodList = bkQuery.get("Production")
        if isinstance(prodList, list) and len(prodList) == 1:
            bkQuery["Production"] = prodList[0]
        self.__bkQueryDict = bkQuery.copy()
        self.setVisible(visible)

        # Set both event type entries
        # print "Before setEventType", self.__bkQueryDict
        if not self.setEventType(bkQuery.get("EventType")):
            self.__bkQueryDict = {}
            return self.__bkQueryDict
        # Set conditions
        # print "Before setConditions", self.__bkQueryDict
        self.setConditions(
            bkQuery.get(
                "ConditionDescription", bkQuery.get("DataTakingConditions", bkQuery.get("SimulationConditions"))
            )
        )
        # print "Returned value", self.__bkQueryDict
        return self.__bkQueryDict

    def setOption(self, key, val):
        """It insert an item to the dictionary.

        The key is an bookkeeping attribute (condition).
        """
        if val:
            self.__bkQueryDict[key] = val
        else:
            self.__bkQueryDict.pop(key, None)
        return self.__bkQueryDict

    def setConditions(self, cond=None):
        """Set the dictionary items for a given condition, or remove it
        (cond=None)"""
        if "ConfigName" not in self.__bkQueryDict and cond:
            gLogger.warn("Impossible to set Conditions to a BK Query without Configuration")
            return self.__bkQueryDict
        # There are two items in the dictionary: ConditionDescription and Simulation/DataTaking-Conditions
        eventType = self.__bkQueryDict.get("EventType", "ALL")
        if self.__bkQueryDict.get("ConfigName") == "MC" or (
            isinstance(eventType, six.string_types) and eventType.upper() != "ALL" and eventType[0] != "9"
        ):
            conditionsKey = "SimulationConditions"
        else:
            conditionsKey = "DataTakingConditions"
        self.setOption("ConditionDescription", cond)
        return self.setOption(conditionsKey, cond)

    def setFileType(self, fileTypes=None):
        """insert the file type to the Boookkeeping dictionary."""
        return self.setOption("FileType", self.__fileType(fileTypes))

    def setDQFlag(self, dqFlag="OK"):
        """Sets the data quality."""
        if isinstance(dqFlag, six.string_types):
            dqFlag = dqFlag.upper()
        elif isinstance(dqFlag, list):
            dqFlag = [dq.upper() for dq in dqFlag]
        return self.setOption("DataQuality", dqFlag)

    def setStartDate(self, startDate):
        """Sets the start date."""
        return self.setOption("StartDate", startDate)

    def setEndDate(self, endDate):
        """Sets the end date."""
        return self.setOption("EndDate", endDate)

    def setProcessingPass(self, processingPass):
        """Sets the processing pass."""
        return self.setOption("ProcessingPass", processingPass)

    def setEventType(self, eventTypes=None):
        """Sets the event type."""
        if eventTypes:
            if isinstance(eventTypes, six.string_types):
                eventTypes = eventTypes.split(",")
            elif not isinstance(eventTypes, list):
                eventTypes = [eventTypes]
            try:
                eventTypes = [str(int(et)) for et in eventTypes]
            except ValueError as ex:
                gLogger.warn(ex)
                gLogger.error("Invalid list of event types", eventTypes)
                return {}
            if isinstance(eventTypes, list) and len(eventTypes) == 1:
                eventTypes = eventTypes[0]
        return self.setOption("EventType", eventTypes)

    def setVisible(self, visible=None):
        """Sets the visibility flag."""
        if visible is True or (isinstance(visible, six.string_types) and visible[0].lower() == "y"):
            visible = "Yes"
        if visible is False:
            visible = "No"
        return self.setOption("Visible", visible)

    def setExceptFileTypes(self, fileTypes):
        """Sets the expected file types."""
        if not isinstance(fileTypes, list):
            fileTypes = [fileTypes]
        self.__exceptFileTypes.update(fileTypes)
        self.setFileType([t for t in self.getFileTypeList() if t not in fileTypes])

    def getExceptFileTypes(self):
        return list(self.__exceptFileTypes)

    def getQueryDict(self):
        """Returns the bookkeeping dictionary."""
        return self.__bkQueryDict

    def getPath(self):
        """Returns the Bookkeeping path."""
        return self.__bkPath

    def makePath(self):
        """Builds a path from the dictionary."""
        bk = self.__bkQueryDict
        fileType = bk.get("FileType", "")
        if isinstance(fileType, list):
            fileType = ",".join(fileType)
        path = os.path.join(
            "/",
            bk.get("ConfigName", ""),
            bk.get("ConfigVersion", ""),
            bk.get("ConditionDescription", "."),
            bk.get("ProcessingPass", ".")[1:],
            str(bk.get("EventType", ".")).replace("90000000", "."),
            fileType,
        ).replace("/./", "//")
        while True:
            if path.endswith("/"):
                path = path[:-1]
            else:
                return path

    def getFileTypeList(self):
        """Returns the file types."""
        fileTypes = self.__bkQueryDict.get("FileType", [])
        if not isinstance(fileTypes, list):
            fileTypes = [fileTypes]
        return fileTypes

    def getEventTypeList(self):
        """Returns the event types."""
        eventType = self.__bkQueryDict.get("EventType", [])
        if eventType:
            if not isinstance(eventType, list):
                eventType = [eventType]
        return eventType

    def getProcessingPass(self):
        """Returns the processing pass."""
        return self.__bkQueryDict.get("ProcessingPass", "")

    def getConditions(self):
        """Returns the Simulation/data taking conditions."""
        return self.__bkQueryDict.get("ConditionDescription", "")

    def getConfiguration(self):
        """Returns the configuration name and configuration version."""
        configName = self.__bkQueryDict.get("ConfigName", "")
        configVersion = self.__bkQueryDict.get("ConfigVersion", "")
        if not configName or not configVersion:
            return ""
        return os.path.join("/", configName, configVersion)

    def isVisible(self):
        """Returns True/False depending on the visibility flag."""
        return self.__bkQueryDict.get("Visible", "All")

    def __fileType(self, fileType=None, returnList=False):
        """return the file types taking into account the expected file types."""
        gLogger.verbose("BKQuery.__fileType: %s, fileType: %s" % (self, fileType))
        if not fileType:
            return []
        self.__getAllBKFileTypes()
        if isinstance(fileType, list):
            fileTypes = fileType
        else:
            fileTypes = fileType.split(",")
        allRequested = None
        if fileTypes[0].lower() == "all":
            allRequested = True
            bkTypes = self.getBKFileTypes()
            gLogger.verbose("BKQuery.__fileType: bkTypes %s" % str(bkTypes))
            if bkTypes:
                fileTypes = list(set(bkTypes) - self.__exceptFileTypes)
            else:
                fileTypes = []
        expandedTypes = set()
        # print "Requested", fileTypes
        for ft in fileTypes:
            if ft.lower() == "all.hist":
                allRequested = False
                expandedTypes.update(
                    [t for t in self.__exceptFileTypes.union(self.__bkFileTypes) if t.endswith("HIST")]
                )
            elif ft.lower().find("all.") == 0:
                ext = "." + ft.split(".")[1]
                ft = []
                if allRequested is None:
                    allRequested = True
                expandedTypes.update(
                    [t for t in set(self.getBKFileTypes()) - self.__exceptFileTypes if t.endswith(ext)]
                )
            else:
                expandedTypes.add(ft)
        # Remove __exceptFileTypes only if not explicitly required
        # print "Obtained", fileTypes, expandedTypes
        gLogger.verbose(
            "BKQuery.__fileType: requested %s, expanded %s, except %s"
            % (allRequested, expandedTypes, self.__exceptFileTypes)
        )
        if expandedTypes - self.__bkFileTypes and not self.__alreadyWarned:
            self.__alreadyWarned = True
            gLogger.always(
                "**** Take care: some requested file types do not exist!!",
                str(sorted(expandedTypes - self.__bkFileTypes)),
            )
        if allRequested or not expandedTypes & self.__exceptFileTypes:
            expandedTypes -= self.__exceptFileTypes
        gLogger.verbose("BKQuery.__fileType: result %s" % sorted(expandedTypes))
        if len(expandedTypes) == 1 and not returnList:
            return list(expandedTypes)[0]
        return list(expandedTypes)

    def __getAllBKFileTypes(self):
        """Returns the file types from the bookkeeping database."""
        if not self.__bkFileTypes:
            self.__bkFileTypes = set([self.__fakeAllDST])
            warned = False
            while True:
                res = self.__bkClient.getAvailableFileTypes()
                if res["OK"]:
                    dbresult = res["Value"]
                    for record in dbresult["Records"]:
                        if (
                            record[0].endswith("HIST")
                            or record[0].endswith("ETC")
                            or record[0] == "LOG"
                            or record[0].endswith("ROOT")
                        ):
                            self.__exceptFileTypes.add(record[0])
                        self.__bkFileTypes.add(record[0])
                    break
                if not warned:
                    gLogger.always("Error getting BK file types, retrying", res["Message"])
                    warned = True

    def __getBKFiles(self, bkQueryDict, retries=5):
        """Call BK getFiles() with some retries."""
        if not retries:
            retries = sys.maxsize
        errorLogged = False
        while retries:
            res = self.__bkClient.getFiles(bkQueryDict)
            if res["OK"]:
                break
            retries -= 1
            if not errorLogged:
                errorLogged = True
                gLogger.warn("Error getting files from BK, retrying...", res["Message"])
        return res

    def getLFNsAndSize(self, getSize=True):
        """Returns the LFNs and their size for a given data set."""
        self.__getAllBKFileTypes()
        res = self.__getBKFiles(self.__bkQueryDict)
        lfns = []
        lfnSize = 0
        if not res["OK"]:
            gLogger.error("Error from BK for %s:" % self.__bkQueryDict, res["Message"])
        else:
            lfns = set(res["Value"])
            exceptFiles = list(self.__exceptFileTypes)
            if exceptFiles and not self.__bkQueryDict.get("FileType"):
                res = self.__getBKFiles(BKQuery(self.__bkQueryDict).setOption("FileType", exceptFiles))
                if res["OK"]:
                    lfnsExcept = set(res["Value"]) & lfns
                else:
                    gLogger.error(
                        "***** ERROR ***** Error in getting dataset from BK for %s files:" % exceptFiles, res["Message"]
                    )
                    lfnsExcept = set()
                if lfnsExcept:
                    gLogger.warn(
                        "***** WARNING ***** Found %d files in BK query that will be excluded!" % len(lfnsExcept)
                    )
                    gLogger.verbose("Exclusion file types", str(exceptFiles))
                    gLogger.warn("                    If creating a transformation, set '--FileType ALL'")
                    lfns = lfns - lfnsExcept
                else:
                    exceptFiles = False
            if getSize:
                # Get size only if needed
                query = BKQuery(self.__bkQueryDict)
                query.setOption("FileSize", True)
                res = self.__getBKFiles(query.getQueryDict())
                if res["OK"] and isinstance(res["Value"], list) and res["Value"][0]:
                    lfnSize = res["Value"][0]
                if exceptFiles and not self.__bkQueryDict.get("FileType"):
                    res = self.__getBKFiles(query.setOption("FileType", exceptFiles))
                    if res["OK"] and isinstance(res["Value"], list) and res["Value"][0]:
                        lfnSize -= res["Value"][0]

                lfnSize /= 1000000000000.0
            else:
                lfnSize = 0.0
        return {"LFNs": list(lfns), "LFNSize": lfnSize}

    def getLFNSize(self, visible=None):
        """Returns the size of a  given data set."""
        if visible is None:
            visible = self.isVisible()
        res = self.__getBKFiles(BKQuery(self.__bkQueryDict, visible=visible).setOption("FileSize", True))
        if res["OK"] and isinstance(res["Value"], list) and res["Value"][0]:
            lfnSize = res["Value"][0]
        else:
            lfnSize = 0
        return lfnSize

    def getNumberOfLFNs(self, visible=None):
        """Returns the number of LFNs correspond to a given data set."""
        if visible is None:
            visible = self.isVisible()
        if self.isVisible() != visible:
            query = BKQuery(self.__bkQueryDict, visible=visible)
        else:
            query = self
        fileTypes = query.getFileTypeList()
        nbFiles = 0
        size = 0

        for ft in fileTypes:
            if ft:
                res = self.__bkClient.getFilesSummary(query.setFileType(ft))
                # print query, res
                if res["OK"]:
                    res = res["Value"]
                    ind = res["ParameterNames"].index("NbofFiles")
                    if res["Records"][0][ind]:
                        nbFiles += res["Records"][0][ind]
                        ind1 = res["ParameterNames"].index("FileSize")
                        size += res["Records"][0][ind1]
                        # print 'Visible',query.isVisible(),ft, 'Files:',
                        # res['Records'][0][ind], 'Size:', res['Records'][0][ind1]
                else:
                    gLogger.error("Error getting files summary", res["Message"])
                    break
        return {"NumberOfLFNs": nbFiles, "LFNSize": size}

    def getLFNs(self, printSEUsage=False, printOutput=True, visible=None):
        """returns a list of lfns.

        It prints statistics about the data sets if it is requested.
        """
        if visible is None:
            visible = self.isVisible()

        if self.isVisible() != visible:
            query = BKQuery(self.__bkQueryDict, visible=visible)
        else:
            query = self

        # Loop for each production or each event type rather than make a single query
        loopItem = None
        prods = self.__bkQueryDict.get("Production")
        eventTypes = self.__bkQueryDict.get("EventType")
        if prods and isinstance(prods, list):
            loopItem = "Production"
            loopList = prods
        elif eventTypes and isinstance(eventTypes, list):
            loopItem = "EventType"
            loopList = eventTypes
        if loopItem:
            # It's faster to loop on a list of prods or event types than query the BK with a list as argument
            lfns = []
            lfnSize = 0
            if query == self:
                query = BKQuery(self.__bkQueryDict, visible=visible)
            for item in loopList:
                query.setOption(loopItem, item)
                lfnsAndSize = query.getLFNsAndSize(getSize=printOutput)
                lfns += lfnsAndSize["LFNs"]
                lfnSize += lfnsAndSize["LFNSize"]
        else:
            lfnsAndSize = query.getLFNsAndSize(getSize=printOutput)
            lfns = lfnsAndSize["LFNs"]
            lfnSize = lfnsAndSize["LFNSize"]

        if not lfns:
            gLogger.verbose("No files found for BK query %s" % str(self.__bkQueryDict))
        else:
            lfns.sort()

            # Only for printing
            if printOutput:
                gLogger.notice("\n%d files (%.1f TB) in directories:" % (len(lfns), lfnSize))
                dirs = {}
                for lfn in lfns:
                    directory = os.path.join(os.path.dirname(lfn), "")
                    dirs[directory] = dirs.setdefault(directory, 0) + 1
                for directory in sorted(dirs):
                    gLogger.notice("%s %s files" % (directory, dirs[directory]))
                if printSEUsage:
                    rpc = StorageUsageClient()
                    totalUsage = {}
                    totalSize = 0
                    for directory in dirs:
                        res = rpc.getStorageSummary(directory, "", "", [])
                        if res["OK"]:
                            for se in [se for se in res["Value"] if not se.endswith("-ARCHIVE")]:
                                totalUsage[se] = totalUsage.setdefault(se, 0) + res["Value"][se]["Size"]
                                totalSize += res["Value"][se]["Size"]
                    ses = sorted(totalUsage)
                    totalUsage["Total"] = totalSize
                    ses.append("Total")
                    gLogger.notice("\n%s %s" % ("SE".ljust(20), "Size (TB)"))
                    for se in ses:
                        gLogger.notice("%s %s" % (se.ljust(20), ("%.1f" % (totalUsage[se] / 1000000000000.0))))
        return lfns

    def getDirs(self, printOutput=False, visible=None):
        """Returns the directories."""
        if visible is None:
            visible = self.isVisible()
        lfns = self.getLFNs(printSEUsage=True, printOutput=printOutput, visible=visible)
        dirs = set()
        for lfn in lfns:
            dirs.add(os.path.dirname(lfn))
        return sorted(dirs)

    @staticmethod
    def __getProdStatus(prod):
        """Returns the status of a given transformation."""
        res = TransformationClient().getTransformation(prod, extraParams=False)
        if not res["OK"]:
            gLogger.error("Could not get information", "on production %d" % prod)
            return None
        return res["Value"]["Status"]

    def getBKRuns(self):
        """It returns a list of runs from the bookkeeping."""
        if self.getProcessingPass().replace("/", "") == "Real Data":
            return self.getBKProductions()

    def getBKProductions(self, visible=None):
        """It returns a list of productions."""
        if visible is None:
            visible = self.isVisible()
        prodList = self.__bkQueryDict.get("Production")
        if prodList:
            if not isinstance(prodList, list):
                prodList = [prodList]
            return sorted(prodList)
        if not self.getProcessingPass():
            gLogger.fatal("Impossible to get a list of productions without the Processing Pass")
            return []
        eventTypes = self.__bkQueryDict.get("EventType")
        if not isinstance(eventTypes, list):
            eventTypes = [eventTypes]
        fullList = set()
        for eventType in eventTypes:
            bkQ = BKQuery(self.__bkQueryDict)
            bkQ.setVisible(visible)
            bkDict = bkQ.setEventType(eventType)
            # gLogger.notice( 'Get productions for BK query', str( bkDict ) )
            res = self.__bkClient.getProductions(bkDict)
            if not res["OK"]:
                gLogger.error("Error getting productions from BK", res["Message"])
                return []
            if self.getProcessingPass().replace("/", "") != "Real Data":
                fileTypes = self.getFileTypeList()
                prodList = set(
                    prod
                    for prods in res["Value"]["Records"]
                    for prod in prods
                    if self.__getProdStatus(prod) != "Deleted"
                )
                # print '\n', self.__bkQueryDict, res['Value']['Records'], '\nVisible:', visible, prodList
                pList = set()
                if fileTypes:
                    transClient = TransformationClient()
                    for prod in prodList:
                        res = transClient.getBookkeepingQuery(prod)
                        if res["OK"] and res["Value"]["FileType"] in fileTypes:
                            pList.add(prod)
                if not pList:
                    pList = prodList
            else:
                runList = sorted([-run for r in res["Value"]["Records"] for run in r])
                startRun = int(self.__bkQueryDict.get("StartRun", 0))
                endRun = int(self.__bkQueryDict.get("EndRun", sys.maxsize))
                pList = set(run for run in runList if run >= startRun and run <= endRun)
            fullList.update(pList)
        return sorted(fullList)

    def getBKConditions(self):
        """It returns the data taking / simulation conditions."""
        conditions = self.__bkQueryDict.get("ConditionDescription")
        if conditions:
            if not isinstance(conditions, list):
                conditions = [conditions]
            return conditions
        result = self.__bkClient.getConditions(self.__bkQueryDict)
        if result["OK"]:
            resList = result["Value"]
        else:
            return []
        conditions = []
        for res in resList:
            ind = res["ParameterNames"].index("Description")
            if res["Records"]:
                conditions += [par[ind] for par in res["Records"]]
                break
        return sorted(conditions)

    def getBKEventTypes(self):
        """It returns the event types."""
        eventType = self.getEventTypeList()
        if eventType:
            return eventType
        res = self.__bkClient.getEventTypes(self.__bkQueryDict)["Value"]
        ind = res["ParameterNames"].index("EventType")
        eventTypes = sorted(rec[ind] for rec in res["Records"])
        return eventTypes

    def getBKFileTypes(self, bkDict=None):
        """It returns the file types."""
        fileTypes = self.getFileTypeList()
        # print "Call getBKFileTypes:", self, fileTypes
        if not fileTypes:
            if not bkDict:
                bkDict = self.__bkQueryDict.copy()
            else:
                bkDict = bkDict.copy()
            bkDict.setdefault("Visible", "All")
            bkDict["ReplicaFlag"] = "All"
            bkDict.pop("RunNumber", None)
            fileTypes = []
            eventTypes = bkDict.get("EventType")
            if isinstance(eventTypes, list):
                for et in eventTypes:
                    bkDict["EventType"] = et
                    fileTypes += self.getBKFileTypes(bkDict)
            else:
                res = self.__bkClient.getFileTypes(bkDict)
                if res["OK"]:
                    res = res["Value"]
                    ind = res["ParameterNames"].index("FileTypes")
                    fileTypes = [rec[ind] for rec in res["Records"] if rec[ind] not in self.__exceptFileTypes]
        if "ALL.DST" in fileTypes:
            fileTypes.remove("ALL.DST")
            fileTypes.append(self.__fakeAllDST)
        # print 'FileTypes1', fileTypes
        fileTypes = self.__fileType(fileTypes, returnList=True)
        # print 'FileTypes2', fileTypes
        if self.__fakeAllDST in fileTypes:
            fileTypes.remove(self.__fakeAllDST)
            fileTypes.append("ALL.DST")
        # print 'FileTypes3', fileTypes
        return fileTypes

    def getBKProcessingPasses(self, queryDict=None, depth=None):
        """It returns the processing pass."""
        if depth is None:
            depth = sys.maxsize
        processingPasses = {}
        if not queryDict:
            queryDict = self.__bkQueryDict.copy()
        initialPP = queryDict.get("ProcessingPass", "/")
        # print "Start", initialPP, queryDict
        res = self.__bkClient.getProcessingPass(queryDict, initialPP)
        if not res["OK"]:
            if "Empty Directory" not in res["Message"]:
                gLogger.error("ERROR getting processing passes for %s" % queryDict, res["Message"])
            return {}
        ppRecords = res["Value"][0]
        if "Name" in ppRecords["ParameterNames"]:
            ind = ppRecords["ParameterNames"].index("Name")
            passes = sorted([os.path.join(initialPP, rec[ind]) for rec in ppRecords["Records"]])
        else:
            passes = []
        evtRecords = res["Value"][1]
        if "EventType" in evtRecords["ParameterNames"]:
            ind = evtRecords["ParameterNames"].index("EventType")
            eventTypes = [str(rec[ind]) for rec in evtRecords["Records"]]
        else:
            eventTypes = []

        if passes and depth:
            depth -= 1
            nextProcessingPasses = {}
            for pName in passes:
                processingPasses[pName] = []
                queryDict["ProcessingPass"] = pName
                nextProcessingPasses.update(self.getBKProcessingPasses(queryDict, depth=depth))
            processingPasses.update(nextProcessingPasses)
        if eventTypes:
            processingPasses[initialPP] = eventTypes
        for pName in ("/Real Data", "/"):
            if pName in processingPasses:
                processingPasses.pop(pName)
        # print "End", initialPP, [(key, processingPasses[key]) for key in sorted(list(processingPasses))]
        return processingPasses
