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
"""Methods for scanning the popularity table."""
import os
import time
from datetime import datetime, timedelta

import DIRAC
from DIRAC import gLogger
from DIRAC.Resources.Catalog.FileCatalog import FileCatalog
from DIRAC.Core.Utilities.List import breakListIntoChunks
from DIRAC.DataManagementSystem.Utilities.DMSHelpers import DMSHelpers, resolveSEGroup

from LHCbDIRAC.DataManagementSystem.Client.StorageUsageClient import StorageUsageClient
from LHCbDIRAC.DataManagementSystem.Client.DataUsageClient import DataUsageClient
from LHCbDIRAC.BookkeepingSystem.Client.BookkeepingClient import BookkeepingClient
from LHCbDIRAC.BookkeepingSystem.Client.BKQuery import BKQuery, makeBKPath
from LHCbDIRAC.TransformationSystem.Client.TransformationClient import TransformationClient

# Code
dmsHelper = DMSHelpers()

# Dictionary containing the BK path for each directory
bkPathForDir = {}
# Set of invisible BK paths
cachedInvisible = set()
# Set of productions for each BK path
prodForBKPath = {}
# Storage usage for each BK path
bkPathUsage = {}
# Processing pass for each BK path
processingPass = {}
# PFN #files and size for each BK path
physicalStorageUsage = {}

# Dictionary with weekly/dayly usage for each BK path
bkPathPopularity = {}

storageTypes = ("Disk", "Tape", "Archived", "All", "LFN")
# Set of BK paths for each storage types (above)
datasetStorage = {}

# We are only interested in CERN and Tier1s
storageSites = dmsHelper.getTiers(tier=(0, 1))
# Caching the site at which an SE is
cachedSESites = {}

# Instantiate clients
duClient = DataUsageClient()
suClient = StorageUsageClient()
bkClient = BookkeepingClient()
transClient = TransformationClient()


def getTimeBin(date):
    """get the bin number as week number."""
    year, week, _day = date.isocalendar()
    week += 52 * year
    return week


def cacheDirectories(directories):
    """Get directories information from popularity and from storageUsage and
    cache the information."""

    # Ignore already cached directories
    dirSet = directories - set(bkPathForDir) - cachedInvisible
    if not dirSet:
        return
    startTime = time.time()
    gLogger.always("\nCaching %d directories, %d not cached yet" % (len(directories), len(dirSet)))

    # Some DBs refer to "long" directory names (i.e. with additional number, see below)
    #     while others refer to the unnumbered directory.
    # Make conversion tables and keep only the first directory when numbered
    # Short is for example /lhcb/LHCb/Collision18/RDST/00074101/
    # Long is for example /lhcb/LHCb/Collision18/RDST/00074101/0008/
    dirLong2Short = {}
    dirShort2Long = {}
    for dirLfn in sorted(dirSet):
        splitDir = dirLfn.split("/")
        if len(splitDir[-2]) == 4 and splitDir[-2].isdigit():
            short = "/".join(splitDir[:-2])
        else:
            short = dirLfn
        dirLong2Short[dirLfn] = short
        dirShort2Long.setdefault(short, dirLfn)

    # # Cache BK path for directories
    # First try cached information in Data Usage DB
    chunkSize = 1000
    gLogger.always("Getting cache metadata for %d directories" % len(dirShort2Long))
    dirMetadata = {}
    for longDirs in breakListIntoChunks(dirShort2Long.values(), chunkSize):
        res = duClient.getDirMetadata(longDirs)
        if not res["OK"]:
            gLogger.error("\nError getting metadata from DataUsage", res["Message"])
        else:
            dirMetadata.update(res["Value"])

    invisible = set()
    lfnsFromBK = set()
    for dirLfn in dirSet:
        longDir = dirShort2Long[dirLong2Short[dirLfn]]
        metadata = dirMetadata.get(longDir)
        if metadata:
            if len(metadata) < 9 or metadata[8] != "N":
                bkPathForDir[dirLfn] = os.path.join(
                    "/", metadata[1], metadata[2], metadata[3], metadata[4][1:], metadata[5], metadata[6]
                )
                processingPass[bkPathForDir[dirLfn]] = metadata[4]
                prodForBKPath.setdefault(bkPathForDir[dirLfn], set()).add(metadata[7])
            else:
                invisible.add(dirLfn)
        else:
            lfnsFromBK.add(longDir)

    # For those not available ask the BK
    chunkSize = 100
    if lfnsFromBK:
        gLogger.always("Getting BK metadata for %d directories" % len(lfnsFromBK))
        success = {}
        for lfns in breakListIntoChunks(lfnsFromBK, chunkSize):
            for trial in range(10, -1, -1):
                res = bkClient.getDirectoryMetadata(lfns)
                if not res["OK"]:
                    if not trial:
                        gLogger.fatal("\nError getting BK metadata", res["Message"])
                        DIRAC.exit(1)
                    else:
                        gLogger.warn("Error getting BK metadata, retrying", res["Message"])
                else:
                    break
            success.update(res["Value"].get("Successful", {}))
        gLogger.always("Successfully obtained BK metadata for %d directories" % len(success))
        for dirLfn in dirSet - set(bkPathForDir):
            longDir = dirShort2Long[dirLong2Short[dirLfn]]
            metadata = success.get(longDir, [{}])[0]
            if metadata:
                if metadata.get("VisibilityFlag", metadata.get("Visibility", "Y")) == "Y":
                    bkDict = BKQuery(metadata).getQueryDict()
                    bkPath = makeBKPath(bkDict)
                    processingPass[bkPath] = metadata["ProcessingPass"]
                    prodForBKPath.setdefault(bkPath, set()).add(metadata["Production"])
                else:
                    invisible.add(dirLfn)
            else:
                bkPath = "Unknown-" + dirLfn
                prodForBKPath.setdefault(bkPath, set())
            if dirLfn not in invisible:
                bkPathForDir[dirLfn] = bkPath
                bkPathUsage.setdefault(bkPath, {}).setdefault("LFN", [0, 0])

    # Ignore invisible directories
    if invisible:
        gLogger.always("%d paths are ignored as invisible" % len(invisible))
        cachedInvisible.update(invisible)
        dirSet -= invisible

    # For remaining directories, get the LFN information and the PFN information SE by SE
    if dirSet:
        missingSU = set(dirLong2Short[dirLfn] for dirLfn in dirSet)
        gLogger.always("Get LFN Storage Usage for %d directories" % len(missingSU))
        for dirLfn in missingSU:
            # LFN usage
            for trial in range(10, -1, -1):
                res = suClient.getSummary(dirLfn)
                if res["OK"]:
                    break
                if not trial:
                    gLogger.fatal("Error getting LFN storage usage %s" % dirLfn, res["Message"])
                    DIRAC.exit(1)
            bkPath = bkPathForDir[dirShort2Long[dirLfn]]
            infoType = "LFN"
            gLogger.verbose("Directory %s: %s" % (dirLfn, str(res["Value"])))
            bkPathUsage.setdefault(bkPath, {}).setdefault(infoType, [0, 0])
            bkPathUsage[bkPath][infoType][0] += sum(val.get("Files", 0) for val in res["Value"].values())
            bkPathUsage[bkPath][infoType][1] += sum(val.get("Size", 0) for val in res["Value"].values())

        # # get the PFN usage per storage type
        # Storage type is Disk, Archived, Tape and All
        gLogger.always("Check storage type and PFN usage for %d directories" % len(dirSet))
        for dirLfn in dirSet:
            for trial in range(10, -1, -1):
                res = suClient.getDirectorySummaryPerSE(dirLfn)
                if not res["OK"]:
                    if not trial:
                        gLogger.fatal("Error getting storage usage per SE", "%s %s" % (dirLfn, res["Message"]))
                        DIRAC.exit(1)
                    else:
                        gLogger.warn("Error getting storage usage per SE, retrying", "%s %s" % (dirLfn, res["Message"]))
                else:
                    break
            info = physicalStorageUsage.setdefault(dirLfn, {})
            for infoType in storageTypes:
                # Active type will be recorded in Disk, just a special flag
                if infoType != "LFN" and infoType not in info:
                    nf = sum(val["Files"] for se, val in res["Value"].items() if isType(se, infoType))
                    size = sum(val["Size"] for se, val in res["Value"].items() if isType(se, infoType))
                    info[infoType] = {"Files": nf, "Size": size}
            for site in storageSites:
                if site not in info:
                    nf = sum(
                        val["Files"] for se, val in res["Value"].items() if isAtSite(se, site) and isType(se, "Disk")
                    )
                    size = sum(
                        val["Size"] for se, val in res["Value"].items() if isAtSite(se, site) and isType(se, "Disk")
                    )
                    info[site] = {"Files": nf, "Size": size}
            bkPath = bkPathForDir[dirLfn]
            for infoType in info:
                bkPathUsage.setdefault(bkPath, {}).setdefault(infoType, [0, 0])
                bkPathUsage[bkPath][infoType][0] += info[infoType].get("Files", 0)
                bkPathUsage[bkPath][infoType][1] += info[infoType].get("Size", 0)
            datasetStorage[storageType(res["Value"])].add(bkPath)

    gLogger.always(
        "Obtained BK path and storage usage of %d directories in %.1f seconds" % (len(dirSet), time.time() - startTime)
    )


def isType(se, infoType):
    """check if an SE is of a given type."""
    if infoType == "All":
        return True
    if infoType == "LFN":
        return False
    return storageType([se]) == infoType


def isAtSite(se, site):
    """checks if an SE is at a given site."""
    seSite = cachedSESites.get(se)
    if seSite is None:
        seSite = dmsHelper.getLocalSiteForSE(se)
        if seSite["OK"]:
            cachedSESites[se] = seSite["Value"]
    return site == seSite


def prBinNumber(binNumber):
    """Return bin number as a string."""
    week = binNumber
    year = week / 52
    week = week % 52
    return "y%4d/w%02d" % (year, week)


def prSize(size):
    """Return size as a string with sensible unit."""
    units = ("Bytes", "kB", "MB", "GB", "TB", "PB")
    for unit in units:
        if size < 1000.0:
            return "%.1f %s" % (size, unit)
        size /= 1000.0
    return "???"


def getPhysicalUsage(baseDir):
    """Extract information about storage usage from the StorageusageDB."""
    for trial in range(10, -1, -1):
        res = suClient.getStorageDirectoryData(baseDir, None, None, None, timeout=3600)
        if not res["OK"]:
            if not trial:
                gLogger.fatal("Error getting list of directories for %s" % baseDir, res["Message"])
                DIRAC.exit(1)
        else:
            break
    # The returned value is a dictionary of all directory leaves
    info = res["Value"]
    dirSet = set()
    nf = 0
    size = 0
    gLogger.info("Storage usage OK for %d directories in %s" % (len(info), baseDir))
    for directory in info:
        nodes = directory.split("/")
        try:
            prod = int(nodes[5])
            # FIXME
            # Don't count the certification productions
            if prod < 2000 and nodes[2] == "validation":
                continue
        except (IndexError, ValueError):
            pass
        if len(nodes) < 5 or nodes[4] not in ("LOG", "HIST", "BRUNELHIST", "DAVINCIHIST", "GAUSSHIST"):
            physicalStorageUsage.setdefault(directory, {}).setdefault("All", info[directory])
            dirSet.add(directory)
            nf += info[directory]["Files"]
            size += info[directory]["Size"]
    # In case the base directory was not a leave, cache its physical storage data
    physicalStorageUsage.setdefault(baseDir, {}).setdefault("All", {"Files": nf, "Size": size})
    return dirSet


def storageType(seList):
    """Return the storage type: disk, tape or archive."""
    if not (
        set(se for se in seList if not dmsHelper.isSEArchive(se))
        - set(["CERN-SWTEST", "CERN-FREEZER-EOS", "CERN-FREEZER"])
    ) and set(se for se in seList if dmsHelper.isSEArchive(se)):
        # Only -ARCHIVE
        return "Archived"
    tapeSEs = resolveSEGroup("Tier1-RAW") + resolveSEGroup("Tier1-RDST")
    if [se for se in seList if se in tapeSEs]:
        # Any file on Tape
        return "Tape"
    # Others
    return "Disk"


def scanPopularity(since, getAllDatasets, topDirectory="/lhcb", csvFile=None):
    """That function does the job to cache the directories, get the corresponding
    datasets and join with the popularity."""
    # Reset global variables

    bkPathForDir.clear()
    cachedInvisible.clear()
    prodForBKPath.clear()
    bkPathUsage.clear()
    processingPass.clear()
    bkPathPopularity.clear()
    physicalStorageUsage.clear()
    datasetStorage.clear()
    for infoType in storageTypes:
        datasetStorage[infoType] = set()

    # set of used directories
    usedDirectories = set()
    usedSEs = {}
    binSize = "week"
    nbBins = int((since + 6) / 7)
    since = 7 * nbBins

    from DIRAC.ConfigurationSystem.Client.Helpers.Operations import Operations

    ignoreDirectories = Operations().getValue(
        "DataManagement/PopularityIgnoreDirectories",
        ["user", "test", "debug", "dataquality", "software", "database", "swtest", "certification", "validation"],
    )
    nowBin = getTimeBin(datetime.now() - timedelta(days=1))
    notCached = set()

    if getAllDatasets:
        # Get list of directories
        startTime = time.time()
        res = FileCatalog().listDirectory(topDirectory)
        if not res["OK"]:
            gLogger.fatal("Cannot get list of directories", res["Message"])
            DIRAC.exit(1)
        directories = set(
            subDir
            for subDir in res["Value"]["Successful"][topDirectory]["SubDirs"]
            if subDir.split("/")[2] not in ignoreDirectories
            and "RAW" not in subDir
            and "RDST" not in subDir
            and "SDST" not in subDir
        )
        allDirectoriesSet = set()
        for baseDir in directories:
            allDirectoriesSet.update(getPhysicalUsage(baseDir))
        gLogger.always(
            "Obtained %d directories storage usage information in %.1f seconds)"
            % (len(allDirectoriesSet), time.time() - startTime)
        )
        cacheDirectories(allDirectoriesSet)

    # Get the popularity raw information for the specified number of days
    if since:
        entries = 0
        now = datetime.now()
        endTime = datetime(now.year, now.month, now.day, 0, 0, 0)
        startTime = endTime
        gLogger.always("Get popularity day-by-day")
        stTime = time.time()
        for _i in range(since):
            endTime = startTime
            startTime = endTime - timedelta(days=1)
            endTimeQuery = endTime.isoformat()
            startTimeQuery = startTime.isoformat()
            status = "Used"
            # Getting the popularity with 10 retries for the given day
            for _i in range(10):
                res = duClient.getDataUsageSummary(startTimeQuery, endTimeQuery, status, timeout=7200)
                if res["OK"]:
                    break
                gLogger.error("Error getting popularity entries, retrying...", res["Message"])
            if not res["OK"]:
                gLogger.fatal("Error getting popularity entries", res["Message"])
                DIRAC.exit(1)
            val = res["Value"]
            entries += len(val)

            # Get information on useful directories
            directories = set(row[1] for row in val if row[1].split("/")[2] not in ignoreDirectories)
            usedDirectories.update(directories)
            cacheDirectories(directories)

            # Get information in bins (day or week)
            for _rowId, dirLfn, se, count, insertTime in val:
                if dirLfn not in directories:
                    # print rowId, dirLfn, count, insertTime, 'ignored'
                    continue
                # get the binNumber (day or week)
                binNumber = getTimeBin(insertTime)
                bkPath = bkPathForDir.get(dirLfn)
                if not bkPath:
                    if dirLfn not in notCached:
                        notCached.add(dirLfn)
                        gLogger.error("Directory %s was not cached" % dirLfn)
                    bkPath = "Unknown-" + dirLfn
                bkPathPopularity[bkPath][binNumber] = (
                    bkPathPopularity.setdefault(bkPath, {}).setdefault(binNumber, 0) + count
                )
                usedSEs.setdefault(bkPath, set()).add(se)

        gLogger.always("\n=============================================================")
        gLogger.always("Retrieved %d entries from Popularity table in %.1f seconds" % (entries, time.time() - stTime))
        gLogger.always("Found %d datasets used since %d days" % (len(bkPathPopularity), since))
        counters = {}
        strangeBKPaths = set(
            bkPath for bkPath in bkPathPopularity if not bkPathUsage.get(bkPath, {}).get("LFN", (0, 0))[0]
        )
        if strangeBKPaths:
            gLogger.always("%d used datasets do not have an LFN count:" % len(strangeBKPaths))
            gLogger.always(
                "\n".join("%s : %s" % (bkPath, str(bkPathUsage.get(bkPath, {}))) for bkPath in strangeBKPaths)
            )
        gLogger.always("\nDataset usage for %d datasets" % len(bkPathPopularity))
        for infoType in ("All", "LFN"):
            for i in range(2):
                counters.setdefault(infoType, []).append(
                    sum(bkPathUsage.get(bkPath, {}).get(infoType, (0, 0))[i] for bkPath in bkPathPopularity)
                )
        for bkPath in sorted(bkPathPopularity):
            if bkPath not in datasetStorage["Disk"] | datasetStorage["Archived"] | datasetStorage["Tape"]:
                ses = usedSEs.get(bkPath)
                if ses is None:
                    gLogger.error("BK path not in usedSEs", bkPath)
                else:
                    datasetStorage[storageType(ses)].add(bkPath)
            nLfns, lfnSize = bkPathUsage.get(bkPath, {}).get("LFN", (0, 0))
            nPfns, pfnSize = bkPathUsage.get(bkPath, {}).get("All", (0, 0))
            gLogger.always(
                "%s (%d LFNs, %s), (%d PFNs, %s, %.1f replicas)"
                % (
                    bkPath,
                    nLfns,
                    prSize(lfnSize),
                    nPfns,
                    prSize(pfnSize),
                    float(nPfns) / float(nLfns) if nLfns else 0.0,
                )
            )
            bins = sorted(bkPathPopularity[bkPath])
            lastBin = bins[-1]
            accesses = sum(bkPathPopularity[bkPath][binNumber] for binNumber in bins)
            gLogger.always(
                "\tUsed first in %s, %d accesses (%.1f%%), %d accesses during last %s %s"
                % (
                    prBinNumber(bins[0]),
                    accesses,
                    accesses * 100.0 / nLfns if nLfns else 0.0,
                    bkPathPopularity[bkPath][lastBin],
                    binSize,
                    prBinNumber(lastBin),
                )
            )
        gLogger.always(
            "\nA total of %d LFNs (%s), %d PFNs (%s) have been used"
            % (counters["LFN"][0], prSize(counters["LFN"][1]), counters["All"][0], prSize(counters["All"][1]))
        )

    if getAllDatasets:
        # Consider only unused directories
        unusedDirectories = allDirectoriesSet - usedDirectories
        if unusedDirectories:
            gLogger.always("\n=============================================================")
            gLogger.always("%d directories have not been used" % len(unusedDirectories))
            # Remove the used datasets (from other directories)
            unusedBKPaths = set(bkPathForDir[dirLfn] for dirLfn in unusedDirectories if dirLfn in bkPathForDir) - set(
                bkPathPopularity
            )
            # Remove empty datasets
            strangeBKPaths = set(
                bkPath for bkPath in unusedBKPaths if not bkPathUsage.get(bkPath, {}).get("LFN", (0, 0))[0]
            )
            if strangeBKPaths:
                gLogger.always("%d unused datasets do not have an LFN count:" % len(strangeBKPaths))
                gLogger.always(
                    "\n".join("%s : %s" % (bkPath, str(bkPathUsage.get(bkPath, {}))) for bkPath in strangeBKPaths)
                )
            unusedBKPaths = set(bkPath for bkPath in unusedBKPaths if bkPathUsage.get(bkPath, {}).get("LFN", (0, 0))[0])

            # In case there are datasets both on tape and disk, priviledge tape
            datasetStorage["Disk"] -= datasetStorage["Tape"]
            gLogger.always("\nThe following %d BK paths were not used since %d days" % (len(unusedBKPaths), since))
            for infoType in storageTypes[0:3]:
                gLogger.always("\n=========== %s datasets ===========" % infoType)
                unusedPaths = unusedBKPaths & datasetStorage[infoType]
                counters = {}
                for ty in ("All", "LFN"):
                    for i in range(2):
                        counters.setdefault(ty, []).append(
                            sum(bkPathUsage.get(bkPath, {}).get(ty, (0, 0))[i] for bkPath in unusedPaths)
                        )
                for bkPath in sorted(unusedPaths):
                    nLfns, lfnSize = bkPathUsage.get(bkPath, {}).get("LFN", (0, 0))
                    nPfns, pfnSize = bkPathUsage.get(bkPath, {}).get("All", (0, 0))
                    gLogger.always(
                        "\t%s (%d LFNs, %s), (%d PFNs, %s, %.1f replicas)"
                        % (bkPath, nLfns, prSize(lfnSize), nPfns, prSize(pfnSize), float(nPfns) / float(nLfns))
                    )
                gLogger.always(
                    "\nA total of %d %s LFNs (%s), %d PFNs (%s) were not used"
                    % (
                        counters["LFN"][0],
                        infoType,
                        prSize(counters["LFN"][1]),
                        counters["All"][0],
                        prSize(counters["All"][1]),
                    )
                )
    else:
        unusedBKPaths = set()
        datasetStorage["Disk"] -= datasetStorage["Tape"]

    # Now create a CSV file with all dataset information
    # Name, ProcessingPass, #files, size, SE type, each week's usage (before now)
    csvFile = "popularity-%ddays.csv" % since if csvFile is None else csvFile
    gLogger.always("\n=============================================================")
    gLogger.always("Creating %s file with %d datasets" % (csvFile, len(bkPathPopularity) + len(unusedBKPaths)))
    with open(csvFile, "w") as fd:
        title = (
            "Name;Configuration;ProcessingPass;FileType;Type;Creation-%s;" % binSize
            + "NbLFN;LFNSize;NbDisk;DiskSize;NbTape;TapeSize;NbArchived;ArchivedSize;"
            + ";".join(site.split(".")[1] for site in storageSites)
            + ";Nb Replicas;Nb ArchReps;Storage;FirstUsage;LastUsage;Now"
        )
        for binNumber in range(nbBins):
            title += ";%d" % (1 + binNumber)
        fd.write(title + "\n")
        teraByte = 1000.0 * 1000.0 * 1000.0 * 1000.0
        for bkPath in sorted(bkPathPopularity) + sorted(unusedBKPaths):
            # Skip unknown datasets
            if bkPath.startswith("Unknown-"):
                continue
            # Not interested in histograms
            splitBKPath = bkPath.split("/")
            fileType = splitBKPath[-1]
            if "HIST" in fileType:
                continue
            # Only RAW for partition LHCb may be of interest (and even...)
            if fileType == "RAW" and not bkPath.startswith("/LHCb"):
                continue
            info = bkPathUsage.get(bkPath, {})
            # check if the production is still active
            prods = prodForBKPath[bkPath]
            res = transClient.getTransformations({"TransformationID": list(prods)})
            creationTime = datetime.now()
            active = []
            for prodDict in res.get("Value", []):
                creationTime = min(creationTime, prodDict["CreationDate"])
                if prodDict["Status"] in ("Active", "Idle", "Completed"):
                    active.append(str(prodDict["TransformationID"]))
            if active:
                gLogger.always("Active productions %s found in %s" % (",".join(sorted(active)), bkPath))
            if info["LFN"][0] == 0:
                continue
            for infoType in info:
                info[infoType][1] /= teraByte
            # Some BK paths contain a , to be replaces by a . for the CSV file!!
            config = "/".join(splitBKPath[0:3])
            if "," in bkPath:
                gLogger.always("BK path found with ',':", bkPath)
            # Name,Configuration,ProcessingPass, FileType
            row = "%s;%s;%s;%s" % (
                bkPath.replace("Real Data", "RealData"),
                config,
                processingPass.get(bkPath, "Unknown").replace("Real Data", "RealData"),
                fileType,
            )
            # Type
            configTypes = {"/MC/Dev": 2, "/MC/Upgrade": 3}
            configType = configTypes.get(config, 0 if bkPath.startswith("/MC") else 1)
            row += ";%d" % configType
            # CreationTime
            row += ";%d" % (getTimeBin(creationTime))
            # NbLFN,LFNSize,NbDisk,DiskSize,NbTape,TapeSize, NbArchived,ArchivedSize
            for infoType in ("LFN", "Disk", "Tape", "Archived"):
                row += ";%d;%f" % tuple(info[infoType])
            for site in storageSites:
                row += ";%f" % info[site][1]
            row += ";%f;%f" % (
                float(info["Disk"][0]) / float(info["LFN"][0]),
                float(info["Archived"][0]) / float(info["LFN"][0]),
            )
            if active:
                dsType = "Active"
            else:
                dsType = "Unknown"
                for infoType in storageTypes[0:3]:
                    if bkPath in datasetStorage[infoType]:
                        dsType = infoType
                        break
            row += ";%s" % dsType
            bins = sorted(bkPathPopularity.get(bkPath, {}))
            if not bins:
                bins = [0]
            row += ";%d;%d;%d" % (bins[0], bins[-1], nowBin)
            usage = 0
            for binNumber in range(nbBins):
                usage += bkPathPopularity.get(bkPath, {}).get(nowBin - binNumber, 0)
                row += ";%d" % usage
            fd.write(row + "\n")
    gLogger.always("\nSuccessfully wrote CSV file %s" % csvFile)
