#! /usr/bin/env python
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
"""This script is used to flag a given files which belongs a certain run.

1. We flag OK or BAD without specifying a processing pass: this flags the RAW and all derived files as OK or BAD
2. If a processing pass is specified (and we allow one PP at a time only):
     2.1 For BAD, only that processing pass (and derived) is flagged BAD.
         RAW is left unchanged unless PP is '/Real Data' which is then similar to 1
     2.2 For OK:
               - if '/Real Data', only the RAW are flagged OK.
                 Derived data are left unchanged. If one wants to flag everything, use 1.
               - else that processing pass (and derived) and the RAW are flagged OK
"""

import os

import DIRAC
from DIRAC import S_OK, S_ERROR, gLogger
from DIRAC.Core.Base import Script
from DIRAC.Core.Utilities.DIRACScript import DIRACScript


def checkDQFlag(dqFlag):
    """Make sure the DQ flag is a known one."""
    from LHCbDIRAC.BookkeepingSystem.Client.BookkeepingClient import BookkeepingClient

    res = BookkeepingClient().getAvailableDataQuality()
    if not res["OK"]:
        return res

    if dqFlag in res["Value"]:
        return S_OK()
    else:
        return S_ERROR("Data quality flag is not in the db")


def flagFileList(filename, dqFlag):
    """Flag a LFN or a list of LFN contained in a file."""
    from LHCbDIRAC.BookkeepingSystem.Client.BookkeepingClient import BookkeepingClient

    lfns = []

    # Load the list of LFN
    try:
        with open(filename) as f:
            for lfn in f:
                lfns.append(lfn.strip())
    except IOError:
        lfns = filename.split(",")

    # Now flag the LFN
    res = BookkeepingClient().setFileDataQuality(lfns, dqFlag)

    if not res["OK"]:
        return res
    else:
        gLogger.notice("The data quality has been set %s for %d files:" % (dqFlag, len(lfns)))

    return S_OK()


def flagRun(runNumber, procPass, dqFlag, flagRAW=False):
    """Flag a run given its number, the processing pass and the DQ flag."""
    from LHCbDIRAC.BookkeepingSystem.Client.BookkeepingClient import BookkeepingClient

    res = getProcessingPasses(runNumber, "/Real Data")
    if not res["OK"]:
        return S_ERROR("flagRun: %s" % res["Message"])

    allProcessingPasses = set(res["Value"])

    gLogger.notice("Available processing passes:", str(allProcessingPasses))

    processingPasses = []
    if procPass:  # we will flag a certain processing: for example: /Real Data/Reco09
        for processingPass in allProcessingPasses:
            if processingPass.startswith(procPass):
                processingPasses.append(processingPass)
    else:  # we will flag everything
        processingPasses = allProcessingPasses

    if flagRAW:
        processingPasses.append("/Real Data")

    if not processingPasses:
        return S_ERROR("%s is not a valid processing pass." % procPass)

        # Flag the processing passes
    for processingPass in processingPasses:
        res = BookkeepingClient().setRunAndProcessingPassDataQuality(
            runNumber,
            processingPass,
            dqFlag,
        )
        if not res["OK"]:
            return S_ERROR("flagRun: processing pass %s\n error: %s" % (processingPass, res["Message"]))
        else:
            gLogger.notice("Run %d Processing Pass %s flagged %s" % (runNumber, processingPass, dqFlag))

    return S_OK()


def getProcessingPasses(runNumber, procPass):
    """Find all known processing passes for the selected configurations."""
    from LHCbDIRAC.BookkeepingSystem.Client.BookkeepingClient import BookkeepingClient

    res = BookkeepingClient().getRunConfigurationsAndDataTakingCondition(int(runNumber))
    if not res["OK"]:
        return res

    bkDict = res["Value"]
    bkDict["RunNumber"] = runNumber

    passes = []
    res = browseBkkPath(bkDict, procPass, passes)
    if not res["OK"]:
        return res
    return S_OK(passes)


def browseBkkPath(bkDict, processingPass, visitedProcessingPass):
    """This method visit the processing passes started from processingPass.

    The visited processing passes are kept in visitedProcessingPass
    """
    from LHCbDIRAC.BookkeepingSystem.Client.BookkeepingClient import BookkeepingClient

    res = BookkeepingClient().getProcessingPass(bkDict, processingPass)
    if not res["OK"]:
        gLogger.error(
            "Cannot load the processing passes for head % in Version %s Data taking condition %s"
            % (processingPass, bkDict["ConfigVersion"], bkDict["ConditionDescription"])
        )
        gLogger.error(res["Message"])
        return res

    records = res["Value"][0]  # 0 contains the processing passes 1 contains the event types
    if "Name" in records["ParameterNames"]:  # this mean we have processing passes
        # this is the name of the processing pass: 'ParameterNames': ['Name']
        index = records["ParameterNames"].index("Name")
        passes = sorted([os.path.join(processingPass, record[index]) for record in records["Records"]])
    else:
        passes = []

    if passes:
        for pName in passes:
            visitedProcessingPass.append(pName)
            browseBkkPath(bkDict, pName, visitedProcessingPass)

    return S_OK()


@DIRACScript()
def main():
    from LHCbDIRAC.BookkeepingSystem.Client.BookkeepingClient import BookkeepingClient

    Script.registerSwitch("l:", "lfnfile=", "Flag a LFN or list of LFN")
    Script.registerSwitch("r:", "run=", "Flag a run")
    Script.registerSwitch("p:", "processingPass=", "Processing pass for which a run should be flagged")
    Script.registerSwitch("q:", "dataqualityflag=", "Data quality flag")

    Script.setUsageMessage(
        __doc__
        + "\n".join(
            [
                "\nArguments:",
                "  lfnfile (string) : [LFN|filename]",
                "  processingPass (string) : porcessing pass(es)",
                "  runNumber (int): run number to be flagged",
                "  dataqualityflag (string): data quality\n",
            ]
        )
    )

    Script.parseCommandLine(ignoreErrors=True)

    exitCode = 0

    params = {"lfn": None, "runnumber": None, "dqflag": None, "processingpass": None}

    for switch in Script.getUnprocessedSwitches():
        if switch[0].lower() in ("l", "lfnfile"):
            params["lfn"] = switch[1]
        elif switch[0].lower() in ("r", "run"):
            params["runnumber"] = int(switch[1])
        elif switch[0].lower() in ("q", "dataqualityflag"):
            params["dqflag"] = switch[1]
        elif switch[0].lower() in ("p", "processingPass"):
            params["processingpass"] = switch[1]

    if params["lfn"] is None and params["runnumber"] is None:
        gLogger.fatal("Please specify run number or an lfn!")
        DIRAC.exit(1)
    if params["dqflag"] is None:
        gLogger.fatal("Please specify the data quality flag!")
        DIRAC.exit(1)

    processingPass = None
    if params["processingpass"]:
        if len(params["processingpass"].split(",")) > 1:
            gLogger.fatal("More than one processing pass is given. Please use only one processing pass!")
            DIRAC.exit(1)
        else:
            processingPass = params["processingpass"]
            if not processingPass.startswith("/"):
                processingPass = "/" + processingPass
            processingPass = processingPass.replace(
                "RealData", "Real Data"
            )  # To be consistent with other BK scripts ;-)
            if not processingPass.startswith("/Real Data"):
                processingPass = "/Real Data" + processingPass

    res = checkDQFlag(params["dqflag"])
    if not res["OK"]:
        gLogger.fatal("%s - %s" % (params["dqflag"], res["Message"]))
        DIRAC.exit(1)

    if params["lfn"]:
        res = flagFileList(params["lfn"], params["dqflag"])
        if res["OK"]:
            gLogger.notice("Files are flagged!")
            DIRAC.exit(exitCode)
        else:
            gLogger.fatal(res["Message"])

    if params["runnumber"]:
        if not processingPass:  # processing pass is not given
            # this flags the RAW and all derived files as the given dq flag
            res = flagRun(runNumber=params["runnumber"], procPass="/", dqFlag=params["dqflag"], flagRAW=True)
            if not res["OK"]:
                gLogger.fatal(res["Message"])
                DIRAC.exit(1)
        else:  # the processing pass is given
            if (
                params["dqflag"] == "BAD"
            ):  # only that processing pass (and derived) is flagged BAD. RAW is left unchanged
                res = flagRun(
                    runNumber=params["runnumber"],
                    procPass=processingPass,
                    dqFlag=params["dqflag"],
                )
                if not res["OK"]:
                    gLogger.fatal(res["Message"])
                    DIRAC.exit(1)
            elif params["dqflag"] == "OK":
                if processingPass == "/Real Data":  # only flag the RAW
                    res = BookkeepingClient().setRunAndProcessingPassDataQuality(
                        params["runnumber"],
                        "/Real Data",
                        params["dqflag"],
                    )
                    if not res["OK"]:
                        gLogger.fatal(res["Message"])
                        DIRAC.exit(1)
                    else:
                        gLogger.notice("%d flagged OK" % params["runnumber"])
                else:
                    res = flagRun(
                        runNumber=params["runnumber"],
                        procPass=processingPass,
                        dqFlag=params["dqflag"],
                        flagRAW=True,
                    )
                    if not res["OK"]:
                        gLogger.fatal(res["Message"])
                        DIRAC.exit(1)

    DIRAC.exit(exitCode)


if __name__ == "__main__":
    main()
