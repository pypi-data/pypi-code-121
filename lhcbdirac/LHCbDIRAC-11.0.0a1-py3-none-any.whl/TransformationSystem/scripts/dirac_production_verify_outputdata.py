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

from DIRAC.Core.Base.Script import Script


@Script()
def main():
    from DIRAC.Core.Base.Script import parseCommandLine

    parseCommandLine()

    import sys

    if len(sys.argv) < 2:
        print("Usage: dirac-production-verify-outputdata transID [transID] [transID]")
        sys.exit()
    else:
        transIDs = [int(arg) for arg in sys.argv[1:]]

    from LHCbDIRAC.TransformationSystem.Agent.ValidateOutputDataAgent import ValidateOutputDataAgent
    from LHCbDIRAC.TransformationSystem.Client.TransformationClient import TransformationClient
    from DIRAC import gLogger
    import DIRAC

    agent = ValidateOutputDataAgent(
        "Transformation/ValidateOutputDataAgent",
        "Transformation/ValidateOutputDataAgent",
        "dirac-production-verify-outputdata",
    )
    agent.initialize()

    client = TransformationClient()
    for transID in transIDs:
        agent.checkTransformationIntegrity(transID)


if __name__ == "__main__":
    main()
