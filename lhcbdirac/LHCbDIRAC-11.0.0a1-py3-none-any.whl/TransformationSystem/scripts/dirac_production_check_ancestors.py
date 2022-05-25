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
"""Gets a list of files from BK and checks if they have common ancestors."""
import time
from DIRAC import gLogger
from DIRAC.Core.Base.Script import Script

fixIt = None


def removeFile(lfns, transClient, dm, bkClient):
    """Method for removing a file in the RM as well as in the Transformation
    system."""
    res = bkClient.setFilesInvisible(lfns)
    if res["OK"]:
        gLogger.always("Files were made invisible in BK")
    else:
        gLogger.always("Error making files invisible in BK", res["Message"])
    gLogger.always("Removing %d files from disk" % len(lfns))
    res = dm.getReplicas(lfns)
    success = res.get("Value", {}).get("Successful", [])
    failed = res.get("Value", {}).get("Failed", lfns)
    if res["OK"] and success:
        seLfns = {}
        removeFiles = list(success)
        for lfn in success:
            for se in success[lfn]:
                if not se.endswith("ARCHIVE"):
                    seLfns.setdefault(se, []).append(lfn)
                else:
                    # If there is an archive, we cannot remove the file completely
                    if lfn in removeFiles:
                        removeFiles.remove(lfn)
        if removeFiles:
            gLogger.always("Removing completely %d files" % len(removeFiles))
            res = dm.removeFile(removeFiles)
            if not res["OK"]:
                gLogger.fatal("Error removing %d files" % len(removeFiles), res["Message"])
            else:
                success = res["Value"]["Successful"]
                failed = res["Value"]["Failed"]
                gLogger.always(
                    "Successfully fully removed %d files that only had the duplicate ancestors" % len(success)
                )
                if failed:
                    errors = {}
                    for lfn, reason in failed.items():
                        errors.setdefault(reason, []).append(lfn)
                    gLogger.error(
                        "Failed to remove %d files" % len(failed),
                        "\n".join("%s: %s" % (reason, errors[reason]) for reason in errors),
                    )
        success = []
        failed = {}
        for se, replicas in seLfns.items():
            replicas = [lfn for lfn in replicas if lfn not in removeFiles]
            if replicas:
                res = dm.removeReplica(se, replicas)
                if not res["OK"]:
                    gLogger.fatal("Error removing replicas", res["Message"])
                else:
                    success += res["Value"]["Successful"]
                    if res["Value"]["Failed"]:
                        failed[se] = res["Value"]["Failed"]
        if success:
            gLogger.always(
                "Successfully removed %d replicas of files that only had the duplicate ancestors" % len(success)
            )
        if failed:
            errors = {}
            for se in failed:
                for lfn, reason in failed[se].items():
                    errors.setdefault(reason + " @%s" % se, []).append(lfn)
            gLogger.error(
                "Failed to remove replicas\n", "\n".join("%s: %s" % (reason, errors[reason]) for reason in errors)
            )
        elif not success and not removeFiles:
            gLogger.always("None of the files had replicas left on disk...")
        if not success:
            return
        res = transClient.getTransformationFiles({"LFN": success})
        if res["OK"]:
            transFiles = {}
            processedFiles = {}
            for fileDict in res["Value"]:
                if fileDict["Status"] == "Processed":
                    processedFiles.setdefault(fileDict["TransformationID"], []).append(fileDict["LFN"])
                else:
                    transFiles.setdefault(fileDict["TransformationID"], []).append(fileDict["LFN"])
            if processedFiles:
                gLogger.always("WARNING: some files were already processed!")
                for transID, lfns in processedFiles.items():
                    gLogger.always("%d: %d files" % (transID, len(lfns)))
                    gLogger.info("\n".join(sorted(lfns)))
            for transID, lfns in transFiles.items():
                res = transClient.setFileStatusForTransformation(transID, "Removed", lfns)
                if res["OK"]:
                    gLogger.always("%d: %d files set Removed" % (transID, len(lfns)))
                    gLogger.info("\n".join(sorted(lfns)))
                else:
                    gLogger.fatal(
                        "Error setting %d files to Removed status in transformation %d" % (len(lfns), transID)
                    )
    elif failed:
        gLogger.fatal(
            "Failed to get replicas for %d files:\n" % len(failed),
            res.get("Message", "\n".join(sorted(set(failed.values if isinstance(failed, type({})) else [])))),
        )
        gLogger.info(
            "\n".join(
                ("%s: %s" % (lfn, failed[lfn]) for lfn in sorted(failed))
                if isinstance(failed, dict)
                else sorted(failed)
            )
        )


def analyzeAncestors(commonAncestors, ancestors, transClient, dm, bkClient):
    """Analyse the list of common ancestors and checks whether one can remove
    some files."""
    lfnsToRemove = set()
    allLfns = [lfn for lfnStr in commonAncestors for lfn in lfnStr.split(",")]
    res = bkClient.getFileMetadata(allLfns)
    lfnRuns = {}
    if res["OK"]:
        for lfn, metadata in res["Value"]["Successful"].items():
            lfnRuns[lfn] = metadata["RunNumber"]
    for lfnStr, anc in commonAncestors.items():
        lfns = lfnStr.split(",")
        run = lfnRuns.get(lfns[0], "Unknown")
        gLogger.always("\n%s (run %s):\n\t%s" % ("\n".join(lfns), str(run), "\n\t".join(anc)))
        # Now check if one of the files only has those common ancestors
        for lfn in sorted(lfns, reverse=True):
            if anc == ancestors[lfn]:
                if not fixIt:
                    gLogger.always("%s only has those as ancestors. Use --FixIt to remove the file" % lfn)
                else:
                    gLogger.always("%s only has those as ancestors. We shall remove the file" % lfn)
                    lfnsToRemove.add(lfn)
                    lfns.remove(lfn)
                    if len(lfns) == 1:
                        break
    if lfnsToRemove:
        removeFile(list(lfnsToRemove), transClient=transClient, dm=dm, bkClient=bkClient)


@Script()
def main():
    global fixIt

    from LHCbDIRAC.DataManagementSystem.Client.DMScript import DMScript

    dmScript = DMScript()
    dmScript.registerFileSwitches()
    dmScript.registerBKSwitches()
    depth = 10
    Script.registerSwitch("", "Depth=", "Depth to which one should check ancestors (default %d)" % depth)
    Script.registerSwitch("", "FixIt", "Remove the files that only have the common ancestors")
    Script.registerSwitch("", "Verbose", "Set script level to INFO")

    Script.setUsageMessage(
        "\n".join(
            [
                __doc__,
                "Usage:",
                "  %s [option|cfgfile]" % Script.scriptName,
            ]
        )
    )
    Script.parseCommandLine(ignoreErrors=True)

    fixIt = False
    for switch in Script.getUnprocessedSwitches():
        if switch[0] == "Verbose":
            gLogger.setLevel("INFO")
        elif switch[0] == "FixIt":
            fixIt = True
        elif switch[0] == "Depth":
            depth = int(switch[1])

    # In case the user asked for specific LFNs
    lfnList = dmScript.getOption("LFNs", [])

    from LHCbDIRAC.DataManagementSystem.Client.ConsistencyChecks import ConsistencyChecks
    from DIRAC.DataManagementSystem.Client.DataManager import DataManager
    from LHCbDIRAC.BookkeepingSystem.Client.BookkeepingClient import BookkeepingClient
    from LHCbDIRAC.TransformationSystem.Client.TransformationClient import TransformationClient

    dm = DataManager()
    bkClient = BookkeepingClient()
    transClient = TransformationClient()

    cc = ConsistencyChecks(transClient=transClient, dm=dm, bkClient=bkClient)
    cc.bkQuery = dmScript.getBKQuery()
    cc.lfns = lfnList
    cc.ancestorsDepth = depth
    startTime = time.time()
    cc.checkAncestors()

    # Print out the results
    gLogger.always("\nResults (%.1f seconds):" % (time.time() - startTime))

    if not cc.commonAncestors:
        gLogger.always("No files found with common ancestors ==> OK")
    else:
        gLogger.always("Found %d sets of files with common ancestors ==> ERROR" % len(cc.commonAncestors))
        analyzeAncestors(cc.commonAncestors, cc.ancestors, transClient=transClient, dm=dm, bkClient=bkClient)


if __name__ == "__main__":
    main()
