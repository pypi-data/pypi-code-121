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
import os
import sys
from time import time

from DIRAC.Core.Base.Script import Script


@Script()
def main():
    from DIRAC import exit, gLogger

    Script.registerSwitch("", "User=", "  User name")
    Script.registerSwitch("", "Recursive", "  Set ownership recursively")
    Script.registerSwitch("", "Directory=", "   Directory to change the ownership of")
    Script.registerSwitch("", "Group=", "   Group name (default lhcb_user)")
    Script.registerSwitch("", "Mode=", "   Change permission mode (default: not changed)")
    Script.registerSwitch("", "Create", "   Use for creating the directory if it does not exist")

    Script.parseCommandLine()

    user = None
    recursive = False
    group = None
    dirList = None
    mode = None
    create = False
    for switch in Script.getUnprocessedSwitches():
        if switch[0] == "User":
            user = switch[1].lower()
        elif switch[0] == "Recursive":
            recursive = True
        elif switch[0] == "Directory":
            dirList = switch[1].split(",")
        elif switch[0] == "Group":
            group = switch[1]
        elif switch[0] == "Mode":
            mode = int(switch[1], base=8)
        elif switch[0] == "Create":
            create = True

    args = Script.getPositionalArgs()
    if dirList is None and args:
        dirList = []
        for arg in args:
            dirList += arg.split(",")

    toChange = []
    if user:
        toChange.append("user")
    if group:
        toChange.append("group")
    if mode:
        toChange.append("mode")
    toChange = ",".join(toChange)

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

    if group and not group.startswith("lhcb_"):
        gLogger.fatal("This is not a valid group", group)
        exit(1)

    directories = set()
    for baseDir in dirList:
        if os.path.exists(baseDir):
            f = open(baseDir)
            directories.update([os.path.dirname(line.split()[0] + "/") for line in f.read().splitlines()])
            f.close()
        else:
            directories.add(baseDir if not baseDir.endswith("/") else baseDir[:-1])

    if not directories or (user is None and group is None and mode is None):
        Script.showHelp(exitCode=1)

    from LHCbDIRAC.DataManagementSystem.Client.DMScript import ProgressBar
    from DIRAC.Resources.Catalog.FileCatalogClient import FileCatalogClient

    dfc = FileCatalogClient()

    success = 0
    startTime = time()
    progressBar = ProgressBar(
        len(directories),
        title="Changing %s%s to %d directories:" % (toChange, " recursively" if recursive else "", len(directories)),
        chunk=1,
        interactive=True,
    )
    errors = {}
    for baseDir in directories:
        progressBar.loop()
        if not baseDir.startswith("/lhcb"):
            errors[baseDir] = "Not a valid directory"
            continue
        if not dfc.isDirectory(baseDir).get("Value", {}).get("Successful", {}).get(baseDir):
            if create:
                res = dfc.createDirectory(baseDir)
                if not res["OK"]:
                    errors[baseDir] = res["Message"] + " while creating directory"
                    continue
            else:
                errors[baseDir] = "Directory doesn't exist"
                continue
        res = chown(baseDir, user, group=group, mode=mode, recursive=recursive, fcClient=dfc)
        if not res["OK"]:
            errors[baseDir] = res["Message"] + " executing %s: " % res["Action"]
        else:
            success += res["Value"]

    if success:
        msg = "Successfully changed %s%s in %d directories" % (toChange, " recursively" if recursive else "", success)
    else:
        msg = "Failed changing %s%s in %d directories" % (
            toChange,
            " recursively" if recursive else "",
            len(directories),
        )
    progressBar.endLoop(msg)
    retCode = 0
    if errors:
        retCode = 1
        gLogger.notice("Errors:")
        for baseDir, error in errors.items():
            gLogger.notice("\tDirectory %s - " % baseDir, error)
    elif len(directories) == 1:
        from LHCbDIRAC.DataManagementSystem.Client.DMScript import DMScript
        from LHCbDIRAC.DataManagementSystem.Client.ScriptExecutors import executeLfnMetadata

        dmScript = DMScript()
        dmScript.setLFNs(list(directories)[0])
        sys.stdout.write("Directory metadata: ")
        sys.stdout.flush()
        executeLfnMetadata(dmScript)
    exit(retCode)


if __name__ == "__main__":
    main()
