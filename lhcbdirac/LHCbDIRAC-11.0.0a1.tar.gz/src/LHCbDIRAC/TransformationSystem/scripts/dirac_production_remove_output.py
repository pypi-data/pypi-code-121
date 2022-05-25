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
"""remove output of production."""
import sys

from DIRAC.Core.Base.Script import Script


@Script()
def main():
    from DIRAC.Core.Base.Script import parseCommandLine

    parseCommandLine()

    from DIRAC import exit as DIRACExit
    from DIRAC import gLogger
    from LHCbDIRAC.TransformationSystem.Agent.TransformationCleaningAgent import TransformationCleaningAgent
    from LHCbDIRAC.TransformationSystem.Client.TransformationClient import TransformationClient

    if len(sys.argv) < 2:
        print("Usage: dirac-production-remove-output transID [transID] [transID]")
        DIRACExit(1)
    else:
        try:
            transIDs = [int(arg) for arg in sys.argv[1:]]
        except BaseException:
            print("Invalid list of productions")
            DIRACExit(1)

    agent = TransformationCleaningAgent(
        "Transformation/TransformationCleaningAgent",
        "Transformation/TransformationCleaningAgent",
        "dirac-production-remove-output",
    )
    agent.initialize()

    client = TransformationClient()
    for transID in transIDs:
        res = client.getTransformationParameters(transID, ["Status"])
        if not res["OK"]:
            gLogger.error("Failed to determine transformation status")
            gLogger.error(res["Message"])
            continue
        status = res["Value"]
        if status not in ["RemovingFiles", "RemovingOutput", "ValidatingInput", "Active"]:
            gLogger.error("The transformation is in %s status and the outputs cannot be removed" % status)
            continue
        agent.removeTransformationOutput(transID)


if __name__ == "__main__":
    main()
