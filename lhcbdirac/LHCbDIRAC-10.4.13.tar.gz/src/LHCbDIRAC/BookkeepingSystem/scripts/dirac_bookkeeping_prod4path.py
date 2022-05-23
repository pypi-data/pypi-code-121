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
"""Get production numbers given a dataset path."""
import time
import six
from DIRAC import gLogger, exit
from DIRAC.Core.Utilities.DIRACScript import DIRACScript


def printProds(title, prods):
    typeDict = {}
    for prod, prodType in prods.items():
        typeDict.setdefault(prodType, []).append(prod)
    gLogger.notice(title)
    for prodType, prodList in typeDict.items():
        gLogger.notice("(%s): %s" % (prodType, ",".join([str(prod) for prod in sorted(prodList)])))


def execute(dmScript):
    from DIRAC.Core.Base import Script
    from LHCbDIRAC.TransformationSystem.Client.TransformationClient import TransformationClient

    tr = TransformationClient()

    for switch in Script.getUnprocessedSwitches():
        pass

    bkQuery = dmScript.getBKQuery()
    if not bkQuery:
        gLogger.notice("No BKQuery given...")
        exit(1)

    startTime = time.time()
    prods = bkQuery.getBKProductions()  # visible = 'All' )

    parents = {}
    productions = {}
    for prod in prods:
        ptype = tr.getTransformation(prod).get("Value", {}).get("Type", "Unknown")
        productions[prod] = ptype
        parent = tr.getBookkeepingQuery(prod).get("Value", {}).get("ProductionID", "")
        while isinstance(parent, six.integer_types):
            ptype = tr.getTransformation(parent).get("Value", {}).get("Type", "Unknown")
            parents[parent] = ptype
            parent = tr.getBookkeepingQuery(parent).get("Value", {}).get("ProductionID", "")

    gLogger.notice("For BK path %s:" % bkQuery.getPath())
    if not prods:
        gLogger.notice("No productions found!")
    else:
        printProds("Productions found", productions)
        if parents:
            printProds("Parent productions", parents)

    gLogger.notice("Completed in %.1f seconds" % (time.time() - startTime))


@DIRACScript()
def main():
    from DIRAC.Core.Base import Script
    from LHCbDIRAC.DataManagementSystem.Client.DMScript import DMScript

    dmScript = DMScript()
    dmScript.registerBKSwitches()
    Script.setUsageMessage(
        __doc__
        + "\n".join(
            [
                "Usage:",
                "  %s [option|cfgfile]" % Script.scriptName,
            ]
        )
    )

    Script.parseCommandLine(ignoreErrors=False)
    execute(dmScript)


if __name__ == "__main__":
    main()
