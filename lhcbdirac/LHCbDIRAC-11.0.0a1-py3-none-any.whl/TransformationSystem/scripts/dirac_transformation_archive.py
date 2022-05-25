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

import sys

from DIRAC.Core.Base.Script import Script


@Script()
def main():
    from DIRAC.Core.Base.Script import parseCommandLine

    parseCommandLine()

    import DIRAC
    from LHCbDIRAC.TransformationSystem.Agent.TransformationCleaningAgent import TransformationCleaningAgent
    from LHCbDIRAC.TransformationSystem.Utilities.ScriptUtilities import getTransformations

    if len(sys.argv) < 2:
        print("Usage: dirac-transformation-archive transID [transID] [transID]")
        DIRAC.exit(1)
    else:
        transIDs = getTransformations(sys.argv[1:])
        if not transIDs:
            DIRAC.exit(1)

    agent = TransformationCleaningAgent(
        "Transformation/TransformationCleaningAgent",
        "Transformation/TransformationCleaningAgent",
        "dirac-transformation-archive",
    )
    agent.initialize()

    for transID in transIDs:
        agent.archiveTransformation(transID)


if __name__ == "__main__":
    main()
