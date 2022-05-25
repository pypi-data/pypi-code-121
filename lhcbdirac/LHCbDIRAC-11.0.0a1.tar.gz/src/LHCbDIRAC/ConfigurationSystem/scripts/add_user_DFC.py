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
"""This script adds a user directory to the DFC or changes a user directory's
ownership."""
import os
import sys
from time import time

from DIRAC.Core.Base.Script import Script


@Script()
def main():
    from DIRAC import exit, gLogger

    Script.registerSwitch("", "User=", "  User name (no default, mandatory)")
    Script.registerSwitch("", "Recursive", "  Set ownership recursively for existing user")

    Script.parseCommandLine()

    user = None
    recursive = False
    group = "lhcb_user"
    for switch in Script.getUnprocessedSwitches():
        if switch[0] == "User":
            user = switch[1].lower()
        elif switch[0] == "Recursive":
            recursive = True

    from DIRAC.Core.Security.ProxyInfo import getProxyInfo
    from LHCbDIRAC.DataManagementSystem.Utilities.FCUtilities import chown

    res = getProxyInfo()
    if not res["OK"]:
        gLogger.fatal("Can't get proxy info", res["Message"])
        exit(1)
    properties = res["Value"].get("groupProperties", [])
    if "FileCatalogManagement" not in properties:
        gLogger.error("You need to use a proxy from a group with FileCatalogManagement")
        exit(5)

    from DIRAC.Resources.Catalog.FileCatalogClient import FileCatalogClient

    dfc = FileCatalogClient()

    if user is None:
        Script.showHelp(exitCode=1)

    exists = False
    initial = user[0]
    baseDir = os.path.join("/lhcb", "user", initial, user)
    subDirectories = []
    if dfc.isDirectory(baseDir).get("Value", {}).get("Successful", {}).get(baseDir):
        gLogger.always("Directory already existing", baseDir)
        exists = True
        res = dfc.listDirectory(baseDir)
        if res["OK"]:
            success = res["Value"]["Successful"][baseDir]
            subDirectories = success["SubDirs"]
            if success.get("SubDirs") or success.get("Files"):
                gLogger.always(
                    "Directory is not empty:",
                    " %d files / %d subdirectories" % (len(success["Files"]), len(success["SubDirs"])),
                )
            elif recursive:
                gLogger.always("Empty directory, recursive is useless...")
                recursive = False
    if not exists:
        gLogger.always("Creating directory", baseDir)
        res = dfc.createDirectory(baseDir)
        if not res["OK"]:
            gLogger.fatal("Error creating directory", res["Message"])
            exit(2)
    else:
        gLogger.always("Change%s ownership of directory" % " recursively" if recursive else "", baseDir)
    res = chown(baseDir, user, group="lhcb_user", mode=0o755, recursive=False, fcClient=dfc)
    if not res["OK"]:
        gLogger.fatal("Error changing directory owner", res["Message"])
        exit(2)
    startTime = time()
    if recursive and subDirectories:
        res = chown(subDirectories, user, group="lhcb_user", mode=0o755, recursive=True, ndirs=1, fcClient=dfc)
        if not res["OK"]:
            gLogger.fatal("Error changing directory owner", res["Message"])
            exit(2)
        gLogger.always(
            "Successfully changed owner in %d directories in %.1f seconds" % (res["Value"], time() - startTime)
        )
    else:
        gLogger.always("Successfully changed owner in directory %s in %.1f seconds" % (baseDir, time() - startTime))

    from LHCbDIRAC.DataManagementSystem.Client.DMScript import DMScript
    from LHCbDIRAC.DataManagementSystem.Client.ScriptExecutors import executeLfnMetadata

    dmScript = DMScript()
    dmScript.setLFNs(baseDir)
    sys.stdout.write("Directory metadata: ")
    sys.stdout.flush()
    executeLfnMetadata(dmScript)
    exit(0)


if __name__ == "__main__":
    main()
