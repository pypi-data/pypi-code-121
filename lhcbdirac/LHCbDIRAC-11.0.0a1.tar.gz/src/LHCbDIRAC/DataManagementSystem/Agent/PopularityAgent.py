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
:mod: PopularityAgent

.. module: PopularityAgent

:synopsis: The Popularity Agent creates reports about per LFC directory data usage.

The Popularity Agent creates reports about per LFC directory data usage, based on the
StorageUsageDB/Popularity table. Then it creates an accounting record for each directory,
adding all the relevant directory metadata, obtained from the StorageUsageDB/DirMetadata table.
The accounting records are stored in the AccountingDB and then displayed via the web portal.
"""
# imports
from datetime import datetime, timedelta

# # from DIRAC
from DIRAC import S_OK, S_ERROR
from DIRAC.Core.Base.AgentModule import AgentModule
from DIRAC.Core.Utilities import Time
from DIRAC.Core.Utilities.File import mkDir
from DIRAC.AccountingSystem.Client.DataStoreClient import gDataStoreClient
from LHCbDIRAC.AccountingSystem.Client.Types.Popularity import Popularity
from LHCbDIRAC.DataManagementSystem.Client.DataUsageClient import DataUsageClient
from LHCbDIRAC.DataManagementSystem.DB.StorageUsageDB import StorageUsageDB
from LHCbDIRAC.BookkeepingSystem.Client.BookkeepingClient import BookkeepingClient

AGENT_NAME = "DataManagement/PopularityAgent"


class PopularityAgent(AgentModule):
    """
    .. class:: PopularityAgent
    """

    # # DataUsageClient
    __dataUsageClient = None
    # # StorageUsageDB instance or DMS/DataUsage RPS client
    __stDB = None
    # # BKK Client
    __bkClient = None
    # # work directory
    __workDirectory = None
    # # counter for records to be sent to the accouting
    numPopRows = None

    def initialize(self):
        """agent initialisation."""
        self.am_setOption("PollingTime", 43200)
        if self.am_getOption("DirectDB", False):
            self.__stDB = StorageUsageDB()
            # self.bkClient = BookkeepingClient()#the necessary method is still not available in Bookk. client
        else:
            self.__stDB = DataUsageClient()
        self.__bkClient = BookkeepingClient()
        self.__dataUsageClient = DataUsageClient()
        self.__workDirectory = self.am_getOption("WorkDirectory")
        mkDir(self.__workDirectory)
        self.log.info("Working directory is %s" % self.__workDirectory)
        # by default, collects raw records from Popularity table inserted in the last day
        self.timeInterval = self.am_getOption("timeIntervalForPopularityRecords", 1)
        self.queryTimeout = self.am_getOption("queryTimeout", 3600)
        self.cacheMetadata = {}
        self.limitForCommit = self.am_getOption("LimitForCommit", 1000)

        return S_OK()

    # .........................................................................................

    def execute(self):
        """Main loop of Popularity agent."""

        now = datetime.now()
        endTime = datetime(now.year, now.month, now.day, 0, 0, 0)
        startTime = endTime - timedelta(days=self.timeInterval)
        endTimeQuery = endTime.isoformat()
        startTimeQuery = startTime.isoformat()
        # query all traces in popularity in the time rage startTime,endTime and status =new
        # the condition to get th etraces is the AND of the time range and the status new
        self.log.info("Querying Pop db to retrieve entries in time range %s - %s " % (startTimeQuery, endTimeQuery))
        status = "New"
        res = self.__dataUsageClient.getDataUsageSummary(
            startTimeQuery, endTimeQuery, status, timeout=self.queryTimeout
        )
        if not res["OK"]:
            self.log.error("Error querying Popularity table.. %s" % res["Message"])
            return S_ERROR(res["Message"])
        val = res["Value"]
        self.log.info("Retrieved %d entries from Popularity table" % len(val))
        # Build popularity report, and store the Ids in a  list:
        idList = set()
        traceDict = {}
        for row in val:
            self.log.debug("row: %s" % str(row))
            rowId, dirLfn, site, count, insertTime = row
            if rowId not in idList:
                idList.add(rowId)
            else:
                self.log.error("Same Id found twice! %d " % rowId)
                continue
            if dirLfn.startswith("/lhcb/user/"):
                self.log.verbose("Private user directory. No metadata stored in Bkk %s " % dirLfn)
                continue
            # get the day (to do )
            dayBin = (insertTime - startTime).days
            traceDict[dayBin][dirLfn][site] = (
                traceDict.setdefault(dayBin, {}).setdefault(dirLfn, {}).setdefault(site, 0) + count
            )

        # print a summary
        dayList = sorted(traceDict)
        for day in dayList:
            self.log.info(" ###### day %s (starting from %s ) " % (day, startTimeQuery))
            self.log.info("---- %d directories touched:" % len(traceDict[day]))
            for lfn in traceDict[day]:
                self.log.verbose(" ---- lfn %s " % lfn)
                for site in traceDict[day][lfn]:
                    self.log.verbose(" -------- site  %s  count: %d " % (site, traceDict[day][lfn][site]))

        self.log.info("Retrieve meta-data information for each directory ")
        now = Time.dateTime()
        self.numPopRows = 0  # keep a counter of the records to send to accounting data-store
        for day in traceDict:
            timeForAccounting = self.computeTimeForAccounting(startTime, day)
            self.log.info("Processing day %s - time for accounting %s " % (day, timeForAccounting))
            for dirLfn in traceDict[day]:
                # did = configName = configVersion = conditions = processingPass = eventType = fileType = production = "na"
                # retrieve the directory meta-data from the DirMetadata table
                self.log.info("Processing dir %s " % dirLfn)

                metaForDir = self.cacheMetadata.get(dirLfn)
                if not metaForDir:
                    dirList = [dirLfn]
                    # this could be done in a bulk query for a list of directories... TBD
                    res = self.__dataUsageClient.getDirMetadata(dirList)
                    if not res["OK"]:
                        self.log.error("Error retrieving directory meta-data %s " % res["Message"])
                        continue
                    dirMetadata = res["Value"].get(dirLfn)
                    if not res["Value"] or not dirMetadata:
                        self.log.info("Cache missed: query BK to retrieve '%s' metadata and store  cache" % dirList)
                        res = self.__bkClient.getDirectoryMetadata(dirList)
                        if not res["OK"]:
                            self.log.error("Failed to query Bookkeeping %s" % res["Message"])
                            metadata = None
                        else:
                            self.log.verbose("Successfully queried Bookkeeping, result: %s " % res)
                            metadata = res["Value"].get("Successful", {}).get(dirLfn, [{}])[0]
                        if not metadata:
                            self.log.warn("Directory is not registered in Bookkeeping! %s " % dirLfn)
                            configName = (
                                configVersion
                            ) = conditions = processingPass = eventType = fileType = production = "na"
                        else:
                            metadata["Visibility"] = metadata.pop("VisibilityFlag", metadata.get("Visibility", "na"))
                            configName = metadata["ConfigName"]
                            configVersion = metadata["ConfigVersion"]
                            conditions = metadata["ConditionDescription"]
                            processingPass = metadata["ProcessingPass"]
                            eventType = metadata["EventType"]
                            fileType = metadata["FileType"]
                            production = metadata["Production"]

                            self.log.info("Cache this entry in DirMetadata table..")
                            res = self.__dataUsageClient.insertToDirMetadata({dirLfn: metadata})
                            if not res["OK"]:
                                self.log.error("Failed to insert metadata in DirMetadata table! %s " % res["Message"])
                            else:
                                self.log.info(
                                    "Successfully inserted metadata for directory %s in DirMetadata table " % dirLfn
                                )
                                self.log.verbose("result: %s " % res)

                    else:
                        self.log.info("Directory %s was cached in DirMetadata table" % dirLfn)
                        try:
                            (
                                __did,
                                configName,
                                configVersion,
                                conditions,
                                processingPass,
                                eventType,
                                fileType,
                                production,
                            ) = dirMetadata[0:8]
                        except BaseException:
                            self.log.error("Error decoding directory cached information", dirMetadata)
                            continue
                    self.cacheMetadata[dirLfn] = (
                        configName,
                        configVersion,
                        conditions,
                        processingPass,
                        eventType,
                        fileType,
                        production,
                    )
                else:
                    configName, configVersion, conditions, processingPass, eventType, fileType, production = metaForDir

                for site in traceDict[day][dirLfn]:
                    usage = traceDict[day][dirLfn][site]
                    # compute the normalized usage, dividing by the number of files in the directory:
                    normUsage = usage  # to be done! after we have decided how to normalize
                    # Build record for the accounting
                    popRecord = Popularity()
                    popRecord.setStartTime(timeForAccounting)
                    popRecord.setEndTime(timeForAccounting)
                    popRecord.setValueByKey("DataType", configName)
                    popRecord.setValueByKey("Activity", configVersion)
                    popRecord.setValueByKey("FileType", fileType)
                    popRecord.setValueByKey("Production", production)
                    popRecord.setValueByKey("ProcessingPass", processingPass)
                    popRecord.setValueByKey("Conditions", conditions)
                    popRecord.setValueByKey("EventType", eventType)
                    popRecord.setValueByKey("StorageElement", site)
                    popRecord.setValueByKey("Usage", usage)
                    popRecord.setValueByKey("NormalizedUsage", normUsage)
                    res = gDataStoreClient.addRegister(popRecord)
                    if not res["OK"]:
                        self.log.error("ERROR: addRegister returned: %s" % res["Message"])
                        continue
                    self.numPopRows += 1
                    self.log.info(
                        ">>> Sending record to accounting for: %s %s %s %s %s %s %s %s %s %d %d "
                        % (
                            timeForAccounting,
                            configName,
                            configVersion,
                            fileType,
                            production,
                            processingPass,
                            conditions,
                            eventType,
                            site,
                            usage,
                            normUsage,
                        )
                    )
                    if self.numPopRows > self.limitForCommit:
                        res = self.__commitAccounting()
                        if not res["OK"]:
                            return res
        # then set the status to Used
        res = self.__commitAccounting()
        if not res["OK"]:
            return res
        self.log.info("Set the status to Used for %d entries" % len(idList))
        from DIRAC.Core.Utilities.List import breakListIntoChunks

        for idChunk in breakListIntoChunks(list(idList), 1000):
            res = self.__dataUsageClient.updatePopEntryStatus(list(idChunk), "Used", timeout=self.queryTimeout)
            if not res["OK"]:
                self.log.error("Error to update status in  Popularity table.. %s" % res["Message"])
                return res
        self.log.info("Status updated to Used correctly for %s entries " % len(idList))

        return S_OK()

    # .........................................................................................

    def __commitAccounting(self):
        res = gDataStoreClient.commit()
        if not res["OK"]:
            self.log.error("while committing %d Popularity records" % self.numPopRows, res["Message"])
        else:
            self.log.info("%s records for Popularity type successfully committed" % self.numPopRows)
            self.numPopRows = 0
        return res

    def computeTimeForAccounting(self, startTime, day):
        """Compute the time for the accounting record, starting from the start time
        of the query and the day bin."""
        self.log.verbose("find time for accounting for startTime: %s + day %s " % (startTime, day))
        daysToAdd = timedelta(days=day, hours=12)  # add 12h just to put the value in the middle of time bin
        self.log.verbose("timedelta to add: %s " % daysToAdd)
        accTime = startTime + daysToAdd
        self.log.verbose("accTime = %s " % accTime)
        return accTime
