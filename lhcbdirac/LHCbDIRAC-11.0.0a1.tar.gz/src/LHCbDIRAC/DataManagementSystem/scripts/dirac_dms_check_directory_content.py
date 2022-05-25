#!/usr/bin/env python
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
"""For a given LFN directory, check the files that are registered in the FC and
checks that they exist on the SE, and in Bookkeeping, with the  correct
ReplicaFlag."""
import DIRAC
from DIRAC.Core.Base.Script import Script


@Script()
def main():

    unit = "TB"
    sites = []
    dir = ""
    fileType = ""
    prods = []
    prodID = ""
    verbose = False
    Script.registerSwitch("u:", "Unit=", "   Unit to use [%s] (MB,GB,TB,PB)" % unit)
    Script.registerSwitch("D:", "Dir=", "  directory to be checked: mandatory argument")
    Script.registerSwitch("f:", "Output=", " output file name [dirac-dms-chec-dir-cont.out]")
    Script.registerSwitch("v", "Verbose", " use this option for verbose output [False]")

    Script.setUsageMessage(
        __doc__
        + "\n".join(
            [
                "Usage:",
                "  %s [option|cfgfile] ..." % Script.scriptName,
            ]
        )
    )

    Script.parseCommandLine(ignoreErrors=False)

    from DIRAC.Resources.Catalog.FileCatalog import FileCatalog
    from DIRAC.Resources.Storage.StorageElement import StorageElement
    from LHCbDIRAC.BookkeepingSystem.Client.BookkeepingClient import BookkeepingClient

    bkClient = BookkeepingClient()

    outputFileName = "dirac-dms-chec-dir-cont.out"

    for switch in Script.getUnprocessedSwitches():
        if switch[0].lower() == "u" or switch[0].lower() == "unit":
            unit = switch[1]
        if switch[0] == "D" or switch[0].lower() == "dir":
            dir = switch[1]
        if switch[0] == "f" or switch[0].lower() == "output":
            outputFile = switch[1]
            outputFileName = outputFile
        if switch[0] == "v" or switch[0].lower() == "verbose":
            verbose = True

    if verbose:
        print("Verbose output")

    if not dir:
        print("One directory should be provided!")
        Script.showHelp()

    scaleDict = {
        "MB": 1000 * 1000.0,
        "GB": 1000 * 1000 * 1000.0,
        "TB": 1000 * 1000 * 1000 * 1000.0,
        "PB": 1000 * 1000 * 1000 * 1000 * 1000.0,
    }
    if unit not in scaleDict:
        Script.showHelp()
    scaleFactor = scaleDict[unit]

    currentDir = dir
    print("Obtaining the catalog contents for %s directory" % currentDir)
    res = FileCatalog().listDirectory(currentDir)
    if not res["OK"]:
        print("ERROR: Cannot get directory content")
        DIRAC.exit(-1)

    successfulDirs = res["Value"]["Successful"]
    failedDirs = res["Value"]["Failed"]
    print("Failed directories: % s" % list(failedDirs))
    print("Successful directories: % s" % list(successfulDirs))

    if not successfulDirs:
        print("No directory to analyse. Exit.")
        DIRAC.exit(0)

    if verbose:
        print("Analysing directory: %s " % currentDir)
    dirData = successfulDirs[currentDir]
    NumOfFilesInLFC = len(dirData["Files"])
    if verbose:
        print("Number of files registered in LFC: %d " % NumOfFilesInLFC)
    LFNsInLFC = list(dirData["Files"])
    # print 'List of lfns in lfc: ' , LFNsInLFC

    allFiles = {}
    dirContents = res["Value"]["Successful"][currentDir]
    allFiles.update(dirContents["Files"])

    fp = open(outputFileName, "w")

    zeroReplicaFiles = []
    zeroSizeFiles = []
    allReplicaDict = {}
    allMetadataDict = {}
    problematicFiles = {}
    replicasPerSE = {}
    n = 10
    totalSoFar = 0
    fp.write("-------- Checks FC -> SE ---------------------------------------------------------\n")
    for lfn, lfnDict in allFiles.items():
        # checks LFC -> SE
        totalSoFar += 1
        if totalSoFar % n == 0:
            print("%d LFNs processed so far. %d left" % (totalSoFar, len(LFNsInLFC) - totalSoFar))
        if verbose:
            fp.write("LFN: %s\n" % lfn)
        lfnReplicas = []
        for se, replicaDict in lfnDict["Replicas"].items():
            # print 'SE: %s -- replica: %s ' % ( se, replicaDict )
            lfnReplicas.append(se)
            if not lfnReplicas:
                zeroReplicaFiles.append(lfn)
        allReplicaDict[lfn] = lfnReplicas
        allMetadataDict[lfn] = lfnDict["MetaData"]
        if lfnDict["MetaData"]["Size"] == 0:
            zeroSizeFiles.append(lfn)
        if verbose:
            fp.write("All replicas: %s \n" % lfnReplicas)
        # check each replica if it is exists on the storage
        for se in lfnReplicas:
            if se not in replicasPerSE:
                replicasPerSE[se] = []
            replicasPerSE[se].append(lfn)
            if verbose:
                fp.write("Checking on storage LFN, SE: %s %s\n" % (lfn, se))
            res = StorageElement(se).getFileMetadata(lfn)
            if not res["OK"]:
                fp.write("ERROR: could not get storage file metadata! %s - %s \n" % (lfn, se))
                if lfn not in problematicFiles:
                    problematicFiles[lfn] = {}
                if "BadReplicas" not in problematicFiles[lfn]:
                    problematicFiles[lfn]["BadReplicas"] = []
                problematicFiles[lfn]["BadReplicas"].append(se)
                continue
            if lfn in res["Value"]["Failed"]:
                fp.write("ERROR: bad LFN! %s\n" % lfn)
                if lfn not in problematicFiles:
                    problematicFiles[lfn] = {}
                    if "BadPFN" not in problematicFiles[lfn]:
                        problematicFiles[lfn]["BadPFN"] = []
                    problematicFiles[lfn]["BadPFN"].append(se)
            elif lfn in res["Value"]["Successful"]:
                if verbose:
                    fp.write("Replica is ok\n")
        fp.flush()

    BkkChecks = False
    print("-------- Checks LFC -> Bkk ---------------------------------------------------------")
    fp.write("-------- Checks LFC -> Bkk ---------------------------------------------------------\n")
    res = bkClient.getFileMetadata(LFNsInLFC)
    if res["OK"]:
        BkkChecks = True
        metadata = res["Value"]["Successful"]
        missingLFNs = [lfn for lfn in LFNsInLFC if metadata.get(lfn, {}).get("GotReplica") is None]
        noFlagLFNs = [lfn for lfn in LFNsInLFC if metadata.get(lfn, {}).get("GotReplica") == "No"]
        okLFNs = [lfn for lfn in LFNsInLFC if metadata.get(lfn, {}).get("GotReplica") == "Yes"]
        if verbose:
            print(
                "Out of %d files, %d have a replica flag in the BK, %d are not in the BK and %d don't have the flag"
                % (len(LFNsInLFC), len(okLFNs), len(missingLFNs), len(noFlagLFNs))
            )

    fp.write(" ++++++++++++++++++++++++++++++ Final summary ++++++++++++++++++++++++++\n")
    fp.write(" +++++++++++++++++++++++++++++ Checks LFC -> SE: ++++++++++++++++++++++++++++\n")
    fp.write("Replicas per SE:\n")
    for se in replicasPerSE:
        fp.write("SE: %s has %d replicas\n" % (se, len(replicasPerSE[se])))
        if verbose:
            for r in replicasPerSE[se]:
                fp.write("%s\n" % r)

    directoryConsistency = True
    if zeroReplicaFiles:
        fp.write("Files with zero replicas: %s \n" % zeroReplicaFiles)
        directoryConsistency = False
    if zeroSizeFiles:
        fp.write("Files with zero size: %s\n" % zeroSizeFiles)
        directoryConsistency = False
    if problematicFiles:
        fp.write("Found some problematic replicas: \n")
        for lfn in problematicFiles:
            fp.write("LFN: %s\n" % lfn)
            for k in problematicFiles[lfn]:
                fp.write("%s : %s \n" % (k, problematicFiles[lfn][k]))
        directoryConsistency = False
    fp.write(" +++++++++++++++++++++++++++++++ Checks LFC -> Bookkeeping: +++++++++++++++++++++++++++++\n")

    if BkkChecks:
        fp.write(
            "Out of %d files:\n %d are OK - ReplicaFlag=Yes\n %d are not in the BK\n %d have ReplicaFlag=No\n"
            % (len(LFNsInLFC), len(okLFNs), len(missingLFNs), len(noFlagLFNs))
        )
        if len(missingLFNs) > 0:
            directoryConsistency = False
            fp.write("LFNs present in LFC but missing from Bookkeeping:\n")
            for lfn in missingLFNs:
                fp.write("%s\n" % lfn)
        if len(noFlagLFNs) > 0:
            directoryConsistency = False
            fp.write("LFNs present in LFC but with ReplicaFlag=No in Bookkeeping:\n")
            for lfn in noFlagLFNs:
                fp.write("%s\n" % lfn)
    else:
        fp.write("Bookkeeping didn't return any valid result for the LFNs\n")

    if directoryConsistency:
        fp.write("--------->All replicas in LFC have been checked on Storage. Ok!!\n")
    else:
        fp.write("--------->Directory is not consistent\n")

    fp.close()
    print("Summary written to file: %s" % outputFileName)
    DIRAC.exit(0)


if __name__ == "__main__":
    main()
