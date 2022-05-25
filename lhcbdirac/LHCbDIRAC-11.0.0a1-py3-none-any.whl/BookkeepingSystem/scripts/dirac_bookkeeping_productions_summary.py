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
"""Retrieve production summary from the Bookkeeping."""
import DIRAC
from DIRAC import gLogger
from DIRAC.Core.Base.Script import Script


@Script()
def main():
    from LHCbDIRAC.DataManagementSystem.Client.DMScript import DMScript

    dmScript = DMScript()
    dmScript.registerBKSwitches()
    Script.setUsageMessage(__doc__ + "\n".join(["Usage:", "  %s [option|cfgfile] ..." % Script.scriptName]))
    Script.parseCommandLine(ignoreErrors=True)

    from LHCbDIRAC.BookkeepingSystem.Client.BookkeepingClient import BookkeepingClient

    bk = BookkeepingClient()

    bkQuery = dmScript.getBKQuery()
    if not bkQuery:
        gLogger.error("No BKQuery given...")
        DIRAC.exit(1)

    bkQueryDict = bkQuery.getQueryDict()
    dictItems = (
        "ConfigName",
        "ConfigVersion",
        "Production",
        "ConditionDescription",
        "ProcessingPass",
        "FileType",
        "EventType",
    )
    for item in dictItems:
        bkQueryDict.setdefault(item, "ALL")
    for item in list(bkQueryDict):
        if item not in dictItems:
            bkQueryDict.pop(item)

    gLogger.verbose("BKQuery:", bkQueryDict)
    res = bk.getProductionSummary(bkQueryDict)

    if not res["OK"]:
        gLogger.error(res["Message"])
        DIRAC.exit(1)

    records = res["Value"]["Records"]
    params = res["Value"]["ParameterNames"]
    width = 20

    gLogger.showHeaders(False)

    gLogger.notice("")
    gLogger.notice(
        params[0].ljust(30)
        + str(params[1]).ljust(30)
        + str(params[2]).ljust(30)
        + str(params[3]).ljust(30)
        + str(params[4]).ljust(30)
        + str(params[5]).ljust(30)
        + str(params[6]).ljust(20)
        + str(params[7]).ljust(20)
        + str(params[8]).ljust(20),
    )
    gLogger.notice("")
    for record in records:
        gLogger.notice(
            str(record[0]).ljust(15)
            + str(record[1]).ljust(15)
            + str(record[2]).ljust(20)
            + str(record[3]).ljust(width)
            + str(record[4]).ljust(width)
            + str(record[5]).ljust(width)
            + str(record[6]).ljust(width)
            + str(record[7]).ljust(width)
            + str(record[8]).ljust(width),
        )

    gLogger.notice("")
    gLogger.notice("TotalRecords = %d" % res["Value"]["TotalRecords"])


if __name__ == "__main__":
    main()
