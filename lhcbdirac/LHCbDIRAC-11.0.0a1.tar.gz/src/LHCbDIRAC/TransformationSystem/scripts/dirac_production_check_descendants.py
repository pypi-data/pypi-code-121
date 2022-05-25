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
"""Does a TS -> BK check for processed files with descendants."""
import sys
import os
import time

import DIRAC
from DIRAC import gLogger
from DIRAC.Core.Base.Script import Script


@Script()
def main():
    from LHCbDIRAC.DataManagementSystem.Client.DMScript import DMScript

    dmScript = DMScript()
    dmScript.registerFileSwitches()
    depth = 1

    Script.setUsageMessage(
        "\n".join(
            [
                __doc__,
                "Usage:",
                "  %s [option|cfgfile] [ProdIDs]" % Script.scriptName,
            ]
        )
    )
    Script.registerSwitch("", "Runs=", "   Specify the run range")
    Script.registerSwitch(
        "", "ActiveRunsProduction=", "   Specify the production from which the runs should be derived"
    )
    Script.registerSwitch("", "FileType=", "S   pecify the descendants file type")
    Script.registerSwitch("", "NoFC", "   Trust the BK replica flag, no LFC check")
    Script.registerSwitch("", "FixIt", "   Fix the files in transformation table")
    Script.registerSwitch("", "Verbose", "   Print full list of files with error")
    Script.registerSwitch("", "Status=", "   Select files with a given status in the production")
    Script.registerSwitch("", "Depth=", "   Depth to which to check descendants (default=%d)" % depth)
    Script.registerSwitch("", "Force", "   Use this flag to force checking a whole production")
    Script.parseCommandLine(ignoreErrors=True)
    fileType = []
    runsList = []
    lfnList = []
    fixIt = False
    fromProd = None
    verbose = False
    status = None
    noFC = False
    force = False
    for switch in Script.getUnprocessedSwitches():
        if switch[0] == "Runs":
            try:
                runs = switch[1].split(",")
                runsList = []
                for run in runs:
                    runRange = run.split(":")
                    if len(runRange) == 2:
                        runsList += list(range(int(runRange[0]), int(runRange[1]) + 1))
                    else:
                        runsList.append(int(run))
            except Exception as e:
                gLogger.exception("Bad run range", switch[1], lException=e)
                DIRAC.exit(1)
        elif switch[0] == "Status":
            status = switch[1].split(",")
        elif switch[0] == "Verbose":
            verbose = True
        elif switch[0] == "FileType":
            fileType = switch[1].split(",")
        elif switch[0] == "FixIt":
            fixIt = True
        elif switch[0] == "NoFC":
            noFC = True
        elif switch[0] == "Depth":
            depth = min(10, max(1, int(switch[1])))
        elif switch[0] == "Force":
            force = True
        elif switch[0] == "ActiveRunsProduction":
            try:
                fromProd = int(switch[1])
            except ValueError as e:
                gLogger.exception("Wrong production number: %s" % switch[1], lException=e)
                DIRAC.exit(0)

    args = Script.getPositionalArgs()
    if not len(args):
        gLogger.error("Specify transformation number...")
        DIRAC.exit(0)
    else:
        ids = args[0].split(",")
        prodList = []
        try:
            for id in ids:
                r = id.split(":")
                if len(r) > 1:
                    for i in range(int(r[0]), int(r[1]) + 1):
                        prodList.append(i)
                else:
                    prodList.append(int(eval(r[0])))
        except (ValueError, NameError) as e:
            gLogger.exception("Bad production list: %s" % args[0], lException=e)
    # In case the user asked for specific LFNs
    if not status:
        lfnList = dmScript.getOption("LFNs", [])

    if not status and not lfnList and not runsList and not fromProd and not force:
        gLogger.fatal("You are about to check descendants for all files in a production")
        gLogger.fatal("If you really want to do so, use --Force")
        DIRAC.exit(0)

    from LHCbDIRAC.DataManagementSystem.Client.ConsistencyChecks import ConsistencyChecks
    from LHCbDIRAC.BookkeepingSystem.Client.BKQuery import BKQuery
    from DIRAC.TransformationSystem.Client.TransformationClient import TransformationClient

    tr = TransformationClient()
    for prod in prodList:
        startTime = time.time()
        cc = ConsistencyChecks()
        # Setting the prod also sets its type
        try:
            cc.prod = prod
        except RuntimeError as e:
            gLogger.exception(lException=e)
            continue
        if fileType and cc.transType in ("Merge", "MCMerge"):
            gLogger.notice("It is not allowed to select file type for merging transformation", prod)
            continue
        cc.verbose = verbose
        cc.noFC = noFC
        cc.descendantsDepth = depth
        if prod != prodList[0]:
            gLogger.notice("====================")
        gLogger.notice("Processing %s production %d" % (cc.transType, cc.prod))

        if status:
            cc.status = status
        if lfnList:
            cc.lfns = lfnList
        if not fileType:
            bkQuery = BKQuery({"Production": prod, "FileType": "ALL", "Visible": "All"})
            cc.fileType = bkQuery.getBKFileTypes()
            gLogger.notice("Looking for descendants of type %s" % str(cc.fileType))
            notAllFileTypes = False
        else:
            cc.fileType = fileType
            cc.fileTypesExcluded = ["LOG"]
            notAllFileTypes = True
        cc.runsList = runsList
        cc.runStatus = "Active"
        cc.fromProd = fromProd
        cc.checkTS2BK()

        # Print out the results
        gLogger.notice("\nResults:")
        if verbose:
            nMax = sys.maxsize
        else:
            nMax = 20
        suffix = ""
        n = 0
        while True:
            fileName = "CheckDescendantsResults_%s%s.txt" % (str(cc.prod), suffix)
            if not os.path.exists(fileName):
                break
            n += 1
            suffix = "-%d" % n
        fp = None
        if cc.inFCNotInBK:
            lfns = cc.inFCNotInBK
            gLogger.notice("%d descendants were found in FC but don't have replica flag in BK" % len(lfns))
            if not fp:
                fp = open(fileName, "w")
            fp.write("\nInFCNotInBK ".join([""] + lfns))
            gLogger.notice(
                "First %d files:" % nMax if not verbose and len(lfns) > nMax else "All files:",
                "\n".join([""] + lfns[0:nMax]),
            )
            gLogger.notice(
                "To fix it:   grep InFCNotInBK %s | dirac-dms-check-fc2bkk\n"
                "\tBeware you can then either fix the BK or the FC/SE" % fileName
            )

        if cc.inFailover:
            lfns = cc.inFailover
            gLogger.notice("%d descendants were found in Failover and have no replica flag in BK" % len(lfns))
            if not fp:
                fp = open(fileName, "w")
            fp.write("\nInFailover ".join([""] + lfns))
            gLogger.notice(
                "First %d files:" % nMax if not verbose and len(lfns) > nMax else "All files:",
                "\n".join([""] + lfns[0:nMax]),
            )
            gLogger.notice(
                "You should check whether they are in a failover request by looking "
                "at their job status and in the RMS..."
            )
            gLogger.notice("To list them:     grep InFailover %s" % fileName)

        if cc.inBKNotInFC:
            lfns = cc.inBKNotInFC
            gLogger.notice("%d descendants were found with replica flag in BK but not in FC" % len(lfns))
            if not fp:
                fp = open(fileName, "w")
            fp.write("\nInBKNotInFC ".join([""] + lfns))
            gLogger.notice(
                "First %d files:" % nMax if not verbose and len(lfns) > nMax else "All files:",
                "\n".join([""] + lfns[0:nMax]),
            )
            gLogger.notice("To try and fix this:    grep InBKNotInFC %s | dirac-dms-check-bkk2fc" % fileName)

        if cc.removedFiles:
            from DIRAC.Core.Utilities.List import breakListIntoChunks

            gLogger.notice(
                "%d input files are Processed, have no descendants but are no longer in the FC\n"
                "  As they cannot be reset Unused, set them Removed" % len(cc.removedFiles)
            )
            if not fp:
                fp = open(fileName, "w")
            fp.write("\nProcNotinFC ".join([""] + cc.removedFiles))
            gLogger.notice(
                "First %d files:" % nMax if not verbose and len(cc.removedFiles) > nMax else "All files:",
                "\n".join([""] + cc.removedFiles[0:nMax]),
            )
            for lfnChunk in breakListIntoChunks(cc.removedFiles, 1000):
                while True:
                    res = cc.transClient.setFileStatusForTransformation(cc.prod, "Removed", lfnChunk, force=True)
                    if not res["OK"]:
                        gLogger.notice("Error setting files Removed, retry...", res["Message"])
                    else:
                        break
            gLogger.notice("\tFiles successfully set to status Removed")

        gLogger.notice(
            "%d unique daughters found with real descendants"
            % (len(set(cc.descForPrcdLFNs).union(cc.descForNonPrcdLFNs)))
        )

        if cc.prcdWithMultDesc:
            lfns = sorted(cc.prcdWithMultDesc)
            gLogger.notice("Processed LFNs with multiple descendants (%d) -> ERROR" % len(lfns))
            gLogger.notice(
                "First %d files:" % nMax if not verbose and len(lfns) > nMax else "All files:",
                "\n".join([""] + lfns[0:nMax]),
            )
            if not fp:
                fp = open(fileName, "w")
            fp.write(
                "\nProcMultDesc ".join(
                    [""] + ["%s: %s" % (lfn, str(multi)) for lfn, multi in cc.prcdWithMultDesc.items()]
                )
            )
            gLogger.notice("I'm not doing anything for them, neither with the 'FixIt' option")
        else:
            gLogger.notice("No processed LFNs with multiple descendants found -> OK!")

        fixItUsed = False
        if cc.prcdWithoutDesc:
            lfns = set(cc.prcdWithoutDesc)
            res = cc.bkClient.getFileMetadata(list(lfns))
            badLfns = set()
            if res["OK"]:
                # Check the DQ flag of these files
                badLfns = set(
                    lfn for lfn, meta in res["Value"]["Successful"].items() if meta["DataqualityFlag"] == "BAD"
                )
            if badLfns:
                gLogger.notice("Processed LFNs without descendants (%d)" % len(lfns))
                gLogger.notice(
                    "WARNING: %d of these files have a BAD data quality flag and thus may have been removed"
                    % len(badLfns)
                )
                lfns -= badLfns
            if fixIt and lfns:
                fixIt = False
                gLogger.notice("Processed LFNs without descendants (%d) -> ERROR!" % len(lfns))
                gLogger.notice("Resetting them 'Unused'")
                res = cc.transClient.setFileStatusForTransformation(prod, "Unused", list(lfns), force=True)
                if not res["OK"]:
                    gLogger.notice("Error resetting files to Unused", res["Message"])
            else:
                fixItUsed = True
                if not fp:
                    fp = open(fileName, "w")
                if badLfns:
                    fp.write("\nProcButBAD ".join([""] + sorted(badLfns)))
                    gLogger.notice("BAD files processed without descendants can be checked using:")
                    gLogger.notice("     grep ProcButBAD %s" % fileName)
                if lfns:
                    lfns = sorted(lfns)
                    gLogger.notice("Processed LFNs without descendants (%d) -> ERROR!" % len(lfns))
                    gLogger.notice(
                        "First %d files:" % nMax if not verbose and len(lfns) > nMax else "All files:",
                        "\n".join([""] + lfns[0:nMax]),
                    )
                    fp.write("\nProcNoDesc ".join([""] + lfns))
                    if notAllFileTypes:
                        gLogger.notice("You may want to check those files again for all file types, using:")
                        gLogger.notice(
                            "     grep ProcNoDesc %s | dirac-production-check-descendants %d" % (fileName, cc.prod)
                        )
                    if cc.transType in ("DataStripping", "MCReconstruction", "MCStripping"):
                        nextProd, nextType = cc._findNextProduction()
                        if nextProd:
                            gLogger.notice(
                                "This is a %s production, thus "
                                "the problem may come from the %s production %d" % (cc.transType, nextType, nextProd)
                            )
                            gLogger.notice("     You may check it with this command:")
                            gLogger.notice(
                                "     grep ProcNoDesc %s | dirac-bookkeeping-get-file-descendants --All | grep %d |"
                                "dirac-production-check-descendants %d " % (fileName, cc.prod, nextProd)
                            )
                    gLogger.notice("If you are sure, use --FixIt for resetting those files Unused in TS")
                else:
                    gLogger.notice("No files processed without descendants that are not BAD")
        else:
            gLogger.notice("No processed LFNs without descendants found -> OK!")

        if cc.nonPrcdWithMultDesc:
            lfns = sorted(cc.nonPrcdWithMultDesc)
            gLogger.notice("Non processed LFNs with multiple descendants (%d) -> ERROR" % len(lfns))
            if not fp:
                fp = open(fileName, "w")
            fp.write("\nNotProcMultDesc ".join([""] + lfns))
            gLogger.notice(
                "First %d files:" % nMax if not verbose and len(lfns) > nMax else "All files:",
                "\n".join([""] + lfns[0:nMax]),
            )
            gLogger.notice("I'm not doing anything for them, neither with the 'FixIt' option")
        else:
            gLogger.notice("No non processed LFNs with multiple descendants found -> OK!")

        # fixing, if requested
        if cc.nonPrcdWithDesc:
            lfns = sorted(cc.nonPrcdWithDesc)
            gLogger.notice("There are %d LFNs not marked Processed but that have descendants -> ERROR" % len(lfns))
            gLogger.notice(
                "First %d files:" % nMax if not verbose and len(lfns) > nMax else "All files:",
                "\n".join([""] + lfns[0:nMax]),
            )
            if fixIt:
                fixIt = False
                gLogger.notice("Marking them as 'Processed'")
                cc.transClient.setFileStatusForTransformation(prod, "Processed", lfns, force=True)
            else:
                if not fp:
                    fp = open(fileName, "w")
                fp.write("\nNotProcWithDesc ".join([""] + lfns))
                if not fixItUsed:
                    gLogger.notice("Use --FixIt for setting files Processed in TS")
                else:
                    gLogger.notice("To get the list of files and check them again:")
                    gLogger.notice("     grep NotProcWithDesc %s | dirac-production-check-descendants" % fileName)
        else:
            gLogger.notice("No non processed LFNs with descendants found -> OK!")
        if fp:
            fp.close()
            gLogger.notice("Complete list of files is in %s" % fileName)
        gLogger.notice("Processed production %d in %.1f seconds" % (cc.prod, time.time() - startTime))


if __name__ == "__main__":
    main()
