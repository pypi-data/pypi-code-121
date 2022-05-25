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
"""Set files Removed in a transformation."""

from DIRAC.Core.Base.Script import Script
from LHCbDIRAC.TransformationSystem.Utilities.ScriptUtilities import getTransformations


@Script()
def main():
    import DIRAC
    from DIRAC import gLogger
    from LHCbDIRAC.DataManagementSystem.Client.DMScript import DMScript

    dmScript = DMScript()
    dmScript.registerFileSwitches()

    Script.parseCommandLine(ignoreErrors=True)

    Script.setUsageMessage(
        "\n".join(
            [
                __doc__,
                "Usage:",
                "Set files as Removed in a (set of) transformations",
                "  %s [option|cfgfile] ..." % Script.scriptName,
            ]
        )
    )

    transList = getTransformations(Script.getPositionalArgs())
    if not transList:
        DIRAC.exit(1)

    requestedLFNs = dmScript.getOption("LFNs")
    if not requestedLFNs:
        gLogger.always("No files to add")
        DIRAC.exit(1)

    from DIRAC.TransformationSystem.Client.TransformationClient import TransformationClient

    trClient = TransformationClient()
    rc = 0
    for transID in transList:
        res = trClient.setFileStatusForTransformation(transID, "Removed", requestedLFNs, force=True)
        if res["OK"]:
            gLogger.always(
                "Successfully set %d files%s Removed in transformation %d"
                % (
                    len(res["Value"]),
                    (" (out of %d)" % len(requestedLFNs)) if len(res["Value"]) != len(requestedLFNs) else "",
                    transID,
                )
            )
        else:
            gLogger.always(
                "Failed to set %d files Removed in transformation %d" % (len(requestedLFNs), transID), res["Message"]
            )
            rc = 2
    DIRAC.exit(rc)


if __name__ == "__main__":
    main()
