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
"""This script allows to print information about a (list of)
transformations."""

from DIRAC.Core.Base.Script import Script


@Script()
def main():

    informations = [
        "AuthorDN",
        "AuthorGroup",
        "Body",
        "CreationDate",
        "Description",
        "EventsPerTask",
        "FileMask",
        "GroupSize",
        "Hot",
        "InheritedFrom",
        "LastUpdate",
        "LongDescription",
        "MaxNumberOfTasks",
        "Plugin",
        "Status",
        "TransformationGroup",
        "TransformationName",
        "Type",
        "Request",
    ]
    Script.registerSwitch("", "Information=", "   Specify which information is required")
    Script.setUsageMessage(
        "\n".join(
            [
                __doc__,
                "Usage:",
                "  %s [options] transID1 [transID2 ...]" % Script.scriptName,
                "Arguments:",
                "\ttransID1,... : transformantion IDs",
                "Possible informations:",
                "\t%s" % ", ".join(sorted(informations)),
            ]
        )
    )
    Script.parseCommandLine(ignoreErrors=True)

    from LHCbDIRAC.TransformationSystem.Client.TransformationClient import TransformationClient
    from LHCbDIRAC.TransformationSystem.Utilities.ScriptUtilities import getTransformations

    from DIRAC import gLogger

    tr = TransformationClient()

    requestedInfo = informations
    switches = Script.getUnprocessedSwitches()
    infoList = []
    for switch, val in switches:
        if switch == "Information":
            infoList = [info.lower() for info in val.split(",")]
            requestedInfo = [info for info in informations if info.lower() in infoList]
    if "body" not in infoList and "Body" in requestedInfo:
        requestedInfo.remove("Body")

    transIDs = getTransformations(Script.getPositionalArgs())

    for transID in transIDs:
        try:
            res = tr.getTransformation(int(transID))
            gLogger.notice("==== Transformation %s ====" % transID)
            for info in requestedInfo:
                getInfo = info if info != "Request" else "TransformationFamily"
                gLogger.notice("\t%s: %s" % (info, res.get("Value", {}).get(getInfo, "Unknown")))
        except Exception:
            gLogger.error("Invalid transformation ID: '%s'" % transID)


if __name__ == "__main__":
    main()
