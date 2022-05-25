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
"""Get the GUID of a (set of) ROOT file The file can be either local, an LFN or
an xrootd URL (root:...)"""
import os

from DIRAC.Core.Base.Script import Script


@Script()
def main():

    Script.setUsageMessage(
        "\n".join([__doc__, "Usage:", "  %s [option|cfgfile] file1 [file2 ...]" % Script.scriptName])
    )
    Script.parseCommandLine(ignoreErrors=True)
    files = []
    for oFile in Script.getPositionalArgs():
        files += oFile.split(",")

    import DIRAC
    from DIRAC.Interfaces.API.Dirac import Dirac
    from LHCbDIRAC.Core.Utilities.File import getRootFileGUIDs
    from LHCbDIRAC.DataManagementSystem.Client.DMScript import printDMResult

    if not files:
        Script.showHelp(exitCode=1)
    existFiles = {}
    nonExisting = []
    dirac = Dirac()

    for localFile in files:
        if os.path.exists(localFile):
            existFiles[os.path.realpath(localFile)] = localFile
        elif localFile.startswith("/lhcb"):
            res = dirac.getReplicas(localFile, active=True, preferDisk=True)
            if res["OK"] and localFile in res["Value"]["Successful"]:
                ses = list(res["Value"]["Successful"][localFile])
                for se in ses:
                    res = dirac.getAccessURL(localFile, se, protocol=["root", "xroot"])
                    if res["OK"] and localFile in res["Value"]["Successful"]:
                        existFiles[res["Value"]["Successful"][localFile]] = "%s @ %s" % (localFile, se)
            else:
                nonExisting.append(localFile)
        elif localFile.startswith("root:"):
            existFiles[localFile] = localFile
        else:
            nonExisting.append(localFile)

    fileGUIDs = getRootFileGUIDs(list(existFiles))
    for status in ("Successful", "Failed"):
        for file in list(fileGUIDs.get("Value", {}).get(status, {})):
            fileGUIDs["Value"][status][existFiles.get(file, file)] = fileGUIDs["Value"][status].pop(file)
    if nonExisting:
        fileGUIDs["Value"]["Failed"].update(dict.fromkeys(nonExisting, "Non existing file"))
    printDMResult(fileGUIDs)

    DIRAC.exit(0)


if __name__ == "__main__":
    main()
